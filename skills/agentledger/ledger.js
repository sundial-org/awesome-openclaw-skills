const fs = require('fs').promises;
const path = require('path');

class AgentLedger {
  constructor(workspaceRoot = process.cwd()) {
    this.ledgerDir = path.join(workspaceRoot, 'workspace', 'ledger');
    this.transactionsFile = path.join(this.ledgerDir, 'transactions.json');
    this.accountsFile = path.join(this.ledgerDir, 'accounts.json');
    this.budgetsFile = path.join(this.ledgerDir, 'budgets.json');
    this.settingsFile = path.join(this.ledgerDir, 'settings.json');
  }

  async init() {
    // Create ledger directory if it doesn't exist
    await fs.mkdir(this.ledgerDir, { recursive: true });
    
    // Initialize files if they don't exist
    const defaultFiles = {
      [this.transactionsFile]: [],
      [this.accountsFile]: [],
      [this.budgetsFile]: {},
      [this.settingsFile]: {
        defaultCurrency: 'USD',
        categories: [
          'API/Services',
          'Infrastructure',
          'Marketing',
          'Tools',
          'Subscriptions',
          'Other'
        ]
      }
    };

    for (const [file, defaultContent] of Object.entries(defaultFiles)) {
      try {
        await fs.access(file);
      } catch {
        await fs.writeFile(file, JSON.stringify(defaultContent, null, 2));
      }
    }
  }

  /**
   * Load transactions with backup recovery support
   * @returns {Promise<Array>} Array of transaction objects
   */
  async loadTransactions() {
    await this.init();
    try {
      const data = await fs.readFile(this.transactionsFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.warn(`Warning: Could not load transactions (${error.message}). Attempting backup recovery...`);
      
      // Try to load from backup
      const backupFile = this.transactionsFile + '.backup';
      try {
        const backupData = await fs.readFile(backupFile, 'utf8');
        const transactions = JSON.parse(backupData);
        console.log(`✅ Recovered ${transactions.length} transactions from backup.`);
        
        // Restore the main file from backup
        await fs.writeFile(this.transactionsFile, backupData);
        return transactions;
      } catch (backupError) {
        console.warn('Could not recover from backup. Starting with empty transaction list.');
        return [];
      }
    }
  }

  /**
   * Save transactions with automatic backup creation
   * @param {Array} transactions - Array of transaction objects
   */
  async saveTransactions(transactions) {
    // Create backup of existing file before overwriting
    try {
      await fs.access(this.transactionsFile);
      const backupFile = this.transactionsFile + '.backup';
      await fs.copyFile(this.transactionsFile, backupFile);
    } catch (error) {
      // File doesn't exist yet, no backup needed
    }
    
    await fs.writeFile(this.transactionsFile, JSON.stringify(transactions, null, 2));
  }

  async loadAccounts() {
    await this.init();
    try {
      const data = await fs.readFile(this.accountsFile, 'utf8');
      return JSON.parse(data);
    } catch {
      return [];
    }
  }

  async saveAccounts(accounts) {
    await fs.writeFile(this.accountsFile, JSON.stringify(accounts, null, 2));
  }

  async loadBudgets() {
    await this.init();
    try {
      const data = await fs.readFile(this.budgetsFile, 'utf8');
      return JSON.parse(data);
    } catch {
      return {};
    }
  }

  async saveBudgets(budgets) {
    await fs.writeFile(this.budgetsFile, JSON.stringify(budgets, null, 2));
  }

  async loadSettings() {
    await this.init();
    try {
      const data = await fs.readFile(this.settingsFile, 'utf8');
      return JSON.parse(data);
    } catch {
      return { defaultCurrency: 'USD' };
    }
  }

  generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  /**
   * Log a new transaction with validation and auto-categorization
   * @param {Object} transaction - Transaction object
   * @param {number} transaction.amount - Transaction amount (positive number)
   * @param {string} transaction.vendor - Vendor/merchant name
   * @param {string} transaction.description - Transaction description
   * @param {string} [transaction.currency] - Currency code (defaults to settings.defaultCurrency)
   * @param {string} [transaction.category] - Category (defaults to 'Other')
   * @param {string} [transaction.account] - Account identifier (defaults to 'default')
   * @param {string} [transaction.context] - Additional context or reason for purchase
   * @param {string} [transaction.receiptUrl] - Receipt URL
   * @param {string} [transaction.confirmationId] - Confirmation or order ID
   * @param {Array<string>} [transaction.tags] - Tags for categorization
   * @returns {Promise<Object>} The created transaction object with ID and timestamp
   */
  async logTransaction(transaction) {
    // Validate required fields
    const required = ['amount', 'vendor', 'description'];
    for (const field of required) {
      if (!transaction[field]) {
        throw new Error(`Missing required field: ${field}`);
      }
    }

    if (typeof transaction.amount !== 'number' || isNaN(transaction.amount) || transaction.amount <= 0) {
      throw new Error('Amount must be a positive number');
    }

    const settings = await this.loadSettings();
    const transactions = await this.loadTransactions();

    const newTransaction = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      amount: transaction.amount,
      currency: transaction.currency || settings.defaultCurrency,
      vendor: transaction.vendor,
      description: transaction.description,
      category: transaction.category || 'Other',
      account: transaction.account || 'default',
      context: transaction.context || '',
      receiptUrl: transaction.receiptUrl || '',
      confirmationId: transaction.confirmationId || '',
      tags: transaction.tags || []
    };

    transactions.push(newTransaction);
    await this.saveTransactions(transactions);

    return newTransaction;
  }

