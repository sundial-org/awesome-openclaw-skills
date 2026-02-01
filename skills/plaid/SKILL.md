---
name: plaid
description: plaid-cli a cli for interacting with the plaid finance platform. link accounts from various institutions, query balances, and transactions by date range listing accounts/balances.
metadata: {"clawdis":{"emoji":"💳","requires":{"bins":["plaid-cli"]},"install":[{"id":"go","kind":"go","module":"github.com/jverdi/plaid-cli@0.0.2","bins":["plaid-cli"],"label":"Install plaid-cli (go)"}]}}
---

# Plaid

Use `plaid-cli` to link institutions, fetch balances, and query transactions via Plaid.
Do not print or log secrets (client id, secret, access tokens).

Install
- `go install github.com/jverdi/plaid-cli@0.0.2`

Setup
- Export `PLAID_CLIENT_ID`, `PLAID_SECRET`, and `PLAID_ENVIRONMENT` (sandbox or production).
- Optional: `PLAID_LANGUAGE` (en, fr, es, nl), `PLAID_COUNTRIES` (US, CA, GB, IE, ES, FR, NL).
- Optional config file: `~/.plaid-cli/config.toml`.
  ```toml
  [plaid]
  client_id = "..."
  secret = "..."
  environment = "sandbox"
  ```
- Data directory: `~/.plaid-cli` (stores tokens and aliases).

Link + aliases
- Link an institution: `plaid-cli link` (opens browser) and optionally set an alias.
- Relink: `plaid-cli link <item-id-or-alias>`.
- Alias: `plaid-cli alias <item-id> <name>`, list with `plaid-cli aliases`.

Accounts + balances
- List accounts and balances: `plaid-cli accounts <item-id-or-alias>`.

Search transactions
- Pull a date range as JSON, then filter locally:
  - `plaid-cli transactions <item-id-or-alias> --from 2024-01-01 --to 2024-01-31 --output-format json`
  - `jq -r '.[] | select(.name | test("grocery"; "i")) | [.date, .name, .amount] | @tsv'`
- Use `--account-id` from `accounts` output to narrow results.
- Output formats: `json` or `csv`.

Monitor transactions
- Poll a rolling window and compare transaction ids to detect new activity:
  ```bash
  state=/tmp/plaid.txids
  next=/tmp/plaid.txids.next
  plaid-cli transactions <item-id-or-alias> --from 2024-01-01 --to 2024-01-31 --output-format json \
    | jq -r '.[].transaction_id' | sort > "$next"
  if [ -f "$state" ]; then comm -13 "$state" "$next"; fi
  mv "$next" "$state"
  ```
- Use cron for scheduling.

Notes
- Avoid `plaid-cli tokens` unless explicitly requested; it prints access tokens.
- Relink is auto-triggered on `ITEM_LOGIN_REQUIRED` errors.

Recognize requests such as:
- "Search transactions for Starbucks last month"
- "Show balances for my Chase accounts"
