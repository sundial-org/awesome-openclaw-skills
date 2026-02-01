---
name: monarch-money
description: TypeScript library and CLI for Monarch Money budget management. Search transactions by date/merchant/amount, update categories, list accounts and budgets, manage authentication. Use when user asks about Monarch Money transactions, wants to categorize spending, needs to find specific transactions, or wants to automate budget tasks.
metadata:
  clawdbot:
    requires:
      env: ["MONARCH_EMAIL", "MONARCH_PASSWORD", "MONARCH_MFA_SECRET"]
    install:
      - id: node
        kind: node
        package: "."
        bins: ["monarch-money"]
        label: "Install Monarch Money CLI"
---

# Monarch Money

CLI and TypeScript library for Monarch Money budget automation.

## Prerequisites

### Environment Variables (Required)

| Variable | Required | Description |
|----------|----------|-------------|
| `MONARCH_EMAIL` | **Yes** | Monarch Money account email |
| `MONARCH_PASSWORD` | **Yes** | Monarch Money account password |
| `MONARCH_MFA_SECRET` | **Yes** | TOTP secret for MFA (see below) |

### Getting Your MFA Secret

Monarch Money requires MFA. Generate the TOTP secret:

1. Login to https://app.monarchmoney.com
2. Go to Settings > Security > Two-Factor Authentication
3. If MFA is already enabled: disable and re-enable to get a new secret
4. When shown the QR code: click "Can't scan? View setup key"
5. Copy the secret key (base32 string like `JBSWY3DPEHPK3PXP`)
6. Complete MFA setup in Monarch Money with an authenticator app
7. Set the secret: `export MONARCH_MFA_SECRET="YOUR_SECRET"`

## Quick Start

```bash
# Check setup
monarch-money doctor

# Login (uses env vars by default)
monarch-money auth login

# List transactions
monarch-money tx list --limit 10

# List categories
monarch-money cat list
```

## CLI Commands

### Authentication

```bash
# Login with environment variables
monarch-money auth login

# Login with explicit credentials
monarch-money auth login -e email@example.com -p password --mfa-secret SECRET

# Check auth status
monarch-money auth status

# Logout
monarch-money auth logout
```

### Transactions

```bash
# List recent transactions
monarch-money tx list --limit 20

# Search by date
monarch-money tx list --start-date 2026-01-01 --end-date 2026-01-31

# Search by merchant
monarch-money tx list --merchant "Walmart"

# Get transaction by ID
monarch-money tx get <transaction_id>

# Update category
monarch-money tx update <id> --category <category_id>

# Update merchant name
monarch-money tx update <id> --merchant "New Name"

# Add notes
monarch-money tx update <id> --notes "My notes here"
```

### Categories

```bash
# List all categories
monarch-money cat list

# List with IDs (for updates)
monarch-money cat list --show-ids
```

### Accounts

```bash
# List accounts
monarch-money acc list

# Show account details
monarch-money acc get <account_id>
```

### Doctor (Diagnostics)

```bash
# Run diagnostic checks
monarch-money doctor
```

Checks:
- Environment variables set
- API connectivity
- Session validity
- Node.js version

## Library Usage

Import and use the TypeScript library directly:

```typescript
import { MonarchClient } from 'monarch-money';

const client = new MonarchClient({ baseURL: 'https://api.monarch.com' });

// Login
await client.login({
  email: process.env.MONARCH_EMAIL,
  password: process.env.MONARCH_PASSWORD,
  mfaSecretKey: process.env.MONARCH_MFA_SECRET
});

// Get transactions
const transactions = await client.transactions.getTransactions({ limit: 10 });

// Get categories
const categories = await client.categories.getCategories();

// Get accounts
const accounts = await client.accounts.getAll();
```

## Common Workflows

### Find and Update a Transaction

```bash
# 1. Find the transaction
monarch-money tx list --date 2026-01-15 --merchant "Target"

# 2. Get category ID
monarch-money cat list --show-ids

# 3. Update the transaction
monarch-money tx update <transaction_id> --category <category_id>
```

### Search Transactions by Date Range

```bash
monarch-money tx list --start-date 2026-01-01 --end-date 2026-01-31 --limit 100
```

### Check Budget Status

```bash
monarch-money acc list
```

## Error Handling

| Error | Solution |
|-------|----------|
| "Not logged in" | Run `monarch-money auth login` |
| "MFA code required" | Set `MONARCH_MFA_SECRET` environment variable |
| "Invalid credentials" | Verify email/password work at app.monarchmoney.com |
| "Session expired" | Run `monarch-money auth login` again |

## Session Management

Sessions are cached locally at `~/.mm/session.json`. After initial login, subsequent commands reuse the saved session for faster execution.

To clear the session: `monarch-money auth logout`

## References

- [API.md](references/API.md) - GraphQL API details and advanced usage
- [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) - Common issues and solutions
