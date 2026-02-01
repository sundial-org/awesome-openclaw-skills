class BudgetManager {
  constructor(ledger) {
    this.ledger = ledger;
  }

  async setBudget(category, amount, period = 'monthly', options = {}) {
    const budgets = await this.ledger.loadBudgets();
    
    const budget = {
      amount: parseFloat(amount),
      period: period,
      currency: options.currency || 'USD',
      alertThreshold: options.alertThreshold || 80, // Alert at 80%
      created: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      enabled: true
    };

    budgets[category] = budget;
    await this.ledger.saveBudgets(budgets);
    
    return budget;
  }

  async getBudget(category) {
    const budgets = await this.ledger.loadBudgets();
    return budgets[category] || null;
  }

  async getAllBudgets() {
    return await this.ledger.loadBudgets();
  }

  async removeBudget(category) {
    const budgets = await this.ledger.loadBudgets();
    if (budgets[category]) {
      delete budgets[category];
      await this.ledger.saveBudgets(budgets);
      return true;
    }
    return false;
  }

  async checkBudget(category, period = null) {
    const budget = await this.getBudget(category);
    if (!budget || (budget.enabled === false)) {
      return { hasBudget: false };
    }

    // Use budget period if no specific period provided
    const checkPeriod = period || this.convertBudgetPeriodToTimePeriod(budget.period);
    
    const spent = await this.ledger.getCategorySpending(category, checkPeriod);
    const percentUsed = (spent / budget.amount) * 100;
    const remaining = budget.amount - spent;
    
    const alertThreshold = budget.alertThreshold || 80; // Default to 80%
    
    return {
      hasBudget: true,
      category: category,
      budgetAmount: budget.amount,
      spent: spent,
      remaining: remaining,
      percentUsed: percentUsed,
      isOverBudget: spent > budget.amount,
      isNearLimit: percentUsed >= alertThreshold,
      alertThreshold: alertThreshold,
      period: budget.period || 'monthly',
      daysRemaining: this.getDaysRemainingInPeriod(budget.period || 'monthly')
    };
  }

  async checkAllBudgets() {
    const budgets = await this.getAllBudgets();
    const results = {};
    
    for (const category of Object.keys(budgets)) {
      results[category] = await this.checkBudget(category);
    }
    
    return results;
  }

  async getAlerts() {
    const budgetStatuses = await this.checkAllBudgets();
    const alerts = [];
    
    for (const [category, status] of Object.entries(budgetStatuses)) {
      if (!status.hasBudget) continue;
      
      if (status.isOverBudget) {
        alerts.push({
          type: 'OVER_BUDGET',
          severity: 'HIGH',
          category: category,
          message: `🔴 OVER BUDGET: ${category} - $${status.spent.toFixed(2)} / $${status.budgetAmount} (${status.percentUsed.toFixed(1)}%)`,
          details: status
        });
      } else if (status.isNearLimit) {
        alerts.push({
          type: 'NEAR_LIMIT',
          severity: 'MEDIUM',
          category: category,
          message: `🟡 NEAR LIMIT: ${category} - $${status.spent.toFixed(2)} / $${status.budgetAmount} (${status.percentUsed.toFixed(1)}%)`,
          details: status
        });
      }
    }
    
    return alerts;
  }

  async generateBudgetReport() {
    const budgetStatuses = await this.checkAllBudgets();
    const alerts = await this.getAlerts();
    
    let report = `💰 Budget Report\n`;
    report += `Generated: ${new Date().toLocaleDateString()}\n`;
    report += `═══════════════════════════════════════════\n\n`;
    
    // Alerts section
    if (alerts.length > 0) {
      report += `🚨 ALERTS (${alerts.length}):\n`;
      for (const alert of alerts) {
        report += `   ${alert.message}\n`;
      }
      report += '\n';
    } else {
      report += `✅ No budget alerts - all spending within limits!\n\n`;
    }
    
    // Detailed budget status
    report += `📊 Budget Status:\n`;
    
    for (const [category, status] of Object.entries(budgetStatuses)) {
      if (!status.hasBudget) continue;
      
      const emoji = status.isOverBudget ? '🔴' : status.isNearLimit ? '🟡' : '🟢';
      const progressBar = this.createProgressBar(status.percentUsed);
      
      report += `   ${emoji} ${category} (${status.period})\n`;
      report += `      ${progressBar} ${status.percentUsed.toFixed(1)}%\n`;
      report += `      $${status.spent.toFixed(2)} / $${status.budgetAmount} (${status.remaining >= 0 ? '+' : ''}$${status.remaining.toFixed(2)} remaining)\n`;
      
      if (status.daysRemaining !== null) {
        const dailyBudget = status.remaining / Math.max(1, status.daysRemaining);
        report += `      Daily budget remaining: $${dailyBudget.toFixed(2)} (${status.daysRemaining} days left)\n`;
      }
      report += '\n';
    }
    
    return report;
  }

  async predictBudgetStatus(category, additionalSpending = 0) {
    const currentStatus = await this.checkBudget(category);
    if (!currentStatus.hasBudget) {
      return { hasBudget: false };
    }

    const projectedSpent = currentStatus.spent + additionalSpending;
    const projectedPercentUsed = (projectedSpent / currentStatus.budgetAmount) * 100;
    const projectedRemaining = currentStatus.budgetAmount - projectedSpent;
    
    return {
      ...currentStatus,
      projectedSpent,
      projectedPercentUsed,
      projectedRemaining,
      willExceedBudget: projectedSpent > currentStatus.budgetAmount,
      additionalSpending
    };
  }

  async suggestBudgetAdjustment(category) {
    // Look at last 3 months of spending to suggest budget
    const transactions = await this.ledger.loadTransactions();
    const last3Months = transactions.filter(t => {
      const date = new Date(t.timestamp);
      const threeMonthsAgo = new Date();
      threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
      return date >= threeMonthsAgo && t.category === category;
    });

    if (last3Months.length === 0) {
      return null;
    }

    // Calculate monthly averages
    const monthlySpending = {};
    last3Months.forEach(t => {
      const month = t.timestamp.substring(0, 7);
      monthlySpending[month] = (monthlySpending[month] || 0) + t.amount;
    });

    const months = Object.values(monthlySpending);
    const averageMonthly = months.reduce((a, b) => a + b, 0) / months.length;
    const maxMonthly = Math.max(...months);
    const minMonthly = Math.min(...months);

    // Suggest budget with 20% buffer above average
    const suggestedBudget = averageMonthly * 1.2;

    return {
      category,
      currentAverage: averageMonthly,
      historicalRange: { min: minMonthly, max: maxMonthly },
      suggestedBudget,
      confidence: months.length >= 3 ? 'high' : 'medium'
    };
  }

  convertBudgetPeriodToTimePeriod(budgetPeriod) {
    switch (budgetPeriod) {
      case 'daily':
        return 'today';
      case 'weekly':
        return 'this-week';
      case 'monthly':
        return 'this-month';
      case 'quarterly':
        return 'this-quarter';
      case 'yearly':
        return 'this-year';
      default:
        return 'this-month';
    }
  }

  getDaysRemainingInPeriod(period) {
    const now = new Date();
    
    switch (period) {
      case 'daily':
        return 0; // Already in the day
      case 'weekly':
        const endOfWeek = new Date(now);
        endOfWeek.setDate(now.getDate() + (6 - now.getDay()));
        return Math.ceil((endOfWeek - now) / (1000 * 60 * 60 * 24));
      case 'monthly':
        const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        return Math.ceil((endOfMonth - now) / (1000 * 60 * 60 * 24));
      case 'quarterly':
        const quarter = Math.floor(now.getMonth() / 3);
        const endOfQuarter = new Date(now.getFullYear(), (quarter + 1) * 3, 0);
        return Math.ceil((endOfQuarter - now) / (1000 * 60 * 60 * 24));
      case 'yearly':
        const endOfYear = new Date(now.getFullYear(), 11, 31);
        return Math.ceil((endOfYear - now) / (1000 * 60 * 60 * 24));
      default:
        return null;
    }
  }

  createProgressBar(percentage, width = 20) {
    const filled = Math.round((Math.min(percentage, 100) / 100) * width);
    const empty = width - filled;
    
    let bar = '';
    if (percentage <= 50) {
      bar = '🟢'.repeat(filled);
    } else if (percentage <= 80) {
      bar = '🟡'.repeat(filled);
    } else {
      bar = '🔴'.repeat(filled);
    }
    
    bar += '⚪'.repeat(empty);
    return bar;
  }

  async setBudgetAlert(category, threshold) {
    const budgets = await this.ledger.loadBudgets();
    if (budgets[category]) {
      budgets[category].alertThreshold = threshold;
      budgets[category].lastModified = new Date().toISOString();
      await this.ledger.saveBudgets(budgets);
      return true;
    }
    return false;
  }

  async enableBudget(category, enabled = true) {
    const budgets = await this.ledger.loadBudgets();
    if (budgets[category]) {
      budgets[category].enabled = enabled;
      budgets[category].lastModified = new Date().toISOString();
      await this.ledger.saveBudgets(budgets);
      return true;
    }
    return false;
  }

  async copyBudgetToPeriod(category, targetPeriod) {
    const budget = await this.getBudget(category);
    if (!budget) {
      throw new Error(`No budget found for category: ${category}`);
    }

    // Create a new budget with the same amount but different period
    return await this.setBudget(category, budget.amount, targetPeriod, {
      currency: budget.currency,
      alertThreshold: budget.alertThreshold
    });
  }

  async getBudgetHistory(category, months = 6) {
    const transactions = await this.ledger.loadTransactions();
    const history = {};
    const now = new Date();

    // Get spending for each of the last N months
    for (let i = months - 1; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthKey = date.toISOString().substring(0, 7);
      const monthName = date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
      
      const monthTransactions = transactions.filter(t => 
        t.timestamp.startsWith(monthKey) && t.category === category
      );
      
      const spent = monthTransactions.reduce((sum, t) => sum + t.amount, 0);
      
      history[monthName] = {
        spent,
        count: monthTransactions.length,
        date: monthKey
      };
    }

    return history;
  }
}

module.exports = BudgetManager;