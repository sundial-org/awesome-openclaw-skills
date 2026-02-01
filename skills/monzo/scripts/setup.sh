#!/bin/bash
# Monzo OAuth setup - one-time configuration
# Usage: setup [--reset] [--continue] [--non-interactive ...]
#
# Interactive mode (default):
#   setup
#   setup --reset
#
# Non-interactive mode:
#   setup --non-interactive --client-id ID --client-secret SECRET --auth-code CODE
#
# Continue mode (resume after SCA approval):
#   setup --continue

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREDENTIALS_DIR="${CLAWDBOT_CREDENTIALS_DIR:-${HOME}/.clawdbot/credentials}"
CREDENTIALS_FILE="${CREDENTIALS_DIR}/monzo.json"
MONZO_API_BASE="${MONZO_API_BASE:-https://api.monzo.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Mode flags
RESET_MODE=false
CONTINUE_MODE=false
NON_INTERACTIVE=false
ARG_CLIENT_ID=""
ARG_CLIENT_SECRET=""
ARG_AUTH_CODE=""

# ============================================================================
# Helper Functions
# ============================================================================

print_step() {
  echo -e "${BLUE}$1${NC}"
}

print_success() {
  echo -e "${GREEN}✓${NC} $1"
}

print_info() {
  echo -e "${YELLOW}ℹ${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1" >&2
}

print_sca_instructions() {
  echo ""
  echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
  echo -e "${YELLOW}  IMPORTANT: Strong Customer Authentication (SCA) Required${NC}"
  echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
  echo ""
  echo "Monzo requires you to approve API access in your app:"
  echo ""
  echo "  1. Open the Monzo app on your phone"
  echo "  2. Look for a notification about 'API access'"
  echo "  3. Tap to approve the connection"
  echo ""
  echo "If you don't see a notification:"
  echo "  • Go to Account → Settings → Privacy & Security"
  echo "  • Find 'Manage connected apps' and approve from there"
  echo ""
}

# Encrypt and save credentials
save_credentials() {
  local json="$1"

  if [[ -z "${MONZO_KEYRING_PASSWORD:-}" ]]; then
    print_error "MONZO_KEYRING_PASSWORD not set"
    exit 1
  fi

  mkdir -p "$CREDENTIALS_DIR"

  echo "$json" | openssl enc -aes-256-cbc \
    -salt -pbkdf2 -iter 100000 \
    -pass env:MONZO_KEYRING_PASSWORD \
    -out "$CREDENTIALS_FILE" 2>/dev/null

  chmod 600 "$CREDENTIALS_FILE"
}

# Decrypt credentials from file
load_credentials() {
  if [[ ! -f "$CREDENTIALS_FILE" ]]; then
    return 1
  fi

  if [[ -z "${MONZO_KEYRING_PASSWORD:-}" ]]; then
    return 1
  fi

  openssl enc -aes-256-cbc -d \
    -salt -pbkdf2 -iter 100000 \
    -pass env:MONZO_KEYRING_PASSWORD \
    -in "$CREDENTIALS_FILE" 2>/dev/null
}

# Sanitize sensitive data from responses
sanitize_response() {
  local response="$1"
  echo "$response" | sed 's/acc_[a-zA-Z0-9_]*/acc_REDACTED/g' \
    | sed 's/user_[a-zA-Z0-9_]*/user_REDACTED/g' \
    | sed 's/"client_secret":"[^"]*"/"client_secret":"REDACTED"/g' \
    | sed 's/"access_token":"[^"]*"/"access_token":"REDACTED"/g' \
    | sed 's/"refresh_token":"[^"]*"/"refresh_token":"REDACTED"/g'
}

# Check if error is SCA-related
is_sca_error() {
  local response="$1"
  local code
  code=$(jq -r '.code // empty' <<< "$response" 2>/dev/null)
  [[ "$code" == "forbidden.insufficient_permissions" ]]
}

