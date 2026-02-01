#!/bin/bash
# Trakt OAuth Token Helper
# Usage: ./get_trakt_token.sh

set -e

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo "Install it with: brew install jq (macOS) or apt-get install jq (Linux)"
    exit 1
fi

# Prompt for credentials if not set
if [ -z "$TRAKT_CLIENT_ID" ]; then
    echo -n "Enter your Trakt Client ID: "
    read TRAKT_CLIENT_ID
fi

if [ -z "$TRAKT_CLIENT_SECRET" ]; then
    echo -n "Enter your Trakt Client Secret: "
    read TRAKT_CLIENT_SECRET
fi

REDIRECT_URI="urn:ietf:wg:oauth:2.0:oob"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Trakt OAuth Token Generator                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Step 1: Open this URL in your browser:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "https://trakt.tv/oauth/authorize?response_type=code&client_id=$TRAKT_CLIENT_ID&redirect_uri=$REDIRECT_URI"
echo ""
echo "Step 2: Authorize the application"
echo "Step 3: Copy the authorization code from the page"
echo ""
echo -n "Step 4: Paste the code here: "
read CODE

if [ -z "$CODE" ]; then
    echo "Error: No code provided"
    exit 1
fi

echo ""
echo "Exchanging authorization code for access token..."
echo ""

RESPONSE=$(curl -s -X POST https://api.trakt.tv/oauth/token \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": \"$CODE\",
    \"client_id\": \"$TRAKT_CLIENT_ID\",
    \"client_secret\": \"$TRAKT_CLIENT_SECRET\",
    \"redirect_uri\": \"$REDIRECT_URI\",
    \"grant_type\": \"authorization_code\"
  }")

# Check if response contains an error
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "Error from Trakt API:"
    echo "$RESPONSE" | jq .
    exit 1
fi

# Extract tokens
ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
REFRESH_TOKEN=$(echo "$RESPONSE" | jq -r '.refresh_token')
EXPIRES_IN=$(echo "$RESPONSE" | jq -r '.expires_in')

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "Error: Failed to get access token"
    echo "Response:"
    echo "$RESPONSE" | jq .
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    SUCCESS!                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Access Token obtained successfully!"
echo "Expires in: $EXPIRES_IN seconds ($(($EXPIRES_IN / 86400)) days)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Add these to ~/.openclaw/openclaw.json:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo '{
  "skills": {
    "entries": {
      "trakt": {
        "enabled": true,
        "env": {
          "TRAKT_CLIENT_ID": "'"$TRAKT_CLIENT_ID"'",
          "TRAKT_CLIENT_SECRET": "'"$TRAKT_CLIENT_SECRET"'",
          "TRAKT_ACCESS_TOKEN": "'"$ACCESS_TOKEN"'",
          "TRAKT_REFRESH_TOKEN": "'"$REFRESH_TOKEN"'"
        }
      }
    }
  }
}'
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Or export as environment variables:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "export TRAKT_CLIENT_ID=\"$TRAKT_CLIENT_ID\""
echo "export TRAKT_CLIENT_SECRET=\"$TRAKT_CLIENT_SECRET\""
echo "export TRAKT_ACCESS_TOKEN=\"$ACCESS_TOKEN\""
echo "export TRAKT_REFRESH_TOKEN=\"$REFRESH_TOKEN\""
echo ""
