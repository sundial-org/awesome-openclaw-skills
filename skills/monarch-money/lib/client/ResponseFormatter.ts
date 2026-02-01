/**
 * Response formatters for different verbosity levels
 * Optimizes context usage for MCP and other integrations
 */

export type VerbosityLevel = 'ultra-light' | 'light' | 'standard';

export class ResponseFormatter {
  /**
   * Format accounts based on verbosity level
   */
  static formatAccounts(accounts: any[], verbosity: VerbosityLevel): string {
    switch (verbosity) {
      case 'ultra-light': {
        const total = accounts.reduce((sum, acc) => sum + (acc.currentBalance || 0), 0);
        return `💰 ${accounts.length} accounts, Total: $${total.toLocaleString()}`;
      }

      case 'light':
        return accounts.map(acc => {
          const balance = acc.currentBalance || 0;
          const hiddenFlag = acc.isHidden ? ' (hidden)' : '';
          return `• ${acc.displayName}: $${balance.toLocaleString()}${hiddenFlag}`;
        }).join('\n') +
        `\n\nTotal: $${accounts.reduce((s, a) => s + (a.currentBalance || 0), 0).toLocaleString()}`;

      default: // standard - return raw data as JSON string
        return JSON.stringify(accounts, null, 2);
    }
  }

  /**
   * Format transactions based on verbosity level
   */
  static formatTransactions(transactions: any[], verbosity: VerbosityLevel, originalQuery?: string): string {
    if (!transactions.length) return '';

    const header = originalQuery ? `🧠 **Smart Query**: "${originalQuery}"\n\n` : '';

    switch (verbosity) {
      case 'ultra-light': {
        const total = transactions.reduce((sum, txn) => sum + Math.abs(txn.amount), 0);
        return `${header}💳 ${transactions.length} transactions, Volume: $${total.toLocaleString()}`;
      }

      case 'light':
        return header + transactions.map(txn => {
          const date = new Date(txn.date).toLocaleDateString();
          const amount = Math.abs(txn.amount).toLocaleString();
          const merchant = txn.merchant?.name || 'Unknown merchant';
          const category = txn.category?.name || 'Uncategorized';

          return `• ${date} - ${merchant}\n  ${txn.amount < 0 ? '-' : ''}$${amount} • ${category}`;
        }).join('\n');

      default: // standard - return raw data as JSON string
        return JSON.stringify(transactions, null, 2);
    }
  }

  /**
   * Format quick financial overview (ultra-compact)
   */
  static formatQuickStats(accounts: any[], recentTransactions?: any[]): string {
    const totalBalance = accounts
      .filter(acc => acc.includeInNetWorth)
      .reduce((sum, acc) => sum + (acc.currentBalance || 0), 0);

    const accountCount = accounts.length;

    // Calculate month-over-month change (simplified)
    const thisMonth = recentTransactions?.filter(t => {
      const txnDate = new Date(t.date);
      const now = new Date();
      return txnDate.getMonth() === now.getMonth() && txnDate.getFullYear() === now.getFullYear();
    }) || [];

    const monthlyChange = thisMonth.reduce((sum, t) => sum + t.amount, 0);
    const changeSymbol = monthlyChange >= 0 ? '⬆️' : '⬇️';

    return `💰 $${totalBalance.toLocaleString()} • ${changeSymbol} ${monthlyChange >= 0 ? '+' : ''}$${Math.abs(monthlyChange).toLocaleString()} • 📊 ${accountCount} accounts`;
  }

  /**
   * Format spending by category summary (ultra-compact)
   */
  static formatSpendingSummary(transactions: any[], topN: number = 5): string {
    // Group by category and sum amounts
    const categoryTotals = new Map<string, number>();

    transactions.forEach(txn => {
      if (txn.amount < 0) { // Only expenses
        const category = txn.category?.name || 'Uncategorized';
        categoryTotals.set(category, (categoryTotals.get(category) || 0) + Math.abs(txn.amount));
      }
    });

    // Sort and take top N
    const sortedCategories = Array.from(categoryTotals.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, topN);

    if (sortedCategories.length === 0) {
      return '💸 No expenses found';
    }

    // Create ultra-compact summary
    const topCategoriesStr = sortedCategories
      .slice(0, 3)
      .map(([category, amount]) => {
        const icon = this.getCategoryIcon(category);
        return `${icon} $${Math.round(amount).toLocaleString()}`;
      })
      .join(' • ');

    return topCategoriesStr + ` (top ${Math.min(3, sortedCategories.length)} this month)`;
  }

  /**
   * Get emoji icon for category
   */
  private static getCategoryIcon(category: string): string {
    const categoryIcons: Record<string, string> = {
      'dining': '🍽️',
      'restaurants': '🍽️',
      'food': '🍽️',
      'groceries': '🛒',
      'gas': '⛽',
      'fuel': '⛽',
      'transportation': '🚗',
      'shopping': '🛍️',
      'entertainment': '🎬',
      'utilities': '⚡',
      'rent': '🏠',
      'mortgage': '🏠',
      'insurance': '🛡️',
      'healthcare': '🏥',
      'medical': '🏥',
      'travel': '✈️',
      'education': '📚',
      'fitness': '💪',
      'subscriptions': '📱',
      'income': '💰',
      'salary': '💰'
    };

    const lowerCategory = category.toLowerCase();
    for (const [key, icon] of Object.entries(categoryIcons)) {
      if (lowerCategory.includes(key)) {
        return icon;
      }
    }

    return '💸'; // Default expense icon
  }
}