# Fetch and set account ID
fetch_account_id() {
  local access_token="$1"
  
  local accounts_response
  accounts_response=$(curl -s -H "Authorization: Bearer $access_token" \
    "$MONZO_API_BASE/accounts")

  # Check for SCA error
  if is_sca_error "$accounts_response"; then
    print_sca_instructions
    echo "After approving, run: $SCRIPT_DIR/setup --continue"
    echo ""
    return 1
  fi

  # Check for other errors
  local error
  error=$(jq -r '.error // empty' <<< "$accounts_response")
  if [[ -n "$error" ]]; then
    print_error "Error fetching accounts: $error"
    if [[ "${DEBUG:-0}" == "1" ]]; then
      echo "Debug response: $(sanitize_response "$accounts_response")" >&2
    fi
    return 1
  fi

  # Get the first active retail account (prefer personal over joint/business)
  local account_id
  account_id=$(jq -r '(.accounts // [])[] | select(.closed == false and .type == "uk_retail") | .id' <<< "$accounts_response" 2>/dev/null | head -n1)
  
  # If no retail account, try any active account
  if [[ -z "$account_id" ]]; then
    account_id=$(jq -r '(.accounts // [])[] | select(.closed == false) | .id' <<< "$accounts_response" 2>/dev/null | head -n1)
  fi

  if [[ -z "$account_id" || "$account_id" == "null" ]]; then
    print_info "No active account found - you can set one later"
    echo ""
    return 0
  fi

  local account_desc
  account_desc=$(jq -r --arg id "$account_id" '(.accounts // [])[] | select(.id == $id) | .description // .type' <<< "$accounts_response" 2>/dev/null)

  echo "$account_id"
}

usage() {
  echo "Usage: setup [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --reset              Reset existing credentials and reconfigure"
  echo "  --continue           Continue setup after SCA approval (fetch account ID)"
  echo "  --non-interactive    Run without prompts (requires --client-id, --client-secret, --auth-code)"
  echo "  --client-id ID       OAuth client ID (for non-interactive mode)"
  echo "  --client-secret SEC  OAuth client secret (for non-interactive mode)"
  echo "  --auth-code CODE     Authorization code from redirect URL (for non-interactive mode)"
  echo "  --help               Show this help message"
  echo ""
  echo "Examples:"
  echo "  setup                                    # Interactive setup"
  echo "  setup --reset                            # Reset and reconfigure"
  echo "  setup --continue                         # Fetch account ID after SCA approval"
  echo "  setup --non-interactive --client-id oauth2client_xxx --client-secret mnzconf.xxx --auth-code eyJ..."
}

# ============================================================================
# Parse Arguments
# ============================================================================

while [[ $# -gt 0 ]]; do
  case $1 in
    --reset)
      RESET_MODE=true
      shift
      ;;
    --continue)
      CONTINUE_MODE=true
      shift
      ;;
    --non-interactive)
      NON_INTERACTIVE=true
      shift
      ;;
    --client-id)
      ARG_CLIENT_ID="$2"
      shift 2
      ;;
    --client-secret)
      ARG_CLIENT_SECRET="$2"
      shift 2
      ;;
    --auth-code)
      ARG_AUTH_CODE="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

# ============================================================================
# Environment Check
# ============================================================================

if [[ -z "${MONZO_KEYRING_PASSWORD:-}" ]]; then
  print_error "MONZO_KEYRING_PASSWORD environment variable not set"
  echo ""
  echo "This password is used to encrypt your Monzo credentials."
  echo "Add it to your shell environment or Clawdbot config:"
  echo ""
  echo "  export MONZO_KEYRING_PASSWORD='your-secure-password'"
  echo ""
  exit 1
fi

# ============================================================================
# Continue Mode - Just fetch account ID
# ============================================================================

if [[ "$CONTINUE_MODE" == true ]]; then
  echo ""
  print_step "Continuing setup - fetching account information..."
  echo ""

  CREDENTIALS=$(load_credentials) || {
    print_error "No existing credentials found. Run setup without --continue first."
    exit 1
  }

  ACCESS_TOKEN=$(jq -r '.access_token // empty' <<< "$CREDENTIALS")
  if [[ -z "$ACCESS_TOKEN" ]]; then
    print_error "No access token in credentials. Run setup without --continue."
    exit 1
  fi

  ACCOUNT_ID=$(fetch_account_id "$ACCESS_TOKEN") || exit 1

  if [[ -n "$ACCOUNT_ID" ]]; then
    # Update credentials with account ID
    UPDATED=$(echo "$CREDENTIALS" | jq --arg id "$ACCOUNT_ID" '.account_id = $id')
    save_credentials "$UPDATED"
    print_success "Default account set: $ACCOUNT_ID"
  fi

  echo ""
  print_success "Setup complete!"
  echo ""
  echo "Test with:"
  echo "  $SCRIPT_DIR/whoami"
  echo "  $SCRIPT_DIR/balance"
  echo ""
  exit 0
fi

# ============================================================================
# Main Setup Flow
# ============================================================================

