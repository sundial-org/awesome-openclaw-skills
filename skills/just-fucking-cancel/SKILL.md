---
name: just-fucking-cancel
description: "Find and cancel unwanted subscriptions by analyzing bank transactions. Detects recurring charges, calculates annual waste, and helps you cancel with direct URLs and browser automation. Use when: 'cancel subscriptions', 'audit subscriptions', 'find recurring charges', 'what am I paying for', 'save money', 'subscription cleanup', 'stop wasting money'. Supports CSV import (Apple Card, Chase, Amex, Citi, Bank of America, Capital One, Mint, Copilot) OR Plaid API for automatic transaction pull. Outputs interactive HTML audit with one-click cancel workflow. Pairs with Plaid integration for real-time transaction access without CSV exports."
attribution: Originally created by rohunvora (https://github.com/rohunvora/just-fucking-cancel)
tags:
  - subscriptions
  - cancel
  - money
  - savings
  - finance
  - personal-finance
  - budgeting
  - recurring-charges
  - bank-transactions
  - csv-analysis
  - subscription-audit
  - subscription-management
  - plaid
  - fintech
  - money-saving
  - expense-tracking
  - dark-patterns
  - consumer-rights
  - automation
  - browser-automation
  - apple-card
  - chase
  - amex
  - mint
  - copilot
  - bank-of-america
  - capital-one
  - citi
  - credit-card
  - debit-card
---

# just-fucking-cancel

Analyze transactions, categorize subscriptions, generate HTML audit, help cancel.

## Triggers
- "cancel subscriptions", "audit subscriptions"
- "find recurring charges", "what am I paying for"
- "subscription audit", "clean up subscriptions"

## Workflow

### 1. Get Transactions

**Option A: Plaid API (recommended — no CSV needed)**

If the user has Plaid connected (check for Plaid integration/API access):
1. Pull last 6-12 months of transactions via Plaid Transactions API
2. All accounts are automatically included — no manual export needed
3. Skip straight to Step 2

**Option B: CSV Upload**

Ask user for bank/card CSV export. Common sources:
- Apple Card: Wallet → Card Balance → Export
- Chase: Accounts → Download activity → CSV
- Amex: Statements & Activity → Download → CSV
- Citi: Account Details → Download Transactions
- Bank of America: Activity → Download → CSV
- Capital One: Transactions → Download
- Mint / Copilot: Transactions → Export

### 2. Analyze Recurring Charges
Read CSV, identify recurring patterns:
- Same merchant, similar amounts, monthly/annual frequency
- Flag subscription-like charges (streaming, SaaS, memberships)
- Note charge frequency and total annual cost

### 3. Categorize with User
For each subscription, ask user to categorize:
- **Cancel** - Stop immediately
- **Investigate** - Needs decision (unsure, trapped in contract)
- **Keep** - Intentional, continue paying

Ask in batches of 5-10 to avoid overwhelming.

### 4. Generate HTML Audit
Copy [template.html](assets/template.html) and populate:
- Update header summary:
  - Scope line: "found N subscriptions · N transactions"
  - Breakdown: "Cancelled N · Keeping N"
  - Savings: yearly amount big, monthly in parentheses
  - Timestamp: current date
- Add rows to appropriate sections (cancelled/investigate/keep)
- Include notes from user responses

Row templates in the HTML comments show the structure.

### 5. Cancel Subscriptions
When user checks items and copies from floating button, they'll paste:
`Cancel these: Service1 ($XX), Service2 ($XX)...`

For each service:
1. Check [common-services.md](references/common-services.md) for cancel URL
2. Use browser automation to navigate and cancel
3. Update HTML row to cancelled status with date

## HTML Structure

Three sections, auto-hide when empty:
- **Cancelled** (green badge, strikethrough) - Done items, the win
- **Needs Decision** (orange badge) - Has checkboxes for cancel selection
- **Keeping** (grey badge) - No checkboxes, just reference

Features:
- Floating copy button appears when items checked
- Privacy toggle blurs service names
- Collapsible sections via header click
- Dark mode support

## Cancellation Tips

For difficult services, see [common-services.md](references/common-services.md):
- Direct cancel URLs for 50+ services
- Dark pattern warnings (gym contracts, phone-only)
- Retention script responses
- Credit card dispute backup

## Privacy

All data stays local. Transaction CSVs are analyzed in-session only.
