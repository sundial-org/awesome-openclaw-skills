---
name: agentledger
description: Expense tracking and accounting for AI agents. Log purchases, set budgets, generate spending reports, and manage multi-currency finances — all stored locally. Privacy.com card import, natural language queries, CSV/JSON export. Use when agents make purchases and need a financial audit trail.
metadata: {"openclaw": {"requires": {"bins": ["node"]}}}
---

# AgentLedger - AI Agent Expense Tracking

## Overview
AgentLedger is an accounting skill that logs every transaction you make, tracks spending across multiple accounts, and provides detailed reports. Use this to maintain a complete financial record of your purchases.

**Important**: Always log transactions immediately after making purchases. This skill is designed for AI agents to track their own expenses (API costs, tool subscriptions, etc.).

## Core Functions

### 1. Log a Transaction
When you make any purchase, immediately log it:

```javascript
// In Node.js context, require the ledger
const AgentLedger = require('./src/ledger.js');
const ledger = new AgentLedger();

// Log a transaction
await ledger.logTransaction({
  amount: 29.99,
  currency: 'USD',
  vendor: 'OpenAI',
  description: 'GPT-4 API credits',
  category: 'API/Services',
  account: 'privacy-card-1',
  context: 'Needed additional tokens for user project analysis',
  receiptUrl: 'https://platform.openai.com/receipts/xyz',
  confirmationId: 'sub_1234567890'
});
```

**CLI Usage** (supports both positional and named parameters):
```bash
# Positional style
node src/cli.js log 29.99 "OpenAI" "GPT-4 API credits" --category="API/Services"

# Named parameter style  
node src/cli.js log --amount=29.99 --vendor="OpenAI" --description="GPT-4 API credits" --category="API/Services" --context="Monthly API refill"
```

### 2. Check Current Spending
```javascript
// Get spending summary
const summary = await ledger.getSummary('this-month');
console.log(`Total spent this month: $${summary.total}`);

// Check specific category
const apiSpending = await ledger.getCategorySpending('API/Services', 'this-month');
```

### 3. Generate Reports
```javascript
// Monthly report
const report = await ledger.generateReport('monthly', { month: '2024-01' });

// Custom date range
const customReport = await ledger.generateReport('custom', {
  startDate: '2024-01-01',
  endDate: '2024-01-31'
});
```

### 4. Budget Management
```javascript
// Set monthly budget for API services
await ledger.setBudget('API/Services', 500, 'monthly');

// Check budget status
const budgetStatus = await ledger.checkBudget('API/Services');
if (budgetStatus.isNearLimit) {
  console.log(`Warning: ${budgetStatus.percentUsed}% of API budget used`);
}
```

## Categories
Use these predefined categories for consistent tracking:
- **API/Services** - API credits, SaaS subscriptions
- **Infrastructure** - Hosting, domains, CDN
- **Marketing** - Ads, social media tools
- **Tools** - Software licenses, utilities
- **Subscriptions** - Recurring monthly/yearly services
- **Other** - Miscellaneous expenses

## Account Integration

### Privacy.com Cards
The ledger automatically detects Privacy.com card data if available:
```javascript
// If you have Privacy.com JSON exports in workspace/privacy/
await ledger.importPrivacyTransactions('./privacy/card-1.json');
```

### Manual Account Setup
```javascript
// Register a new payment method
await ledger.addAccount({
  id: 'stripe-main',
  name: 'Main Stripe Account',
  type: 'credit_card',
  currency: 'USD'
});
```

## Natural Language Queries

Ask questions like:
- "How much did I spend on API keys this month?"
- "What was that $20 charge from yesterday?"
- "Show me all infrastructure costs from last quarter"
- "Am I over budget on marketing spend?"

The CLI handles these queries:
```bash
node src/cli.js query "API spending this month"
node src/cli.js find "OpenAI" --last-week
```

## Time Periods
Supported natural language time periods:
- `today`, `yesterday`
- `this-week`, `last-week`
- `this-month`, `last-month`
- `this-quarter`, `last-quarter`
- `this-year`, `last-year`
- `last-30-days`, `last-90-days`

## Data Export
```javascript
// Export to CSV
await ledger.exportTransactions('csv', './exports/transactions.csv');

// Export to JSON
await ledger.exportTransactions('json', './exports/transactions.json');
```

## CLI Quick Reference

### Essential Commands for AI Agents

```bash
# Initialize (run once)
node src/cli.js init

# Log transactions (supports both styles)
node src/cli.js log 29.99 "OpenAI" "API credits" --category="API/Services"
node src/cli.js log --amount=29.99 --vendor="OpenAI" --description="API credits" --category="API/Services"

# Check current spending
node src/cli.js summary                    # This month
node src/cli.js summary --period="today"   # Today only
node src/cli.js summary --period="this-week" # This week

# Set and check budgets
node src/cli.js budget set "API/Services" 500    # Set monthly budget
node src/cli.js budget status                    # Check all budgets

# Generate detailed reports  
node src/cli.js report monthly
node src/cli.js report --type=category
node src/cli.js report --type=vendor

# Search transactions
node src/cli.js find "OpenAI"                    # Search by vendor
node src/cli.js find "API" --category="API/Services"  # Search by category
node src/cli.js find --min-amount=50             # Find large expenses

# Export data
node src/cli.js export csv                       # Export to CSV
node src/cli.js export --format=json            # Export to JSON

# Natural language queries
node src/cli.js query "How much did I spend on APIs this month?"
node src/cli.js query "What was that $25 charge?"

# Import from Privacy.com
node src/cli.js import privacy ./privacy-export.json
```

## File Storage
- Transactions: `workspace/ledger/transactions.json`
- Accounts: `workspace/ledger/accounts.json`
- Budgets: `workspace/ledger/budgets.json`
- Settings: `workspace/ledger/settings.json`

## Best Practices
1. **Log immediately** - Don't wait, log every purchase as it happens
2. **Add context** - Explain why the purchase was necessary
3. **Use consistent categories** - Stick to the predefined categories
4. **Include receipts** - Store confirmation numbers and receipt URLs
5. **Set budgets** - Establish spending limits for each category
6. **Review regularly** - Generate monthly reports to track spending patterns

## Error Handling & Edge Cases

The ledger handles common errors gracefully:

### Input Validation
- **Negative amounts**: Rejected (use positive amounts only)
- **Missing required fields**: Clear error messages with usage examples
- **Invalid currency**: Accepted (no validation - assumes user knows what they're doing)
- **Very long descriptions**: Handled without truncation

### Data Safety
- **Automatic backups**: Created before each save operation
- **Corrupted data recovery**: Automatic recovery from `.backup` files
- **Empty periods**: Gracefully shows $0.00 totals
- **Multi-currency**: Properly separated in summaries and reports

### Example Error Recovery
```bash
# If you see "Could not load transactions" message:
# The system automatically tries to recover from backup
# Your data should be restored automatically

# Manual backup check
ls workspace/ledger/*.backup  # Check if backups exist
```

## Security & Privacy
- **Local storage only**: All data stays in `workspace/ledger/` JSON files
- **No external API calls**: Core functionality works offline
- **No sensitive data**: Never store actual card numbers or passwords
- **Account aliases**: Use descriptive IDs like `privacy-card-1` or `company-amex`
- **Receipt URLs**: Store links to receipts, not receipt content itself