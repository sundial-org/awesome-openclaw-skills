#!/usr/bin/env bash
# Go4Me address lookup script
# Usage: source go4me-lookup.sh && go4me_lookup "username"
# Returns JSON on success, exits 1 on failure

go4me_lookup() {
    local username="${1#@}"  # Strip @ if present
    
    if [[ -z "$username" ]]; then
        echo '{"error":"Username required"}' >&2
        return 1
    fi
    
    local url="https://${username}.go4.me/"
    local response
    local http_code
    
    # Fetch page and capture HTTP code
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | sed '$d')
    
    # Check for 404
    if [[ "$http_code" == "404" ]]; then
        echo '{"error":"User not found on Go4Me"}' >&2
        return 1
    fi
    
    # Check for other errors
    if [[ "$http_code" != "200" ]]; then
        echo "{\"error\":\"HTTP $http_code\"}" >&2
        return 1
    fi
    
    # Extract __NEXT_DATA__ JSON
    local next_data
    next_data=$(echo "$response" | grep -o '<script id="__NEXT_DATA__"[^>]*>[^<]*</script>' | sed 's/<[^>]*>//g')
    
    if [[ -z "$next_data" ]]; then
        echo '{"error":"Failed to parse Go4Me page"}' >&2
        return 1
    fi
    
    # Extract user object from pageProps
    local user_json
    user_json=$(echo "$next_data" | jq -r '.props.pageProps.user // empty' 2>/dev/null)
    
    if [[ -z "$user_json" ]]; then
        echo '{"error":"No user data found"}' >&2
        return 1
    fi
    
    # Return relevant fields
    echo "$user_json" | jq '{
        username: .username,
        fullName: .fullName,
        xchAddress: .xchAddress,
        description: .description,
        avatarUrl: .avatarUrl,
        totalBadgeScore: .totalBadgeScore,
        rankCopiesSold: .rankCopiesSold
    }'
}

# If run directly (not sourced), execute with args
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    go4me_lookup "$@"
fi