echo ""
echo "╔════════════════════════════════════════╗"
echo "║      Monzo OAuth Setup Wizard          ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check for existing credentials
if [[ -f "$CREDENTIALS_FILE" && "$RESET_MODE" != true ]]; then
  if [[ "$NON_INTERACTIVE" == true ]]; then
    print_error "Credentials already exist. Use --reset to reconfigure."
    exit 1
  fi
  echo "Existing credentials found at: $CREDENTIALS_FILE"
  echo ""
  read -p "Reset and reconfigure? (y/N): " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
  fi
  rm -f "$CREDENTIALS_FILE"
fi

if [[ "$RESET_MODE" == true && -f "$CREDENTIALS_FILE" ]]; then
  rm -f "$CREDENTIALS_FILE"
  print_info "Existing credentials removed"
  echo ""
fi

# ============================================================================
# Get OAuth Client Credentials
# ============================================================================

if [[ "$NON_INTERACTIVE" == true ]]; then
  # Non-interactive mode - use arguments
  if [[ -z "$ARG_CLIENT_ID" || -z "$ARG_CLIENT_SECRET" || -z "$ARG_AUTH_CODE" ]]; then
    print_error "Non-interactive mode requires --client-id, --client-secret, and --auth-code"
    usage
    exit 1
  fi
  CLIENT_ID="$ARG_CLIENT_ID"
  CLIENT_SECRET="$ARG_CLIENT_SECRET"
  AUTH_CODE="$ARG_AUTH_CODE"
  print_success "Using provided credentials"
else
  # Interactive mode
  echo "This wizard will guide you through setting up Monzo API access."
  echo ""

  print_step "Step 1: OAuth Client Setup"
  echo ""
  echo "You need to create an OAuth client at: https://developers.monzo.com/"
  echo ""
  echo "Client settings:"
  echo "  • Name: Clawdbot (or your preferred name)"
  echo "  • Confidentiality: Confidential  ← IMPORTANT for refresh tokens"
  echo "  • Redirect URL: http://localhost"
  echo ""
  echo "After creating the client, you'll receive:"
  echo "  • Client ID (starts with 'oauth2client_')"
  echo "  • Client Secret (starts with 'mnzconf.')"
  echo ""

  read -p "Press Enter when you have your OAuth client ready..."
  echo ""

  read -p "Enter Client ID: " CLIENT_ID
  read -p "Enter Client Secret: " CLIENT_SECRET

  if [[ -z "$CLIENT_ID" || -z "$CLIENT_SECRET" ]]; then
    print_error "Client ID and Secret are required"
    exit 1
  fi

  # Validate client ID format
  if [[ ! "$CLIENT_ID" =~ ^oauth2client_ ]]; then
    print_info "Warning: Client ID should start with 'oauth2client_'"
  fi

  echo ""
  print_success "Client credentials received"

  # Step 2: Authorization URL
  print_step "Step 2: Authorization"
  echo ""

  STATE="clawd_$(date +%s)_$RANDOM"
  REDIRECT_URI="http://localhost"

  AUTH_URL="https://auth.monzo.com/?client_id=$CLIENT_ID&redirect_uri=$REDIRECT_URI&response_type=code&state=$STATE"

  echo "Visit this URL in your browser to authorize:"
  echo ""
  echo "  $AUTH_URL"
  echo ""
  echo "After authorizing, you'll be redirected to a page that won't load."
  echo "That's OK! Copy the ENTIRE URL from your browser's address bar."
  echo "(It will look like: http://localhost/?code=...&state=...)"
  echo ""

  read -p "Paste the redirect URL here: " REDIRECT_URL

  if [[ -z "$REDIRECT_URL" ]]; then
    print_error "Redirect URL is required"
    exit 1
  fi

  # Extract authorization code from URL
  AUTH_CODE=$(echo "$REDIRECT_URL" | sed -n 's/.*code=\([^&]*\).*/\1/p')

  if [[ -z "$AUTH_CODE" ]]; then
    print_error "Could not extract authorization code from URL"
    echo "Make sure you pasted the complete redirect URL"
    exit 1
  fi

  # Validate state (security check)
  URL_STATE=$(echo "$REDIRECT_URL" | sed -n 's/.*state=\([^&]*\).*/\1/p')
  if [[ "$URL_STATE" != "$STATE" ]]; then
    print_error "State parameter mismatch - possible CSRF attack"
    echo "Expected: $STATE"
    echo "Received: $URL_STATE"
    echo ""
    echo "This could indicate:"
    echo "  • You're using an authorization URL from a previous attempt"
    echo "  • Someone is trying to intercept your OAuth flow"
    echo ""
    echo "Please start fresh: $SCRIPT_DIR/setup --reset"
    exit 1
  fi

  echo ""
  print_success "Authorization code extracted"
fi

# ============================================================================
# Exchange Code for Tokens
# ============================================================================