  parseTimePeriod(period) {
    const now = new Date();
    const start = new Date();
    const end = new Date();

    switch (period) {
      case 'today':
        start.setHours(0, 0, 0, 0);
        end.setHours(23, 59, 59, 999);
        break;
      case 'yesterday':
        start.setDate(now.getDate() - 1);
        start.setHours(0, 0, 0, 0);
        end.setDate(now.getDate() - 1);
        end.setHours(23, 59, 59, 999);
        break;
      case 'this-week':
        const dayOfWeek = now.getDay();
        start.setDate(now.getDate() - dayOfWeek);
        start.setHours(0, 0, 0, 0);
        break;
      case 'last-week':
        const lastWeekStart = now.getDate() - now.getDay() - 7;
        start.setDate(lastWeekStart);
        start.setHours(0, 0, 0, 0);
        end.setDate(lastWeekStart + 6);
        end.setHours(23, 59, 59, 999);
        break;
      case 'this-month':
        start.setDate(1);
        start.setHours(0, 0, 0, 0);
        break;
      case 'last-month':
        start.setMonth(now.getMonth() - 1, 1);
        start.setHours(0, 0, 0, 0);
        end.setMonth(now.getMonth(), 0);
        end.setHours(23, 59, 59, 999);
        break;
      case 'last-30-days':
        start.setDate(now.getDate() - 30);
        start.setHours(0, 0, 0, 0);
        break;
      case 'last-90-days':
        start.setDate(now.getDate() - 90);
        start.setHours(0, 0, 0, 0);
        break;
      case 'this-year':
        start.setMonth(0, 1);
        start.setHours(0, 0, 0, 0);
        break;
      default:
        throw new Error(`Unsupported time period: ${period}`);
    }

    return { start, end };
  }

  filterTransactionsByPeriod(transactions, period) {
    const { start, end } = this.parseTimePeriod(period);
    return transactions.filter(t => {
      const transactionDate = new Date(t.timestamp);
      return transactionDate >= start && transactionDate <= end;
    });
  }

  /**
   * Get spending summary for a specific time period
   * @param {string} [period='this-month'] - Time period (today, this-week, this-month, etc.)
   * @returns {Promise<Object>} Summary object with totals by category, currency, and account
   */
  async getSummary(period = 'this-month') {
    const transactions = await this.loadTransactions();
    const filtered = this.filterTransactionsByPeriod(transactions, period);
    
    const summary = {
      total: 0,
      count: filtered.length,
      byCategory: {},
      byCurrency: {},
      byAccount: {}
    };

    filtered.forEach(t => {
      summary.total += t.amount;
      summary.byCategory[t.category] = (summary.byCategory[t.category] || 0) + t.amount;
      summary.byCurrency[t.currency] = (summary.byCurrency[t.currency] || 0) + t.amount;
      summary.byAccount[t.account] = (summary.byAccount[t.account] || 0) + t.amount;
    });

    return summary;
  }

  async getCategorySpending(category, period = 'this-month') {
    const transactions = await this.loadTransactions();
    const filtered = this.filterTransactionsByPeriod(transactions, period)
      .filter(t => t.category === category);
    
    return filtered.reduce((total, t) => total + t.amount, 0);
  }

