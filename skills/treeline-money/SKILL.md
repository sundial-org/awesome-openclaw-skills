---
name: treeline
description: Chat with your finances from Treeline Money. Query balances, spending, budgets, and transactions.
version: 0.0.4
user-invocable: true
homepage: https://treeline.money
metadata: {"clawdbot":{"emoji":"🌲","requires":{"bins":["tl"]}}}
---

# Treeline Money

**Chat with your finances.** Ask questions like "What's my net worth?", "How much did I spend on groceries?", or "Am I over budget?" and get instant answers from your own financial data.

## What is Treeline?

[Treeline Money](https://treeline.money) is a local-first personal finance app. Learn more and download at [treeline.money](https://treeline.money).

---

## Requirements

1. **Treeline app installed** — [Download here](https://treeline.money/download)
2. **Treeline CLI installed** — Install via `curl -fsSL https://treeline.money/install.sh | sh` (Mac/Linux) or `irm https://treeline.money/install.ps1 | iex` (Windows). The CLI (`tl`) must be in your PATH.
3. **App must be closed** when querying — CLI and app can't access DuckDB simultaneously

---

## Limitations

**Encrypted databases not supported.** If the user has enabled database encryption in Treeline, CLI commands will fail. They'll need to either:
- Disable encryption if they want moltbot access
- Use the Treeline app directly for encrypted databases

If you see "database is encrypted" errors, explain this limitation.

---

## Response Formatting

**Format all responses for mobile/chat:**
- Use bullet points, not markdown tables
- Round numbers for readability ($1,234 not $1,234.56)
- Lead with the answer, details second
- Keep responses concise — chat isn't a spreadsheet
- Use line breaks to separate sections

**Example good response:**
```
Your net worth is $125k

Assets: $180k
- Retirement: $85k
- Savings: $25k
- Checking: $10k
- Home equity: $60k

Liabilities: $55k
- Mortgage: $52k
- Credit cards: $3k
```

**Example bad response:**
```
| Account | Type | Balance |
|---------|------|---------|
| My 401k Account | asset | 85234.56 |
...
```

---

## CLI Commands

The `tl` CLI can do more than just queries:

```bash
tl status              # Quick account summary with balances
tl status --json       # Same, but JSON output

tl query "SQL" --json  # Run any SQL query

tl sync                # Sync accounts/transactions from bank integrations
tl sync --dry-run      # Preview what would sync

tl backup create       # Create a backup
tl backup list         # List available backups
tl backup restore NAME # Restore a backup

tl doctor              # Check database health
tl compact             # Compact database (reclaim space, optimize)

tl tag "groceries" --ids ID1,ID2  # Apply tags to transactions

tl demo on|off         # Toggle demo mode (sample data)
```

**Use `tl status` for quick balance checks** — it's faster than a SQL query.

**Use `tl compact` if the user mentions slow queries** — it optimizes the database.

---

## User Context

**Before answering finance questions, check for `CONTEXT.md` in this skill directory.**

If it exists, read it first — it contains user-specific knowledge:
- Account meanings (which accounts are retirement vs brokerage, etc.)
- Tag conventions and cash flow rules
- Plugin configurations
- Personal preferences

**Learning new context:** When you discover something about the user's setup:
1. For small observations, note them in CONTEXT.md silently
2. For significant assumptions or corrections, ask: "Want me to save that to your Treeline context?"

See the [User Context Pattern](#user-context-pattern) section at the end for the template.

---

## Quick Reference

### Net Worth
```bash
tl query "
WITH latest AS (
  SELECT DISTINCT ON (account_id) account_id, balance
  FROM sys_balance_snapshots
  ORDER BY account_id, snapshot_time DESC
)
SELECT
  SUM(CASE WHEN a.classification = 'asset' THEN s.balance ELSE 0 END) as assets,
  SUM(CASE WHEN a.classification = 'liability' THEN ABS(s.balance) ELSE 0 END) as liabilities,
  SUM(CASE WHEN a.classification = 'asset' THEN s.balance ELSE -ABS(s.balance) END) as net_worth
FROM accounts a
JOIN latest s ON a.account_id = s.account_id
" --json
```

### Account Balances
```bash
tl query "
WITH latest AS (
  SELECT DISTINCT ON (account_id) account_id, balance
  FROM sys_balance_snapshots
  ORDER BY account_id, snapshot_time DESC
)
SELECT a.name, a.classification, a.institution_name, s.balance
FROM accounts a
JOIN latest s ON a.account_id = s.account_id
ORDER BY s.balance DESC
" --json
```

### True Spending (Excluding Internal Moves)

Check CONTEXT.md for `internal_transfer_tags`. Default pattern:

```bash
tl query "
SELECT SUM(ABS(amount)) as total_spent
FROM transactions
WHERE amount < 0
  AND transaction_date >= date_trunc('month', current_date)
  AND NOT (tags && ARRAY['transfer', 'savings', 'investment'])
" --json
```

### Spending by Tag
```bash
tl query "
SELECT tags, SUM(ABS(amount)) as spent
FROM transactions
WHERE amount < 0
  AND transaction_date >= '2026-01-01' AND transaction_date < '2026-02-01'
  AND tags IS NOT NULL AND tags != '[]'
GROUP BY tags
ORDER BY spent DESC
" --json
```

### Recent Transactions
```bash
tl query "
SELECT t.description, t.amount, t.transaction_date, a.name as account
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
ORDER BY t.transaction_date DESC
LIMIT 10
" --json
```

---

## Database Schema

### Core Tables

**accounts**
| Column | Description |
|--------|-------------|
| `account_id` | UUID primary key |
| `name` | Account display name |
| `classification` | `asset` or `liability` |
| `account_type` | `credit`, `investment`, `Loan`, `other`, or null |
| `institution_name` | Bank/institution name |
| `currency` | Currency code (e.g., `USD`) |
| `is_manual` | Boolean — manually added vs synced |

**sys_balance_snapshots** — Source of truth for balances
| Column | Description |
|--------|-------------|
| `snapshot_id` | UUID primary key |
| `account_id` | FK to accounts |
| `balance` | Balance at snapshot time |
| `snapshot_time` | When recorded |
| `source` | `sync`, `manual`, etc. |

**transactions**
| Column | Description |
|--------|-------------|
| `transaction_id` | UUID primary key |
| `account_id` | FK to accounts |
| `amount` | Signed (negative = expense) |
| `description` | Transaction description |
| `transaction_date` | When it occurred |
| `posted_date` | When it cleared |
| `tags` | Array of tags |

### Tags vs Categories

**Tags** are the primary concept in Treeline — transactions can have multiple tags.

**Categories** come from the budget plugin (`plugin_budget`), which maps tags to budget categories. Not all users have this plugin.

---

## Plugin System

Plugins have their own DuckDB schemas: `plugin_<name>.*`

### Discovering Installed Plugins
```bash
tl query "
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name LIKE 'plugin_%'
" --json
```

### Common Plugin Schemas

**plugin_budget.categories** — Budget categories
| Column | Description |
|--------|-------------|
| `category_id` | UUID primary key |
| `month` | `YYYY-MM` format |
| `type` | `income` or `expense` |
| `name` | Category name |
| `expected` | Budgeted amount |
| `tags` | Array of tags to match |

**plugin_goals.goals** — Savings goals
| Column | Description |
|--------|-------------|
| `id` | UUID primary key |
| `name` | Goal name |
| `target_amount` | Target amount |
| `target_date` | Target date |
| `completed` | Boolean |
| `active` | Boolean |

**plugin_subscriptions** — Detected recurring charges

**plugin_cashflow** — Cash flow projections

**plugin_emergency_fund** — Emergency fund tracking

Check CONTEXT.md for which plugins the user has and cares about.

---

## Common Patterns

### Getting Current Balances

Always use latest snapshot:
```sql
WITH latest AS (
  SELECT DISTINCT ON (account_id) account_id, balance
  FROM sys_balance_snapshots
  ORDER BY account_id, snapshot_time DESC
)
SELECT a.name, s.balance
FROM accounts a
JOIN latest s ON a.account_id = s.account_id
```

### Working with Tags

Tags are arrays:
```sql
-- Contains a specific tag
WHERE tags @> ARRAY['groceries']

-- Contains any of these tags
WHERE tags && ARRAY['food', 'dining']

-- Note: UNNEST doesn't work in all contexts in DuckDB
-- Instead, GROUP BY tags directly
```

### Date Filters
```sql
-- This month
WHERE transaction_date >= date_trunc('month', current_date)

-- Specific month
WHERE transaction_date >= '2026-01-01'
  AND transaction_date < '2026-02-01'
```

### Budget vs Actual
```sql
SELECT
  c.name,
  c.expected,
  COALESCE(SUM(ABS(t.amount)), 0) as actual,
  c.expected - COALESCE(SUM(ABS(t.amount)), 0) as remaining
FROM plugin_budget.categories c
LEFT JOIN transactions t ON t.tags && c.tags
  AND t.amount < 0
  AND t.transaction_date >= (c.month || '-01')::DATE
  AND t.transaction_date < (c.month || '-01')::DATE + INTERVAL '1 month'
WHERE c.month = strftime(current_date, '%Y-%m')
  AND c.type = 'expense'
GROUP BY c.category_id, c.name, c.expected
```

---

## Question Mapping

| User asks | Approach |
|-----------|----------|
| "Net worth?" | Net worth query |
| "Balances?" | Account balances query |
| "How much in [X]?" | Filter by `name ILIKE '%X%'` |
| "How much did I spend?" | True spending query (exclude internal moves) |
| "Spending on [tag]?" | Filter by tag |
| "Am I over budget?" | Budget vs actual (requires budget plugin) |
| "Recent transactions" | Order by date DESC, limit |
| "Savings?" | Filter accounts by name/type |
| "Retirement?" | Filter by 401k, IRA, retirement keywords |

---

## Tips

1. **Always use `--json`** for parseable output
2. **Amounts are signed** — negative = expense
3. **Use `classification`** for asset/liability
4. **Balances live in snapshots**, not the accounts table
5. **Check CONTEXT.md** for user-specific account meanings and tag conventions

---

## User Context Pattern

When this skill is installed, create `CONTEXT.md` alongside it to store user-specific knowledge. This keeps the skill generic/shareable while personalizing behavior.

**Template for CONTEXT.md:**

```markdown
# Treeline User Context
*Auto-updated by your assistant as it learns your setup*

## Account Notes
<!-- What specific accounts mean, e.g.: -->
<!-- - "Company 401k" = retirement account -->
<!-- - "Home Equity" = home value estimate (manual) -->

## Tag Conventions
<!-- How the user uses tags -->

## Cash Flow Rules
<!-- Tags to exclude from "true spending" calculations -->
internal_transfer_tags: [transfer, savings, investment]

## Income Sources
<!-- Known income sources for better reporting -->

## Active Plugins
<!-- Which plugins are installed and relevant -->

## Preferences
<!-- Reporting style, rounding, spouse-friendly mode, etc. -->

## Learned Facts
<!-- Anything else discovered about the user's financial setup -->
```

**Maintenance:**
- Update silently for small observations
- Ask before recording significant assumptions
- Periodically validate against live data (accounts may close, tags may change)

---

## Privacy Note

All data is local (`~/.treeline/treeline.duckdb`). Never share transaction descriptions or account details outside the conversation unless explicitly asked.
