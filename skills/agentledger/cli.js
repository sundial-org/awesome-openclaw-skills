#!/usr/bin/env node

const AgentLedger = require('./ledger.js');
const reports = require('./reports.js');
const BudgetManager = require('./budget.js');

class CLI {
  constructor() {
    this.ledger = new AgentLedger();
    this.reports = new reports(this.ledger);
    this.budgetManager = new BudgetManager(this.ledger);
  }

  async run() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
      this.showHelp();
      return;
    }

    const command = args[0];
    
    try {
      switch (command) {
        case 'log':
          await this.handleLog(args.slice(1));
          break;
        case 'summary':
          await this.handleSummary(args.slice(1));
          break;
        case 'find':
        case 'search':
          await this.handleFind(args.slice(1));
          break;
        case 'report':
          await this.handleReport(args.slice(1));
          break;
        case 'budget':
          await this.handleBudget(args.slice(1));
          break;
        case 'export':
          await this.handleExport(args.slice(1));
          break;
        case 'query':
          await this.handleQuery(args.slice(1));
          break;
        case 'account':
          await this.handleAccount(args.slice(1));
          break;
        case 'import':
          await this.handleImport(args.slice(1));
          break;
        case 'init':
          await this.handleInit();
          break;
        case 'help':
        case '--help':
        case '-h':
          this.showHelp();
          break;
        default:
          console.error(`Unknown command: ${command}`);
          this.showHelp();
          process.exit(1);
      }
    } catch (error) {
      console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  }

  async handleLog(args) {
    const options = this.parseOptions(args);
    
    // Support both positional and named arguments
    let amount, vendor, description;
    
    if (options.amount && options.vendor && options.description) {
      // Named parameters style
      amount = parseFloat(options.amount);
      vendor = options.vendor;
      description = options.description;
    } else {
      // Positional parameters style
      const positionalArgs = args.filter(arg => !arg.startsWith('--'));
      if (positionalArgs.length < 3) {
        console.error('Usage: agentledger log <amount> <vendor> <description> [options]');
        console.error('   OR: agentledger log --amount=<amount> --vendor=<vendor> --description=<description> [options]');
        console.error('Options: --category, --account, --context, --receipt, --confirmation');
        process.exit(1);
      }
      amount = parseFloat(positionalArgs[0]);
      vendor = positionalArgs[1];
      description = positionalArgs[2];
    }

    const transaction = {
      amount: amount,
      vendor: vendor,
      description: description,
      category: options.category,
      account: options.account,
      context: options.context,
      receiptUrl: options.receipt,
      confirmationId: options.confirmation,
      currency: options.currency
    };

    const result = await this.ledger.logTransaction(transaction);
    console.log(`✅ Transaction logged: ${result.id}`);
    
    // Format currency display
    const displayAmount = result.currency === 'USD' ? `$${result.amount}` : `${result.amount} ${result.currency}`;
    console.log(`   ${displayAmount} - ${result.vendor}`);
    console.log(`   Category: ${result.category}`);
  }

  async handleSummary(args) {
    const options = this.parseOptions(args);
    const period = options.period || 'this-month';
    
    const summary = await this.ledger.getSummary(period);
    
    console.log(`📊 Spending Summary (${period})`);
    console.log(`═══════════════════════════════════`);
    
    // Display totals by currency
    const currencies = Object.keys(summary.byCurrency);
    if (currencies.length === 1 && currencies[0] === 'USD') {
      console.log(`Total: $${summary.total.toFixed(2)}`);
    } else {
      console.log('Totals by Currency:');
      for (const [currency, amount] of Object.entries(summary.byCurrency)) {
        const displayAmount = currency === 'USD' ? `$${amount.toFixed(2)}` : `${amount.toFixed(2)} ${currency}`;
        console.log(`  ${displayAmount}`);
      }
    }
    
    console.log(`Transactions: ${summary.count}`);
    console.log('');
    
    if (Object.keys(summary.byCategory).length > 0) {
      console.log('By Category:');
      for (const [category, amount] of Object.entries(summary.byCategory)) {
        // Only calculate percentage if single currency
        if (currencies.length === 1) {
          const percentage = ((amount / summary.total) * 100).toFixed(1);
          const displayAmount = currencies[0] === 'USD' ? `$${amount.toFixed(2)}` : `${amount.toFixed(2)} ${currencies[0]}`;
          console.log(`  ${category}: ${displayAmount} (${percentage}%)`);
        } else {
          console.log(`  ${category}: $${amount.toFixed(2)} (mixed currencies)`);
        }
      }
    }
    
    if (Object.keys(summary.byAccount).length > 1) {
      console.log('');
      console.log('By Account:');
      for (const [account, amount] of Object.entries(summary.byAccount)) {
        console.log(`  ${account}: $${amount.toFixed(2)}`);
      }
    }
  }

  async handleFind(args) {
    const options = this.parseOptions(args);
    const query = args.filter(arg => !arg.startsWith('--')).join(' ');
    
    const searchOptions = {
      period: options.period,
      category: options.category,
      minAmount: options.minAmount ? parseFloat(options.minAmount) : undefined,
      maxAmount: options.maxAmount ? parseFloat(options.maxAmount) : undefined
    };

    const transactions = await this.ledger.findTransactions(query, searchOptions);
    
    if (transactions.length === 0) {
      console.log('No transactions found matching your criteria.');
      return;
    }

    console.log(`🔍 Found ${transactions.length} transaction(s):`);
    console.log('');
    
    for (const t of transactions.slice(0, 10)) { // Show max 10 results
      const date = new Date(t.timestamp).toLocaleDateString();
      console.log(`${t.id} | ${date} | $${t.amount} ${t.currency}`);
      console.log(`   ${t.vendor} - ${t.description}`);
      console.log(`   Category: ${t.category} | Account: ${t.account}`);
      if (t.context) {
        console.log(`   Context: ${t.context}`);
      }
      console.log('');
    }
    
    if (transactions.length > 10) {
      console.log(`... and ${transactions.length - 10} more. Use --limit to see more.`);
    }
  }

  async handleReport(args) {
    const options = this.parseOptions(args);
    
    // Support both positional and named arguments
    let reportType;
    if (options.type) {
      reportType = options.type;
    } else {
      const positionalArgs = args.filter(arg => !arg.startsWith('--'));
      reportType = positionalArgs[0] || 'monthly';
    }
    
    const report = await this.reports.generate(reportType, options);
    console.log(report);
  }

  async handleBudget(args) {
    const options = this.parseOptions(args);
    
    // Support both positional and named arguments
    let action, category, amount, period;
    
    if (options.set) {
      action = 'set';
      category = options.category;
      amount = parseFloat(options.amount);
      period = options.period || 'monthly';
    } else {
      const positionalArgs = args.filter(arg => !arg.startsWith('--'));
      action = positionalArgs[0];
      if (action === 'set') {
        category = positionalArgs[1];
        amount = parseFloat(positionalArgs[2]);
        period = positionalArgs[3] || 'monthly';
      }
    }
    
    switch (action) {
      case 'set':
        if (!category || !amount) {
          console.error('Usage: agentledger budget set <category> <amount> [period]');
          console.error('   OR: agentledger budget --set --category=<category> --amount=<amount> [--period=<period>]');
          process.exit(1);
        }
        
        await this.budgetManager.setBudget(category, amount, period);
        console.log(`✅ Budget set: ${category} - $${amount}/${period}`);
        break;
        
      case 'status':
      case 'check':
        const budgetReport = await this.budgetManager.generateBudgetReport();
        console.log(budgetReport);
        break;
        
      default:
        console.error('Budget actions: set, status');
        process.exit(1);
    }
  }

  async handleExport(args) {
    const options = this.parseOptions(args);
    
    // Support both positional and named arguments
    let format;
    if (options.format) {
      format = options.format;
    } else {
      const positionalArgs = args.filter(arg => !arg.startsWith('--'));
      format = positionalArgs[0] || 'csv';
    }
    
    const filename = options.output || `transactions.${format}`;
    
    const result = await this.ledger.exportTransactions(format, filename, {
      period: options.period
    });
    
    console.log(`📁 Exported ${result.count} transactions to ${result.path}`);
  }

  async handleQuery(args) {
    const query = args.join(' ').toLowerCase();
    
    // Simple natural language processing
    if (query.includes('spend') && query.includes('month')) {
      const summary = await this.ledger.getSummary('this-month');
      console.log(`You've spent $${summary.total.toFixed(2)} this month across ${summary.count} transactions.`);
    } else if (query.includes('api') && query.includes('month')) {
      const apiSpending = await this.ledger.getCategorySpending('API/Services', 'this-month');
      console.log(`API/Services spending this month: $${apiSpending.toFixed(2)}`);
    } else if (query.match(/\$\d+/)) {
      // Look for dollar amount mentions
      const amount = query.match(/\$(\d+(?:\.\d{2})?)/);
      if (amount) {
        const transactions = await this.ledger.findTransactions('', {
          minAmount: parseFloat(amount[1]) - 0.01,
          maxAmount: parseFloat(amount[1]) + 0.01,
          period: 'last-30-days'
        });
        
        if (transactions.length > 0) {
          console.log(`Found ${transactions.length} transaction(s) for $${amount[1]}:`);
          transactions.forEach(t => {
            const date = new Date(t.timestamp).toLocaleDateString();
            console.log(`  ${date}: ${t.vendor} - ${t.description}`);
          });
        } else {
          console.log(`No transactions found for $${amount[1]} in the last 30 days.`);
        }
      }
    } else {
      console.log('I didn\'t understand that query. Try:');
      console.log('  "How much did I spend this month?"');
      console.log('  "API spending this month"');
      console.log('  "What was that $20 charge?"');
    }
  }

  async handleAccount(args) {
    const action = args[0];
    
    switch (action) {
      case 'add':
        if (args.length < 3) {
          console.error('Usage: agentledger account add <id> <name> [type]');
          process.exit(1);
        }
        
        const account = await this.ledger.addAccount({
          id: args[1],
          name: args[2],
          type: args[3] || 'credit_card'
        });
        
        console.log(`✅ Account added: ${account.name} (${account.id})`);
        break;
        
      case 'list':
        const accounts = await this.ledger.loadAccounts();
        console.log('💳 Accounts:');
        accounts.forEach(acc => {
          console.log(`  ${acc.id}: ${acc.name} (${acc.type})`);
        });
        break;
        
      default:
        console.error('Account actions: add, list');
    }
  }

  async handleImport(args) {
    const source = args[0];
    const file = args[1];
    
    if (source === 'privacy' && file) {
      const result = await this.ledger.importPrivacyTransactions(file);
      console.log(`✅ Imported ${result.imported} transactions from Privacy.com`);
    } else {
      console.error('Usage: agentledger import privacy <file.json>');
      process.exit(1);
    }
  }

  async handleInit() {
    await this.ledger.init();
    console.log('✅ AgentLedger initialized successfully!');
    console.log('📁 Data will be stored in workspace/ledger/');
    console.log('📖 Run "agentledger help" for usage information.');
  }

  parseOptions(args) {
    const options = {};
    
    for (let i = 0; i < args.length; i++) {
      const arg = args[i];
      if (arg.startsWith('--')) {
        if (arg.includes('=')) {
          // Handle --key=value format
          const [key, ...valueParts] = arg.substring(2).split('=');
          options[key] = valueParts.join('=');
        } else {
          // Handle --key value format
          const key = arg.substring(2);
          const value = args[i + 1];
          
          if (value && !value.startsWith('--')) {
            options[key] = value;
            i++; // Skip the value
          } else {
            options[key] = true;
          }
        }
      }
    }
    
    return options;
  }

  showHelp() {
    console.log(`
🧾 AgentLedger - AI Agent Expense Tracking

Usage: agentledger <command> [options]

Commands:
  init                           Initialize ledger data files
  log <amt> <vendor> <desc>      Log a new transaction
  summary [--period=<period>]    Show spending summary
  find <query> [options]         Search transactions
  report <type> [options]        Generate detailed report
  budget <action> [args]         Manage budgets
  export <format> [options]      Export transactions
  query "<question>"             Natural language query
  account <action> [args]        Manage accounts
  import <source> <file>         Import transactions

Log Options:
  --category=<category>          Transaction category
  --account=<account>            Payment account/card
  --context=<context>            Why this was purchased
  --receipt=<url>                Receipt URL
  --confirmation=<id>            Confirmation/order ID

Find Options:
  --period=<period>              Time period filter
  --category=<category>          Category filter
  --min-amount=<amount>          Minimum amount
  --max-amount=<amount>          Maximum amount

Time Periods:
  today, yesterday, this-week, last-week, this-month, last-month,
  this-quarter, last-quarter, this-year, last-year, last-30-days, last-90-days

Categories:
  API/Services, Infrastructure, Marketing, Tools, Subscriptions, Other

Examples:
  agentledger log 29.99 "OpenAI" "API credits" --category="API/Services"
  agentledger summary --period="this-month"
  agentledger find "OpenAI" --last-month
  agentledger budget set "API/Services" 500
  agentledger query "How much did I spend on API keys this month?"

For more information, see SKILL.md
`);
  }
}

// Run CLI if called directly
if (require.main === module) {
  const cli = new CLI();
  cli.run().catch(error => {
    console.error(`Fatal error: ${error.message}`);
    process.exit(1);
  });
}

module.exports = CLI;