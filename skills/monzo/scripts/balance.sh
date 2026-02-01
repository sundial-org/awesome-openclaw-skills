#!/bin/bash
# Check Monzo account balance
# Usage: balance [account-id] [--json]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/monzo.sh"

# Parse arguments
OUTPUT_MODE="human"
ARG_ACCOUNT_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      OUTPUT_MODE="json"
      shift
      ;;
    -h|--help)
      echo "Usage: balance [account-id] [--json]"
      echo ""
      echo "Check account balance"
      echo ""
      echo "Arguments:"
      echo "  account-id      Account ID (uses default if not specified)"
      echo ""
      echo "Options:"
      echo "  --json          Output raw JSON response"
      echo "  -h, --help      Show this help message"
      exit 0
      ;;
    acc_*)
      ARG_ACCOUNT_ID="$1"
      shift
      ;;
    *)
      echo "Error: Unknown option: $1" >&2
      echo "Use --help for usage information" >&2
      exit 1
      ;;
  esac
done

# Load credentials
monzo_load_credentials

# Get account ID
ACCOUNT_ID=$(monzo_ensure_account_id "$ARG_ACCOUNT_ID") || exit 1

# Fetch balance
response=$(monzo_api_call GET "/balance?account_id=$ACCOUNT_ID")

# JSON mode - output raw response
if [[ "$OUTPUT_MODE" == "json" ]]; then
  echo "$response"
  exit 0
fi

# Human-readable mode
balance=$(jq -r '.balance' <<< "$response")
total_balance=$(jq -r '.total_balance // .balance' <<< "$response")
currency=$(jq -r '.currency' <<< "$response")
spend_today=$(jq -r '.spend_today // 0' <<< "$response")

# Format as positive for spend
spend_today=$((-spend_today))

echo "Current Balance: $(monzo_format_money "$balance" "$currency")"

# Only show total if different from balance (i.e., pots exist)
if [[ "$balance" != "$total_balance" ]]; then
  echo "Total (with pots): $(monzo_format_money "$total_balance" "$currency")"
fi

echo "Spent today: $(monzo_format_money "$spend_today" "$currency")"
