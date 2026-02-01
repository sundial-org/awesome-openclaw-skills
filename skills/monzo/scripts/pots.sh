#!/bin/bash
# Manage Monzo savings pots
# Usage: pots [command] [options]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/monzo.sh"

# Parse arguments
COMMAND="list"
OUTPUT_MODE="human"
ARG_ACCOUNT_ID=""
POT_ID=""
AMOUNT=""
DEDUPE_ID=""

# Parse command if provided
if [[ $# -gt 0 && ! "$1" =~ ^- && ! "$1" =~ ^acc_ ]]; then
  COMMAND="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --account-id)
      ARG_ACCOUNT_ID="$2"
      shift 2
      ;;
    --dedupe-id)
      DEDUPE_ID="$2"
      shift 2
      ;;
    --json)
      OUTPUT_MODE="json"
      shift
      ;;
    -h|--help)
      echo "Usage: pots [command] [options]"
      echo ""
      echo "Manage savings pots"
      echo ""
      echo "Commands:"
      echo "  list                     List all pots (default)"
      echo "  deposit POT_ID AMOUNT    Deposit to pot (amount in pence)"
      echo "  withdraw POT_ID AMOUNT   Withdraw from pot (amount in pence)"
      echo ""
      echo "Options:"
      echo "  --account-id ID          Account ID (uses default if not specified)"
      echo "  --dedupe-id ID           Idempotency key (auto-generated if not provided)"
      echo "  --json                   Output raw JSON response"
      echo "  -h, --help               Show this help message"
      echo ""
      echo "Examples:"
      echo "  pots"
      echo "  pots list --json"
      echo "  pots deposit pot_... 5000   # Deposit £50"
      echo "  pots withdraw pot_... 2000  # Withdraw £20"
      exit 0
      ;;
    acc_*)
      ARG_ACCOUNT_ID="$1"
      shift
      ;;
    pot_*)
      POT_ID="$1"
      shift
      ;;
    *)
      # Check if it's a numeric amount
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        AMOUNT="$1"
        shift
      else
        echo "Error: Unknown option: $1" >&2
        echo "Use --help for usage information" >&2
        exit 1
      fi
      ;;
  esac
done

# Load credentials
monzo_load_credentials

# Get account ID
ACCOUNT_ID=$(monzo_ensure_account_id "$ARG_ACCOUNT_ID") || exit 1

# Handle deposit command
if [[ "$COMMAND" == "deposit" ]]; then
  if [[ -z "$POT_ID" ]]; then
    echo "Error: POT_ID required for deposit" >&2
    echo "Usage: pots deposit POT_ID AMOUNT" >&2
    exit 1
  fi

  if [[ -z "$AMOUNT" ]]; then
    echo "Error: AMOUNT required for deposit (in pence)" >&2
    echo "Usage: pots deposit POT_ID AMOUNT" >&2
    exit 1
  fi

  # Generate dedupe ID if not provided
  if [[ -z "$DEDUPE_ID" ]]; then
    DEDUPE_ID=$(monzo_generate_dedupe_id)
  fi

  response=$(monzo_api_call PUT "/pots/$POT_ID/deposit" \
    -d "source_account_id=$ACCOUNT_ID" \
    -d "amount=$AMOUNT" \
    -d "dedupe_id=$DEDUPE_ID")

  if [[ "$OUTPUT_MODE" == "json" ]]; then
    echo "$response"
    exit 0
  fi

  # Human-readable output
  pot_name=$(jq -r '.name' <<< "$response")
  new_balance=$(jq -r '.balance' <<< "$response")
  currency=$(jq -r '.currency' <<< "$response")

  echo "✓ Deposited $(monzo_format_money "$AMOUNT" "$currency") to $pot_name"
  echo "New balance: $(monzo_format_money "$new_balance" "$currency")"
  exit 0
fi

# Handle withdraw command
if [[ "$COMMAND" == "withdraw" ]]; then
  if [[ -z "$POT_ID" ]]; then
    echo "Error: POT_ID required for withdraw" >&2
    echo "Usage: pots withdraw POT_ID AMOUNT" >&2
    exit 1
  fi

  if [[ -z "$AMOUNT" ]]; then
    echo "Error: AMOUNT required for withdraw (in pence)" >&2
    echo "Usage: pots withdraw POT_ID AMOUNT" >&2
    exit 1
  fi

  # Generate dedupe ID if not provided
  if [[ -z "$DEDUPE_ID" ]]; then
    DEDUPE_ID=$(monzo_generate_dedupe_id)
  fi

  response=$(monzo_api_call PUT "/pots/$POT_ID/withdraw" \
    -d "destination_account_id=$ACCOUNT_ID" \
    -d "amount=$AMOUNT" \
    -d "dedupe_id=$DEDUPE_ID")

  if [[ "$OUTPUT_MODE" == "json" ]]; then
    echo "$response"
    exit 0
  fi

  # Human-readable output
  pot_name=$(jq -r '.name' <<< "$response")
  new_balance=$(jq -r '.balance' <<< "$response")
  currency=$(jq -r '.currency' <<< "$response")

  echo "✓ Withdrew $(monzo_format_money "$AMOUNT" "$currency") from $pot_name"
  echo "New balance: $(monzo_format_money "$new_balance" "$currency")"
  exit 0
fi

# Handle list command (default)
if [[ "$COMMAND" == "list" ]]; then
  response=$(monzo_api_call GET "/pots?current_account_id=$ACCOUNT_ID")

  # JSON mode
  if [[ "$OUTPUT_MODE" == "json" ]]; then
    echo "$response"
    exit 0
  fi

  # Human-readable mode
  pots=$(jq -r '.pots // []' <<< "$response")
  count=$(jq 'length' <<< "$pots")

  if [[ "$count" == "0" ]]; then
    echo "No pots found"
    exit 0
  fi

  # Display pots in table format
  printf "%-25s %-12s %-12s %s\n" "NAME" "BALANCE" "GOAL" "ID"
  printf "%-25s %-12s %-12s %s\n" "=========================" "============" "============" "===================="

  jq -r '.[] | select(.deleted == false) |
    [
      .name,
      (.balance | tostring),
      (.currency),
      (if .goal_amount then (.goal_amount | tostring) else "null" end),
      .id
    ] | @tsv' <<< "$pots" | \
  while IFS=$'\t' read -r name balance currency goal pot_id; do
    formatted_balance=$(monzo_format_money "$balance" "$currency")

    if [[ "$goal" != "null" ]]; then
      formatted_goal=$(monzo_format_money "$goal" "$currency")
    else
      formatted_goal="-"
    fi

    # Truncate name if too long
    if [[ ${#name} -gt 25 ]]; then
      name="${name:0:22}..."
    fi

    printf "%-25s %-12s %-12s %s\n" "$name" "$formatted_balance" "$formatted_goal" "$pot_id"
  done

  echo ""
  echo "Total: $count pot(s)"
  exit 0
fi

echo "Error: Unknown command: $COMMAND" >&2
echo "Use --help for usage information" >&2
exit 1
