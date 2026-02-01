#!/bin/bash
# Monzo API helper library
# Shared functions for authentication, API calls, and formatting

set -euo pipefail

# Constants
MONZO_API_BASE="${MONZO_API_BASE:-https://api.monzo.com}"
CREDENTIALS_DIR="${CLAWDBOT_CREDENTIALS_DIR:-${HOME}/.clawdbot/credentials}"
CREDENTIALS_FILE="${CREDENTIALS_DIR}/monzo.json"

# Global variables (loaded from credentials)
CREDENTIALS=""
CLIENT_ID=""
CLIENT_SECRET=""
ACCESS_TOKEN=""
REFRESH_TOKEN=""
TOKEN_EXPIRY=0
ACCOUNT_ID=""

# ============================================================================
# Credential Management
# ============================================================================

# Encrypt JSON credentials to file
monzo_encrypt_credentials() {
  local json="$1"

  if [[ -z "${MONZO_KEYRING_PASSWORD:-}" ]]; then
    echo "Error: MONZO_KEYRING_PASSWORD not set" >&2
    return 1
  fi

  echo "$json" | openssl enc -aes-256-cbc \
    -salt -pbkdf2 -iter 100000 \
    -pass env:MONZO_KEYRING_PASSWORD \
    -out "$CREDENTIALS_FILE" 2>/dev/null
}

# Decrypt credentials from file
monzo_decrypt_credentials() {
  if [[ ! -f "$CREDENTIALS_FILE" ]]; then
    echo "Error: Credentials file not found at $CREDENTIALS_FILE" >&2
    echo "Run 'scripts/setup' to configure Monzo authentication" >&2
    return 1
  fi

  if [[ -z "${MONZO_KEYRING_PASSWORD:-}" ]]; then
    echo "Error: MONZO_KEYRING_PASSWORD not set" >&2
    return 1
  fi

  openssl enc -aes-256-cbc -d \
    -salt -pbkdf2 -iter 100000 \
    -pass env:MONZO_KEYRING_PASSWORD \
    -in "$CREDENTIALS_FILE" 2>/dev/null || {
      echo "Error: Failed to decrypt credentials (wrong password?)" >&2
      return 1
    }
}

# Load credentials into memory
monzo_load_credentials() {
  CREDENTIALS=$(monzo_decrypt_credentials) || return 1

  CLIENT_ID=$(jq -r '.client_id // empty' <<< "$CREDENTIALS")
  CLIENT_SECRET=$(jq -r '.client_secret // empty' <<< "$CREDENTIALS")
  ACCESS_TOKEN=$(jq -r '.access_token // empty' <<< "$CREDENTIALS")
  REFRESH_TOKEN=$(jq -r '.refresh_token // empty' <<< "$CREDENTIALS")
  TOKEN_EXPIRY=$(jq -r '.token_expiry // 0' <<< "$CREDENTIALS")
  ACCOUNT_ID=$(jq -r '.account_id // empty' <<< "$CREDENTIALS")

  if [[ -z "$ACCESS_TOKEN" ]]; then
    echo "Error: No access token in credentials" >&2
    return 1
  fi
}

# Save updated credentials to disk
monzo_save_credentials() {
  local json
  json=$(jq -n \
    --arg client_id "$CLIENT_ID" \
    --arg client_secret "$CLIENT_SECRET" \
    --arg access_token "$ACCESS_TOKEN" \
    --arg refresh_token "$REFRESH_TOKEN" \
    --arg token_expiry "$TOKEN_EXPIRY" \
    --arg account_id "$ACCOUNT_ID" \
    '{
      client_id: $client_id,
      client_secret: $client_secret,
      access_token: $access_token,
      refresh_token: $refresh_token,
      token_expiry: ($token_expiry | tonumber),
      account_id: $account_id
    }')

  monzo_encrypt_credentials "$json"
}

# ============================================================================
# Token Management
# ============================================================================