  async findTransactions(query, options = {}) {
    const transactions = await this.loadTransactions();
    let filtered = transactions;

    // Filter by time period
    if (options.period) {
      filtered = this.filterTransactionsByPeriod(filtered, options.period);
    }

    // Text search
    if (query) {
      const searchLower = query.toLowerCase();
      filtered = filtered.filter(t => 
        t.vendor.toLowerCase().includes(searchLower) ||
        t.description.toLowerCase().includes(searchLower) ||
        t.context.toLowerCase().includes(searchLower)
      );
    }

    // Filter by category
    if (options.category) {
      filtered = filtered.filter(t => t.category === options.category);
    }

    // Filter by amount range
    if (options.minAmount) {
      filtered = filtered.filter(t => t.amount >= options.minAmount);
    }
    if (options.maxAmount) {
      filtered = filtered.filter(t => t.amount <= options.maxAmount);
    }

    return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }

  async addAccount(account) {
    const accounts = await this.loadAccounts();
    
    const newAccount = {
      id: account.id || this.generateId(),
      name: account.name,
      type: account.type || 'credit_card',
      currency: account.currency || 'USD',
      created: new Date().toISOString()
    };

    accounts.push(newAccount);
    await this.saveAccounts(accounts);
    return newAccount;
  }

  async setBudget(category, amount, period = 'monthly') {
    const budgets = await this.loadBudgets();
    
    budgets[category] = {
      amount,
      period,
      currency: 'USD',
      created: new Date().toISOString()
    };

    await this.saveBudgets(budgets);
    return budgets[category];
  }

  async checkBudget(category, period = 'this-month') {
    const budgets = await this.loadBudgets();
    const budget = budgets[category];
    
    if (!budget) {
      return { hasBudget: false };
    }

    const spent = await this.getCategorySpending(category, period);
    const percentUsed = (spent / budget.amount) * 100;
    
    return {
      hasBudget: true,
      budgetAmount: budget.amount,
      spent,
      remaining: budget.amount - spent,
      percentUsed,
      isOverBudget: spent > budget.amount,
      isNearLimit: percentUsed >= 80
    };
  }

  async exportTransactions(format, filePath, options = {}) {
    const transactions = await this.loadTransactions();
    let filtered = transactions;

    if (options.period) {
      filtered = this.filterTransactionsByPeriod(filtered, options.period);
    }

    if (format === 'csv') {
      const csvHeader = 'Date,Amount,Currency,Vendor,Description,Category,Account,Context,ReceiptURL,ConfirmationID\n';
      const csvRows = filtered.map(t => [
        t.timestamp.split('T')[0],
        t.amount,
        t.currency,
        `"${t.vendor}"`,
        `"${t.description}"`,
        t.category,
        t.account,
        `"${t.context}"`,
        t.receiptUrl,
        t.confirmationId
      ].join(','));
      
      const csvContent = csvHeader + csvRows.join('\n');
      await fs.writeFile(filePath, csvContent);
    } else if (format === 'json') {
      await fs.writeFile(filePath, JSON.stringify(filtered, null, 2));
    }

    return { count: filtered.length, path: filePath };
  }

  async importPrivacyTransactions(jsonFile) {
    try {
      const data = await fs.readFile(jsonFile, 'utf8');
      const privacyData = JSON.parse(data);
      
      let importedCount = 0;
      for (const transaction of privacyData.transactions || []) {
        await this.logTransaction({
          amount: Math.abs(transaction.amount),
          vendor: transaction.merchant || 'Unknown',
          description: transaction.description || 'Privacy.com transaction',
          category: this.categorizePrivacyTransaction(transaction),
          account: `privacy-${transaction.card_id}`,
          confirmationId: transaction.id
        });
        importedCount++;
      }
      
      return { imported: importedCount };
    } catch (error) {
      throw new Error(`Failed to import Privacy transactions: ${error.message}`);
    }
  }

  categorizePrivacyTransaction(transaction) {
    const merchant = (transaction.merchant || '').toLowerCase();
    
    if (merchant.includes('api') || merchant.includes('openai') || merchant.includes('anthropic')) {
      return 'API/Services';
    }
    if (merchant.includes('aws') || merchant.includes('google cloud') || merchant.includes('azure')) {
      return 'Infrastructure';
    }
    if (merchant.includes('github') || merchant.includes('stripe') || merchant.includes('vercel')) {
      return 'Tools';
    }
    
    return 'Other';
  }
}

module.exports = AgentLedger;