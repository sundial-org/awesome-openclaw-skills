# AgentLedger

**AI Agent Expense Tracking & Accounting for OpenClaw**

AgentLedger is a comprehensive expense tracking skill that helps AI agents maintain detailed financial records of purchases and spending. Perfect for tracking API costs, subscription services, infrastructure expenses, and any other purchases made by AI agents.

## 🌟 Features

### Core Functionality
- **Transaction Logging** - Log every purchase with amount, vendor, description, category, and context
- **Multi-Currency Support** - Track spending in different currencies
- **Account Management** - Manage multiple payment methods and cards
- **Budget Tracking** - Set spending limits and get alerts when approaching them
- **Natural Language Queries** - Ask questions like "How much did I spend on API keys this month?"
- **Detailed Reports** - Generate monthly, category, vendor, and trend reports
- **Data Export** - Export transactions to CSV or JSON formats
- **Receipt Storage** - Store receipt URLs and confirmation numbers

### Categories
Pre-defined spending categories for consistent tracking:
- **API/Services** - API credits, SaaS subscriptions
- **Infrastructure** - Hosting, domains, CDN
- **Marketing** - Advertising, social media tools  
- **Tools** - Software licenses, utilities
- **Subscriptions** - Recurring services
- **Other** - Miscellaneous expenses

### Smart Features
- **Privacy.com Integration** - Import transactions from Privacy card exports
- **Budget Alerts** - Automatic warnings when approaching spending limits
- **Trend Analysis** - Track spending patterns over time
- **Vendor Analysis** - See spending patterns by vendor
- **Time Period Filtering** - Support for natural language time periods

## 🚀 Quick Start

### Installation
```bash
# Clone or copy the skill to your workspace
cp -r agentledger /home/claw/.openclaw/workspace/

# Initialize the ledger
cd /home/claw/.openclaw/workspace/agentledger
node src/cli.js init
```

### Basic Usage

#### Log a Transaction
```bash
# Command line
node src/cli.js log 29.99 "OpenAI" "GPT-4 API credits" --category="API/Services"

# In Node.js code
const AgentLedger = require('./src/ledger.js');
const ledger = new AgentLedger();

await ledger.logTransaction({
  amount: 29.99,
  vendor: 'OpenAI',
  description: 'GPT-4 API credits',
  category: 'API/Services',
  context: 'Monthly API refill for user projects'
});
```

#### Check Spending
```bash
# Get monthly summary
node src/cli.js summary --period="this-month"

# Search transactions
node src/cli.js find "OpenAI" --last-month

# Generate detailed report
node src/cli.js report monthly
```

#### Budget Management
```bash
# Set budget
node src/cli.js budget set "API/Services" 500

# Check budget status
node src/cli.js budget status
```

## 📖 Documentation

### For AI Agents
See [SKILL.md](SKILL.md) for detailed instructions on how AI agents should use this skill.

### CLI Reference
```bash
# Initialize ledger
node src/cli.js init

# Log transactions
node src/cli.js log <amount> <vendor> <description> [options]
  --category=<category>      Transaction category
  --account=<account>        Payment account
  --context=<context>        Purchase context/reason
  --receipt=<url>            Receipt URL
  --confirmation=<id>        Confirmation number

# View summaries
node src/cli.js summary [options]
  --period=<period>          Time period (this-month, last-week, etc.)

# Search transactions
node src/cli.js find <query> [options]
  --period=<period>          Time period filter
  --category=<category>      Category filter
  --min-amount=<amount>      Minimum amount
  --max-amount=<amount>      Maximum amount

# Generate reports
node src/cli.js report <type> [options]
  Types: monthly, category, vendor, trend, custom
  --month=<YYYY-MM>         Specific month for monthly report
  --period=<period>         Time period for other reports

# Budget management
node src/cli.js budget set <category> <amount> [period]
node src/cli.js budget status
node src/cli.js budget check <category>

# Export data
node src/cli.js export <format> [options]
  Formats: csv, json
  --output=<filename>       Output filename
  --period=<period>         Time period to export

# Account management
node src/cli.js account add <id> <name> [type]
node src/cli.js account list

# Import data
node src/cli.js import privacy <file.json>

# Natural language queries
node src/cli.js query "How much did I spend on APIs this month?"
```

