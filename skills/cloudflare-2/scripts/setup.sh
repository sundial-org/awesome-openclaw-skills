#!/bin/bash
# Cloudflare API Setup - Validate and test connection

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_lib.sh"

TOKEN=$(get_token)

if [ -z "$TOKEN" ]; then
    echo "❌ No API token found!"
    echo ""
    echo "Setup instructions:"
    echo "  1. Get your API token from https://dash.cloudflare.com/profile/api-tokens"
    echo "  2. Save it:"
    echo "     echo 'YOUR_TOKEN' > ~/.cloudflare_token"
    echo "     chmod 600 ~/.cloudflare_token"
    echo ""
    echo "  Or set environment variable:"
    echo "     export CLOUDFLARE_API_TOKEN='YOUR_TOKEN'"
    exit 1
fi

echo "🔑 API token found"
echo "🔗 Testing connection..."

# Verify token
RESPONSE=$(cf_get "/user/tokens/verify")

if echo "$RESPONSE" | jq -e '.success == true' >/dev/null 2>&1; then
    echo "✅ Token valid!"
elif echo "$RESPONSE" | jq -e '.result.id' >/dev/null 2>&1; then
    echo "✅ Token valid!"
else
    # Try listing accounts as fallback verification
    ACCOUNTS=$(cf_get "/accounts")
    if echo "$ACCOUNTS" | jq -e '.success == true' >/dev/null 2>&1; then
        echo "✅ Token valid!"
    else
        echo "❌ Token invalid or expired"
        echo "Get a new token at https://dash.cloudflare.com/profile/api-tokens"
        exit 1
    fi
fi

# Show account info
ACCOUNTS=$(cf_get "/accounts")
ACCOUNT_NAME=$(echo "$ACCOUNTS" | jq -r '.result[0].name // "Unknown"')
echo "📧 Account: $ACCOUNT_NAME"

# Show zones
ZONES=$(cf_get "/zones?per_page=5")
ZONE_COUNT=$(echo "$ZONES" | jq -r '.result_info.total_count // 0')
echo "🌐 Zones: $ZONE_COUNT domain(s)"

if [ "$ZONE_COUNT" -gt 0 ]; then
    echo ""
    echo "Recent domains:"
    echo "$ZONES" | jq -r '.result[].name' | head -5 | while read domain; do
        echo "  - $domain"
    done
fi

echo ""
echo "You're all set! Try:"
echo "  ./scripts/zones/list.sh"
echo "  ./scripts/dns/list.sh yourdomain.com"
