---
name: monzo
description: Access Monzo bank account - check balance, view transactions, manage pots, send feed notifications. For personal finance queries and banking automation.
---

# Monzo Banking Skill

Access your Monzo bank account to check balances, view transactions, manage savings pots, and send notifications to your Monzo app.

## Prerequisites

Before setting up this skill, you need:

- **A Monzo account** (UK personal, joint, or business account)
- **The Monzo app** installed on your phone (for SCA approval)
- **Clawdbot** running with workspace access
- **Standard tools**: `curl`, `jq`, `openssl`, `bc` (pre-installed on most Linux systems)

## Quick Start (TL;DR)

```bash
# 1. Add env var to Clawdbot config (~/.clawdbot/clawdbot.json):
#    skills.entries.monzo.env.MONZO_KEYRING_PASSWORD = "your-secret-password"

# 2. Create OAuth client at https://developers.monzo.com/
#    - Set Confidentiality: Confidential
#    - Set Redirect URL: http://localhost

# 3. Run setup
scripts/setup.sh

# 4. Approve in Monzo app when prompted, then:
scripts/setup.sh --continue

# 5. Test it
scripts/balance.sh
```

---

## Detailed Setup Guide

### Step 1: Configure Clawdbot Environment

Add the encryption password to your Clawdbot config (`~/.clawdbot/clawdbot.json`):

```json5
{
  skills: {
    entries: {
      "monzo": {
        enabled: true,
        env: {
          "MONZO_KEYRING_PASSWORD": "choose-a-secure-password-here"
        }
      }
    }
  }
}
```

**Important:** This password encrypts your Monzo credentials at rest. Choose something secure and don't lose it — you'll need it if you ever move or restore the skill.

After editing, restart Clawdbot:
```bash
clawdbot gateway restart
```

### Step 2: Create Monzo OAuth Client

1. Go to **https://developers.monzo.com/** and sign in with your Monzo account
2. Click **"Clients"** → **"New OAuth Client"**
3. Fill in:
   - **Name**: `Clawdbot` (or your preferred name)
   - **Logo URL**: *(leave blank)*
   - **Redirect URLs**: `http://localhost` ← exactly this, no trailing slash
   - **Description**: *(leave blank)*
   - **Confidentiality**: **Confidential** ← ⚠️ Important! Enables refresh tokens
4. Click **Submit**
5. Note your **Client ID** (`oauth2client_...`) and **Client Secret** (`mnzconf....`)

### Step 3: Run the Setup Wizard

```bash
scripts/setup.sh
```

The wizard will:
1. Ask for your Client ID and Client Secret
2. Give you an authorization URL to open in your browser
3. Ask you to paste the redirect URL back
4. Exchange the code for access tokens
5. Save encrypted credentials

**Alternative: Non-interactive mode** (useful for automation or agents):
```bash
scripts/setup.sh --non-interactive \
  --client-id oauth2client_xxx \
  --client-secret mnzconf.xxx \
  --auth-code eyJ...
```

### Step 4: Approve in Monzo App (SCA)

⚠️ **This step is required!** Monzo requires Strong Customer Authentication.

1. Open the **Monzo app** on your phone
2. Look for a notification about "API access" or a new connection
3. **Tap to approve**

If you don't see a notification:
- Go to **Account → Settings → Privacy & Security → Manage connected apps**
- Find and approve your client

After approving, complete setup:
```bash
scripts/setup.sh --continue
```

### Step 5: Verify It Works

```bash
# Check authentication
scripts/whoami.sh

# Check your balance
scripts/balance.sh
```

You should see your account info and current balance. You're done! 🎉

---

## For the Agent

This section tells the agent how to use this skill effectively.

### When to Use This Skill

Use this skill when the user asks about:
- **Balance**: "How much money do I have?", "What's my balance?"
- **Transactions**: "What did I spend on X?", "Show recent transactions"
- **Spending analysis**: "How much did I spend on coffee this month?"
- **Savings**: "How much is in my savings?", "Move £X to my holiday pot"
- **Notifications**: "Send a reminder to my Monzo app"

### Common Patterns

```bash
# "How much money do I have?"
scripts/balance.sh

# "Show me recent transactions" / "What did I spend?"
scripts/transactions.sh              # All available, newest first

# "Show me my last 5 transactions"
scripts/transactions.sh --limit 5    # 5 most recent

# "What did I spend this week?"
scripts/transactions.sh --since 7d

# "How much did I spend on coffee this month?"
scripts/transactions.sh --search coffee --since 30d

# "What are my savings pots?"
scripts/pots.sh

# "Put £50 in my holiday fund"
scripts/pots.sh deposit pot_XXXXX 5000  # Amount in pence!

# "Send a reminder to my phone"
scripts/feed.sh --title "Don't forget!" --body "Check the gas meter"
```

### Important Notes for Agents

1. **Money is in pence**: £50 = 5000, £1.50 = 150
2. **Dates can be relative**: `--since 7d` means last 7 days
3. **Use human-readable output** by default (no `--json` flag)
4. **Pot IDs**: Use `scripts/pots.sh` first to get pot IDs before depositing/withdrawing
5. **Multiple accounts**: User may have personal, joint, and business accounts. Default is personal. Use `scripts/whoami.sh` to see all accounts.

### Error Handling

If you see `forbidden.insufficient_permissions`:
- Tell the user to check their Monzo app and approve API access
- Then run `scripts/setup.sh --continue`

