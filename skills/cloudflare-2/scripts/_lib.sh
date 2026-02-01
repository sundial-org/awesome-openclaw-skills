#!/bin/bash
# Cloudflare API helper functions

CF_API="https://api.cloudflare.com/client/v4"

# Get API token
get_token() {
    if [ -n "$CLOUDFLARE_API_TOKEN" ]; then
        echo "$CLOUDFLARE_API_TOKEN"
    elif [ -f ~/.cloudflare_token ]; then
        cat ~/.cloudflare_token | tr -d '\n'
    else
        echo ""
    fi
}

# API GET request
cf_get() {
    local endpoint="$1"
    local token=$(get_token)
    curl -s -H "Authorization: Bearer $token" "${CF_API}${endpoint}"
}

# API POST request
cf_post() {
    local endpoint="$1"
    local data="$2"
    local token=$(get_token)
    curl -s -X POST \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$data" \
        "${CF_API}${endpoint}"
}

# API PUT request
cf_put() {
    local endpoint="$1"
    local data="$2"
    local token=$(get_token)
    curl -s -X PUT \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$data" \
        "${CF_API}${endpoint}"
}

# API DELETE request
cf_delete() {
    local endpoint="$1"
    local token=$(get_token)
    curl -s -X DELETE \
        -H "Authorization: Bearer $token" \
        "${CF_API}${endpoint}"
}

# Get zone ID from domain name
get_zone_id() {
    local domain="$1"
    local response=$(cf_get "/zones?name=$domain")
    echo "$response" | jq -r '.result[0].id // empty'
}

# Get account ID
get_account_id() {
    local response=$(cf_get "/accounts?per_page=1")
    echo "$response" | jq -r '.result[0].id // empty'
}

# Check for API errors
check_error() {
    local response="$1"
    if echo "$response" | jq -e '.success == false' >/dev/null 2>&1; then
        local error=$(echo "$response" | jq -r '.errors[0].message // "Unknown error"')
        local code=$(echo "$response" | jq -r '.errors[0].code // ""')
        echo "❌ Error: $error" >&2
        [ -n "$code" ] && echo "   Code: $code" >&2
        return 1
    fi
    return 0
}
