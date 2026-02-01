#!/bin/bash
# Manage Monzo webhooks for real-time notifications
# Usage: webhooks [command] [options]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/monzo.sh"

# Parse arguments
COMMAND=""
OUTPUT_MODE="human"
ARG_ACCOUNT_ID=""
WEBHOOK_URL=""
WEBHOOK_ID=""

# Parse command if provided
if [[ $# -gt 0 && "$1" =~ ^(list|create|delete)$ ]]; then
  COMMAND="$1"
  shift

  # Get URL or webhook ID for command
  if [[ $# -gt 0 && ! "$1" =~ ^- ]]; then
    if [[ "$COMMAND" == "create" ]]; then
      WEBHOOK_URL="$1"
    elif [[ "$COMMAND" == "delete" ]]; then
      WEBHOOK_ID="$1"
    elif [[ "$COMMAND" == "list" && "$1" =~ ^acc_ ]]; then
      ARG_ACCOUNT_ID="$1"
    fi
    shift
  fi
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      OUTPUT_MODE="json"
      shift
      ;;
    -h|--help)
      echo "Usage: webhooks [command] [options]"
      echo ""
      echo "Manage real-time transaction webhooks"
      echo ""
      echo "Commands:"
      echo "  list [account-id]        List webhooks"
      echo "  create URL [account-id]  Register webhook"
      echo "  delete WEBHOOK_ID        Delete webhook"
      echo ""
      echo "Options:"
      echo "  --json                   Output raw JSON response"
      echo "  -h, --help               Show this help message"
      echo ""
      echo "Examples:"
      echo "  webhooks list"
      echo "  webhooks create https://mybot.example.com/monzo-webhook"
      echo "  webhooks delete webhook_..."
      exit 0
      ;;
    acc_*)
      ARG_ACCOUNT_ID="$1"
      shift
      ;;
    webhook_*)
      WEBHOOK_ID="$1"
      shift
      ;;
    https://*)
      WEBHOOK_URL="$1"
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

# Default command
if [[ -z "$COMMAND" ]]; then
  COMMAND="list"
fi

# Handle delete command
if [[ "$COMMAND" == "delete" ]]; then
  if [[ -z "$WEBHOOK_ID" ]]; then
    echo "Error: WEBHOOK_ID required for delete" >&2
    echo "Usage: webhooks delete WEBHOOK_ID" >&2
    exit 1
  fi

  response=$(monzo_api_call DELETE "/webhooks/$WEBHOOK_ID")

  if [[ "$OUTPUT_MODE" == "json" ]]; then
    echo "$response"
  else
    echo "✓ Webhook deleted"
  fi
  exit 0
fi

# Handle create command
if [[ "$COMMAND" == "create" ]]; then
  if [[ -z "$WEBHOOK_URL" ]]; then
    echo "Error: URL required for create" >&2
    echo "Usage: webhooks create URL [account-id]" >&2
    exit 1
  fi

  # Validate HTTPS
  if [[ ! "$WEBHOOK_URL" =~ ^https:// ]]; then
    echo "Error: Webhook URL must use HTTPS" >&2
    exit 1
  fi

  # Get account ID
  ACCOUNT_ID=$(monzo_ensure_account_id "$ARG_ACCOUNT_ID") || exit 1

  response=$(monzo_api_call POST "/webhooks" \
    -d "account_id=$ACCOUNT_ID" \
    -d "url=$WEBHOOK_URL")

  if [[ "$OUTPUT_MODE" == "json" ]]; then
    echo "$response"
    exit 0
  fi

  # Human-readable output
  webhook_id=$(jq -r '.webhook.id' <<< "$response")
  url=$(jq -r '.webhook.url' <<< "$response")

  echo "✓ Webhook registered"
  echo "ID: $webhook_id"
  echo "URL: $url"
  exit 0
fi

# Handle list command (default)
if [[ "$COMMAND" == "list" ]]; then
  # Get account ID
  ACCOUNT_ID=$(monzo_ensure_account_id "$ARG_ACCOUNT_ID") || exit 1

  response=$(monzo_api_call GET "/webhooks?account_id=$ACCOUNT_ID")

  # JSON mode
  if [[ "$OUTPUT_MODE" == "json" ]]; then
    echo "$response"
    exit 0
  fi

  # Human-readable mode
  webhooks=$(jq -r '.webhooks // []' <<< "$response")
  count=$(jq 'length' <<< "$webhooks")

  if [[ "$count" == "0" ]]; then
    echo "No webhooks registered"
    exit 0
  fi

  # Display webhooks in table format
  printf "%-25s %-50s %s\n" "ID" "URL" "ACCOUNT"
  printf "%-25s %-50s %s\n" "=========================" "==================================================" "===================="

  jq -r '.[] |
    [
      .id,
      .url,
      .account_id
    ] | @tsv' <<< "$webhooks" | \
  while IFS=$'\t' read -r webhook_id url account_id; do
    # Truncate URL if too long
    if [[ ${#url} -gt 50 ]]; then
      url="${url:0:47}..."
    fi

    printf "%-25s %-50s %s\n" "$webhook_id" "$url" "$account_id"
  done

  echo ""
  echo "Total: $count webhook(s)"
  exit 0
fi

echo "Error: Unknown command: $COMMAND" >&2
echo "Use --help for usage information" >&2
exit 1
