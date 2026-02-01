#!/bin/bash
# Validate Monzo authentication and show account information
# Usage: whoami [--account-id] [--json]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/monzo.sh"

# Parse arguments
OUTPUT_MODE="human"
ACCOUNT_ID_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      OUTPUT_MODE="json"
      shift
      ;;
    --account-id)
      ACCOUNT_ID_ONLY=true
      shift
      ;;
    -h|--help)
      echo "Usage: whoami [--account-id] [--json]"
      echo ""
      echo "Validate authentication and show account information"
      echo ""
      echo "Options:"
      echo "  --account-id    Print only the default account ID"
      echo "  --json          Output raw JSON response"
      echo "  -h, --help      Show this help message"
      exit 0
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

# If only account ID requested
if [[ "$ACCOUNT_ID_ONLY" == true ]]; then
  if [[ -z "$ACCOUNT_ID" ]]; then
    echo "Error: No default account ID configured" >&2
    exit 1
  fi
  echo "$ACCOUNT_ID"
  exit 0
fi

# Call whoami endpoint
response=$(monzo_api_call GET "/ping/whoami")

# JSON mode - output raw response
if [[ "$OUTPUT_MODE" == "json" ]]; then
  echo "$response"
  exit 0
fi

# Human-readable mode
authenticated=$(jq -r '.authenticated' <<< "$response")
client_id=$(jq -r '.client_id // "N/A"' <<< "$response")
user_id=$(jq -r '.user_id // "N/A"' <<< "$response")

echo "Authenticated: $(if [[ "$authenticated" == "true" ]]; then echo "✓"; else echo "✗"; fi)"
echo "Client ID: $client_id"
echo "User ID: $user_id"

# Fetch and display accounts
accounts_response=$(monzo_api_call GET "/accounts")

echo ""
echo "Accounts:"

# Check if we have any accounts
account_count=$(jq '.accounts | length' <<< "$accounts_response")

if [[ "$account_count" == "0" ]]; then
  echo "  No accounts found"
else
  jq -r '.accounts[] | select(.closed == false) | "  • \(.id) - \(.description) (\(.type))" + (if .id == "'$ACCOUNT_ID'" then " [default]" else "" end)' <<< "$accounts_response"

  # Show closed accounts if any
  closed_count=$(jq '[.accounts[] | select(.closed == true)] | length' <<< "$accounts_response")
  if [[ "$closed_count" -gt "0" ]]; then
    echo ""
    echo "Closed accounts:"
    jq -r '.accounts[] | select(.closed == true) | "  • \(.id) - \(.description) (\(.type))"' <<< "$accounts_response"
  fi
fi

# Show default account if set
if [[ -n "$ACCOUNT_ID" ]]; then
  echo ""
  echo "Default account ID: $ACCOUNT_ID"
fi
