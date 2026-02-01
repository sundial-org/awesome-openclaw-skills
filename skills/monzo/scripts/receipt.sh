#!/bin/bash
# Manage transaction receipts
# Usage: receipt [command] [options]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/monzo.sh"

# Parse arguments
COMMAND=""
TRANSACTION_ID=""
EXTERNAL_ID=""
MERCHANT=""
TOTAL=""
CURRENCY="GBP"
ITEMS=()
JSON_FILE=""

# Parse command if provided
if [[ $# -gt 0 && "$1" =~ ^(create|get|delete)$ ]]; then
  COMMAND="$1"
  shift

  # Get transaction/external ID for command
  if [[ $# -gt 0 && ! "$1" =~ ^- ]]; then
    if [[ "$COMMAND" == "create" ]]; then
      TRANSACTION_ID="$1"
    else
      EXTERNAL_ID="$1"
    fi
    shift
  fi
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --external-id)
      EXTERNAL_ID="$2"
      shift 2
      ;;
    --merchant)
      MERCHANT="$2"
      shift 2
      ;;
    --total)
      TOTAL="$2"
      shift 2
      ;;
    --currency)
      CURRENCY="$2"
      shift 2
      ;;
    --item)
      ITEMS+=("$2")
      shift 2
      ;;
    --json)
      JSON_FILE="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: receipt [command] [options]"
      echo ""
      echo "Manage transaction receipts"
      echo ""
      echo "Commands:"
      echo "  create TRANSACTION_ID   Create receipt for transaction"
      echo "  get EXTERNAL_ID         Retrieve receipt"
      echo "  delete EXTERNAL_ID      Delete receipt"
      echo ""
      echo "Options (for create):"
      echo "  --external-id ID        External ID (auto-generated if not set)"
      echo "  --merchant NAME         Merchant name"
      echo "  --total AMOUNT          Total in pence (required for manual creation)"
      echo "  --currency CODE         Currency code (default: GBP)"
      echo "  --item \"DESC:AMOUNT\"    Line item, can be repeated"
      echo "  --json FILE             Full receipt JSON from file"
      echo ""
      echo "Examples:"
      echo "  receipt create tx_... --merchant \"Tesco\" --total 4523 \\"
      echo "    --item \"Milk:199\" --item \"Bread:145\" --item \"Eggs:279\""
      echo "  receipt create tx_... --json receipt.json"
      echo "  receipt get ext_12345"
      echo "  receipt delete ext_12345"
      exit 0
      ;;
    tx_*)
      TRANSACTION_ID="$1"
      shift
      ;;
    ext_*)
      EXTERNAL_ID="$1"
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

# Handle get command
if [[ "$COMMAND" == "get" ]]; then
  if [[ -z "$EXTERNAL_ID" ]]; then
    echo "Error: EXTERNAL_ID required for get" >&2
    echo "Usage: receipt get EXTERNAL_ID" >&2
    exit 1
  fi

  response=$(monzo_api_call GET "/transaction-receipts?external_id=$EXTERNAL_ID")

  # Pretty print the receipt
  echo "$response" | jq '.'
  exit 0
fi

# Handle delete command
if [[ "$COMMAND" == "delete" ]]; then
  if [[ -z "$EXTERNAL_ID" ]]; then
    echo "Error: EXTERNAL_ID required for delete" >&2
    echo "Usage: receipt delete EXTERNAL_ID" >&2
    exit 1
  fi

  response=$(monzo_api_call DELETE "/transaction-receipts?external_id=$EXTERNAL_ID")

  echo "✓ Receipt deleted"
  exit 0
fi

# Handle create command
if [[ "$COMMAND" == "create" ]]; then
  if [[ -z "$TRANSACTION_ID" ]]; then
    echo "Error: TRANSACTION_ID required for create" >&2
    echo "Usage: receipt create TRANSACTION_ID [options]" >&2
    exit 1
  fi

  # Generate external ID if not provided
  if [[ -z "$EXTERNAL_ID" ]]; then
    EXTERNAL_ID="ext_$(date +%Y%m%d)_$(monzo_generate_dedupe_id)"
  fi

  # If JSON file provided, use that
  if [[ -n "$JSON_FILE" ]]; then
    if [[ ! -f "$JSON_FILE" ]]; then
      echo "Error: JSON file not found: $JSON_FILE" >&2
      exit 1
    fi

    receipt_json=$(cat "$JSON_FILE")

    # Add external_id and transaction_id if not in JSON
    receipt_json=$(jq \
      --arg external_id "$EXTERNAL_ID" \
      --arg transaction_id "$TRANSACTION_ID" \
      '. + {external_id: $external_id, transaction_id: $transaction_id}' \
      <<< "$receipt_json")
  else
    # Build receipt JSON from parameters
    if [[ -z "$TOTAL" ]]; then
      echo "Error: --total required when creating receipt manually" >&2
      exit 1
    fi

    # Build items array
    items_json="[]"
    for item_str in "${ITEMS[@]}"; do
      if [[ "$item_str" =~ ^([^:]+):([0-9]+)$ ]]; then
        desc="${BASH_REMATCH[1]}"
        amount="${BASH_REMATCH[2]}"

        items_json=$(jq \
          --arg desc "$desc" \
          --arg amount "$amount" \
          '. += [{
            description: $desc,
            quantity: 1,
            amount: ($amount | tonumber),
            currency: "GBP",
            units: 1
          }]' \
          <<< "$items_json")
      else
        echo "Error: Invalid item format: $item_str (should be DESC:AMOUNT)" >&2
        exit 1
      fi
    done

    # Build full receipt JSON
    receipt_json=$(jq -n \
      --arg external_id "$EXTERNAL_ID" \
      --arg transaction_id "$TRANSACTION_ID" \
      --arg total "$TOTAL" \
      --arg currency "$CURRENCY" \
      --argjson items "$items_json" \
      --arg merchant "$MERCHANT" \
      '{
        external_id: $external_id,
        transaction_id: $transaction_id,
        total: ($total | tonumber),
        currency: $currency,
        items: $items
      } + (if $merchant != "" then {
        merchant: {
          name: $merchant,
          online: false
        }
      } else {} end)')
  fi

  # Check token expiry before making the request
  monzo_check_expiry

  # Create the receipt
  response=$(curl -s -X PUT "$MONZO_API_BASE/transaction-receipts" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$receipt_json")

  # Check for errors
  error=$(jq -r '.error // empty' <<< "$response")
  if [[ -n "$error" ]]; then
    echo "Error: $error" >&2
    message=$(jq -r '.message // empty' <<< "$response")
    if [[ -n "$message" ]]; then
      echo "Message: $message" >&2
    fi
    echo "Response: $response" >&2
    exit 1
  fi

  echo "✓ Receipt created"
  echo "External ID: $EXTERNAL_ID"
  exit 0
fi

echo "Error: Command required (create, get, delete)" >&2
echo "Use --help for usage information" >&2
exit 1
