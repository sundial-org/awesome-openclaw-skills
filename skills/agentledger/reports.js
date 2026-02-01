class Reports {
  constructor(ledger) {
    this.ledger = ledger;
  }

  async generate(type, options = {}) {
    switch (type) {
      case 'monthly':
        return await this.generateMonthlyReport(options);
      case 'category':
        return await this.generateCategoryReport(options);
      case 'vendor':
        return await this.generateVendorReport(options);
      case 'trend':
        return await this.generateTrendReport(options);
      case 'custom':
        return await this.generateCustomReport(options);
      default:
        throw new Error(`Unknown report type: ${type}`);
    }
  }

  async generateMonthlyReport(options = {}) {
    const month = options.month || new Date().toISOString().substring(0, 7);
    const [year, monthNum] = month.split('-');
    const monthName = new Date(year, monthNum - 1).toLocaleDateString('en-US', { month: 'long' });
    
    const period = options.month ? 
      await this.getCustomPeriod(`${month}-01`, `${month}-31`) : 
      'this-month';
    
    const transactions = await this.ledger.loadTransactions();
    const filtered = this.ledger.filterTransactionsByPeriod(transactions, period);
    
    if (filtered.length === 0) {
      return `📊 Monthly Report - ${monthName} ${year}\n\nNo transactions found for this period.`;
    }

    const summary = this.calculateSummary(filtered);
    const categoryBreakdown = this.calculateCategoryBreakdown(filtered);
    const topVendors = this.getTopVendors(filtered, 5);
    const dailySpending = this.calculateDailySpending(filtered);

    let report = `📊 Monthly Report - ${monthName} ${year}\n`;
    report += `═══════════════════════════════════════════\n\n`;
    
    // Summary
    report += `💰 Summary:\n`;
    report += `   Total Spent: $${summary.total.toFixed(2)}\n`;
    report += `   Transactions: ${summary.count}\n`;
    report += `   Average: $${summary.average.toFixed(2)}\n`;
    report += `   Largest: $${summary.largest.toFixed(2)}\n`;
    report += `   Smallest: $${summary.smallest.toFixed(2)}\n\n`;

    // Category breakdown
    report += `📂 Spending by Category:\n`;
    for (const [category, data] of Object.entries(categoryBreakdown)) {
      const percentage = ((data.amount / summary.total) * 100).toFixed(1);
      report += `   ${category}: $${data.amount.toFixed(2)} (${percentage}%) - ${data.count} transactions\n`;
    }
    report += '\n';

    // Top vendors
    report += `🏪 Top Vendors:\n`;
    for (let i = 0; i < topVendors.length; i++) {
      const vendor = topVendors[i];
      report += `   ${i + 1}. ${vendor.name}: $${vendor.amount.toFixed(2)} (${vendor.count} transactions)\n`;
    }
    report += '\n';

    // Daily spending trend
    report += `📈 Daily Spending Pattern:\n`;
    const maxDaily = Math.max(...Object.values(dailySpending));
    for (const [day, amount] of Object.entries(dailySpending)) {
      const barLength = Math.round((amount / maxDaily) * 20);
      const bar = '█'.repeat(barLength) + '░'.repeat(20 - barLength);
      report += `   ${day}: ${bar} $${amount.toFixed(2)}\n`;
    }

    // Budget comparison if budgets exist
    const budgets = await this.ledger.loadBudgets();
    if (Object.keys(budgets).length > 0) {
      report += '\n💰 Budget Comparison:\n';
      for (const [category, budget] of Object.entries(budgets)) {
        const spent = categoryBreakdown[category]?.amount || 0;
        const percentage = (spent / budget.amount) * 100;
        const status = percentage > 100 ? '🔴 OVER' : percentage > 80 ? '🟡 NEAR' : '🟢 OK';
        report += `   ${category}: ${status} $${spent.toFixed(2)} / $${budget.amount} (${percentage.toFixed(1)}%)\n`;
      }
    }

    return report;
  }

  async generateCategoryReport(options = {}) {
    const period = options.period || 'this-month';
    const transactions = await this.ledger.loadTransactions();
    const filtered = this.ledger.filterTransactionsByPeriod(transactions, period);
    
    const categoryData = {};
    
    filtered.forEach(t => {
      if (!categoryData[t.category]) {
        categoryData[t.category] = {
          transactions: [],
          total: 0,
          count: 0
        };
      }
      categoryData[t.category].transactions.push(t);
      categoryData[t.category].total += t.amount;
      categoryData[t.category].count++;
    });

    let report = `📂 Category Report (${period})\n`;
    report += `═══════════════════════════════════\n\n`;

    for (const [category, data] of Object.entries(categoryData).sort((a, b) => b[1].total - a[1].total)) {
      report += `📁 ${category}\n`;
      report += `   Total: $${data.total.toFixed(2)} (${data.count} transactions)\n`;
      report += `   Average: $${(data.total / data.count).toFixed(2)} per transaction\n`;
      
      // Top vendors in this category
      const vendors = {};
      data.transactions.forEach(t => {
        vendors[t.vendor] = (vendors[t.vendor] || 0) + t.amount;
      });
      
      const topVendors = Object.entries(vendors)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3);
        
      if (topVendors.length > 0) {
        report += `   Top vendors:\n`;
        topVendors.forEach(([vendor, amount]) => {
          report += `     • ${vendor}: $${amount.toFixed(2)}\n`;
        });
      }
      report += '\n';
    }

    return report;
  }

  async generateVendorReport(options = {}) {
    const period = options.period || 'this-month';
    const transactions = await this.ledger.loadTransactions();
    const filtered = this.ledger.filterTransactionsByPeriod(transactions, period);
    
    const vendorData = {};
    
    filtered.forEach(t => {
      if (!vendorData[t.vendor]) {
        vendorData[t.vendor] = {
          transactions: [],
          total: 0,
          count: 0,
          categories: {}
        };
      }
      vendorData[t.vendor].transactions.push(t);
      vendorData[t.vendor].total += t.amount;
      vendorData[t.vendor].count++;
      vendorData[t.vendor].categories[t.category] = (vendorData[t.vendor].categories[t.category] || 0) + t.amount;
    });

    let report = `🏪 Vendor Report (${period})\n`;
    report += `═══════════════════════════════════\n\n`;

    const sortedVendors = Object.entries(vendorData)
      .sort((a, b) => b[1].total - a[1].total)
      .slice(0, 10); // Top 10 vendors

    for (const [vendor, data] of sortedVendors) {
      report += `🏪 ${vendor}\n`;
      report += `   Total: $${data.total.toFixed(2)} (${data.count} transactions)\n`;
      report += `   Average: $${(data.total / data.count).toFixed(2)} per transaction\n`;
      
      // Categories for this vendor
      const categories = Object.entries(data.categories)
        .sort((a, b) => b[1] - a[1]);
        
      if (categories.length > 1) {
        report += `   Categories:\n`;
        categories.forEach(([category, amount]) => {
          const percentage = ((amount / data.total) * 100).toFixed(1);
          report += `     • ${category}: $${amount.toFixed(2)} (${percentage}%)\n`;
        });
      }

      // Recent transactions
      const recent = data.transactions
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 3);
        
      if (recent.length > 0) {
        report += `   Recent transactions:\n`;
        recent.forEach(t => {
          const date = new Date(t.timestamp).toLocaleDateString();
          report += `     • ${date}: $${t.amount} - ${t.description}\n`;
        });
      }
      report += '\n';
    }

    return report;
  }

  async generateTrendReport(options = {}) {
    const months = options.months || 6;
    const transactions = await this.ledger.loadTransactions();
    
    const monthlyData = {};
    const now = new Date();
    
    // Initialize months
    for (let i = months - 1; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthKey = date.toISOString().substring(0, 7);
      monthlyData[monthKey] = {
        total: 0,
        count: 0,
        categories: {}
      };
    }

    // Populate data
    transactions.forEach(t => {
      const monthKey = t.timestamp.substring(0, 7);
      if (monthlyData[monthKey]) {
        monthlyData[monthKey].total += t.amount;
        monthlyData[monthKey].count++;
        monthlyData[monthKey].categories[t.category] = 
          (monthlyData[monthKey].categories[t.category] || 0) + t.amount;
      }
    });

    let report = `📈 Trend Report (Last ${months} Months)\n`;
    report += `══════════════════════════════════════════\n\n`;

    // Monthly totals
    report += `💰 Monthly Spending:\n`;
    const maxMonthly = Math.max(...Object.values(monthlyData).map(m => m.total));
    
    for (const [month, data] of Object.entries(monthlyData)) {
      const monthName = new Date(month + '-01').toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
      const barLength = Math.round((data.total / maxMonthly) * 30);
      const bar = '█'.repeat(barLength) + '░'.repeat(30 - barLength);
      report += `   ${monthName}: ${bar} $${data.total.toFixed(2)} (${data.count} transactions)\n`;
    }

    // Category trends
    report += '\n📂 Category Trends:\n';
    const allCategories = [...new Set(
      Object.values(monthlyData)
        .flatMap(m => Object.keys(m.categories))
    )];

    for (const category of allCategories) {
      const categoryTotals = Object.values(monthlyData)
        .map(m => m.categories[category] || 0);
      const total = categoryTotals.reduce((a, b) => a + b, 0);
      
      if (total > 0) {
        const trend = this.calculateTrend(categoryTotals);
        const trendIndicator = trend > 5 ? '📈' : trend < -5 ? '📉' : '➡️';
        report += `   ${category}: ${trendIndicator} $${total.toFixed(2)} total, ${trend.toFixed(1)}% trend\n`;
      }
    }

    return report;
  }

  async generateCustomReport(options = {}) {
    if (!options.startDate || !options.endDate) {
      throw new Error('Custom report requires startDate and endDate');
    }

    const transactions = await this.ledger.loadTransactions();
    const filtered = transactions.filter(t => {
      const date = new Date(t.timestamp);
      return date >= new Date(options.startDate) && date <= new Date(options.endDate);
    });

    const summary = this.calculateSummary(filtered);
    
    let report = `📊 Custom Report\n`;
    report += `Period: ${options.startDate} to ${options.endDate}\n`;
    report += `═══════════════════════════════════════════\n\n`;
    
    report += `💰 Summary:\n`;
    report += `   Total: $${summary.total.toFixed(2)}\n`;
    report += `   Transactions: ${summary.count}\n`;
    report += `   Daily Average: $${(summary.total / this.getDaysBetween(options.startDate, options.endDate)).toFixed(2)}\n\n`;

    // Add category breakdown
    const categoryBreakdown = this.calculateCategoryBreakdown(filtered);
    report += `📂 By Category:\n`;
    for (const [category, data] of Object.entries(categoryBreakdown)) {
      const percentage = ((data.amount / summary.total) * 100).toFixed(1);
      report += `   ${category}: $${data.amount.toFixed(2)} (${percentage}%)\n`;
    }

    return report;
  }

  calculateSummary(transactions) {
    const amounts = transactions.map(t => t.amount);
    return {
      total: amounts.reduce((a, b) => a + b, 0),
      count: transactions.length,
      average: amounts.reduce((a, b) => a + b, 0) / amounts.length || 0,
      largest: Math.max(...amounts, 0),
      smallest: Math.min(...amounts, Infinity) === Infinity ? 0 : Math.min(...amounts)
    };
  }

  calculateCategoryBreakdown(transactions) {
    const breakdown = {};
    
    transactions.forEach(t => {
      if (!breakdown[t.category]) {
        breakdown[t.category] = { amount: 0, count: 0 };
      }
      breakdown[t.category].amount += t.amount;
      breakdown[t.category].count++;
    });

    // Sort by amount
    const sorted = Object.entries(breakdown)
      .sort((a, b) => b[1].amount - a[1].amount)
      .reduce((obj, [key, value]) => {
        obj[key] = value;
        return obj;
      }, {});

    return sorted;
  }

  getTopVendors(transactions, limit = 5) {
    const vendors = {};
    
    transactions.forEach(t => {
      if (!vendors[t.vendor]) {
        vendors[t.vendor] = { amount: 0, count: 0 };
      }
      vendors[t.vendor].amount += t.amount;
      vendors[t.vendor].count++;
    });

    return Object.entries(vendors)
      .sort((a, b) => b[1].amount - a[1].amount)
      .slice(0, limit)
      .map(([name, data]) => ({ name, ...data }));
  }

  calculateDailySpending(transactions) {
    const daily = {};
    
    transactions.forEach(t => {
      const day = new Date(t.timestamp).toLocaleDateString('en-US', { 
        weekday: 'short' 
      });
      daily[day] = (daily[day] || 0) + t.amount;
    });

    // Ensure all days are represented
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const result = {};
    days.forEach(day => {
      result[day] = daily[day] || 0;
    });

    return result;
  }

  calculateTrend(values) {
    if (values.length < 2) return 0;
    
    const recent = values.slice(-3).reduce((a, b) => a + b, 0) / Math.min(3, values.length);
    const earlier = values.slice(0, -3).reduce((a, b) => a + b, 0) / Math.max(1, values.length - 3);
    
    if (earlier === 0) return recent > 0 ? 100 : 0;
    
    return ((recent - earlier) / earlier) * 100;
  }

  getDaysBetween(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const timeDiff = end.getTime() - start.getTime();
    return Math.ceil(timeDiff / (1000 * 3600 * 24)) + 1;
  }

  async getCustomPeriod(start, end) {
    // This would need to be implemented in the main ledger class
    // For now, return a placeholder
    return 'custom';
  }
}

module.exports = Reports;