### Time Periods
Supported natural language time periods:
- `today`, `yesterday`
- `this-week`, `last-week`
- `this-month`, `last-month`
- `this-quarter`, `last-quarter`  
- `this-year`, `last-year`
- `last-30-days`, `last-90-days`

## 📁 File Structure

```
agentledger/
├── SKILL.md                    # AI agent instructions
├── README.md                   # This file
├── package.json                # Package metadata
├── src/
│   ├── ledger.js              # Core ledger functionality
│   ├── cli.js                 # Command line interface
│   ├── reports.js             # Report generation
│   └── budget.js              # Budget management
└── test/
    └── ledger.test.js         # Basic tests
```

### Data Storage
All data is stored locally in JSON files:
- `workspace/ledger/transactions.json` - All transactions
- `workspace/ledger/accounts.json` - Payment accounts
- `workspace/ledger/budgets.json` - Budget settings
- `workspace/ledger/settings.json` - General settings

## 🔧 API Reference

### AgentLedger Class

#### Transaction Management
```javascript
// Log a transaction
await ledger.logTransaction({
  amount: 29.99,
  currency: 'USD',
  vendor: 'OpenAI',
  description: 'API credits',
  category: 'API/Services',
  account: 'privacy-card-1',
  context: 'Monthly API refill',
  receiptUrl: 'https://...',
  confirmationId: 'sub_123'
});

// Get spending summary
const summary = await ledger.getSummary('this-month');

// Find transactions
const transactions = await ledger.findTransactions('OpenAI', {
  period: 'last-month',
  category: 'API/Services'
});
```

#### Budget Management
```javascript
// Set budget
await ledger.setBudget('API/Services', 500, 'monthly');

// Check budget status
const status = await ledger.checkBudget('API/Services');
console.log(`Used ${status.percentUsed}% of budget`);
```

#### Data Export
```javascript
// Export to CSV
await ledger.exportTransactions('csv', './exports/transactions.csv', {
  period: 'this-year'
});

// Export to JSON
await ledger.exportTransactions('json', './exports/data.json');
```

## 🔌 Integrations

### Privacy.com Cards
AgentLedger can import transaction data from Privacy.com card exports:

```bash
node src/cli.js import privacy ./privacy-export.json
```

The importer automatically:
- Maps merchants to appropriate categories
- Extracts transaction details
- Assigns transactions to the correct Privacy card account
- Handles duplicate detection

### Custom Integrations
Extend AgentLedger by:
1. Adding new import formats in `src/ledger.js`
2. Creating custom categorization rules
3. Adding new report types in `src/reports.js`
4. Implementing webhook notifications for budget alerts

## 🛡️ Security & Privacy

- **Local Storage Only** - All data stays on your machine
- **No External API Calls** - Core functionality works offline
- **No Sensitive Data** - Never store actual card numbers
- **Account Aliases** - Use account IDs instead of real account details

## 🧪 Testing

Run the basic test suite:
```bash
node test/ledger.test.js
```

## 📈 Examples

### Daily Workflow
```javascript
// Morning: Check yesterday's spending
await ledger.getSummary('yesterday');

// Log API purchase
await ledger.logTransaction({
  amount: 50.00,
  vendor: 'OpenAI',
  description: 'Additional GPT-4 credits',
  category: 'API/Services',
  context: 'User requested complex analysis requiring more tokens'
});

// Check if approaching budget limits
const alerts = await budgetManager.getAlerts();
if (alerts.length > 0) {
  console.log('Budget alerts:', alerts);
}

// Weekly: Generate spending report
const report = await reports.generate('weekly');
console.log(report);
```

### Monthly Review
```bash
# Generate comprehensive monthly report
node src/cli.js report monthly

# Export data for accounting
node src/cli.js export csv --output="expenses-2024-01.csv" --period="last-month"

# Review budget performance
node src/cli.js budget status
```

## 🤝 Contributing

AgentLedger is designed to be extended and customized:

1. **Add Categories** - Modify the categories in `settings.json`
2. **Custom Reports** - Add new report types in `reports.js`
3. **New Importers** - Add support for other payment systems
4. **Enhanced CLI** - Add new commands to `cli.js`

## 📄 License

MIT License - See package.json for details.

## 🔗 Links

- [OpenClaw Documentation](https://openclaw.ai)
- [ClawHub Skills Repository](https://hub.openclaw.ai)
- [Privacy.com](https://privacy.com) - Virtual card service

---

**Built for OpenClaw AI Agents** 🤖💰