print_step "Step 3: Exchanging code for tokens..."
echo ""

REDIRECT_URI="http://localhost"

TOKEN_RESPONSE=$(curl -s -X POST "$MONZO_API_BASE/oauth2/token" \
  --data-urlencode "grant_type=authorization_code" \
  --data-urlencode "client_id=$CLIENT_ID" \
  --data-urlencode "client_secret=$CLIENT_SECRET" \
  --data-urlencode "redirect_uri=$REDIRECT_URI" \
  --data-urlencode "code=$AUTH_CODE")

# Check for errors
ERROR=$(jq -r '.error // empty' <<< "$TOKEN_RESPONSE")
if [[ -n "$ERROR" ]]; then
  ERROR_DESC=$(jq -r '.error_description // empty' <<< "$TOKEN_RESPONSE")
  
  if [[ "$ERROR_DESC" == *"has been used"* ]]; then
    print_error "This authorization code has already been used"
    echo ""
    echo "Each code can only be used once. Please authorize again:"
    echo "  $SCRIPT_DIR/setup --reset"
    exit 1
  fi
  
  print_error "Token exchange failed: $ERROR"
  if [[ -n "$ERROR_DESC" ]]; then
    echo "Description: $ERROR_DESC"
  fi
  exit 1
fi

# Extract tokens
ACCESS_TOKEN=$(jq -r '.access_token' <<< "$TOKEN_RESPONSE")
REFRESH_TOKEN=$(jq -r '.refresh_token // empty' <<< "$TOKEN_RESPONSE")
EXPIRES_IN=$(jq -r '.expires_in // 21600' <<< "$TOKEN_RESPONSE")

if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "null" ]]; then
  print_error "Failed to obtain access token"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

if [[ -z "$REFRESH_TOKEN" || "$REFRESH_TOKEN" == "null" ]]; then
  print_info "Warning: No refresh token received"
  echo "Your OAuth client may not be set to 'Confidential'"
  echo "Tokens will expire and require manual re-authorization"
  REFRESH_TOKEN=""
fi

TOKEN_EXPIRY=$(($(date +%s) + EXPIRES_IN))

print_success "Tokens acquired"

# ============================================================================
# SAVE CREDENTIALS IMMEDIATELY (before fetching accounts)
# ============================================================================

print_step "Step 4: Saving credentials..."
echo ""

CREDENTIALS_JSON=$(jq -n \
  --arg client_id "$CLIENT_ID" \
  --arg client_secret "$CLIENT_SECRET" \
  --arg access_token "$ACCESS_TOKEN" \
  --arg refresh_token "$REFRESH_TOKEN" \
  --arg token_expiry "$TOKEN_EXPIRY" \
  --arg account_id "" \
  '{
    client_id: $client_id,
    client_secret: $client_secret,
    access_token: $access_token,
    refresh_token: $refresh_token,
    token_expiry: ($token_expiry | tonumber),
    account_id: $account_id
  }')

save_credentials "$CREDENTIALS_JSON"
print_success "Credentials saved to: $CREDENTIALS_FILE"

# ============================================================================
# Fetch Account Information (non-fatal if fails)
# ============================================================================

print_step "Step 5: Fetching account information..."
echo ""

ACCOUNT_ID=$(fetch_account_id "$ACCESS_TOKEN")
FETCH_STATUS=$?

if [[ $FETCH_STATUS -eq 0 && -n "$ACCOUNT_ID" ]]; then
  # Update credentials with account ID
  CREDENTIALS_JSON=$(jq --arg id "$ACCOUNT_ID" '.account_id = $id' <<< "$CREDENTIALS_JSON")
  save_credentials "$CREDENTIALS_JSON"
  print_success "Default account: $ACCOUNT_ID"
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "╔════════════════════════════════════════╗"
echo "║          Setup Complete!               ║"
echo "╚════════════════════════════════════════╝"
echo ""
print_success "Monzo API credentials saved"
print_success "Encrypted with MONZO_KEYRING_PASSWORD"

if [[ -n "$ACCOUNT_ID" ]]; then
  print_success "Default account configured"
  echo ""
  echo "Test with:"
  echo "  $SCRIPT_DIR/whoami"
  echo "  $SCRIPT_DIR/balance"
else
  echo ""
  print_info "Account not yet configured (SCA may be pending)"
  echo ""
  echo "After approving in the Monzo app, run:"
  echo "  $SCRIPT_DIR/setup --continue"
fi

if [[ -n "$REFRESH_TOKEN" ]]; then
  echo ""
  print_info "Tokens will automatically refresh when needed"
fi

echo ""