If you see `MONZO_KEYRING_PASSWORD not set`:
- The env var isn't configured in Clawdbot
- Guide user to add it to `~/.clawdbot/clawdbot.json` under `skills.entries.monzo.env`

---

## Script Reference

### balance - Check Account Balance

```bash
scripts/balance.sh                 # Default account
scripts/balance.sh acc_...         # Specific account
scripts/balance.sh --json          # JSON output
```

**Output:**
```
Current Balance: £1,234.56
Total (with pots): £2,500.00
Spent today: £12.34
```

### transactions - Transaction History

Fetches **all available transactions** (paginated), displayed **newest first**.

```bash
scripts/transactions.sh                         # All transactions, newest first
scripts/transactions.sh --limit 10              # 10 most recent
scripts/transactions.sh --since 7d              # Last 7 days only
scripts/transactions.sh --since 2026-01-01      # Since specific date
scripts/transactions.sh --search coffee         # Search by merchant/description/notes
scripts/transactions.sh --search "Pret" --since 30d  # Combined filters
scripts/transactions.sh --id tx_...             # Get specific transaction
scripts/transactions.sh --json                  # JSON output
```

**Output:**
```
DATE         AMOUNT     DESCRIPTION                          CATEGORY
============ ========== =================================== ===============
2026-01-29  -£3.50     Pret A Manger                       eating_out
2026-01-29  -£12.00    TfL                                 transport
2026-01-28  -£45.23    Tesco                               groceries

Total: 3 transaction(s)
```

### pots - Savings Management

```bash
scripts/pots.sh                              # List all pots
scripts/pots.sh list --json                  # JSON output
scripts/pots.sh deposit pot_... 5000         # Deposit £50 (5000 pence)
scripts/pots.sh withdraw pot_... 2000        # Withdraw £20 (2000 pence)
```

**Output (list):**
```
NAME                      BALANCE      GOAL         ID
========================= ============ ============ ====================
Holiday Fund              £450.00      £1,000.00    pot_0000...
Emergency                 £2,000.00    £3,000.00    pot_0001...
```

### feed - Send App Notifications

```bash
scripts/feed.sh --title "Reminder"                        # Simple notification
scripts/feed.sh --title "Alert" --body "Details here"    # With body
scripts/feed.sh --title "Link" --url "https://..."       # With tap action
```

### whoami - Check Authentication

```bash
scripts/whoami.sh                  # Show auth status and accounts
scripts/whoami.sh --account-id     # Just the default account ID
scripts/whoami.sh --json           # JSON output
```

### receipt - Attach Receipts to Transactions

```bash
scripts/receipt.sh create tx_... --merchant "Shop" --total 1234 --item "Thing:1234"
scripts/receipt.sh get ext_...
scripts/receipt.sh delete ext_...
```

### webhooks - Manage Webhooks (Advanced)

```bash
scripts/webhooks.sh list
scripts/webhooks.sh create https://your-server.com/webhook
scripts/webhooks.sh delete webhook_...
```

---

## Troubleshooting

### "forbidden.insufficient_permissions"

**Most common issue!** Monzo requires app approval (SCA).

**Fix:**
1. Open Monzo app → check for notification → approve
2. Or: Account → Settings → Privacy & Security → Manage connected apps → approve
3. Run: `scripts/setup.sh --continue`

### "MONZO_KEYRING_PASSWORD not set"

The env var isn't in Clawdbot's environment.

**Fix:** Add to `~/.clawdbot/clawdbot.json`:
```json5
{
  skills: {
    entries: {
      "monzo": {
        env: { "MONZO_KEYRING_PASSWORD": "your-password" }
      }
    }
  }
}
```
Then restart: `clawdbot gateway restart`

### "Authorization code has been used"

Each auth code is single-use. Start fresh:
```bash
scripts/setup.sh --reset
```

### "No refresh token received"

Your OAuth client isn't set to "Confidential". Create a new client with Confidentiality = Confidential, then:
```bash
scripts/setup.sh --reset
```

### "Credentials file not found"

Run setup first:
```bash
scripts/setup.sh
```

### "Failed to decrypt credentials"

Wrong `MONZO_KEYRING_PASSWORD`. Check your config matches what you used during setup.

---

## Security Notes

- Credentials are **encrypted at rest** (AES-256-CBC)
- Encryption key is your `MONZO_KEYRING_PASSWORD`
- Access tokens auto-refresh (no manual intervention needed)
- File permissions are set to 600 (owner only)
- All API calls use HTTPS
- No sensitive data is logged

---

## Files

```
skills/monzo/
├── SKILL.md              # This documentation
└── scripts/
    ├── lib/monzo.sh      # Shared library
    ├── setup             # OAuth setup wizard
    ├── whoami            # Validate authentication
    ├── balance           # Check balance
    ├── transactions      # Transaction history
    ├── pots              # Savings pots
    ├── feed              # App notifications
    ├── receipt           # Receipt management
    └── webhooks          # Webhook management
```

**Credentials:** `~/.clawdbot/credentials/monzo.json` (encrypted)

---

## API Coverage

| Feature | Scripts |
|---------|---------|
| Authentication | setup, whoami |
| Balance | balance |
| Transactions | transactions |
| Pots (Savings) | pots |
| Feed (Notifications) | feed |
| Receipts | receipt |
| Webhooks | webhooks |