# Check if token needs refresh (< 10 minutes remaining)
monzo_check_expiry() {
  local now
  now=$(date +%s)

  if (( TOKEN_EXPIRY - now < 600 )); then
    monzo_refresh_token
  fi
}

# Refresh access token using refresh token
monzo_refresh_token() {
  if [[ -z "$REFRESH_TOKEN" ]]; then
    echo "Error: No refresh token available" >&2
    return 1
  fi

  local response
  response=$(curl -s -X POST "$MONZO_API_BASE/oauth2/token" \
    --data-urlencode "grant_type=refresh_token" \
    --data-urlencode "client_id=$CLIENT_ID" \
    --data-urlencode "client_secret=$CLIENT_SECRET" \
    --data-urlencode "refresh_token=$REFRESH_TOKEN")

  local error
  error=$(jq -r '.error // empty' <<< "$response")

  if [[ -n "$error" ]]; then
    echo "Error refreshing token: $error" >&2
    echo "Response: $response" >&2
    return 1
  fi

  ACCESS_TOKEN=$(jq -r '.access_token' <<< "$response")
  REFRESH_TOKEN=$(jq -r '.refresh_token // empty' <<< "$response")

  # If no new refresh token provided, keep the old one
  if [[ -z "$REFRESH_TOKEN" || "$REFRESH_TOKEN" == "null" ]]; then
    REFRESH_TOKEN=$(jq -r '.refresh_token' <<< "$CREDENTIALS")
  fi

  # Token expires in 6 hours, calculate expiry timestamp
  local expires_in
  expires_in=$(jq -r '.expires_in // 21600' <<< "$response")
  TOKEN_EXPIRY=$(($(date +%s) + expires_in))

  # Save updated credentials
  monzo_save_credentials

  # Update in-memory credentials
  CREDENTIALS=$(jq \
    --arg access_token "$ACCESS_TOKEN" \
    --arg refresh_token "$REFRESH_TOKEN" \
    --arg token_expiry "$TOKEN_EXPIRY" \
    '.access_token = $access_token | .refresh_token = $refresh_token | .token_expiry = ($token_expiry | tonumber)' \
    <<< "$CREDENTIALS")
}

# ============================================================================
# API Calls
# ============================================================================

# Make authenticated API call
# Usage: monzo_api_call GET /path [--data "key=value"]
monzo_api_call() {
  local method="$1"
  local path="$2"
  shift 2

  # Check token expiry before making call
  monzo_check_expiry

  local url="$MONZO_API_BASE$path"
  local response
  local http_code

  # Make the API call
  if [[ "$method" == "GET" ]]; then
    response=$(curl -s -w "\n%{http_code}" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      "$url" "$@")
  else
    response=$(curl -s -w "\n%{http_code}" -X "$method" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      "$url" "$@")
  fi

  # Split response and HTTP code
  http_code=$(tail -n1 <<< "$response")
  response=$(sed '$ d' <<< "$response")

  # Handle 401 Unauthorized - token expired
  if [[ "$http_code" == "401" ]]; then
    echo "Token expired, refreshing..." >&2
    monzo_refresh_token || return 1

    # Retry the request with new token
    if [[ "$method" == "GET" ]]; then
      response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        "$url" "$@")
    else
      response=$(curl -s -w "\n%{http_code}" -X "$method" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        "$url" "$@")
    fi

    http_code=$(tail -n1 <<< "$response")
    response=$(sed '$ d' <<< "$response")
  fi

  # Check for errors
  if [[ "$http_code" != "200" && "$http_code" != "201" ]]; then
    local error_msg
    error_msg=$(jq -r '.message // .error // "Unknown error"' <<< "$response" 2>/dev/null || echo "HTTP $http_code")
    echo "Error: $error_msg (HTTP $http_code)" >&2

    # Only show full response if DEBUG mode is enabled
    if [[ "${DEBUG:-0}" == "1" ]]; then
      echo "Debug response: $(monzo_sanitize_error "$response")" >&2
    fi
    return 1
  fi

  echo "$response"
}

