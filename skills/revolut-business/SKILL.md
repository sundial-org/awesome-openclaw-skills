---
name: revolut
description: "Revolut Business API CLI — accounts, balances, transactions, counterparties, payments, FX exchange, CSV export. Auto-refreshes OAuth tokens. Business accounts only (not personal)."
version: 1.0.0
metadata: {"clawdbot":{"emoji":"💶","requires":{"bins":["python3"]}}}
---

# Revolut Business API

Full CLI for **Revolut Business** — accounts, transactions, payments, FX, exports.

**Entry point:** `python3 {baseDir}/scripts/revolut.py`

## Setup

### Interactive Setup Wizard (recommended)
```bash
python3 {baseDir}/scripts/setup.py
```
Walks you through everything: key generation, Revolut certificate upload, OAuth callback, authorization.

### Manual Setup
- Python 3.10+, `pip install PyJWT cryptography`
- Revolut Business account with API certificate
- See [README](https://github.com/christianhaberl/revolut-openclaw-skill) for detailed step-by-step guide

### Credentials
Stored in `~/.clawdbot/revolut/`:
- `private.pem` — RSA private key (for JWT signing)
- `certificate.pem` — X509 cert (uploaded to Revolut)
- `tokens.json` — OAuth tokens (auto-managed)
- `config.json` — client ID, domain, redirect URI

Environment variables (in `.env`):
- `REVOLUT_CLIENT_ID` — from Revolut API settings
- `REVOLUT_ISS_DOMAIN` — your redirect URI domain (without https://)

## Commands

### Accounts & Balances
```bash
python3 {baseDir}/scripts/revolut.py accounts          # List all accounts with balances
python3 {baseDir}/scripts/revolut.py balance            # Total EUR balance
python3 {baseDir}/scripts/revolut.py accounts --json    # JSON output
```

### Transactions
```bash
python3 {baseDir}/scripts/revolut.py transactions                    # Last 20
python3 {baseDir}/scripts/revolut.py tx -n 50                       # Last 50
python3 {baseDir}/scripts/revolut.py tx --since 2026-01-01           # Since date
python3 {baseDir}/scripts/revolut.py tx --since 2026-01-01 --to 2026-01-31
python3 {baseDir}/scripts/revolut.py tx -a Main                     # Filter by account
python3 {baseDir}/scripts/revolut.py tx --type card_payment          # Filter by type
python3 {baseDir}/scripts/revolut.py tx --json                      # JSON output
```

Transaction types: `card_payment`, `transfer`, `exchange`, `topup`, `atm`, `fee`, `refund`

### Counterparties
```bash
python3 {baseDir}/scripts/revolut.py counterparties     # List all
python3 {baseDir}/scripts/revolut.py cp --name "Lisa"   # Search by name
python3 {baseDir}/scripts/revolut.py cp --json
```

### Payments
```bash
# Send payment (with confirmation prompt)
python3 {baseDir}/scripts/revolut.py pay -c "Lisa Dreischer" --amount 50.00 --currency EUR -r "Lunch"

# Create draft (no immediate send)
python3 {baseDir}/scripts/revolut.py pay -c "Lisa Dreischer" --amount 50.00 --draft -r "Lunch"

# Skip confirmation
python3 {baseDir}/scripts/revolut.py pay -c "Lisa Dreischer" --amount 50.00 -y
```

### Currency Exchange
```bash
python3 {baseDir}/scripts/revolut.py exchange --amount 100 --sell EUR --buy USD
python3 {baseDir}/scripts/revolut.py fx --amount 500 --sell EUR --buy GBP
```

### Internal Transfers
```bash
python3 {baseDir}/scripts/revolut.py transfer --from-account <ID> --to-account <ID> --amount 100
```

### Export (CSV)
```bash
python3 {baseDir}/scripts/revolut.py export                           # Print CSV to stdout
python3 {baseDir}/scripts/revolut.py export -n 200 -o transactions.csv  # Save to file
python3 {baseDir}/scripts/revolut.py export --since 2026-01-01 -o jan.csv
```

### Token Status
```bash
python3 {baseDir}/scripts/revolut.py token-info
```

## Token Auto-Refresh
- Access tokens expire after ~40 minutes
- Automatically refreshed using the refresh token before API calls
- No manual intervention needed after initial auth

## Security Notes
- Private key and tokens are stored in `~/.clawdbot/revolut/` — treat as sensitive
- Payments require explicit confirmation (use `--yes` to skip)
- `--draft` creates payment drafts that need approval in Revolut app
- Never share your private key, tokens, or client assertion JWT
