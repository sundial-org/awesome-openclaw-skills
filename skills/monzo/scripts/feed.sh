#!/bin/bash
# Send custom notifications to Monzo app
# Usage: feed [options]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/monzo.sh"

# Parse arguments
ARG_ACCOUNT_ID=""
TITLE=""
BODY=""
IMAGE_URL=""
ACTION_URL=""
BG_COLOR="#FF0000"
TITLE_COLOR="#FFFFFF"
BODY_COLOR="#FFFFFF"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title)
      TITLE="$2"
      shift 2
      ;;
    --body)
      BODY="$2"
      shift 2
      ;;
    --image-url)
      IMAGE_URL="$2"
      shift 2
      ;;
    --url)
      ACTION_URL="$2"
      shift 2
      ;;
    --bg-color)
      BG_COLOR="$2"
      shift 2
      ;;
    --title-color)
      TITLE_COLOR="$2"
      shift 2
      ;;
    --body-color)
      BODY_COLOR="$2"
      shift 2
      ;;
    --account-id)
      ARG_ACCOUNT_ID="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: feed [options]"
      echo ""
      echo "Send custom notifications to Monzo app"
      echo ""
      echo "Options:"
      echo "  --title TEXT         Feed item title (required)"
      echo "  --body TEXT          Feed item body"
      echo "  --image-url URL      Image URL"
      echo "  --url URL            URL to open when tapped"
      echo "  --bg-color HEX       Background color (default: #FF0000)"
      echo "  --title-color HEX    Title color (default: #FFFFFF)"
      echo "  --body-color HEX     Body color (default: #FFFFFF)"
      echo "  --account-id ID      Account ID (uses default if not specified)"
      echo "  -h, --help           Show this help message"
      echo ""
      echo "Examples:"
      echo "  feed --title \"Remember to check gym schedule\""
      echo "  feed --title \"Package Delivered\" --body \"Your Amazon order arrived\""
      echo "  feed --title \"Savings Goal!\" --bg-color \"#14233C\" --title-color \"#00D4FF\""
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

# Validate required parameters
if [[ -z "$TITLE" ]]; then
  echo "Error: --title is required" >&2
  exit 1
fi

# Validate color formats
validate_color() {
  local color="$1"
  if [[ ! "$color" =~ ^#[0-9A-Fa-f]{6}$ ]]; then
    echo "Error: Invalid color format: $color (use #RRGGBB)" >&2
    exit 1
  fi
}

validate_color "$BG_COLOR"
validate_color "$TITLE_COLOR"
validate_color "$BODY_COLOR"

# Load credentials
monzo_load_credentials

# Get account ID
ACCOUNT_ID=$(monzo_ensure_account_id "$ARG_ACCOUNT_ID") || exit 1

# Build params JSON
params=$(jq -n \
  --arg title "$TITLE" \
  --arg body "$BODY" \
  --arg image_url "$IMAGE_URL" \
  --arg bg_color "$BG_COLOR" \
  --arg title_color "$TITLE_COLOR" \
  --arg body_color "$BODY_COLOR" \
  '{
    title: $title,
    body: $body,
    background_color: $bg_color,
    title_color: $title_color,
    body_color: $body_color
  } + (if $image_url != "" then {image_url: $image_url} else {} end)')

# Build POST data
POST_DATA="account_id=$ACCOUNT_ID&type=basic&params=$(jq -r '@uri' <<< "$params")"

# Add URL if provided
if [[ -n "$ACTION_URL" ]]; then
  POST_DATA="$POST_DATA&url=$(jq -rn --arg url "$ACTION_URL" '$url | @uri')"
fi

# Create feed item
response=$(monzo_api_call POST "/feed" -d "$POST_DATA")

# Check for errors
error=$(jq -r '.error // empty' <<< "$response")
if [[ -n "$error" ]]; then
  echo "Error: $error" >&2
  exit 1
fi

echo "✓ Feed item created"