# ============================================================================
# Helper Functions
# ============================================================================

# Sanitize error response to prevent information disclosure
monzo_sanitize_error() {
  local response="$1"
  # Redact sensitive IDs from error output
  echo "$response" | sed 's/acc_[a-zA-Z0-9_]*/acc_REDACTED/g' \
    | sed 's/user_[a-zA-Z0-9_]*/user_REDACTED/g' \
    | sed 's/tx_[a-zA-Z0-9_]*/tx_REDACTED/g' \
    | sed 's/pot_[a-zA-Z0-9_]*/pot_REDACTED/g'
}

# URL encode a string for safe use in URLs and form data
monzo_urlencode() {
  local string="$1"
  jq -nr --arg str "$string" '$str | @uri'
}

# Validate Monzo ID formats
monzo_validate_account_id() {
  local id="$1"
  if [[ ! "$id" =~ ^acc_[a-zA-Z0-9_]+$ ]]; then
    echo "Error: Invalid account ID format: $id (expected acc_...)" >&2
    return 1
  fi
}

monzo_validate_pot_id() {
  local id="$1"
  if [[ ! "$id" =~ ^pot_[a-zA-Z0-9_]+$ ]]; then
    echo "Error: Invalid pot ID format: $id (expected pot_...)" >&2
    return 1
  fi
}

monzo_validate_transaction_id() {
  local id="$1"
  if [[ ! "$id" =~ ^tx_[a-zA-Z0-9_]+$ ]]; then
    echo "Error: Invalid transaction ID format: $id (expected tx_...)" >&2
    return 1
  fi
}

# Format pence to pounds with currency symbol
monzo_format_money() {
  local pence="$1"
  local currency="${2:-GBP}"

  if [[ "$pence" == "null" || -z "$pence" ]]; then
    echo "-"
    return
  fi

  if [[ "$currency" == "GBP" ]]; then
    printf "£%.2f" "$(echo "scale=2; $pence / 100" | bc)"
  else
    printf "%.2f %s" "$(echo "scale=2; $pence / 100" | bc)" "$currency"
  fi
}

# Parse date to ISO 8601 format
# Supports: "7d" (7 days ago), "YYYY-MM-DD", ISO 8601
monzo_parse_date() {
  local input="$1"

  if [[ -z "$input" ]]; then
    echo ""
    return
  fi

  if [[ "$input" =~ ^[0-9]+d$ ]]; then
    # Relative days (e.g., "7d" = 7 days ago)
    local days="${input%d}"
    date -u -d "$days days ago" +%Y-%m-%dT%H:%M:%SZ
  elif [[ "$input" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    # YYYY-MM-DD to RFC3339
    date -u -d "$input" +%Y-%m-%dT%H:%M:%SZ
  else
    # Assume already RFC3339 or valid date format
    echo "$input"
  fi
}

# Get account ID from argument or use default
monzo_ensure_account_id() {
  local arg_account_id="$1"

  if [[ -n "$arg_account_id" ]]; then
    echo "$arg_account_id"
  elif [[ -n "$ACCOUNT_ID" ]]; then
    echo "$ACCOUNT_ID"
  else
    echo "Error: No account ID specified. Set default in credentials or pass as argument" >&2
    return 1
  fi
}

# Generate unique dedupe ID for idempotent operations
monzo_generate_dedupe_id() {
  echo "dedupe_$(openssl rand -hex 16)"
}

# Format date for display (YYYY-MM-DD)
monzo_format_date() {
  local iso_date="$1"
  date -d "$iso_date" +%Y-%m-%d 2>/dev/null || echo "$iso_date"
}

# ============================================================================
# Initialization
# ============================================================================

# Validate environment
if [[ -z "${MONZO_KEYRING_PASSWORD:-}" ]]; then
  echo "Error: MONZO_KEYRING_PASSWORD environment variable not set" >&2
  echo "This password is required to decrypt stored credentials" >&2
  exit 1
fi
