#!/bin/bash
# AdGuard Home CLI Manager
# Usage: adguard.sh <command> [args]
# API Reference: https://github.com/AdguardTeam/AdGuardHome/wiki/API

set -e

# Configuration
ADGUARD_URL="${ADGUARD_URL:-http://192.168.68.97:3000}"
ADGUARD_USERNAME="${ADGUARD_USERNAME:-admin}"
API_BASE="${ADGUARD_URL}/control"
COOKIE_FILE="/tmp/adguard_cookie_$$.txt"

# Cleanup on exit
trap "rm -f $COOKIE_FILE" EXIT

# Validate environment
check_env() {
    if [ -z "$ADGUARD_PASSWORD" ]; then
        echo "Error: ADGUARD_PASSWORD not set" >&2
        exit 1
    fi
}

# Get and cache session cookie
get_session() {
    local response
    response=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/login" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${ADGUARD_USERNAME}\",\"password\":\"${ADGUARD_PASSWORD}\"}" \
        -c "$COOKIE_FILE" 2>/dev/null)
    
    local http_code=$(echo "$response" | tail -n1)
    if [ "$http_code" != "200" ]; then
        echo "Error: Failed to authenticate (HTTP $http_code)" >&2
        exit 1
    fi
}

# Make authenticated API call
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local response
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}${endpoint}" \
            -H "Content-Type: application/json" \
            -b "$COOKIE_FILE" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "${API_BASE}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -b "$COOKIE_FILE" 2>/dev/null)
    fi
    
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" != "200" ]; then
        echo "Error: API call failed (HTTP $http_code)" >&2
        [ -n "$body" ] && echo "Response: $body" >&2
        return 1
    fi
    
    echo "$body"
}

# Check if domain is filtered
check_domain() {
    local domain=$1
    get_session
    
    local response
    response=$(api_call GET "/filtering/check_host?host=${domain}")
    
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    # Parse response
    local reason=$(echo "$response" | grep -o '"reason":"[^"]*"' | cut -d'"' -f4)
    local filters=$(echo "$response" | grep -o '"filter_name":"[^"]*"' | cut -d'"' -f4 | head -1)
    
    case "$reason" in
        NotFiltered)
            echo "✓ ${domain} is NOT blocked (allowed)"
            return 0
            ;;
        Filtered)
            echo "✗ ${domain} IS BLOCKED"
            [ -n "$filters" ] && echo "  Blocked by: ${filters}"
            return 1
            ;;
        *)
            echo "? Unknown filter status for ${domain}"
            echo "  Response: ${response}"
            return 2
            ;;
    esac
}

# Add domain to user rules (custom filters)
add_user_rule() {
    local domain=$1
    local action=$2  # block or allow
    get_session
    
    local rule
    if [ "$action" = "block" ]; then
        # Blocking rule
        rule="||${domain}^"
    else
        # Allowlist rule (exception)
        rule="@@||${domain}^"
    fi
    
    # Get current rules
    local config response
    config=$(api_call GET "/filtering/config")
    
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    # Extract current user rules - use proper JSON handling
    local current_rules=$(echo "$config" | grep -o '"user_rules":\[[^]]*\]' || echo '{"user_rules":[]}')
    
    # Simple check: does the rule already exist?
    if echo "$config" | grep -q "\"${rule}\""; then
        echo "✓ Rule already exists: ${rule}"
        return 0
    fi
    
    # Add the new rule via /filtering/set_rules endpoint
    response=$(api_call POST "/filtering/set_rules" "{\"rules\":\"${rule}\"}")
    
    if [ $? -eq 0 ]; then
        echo "✓ Added rule: ${rule}"
        echo "  Domain: ${domain}"
        echo "  Action: ${action}"
    else
        return 1
    fi
}

# Allow domain (whitelist)
allow_domain() {
    local domain=$1
    echo "Adding ${domain} to allowlist..."
    add_user_rule "$domain" "allow"
}

# Block domain (blacklist)
block_domain() {
    local domain=$1
    echo "Adding ${domain} to blocklist..."
    add_user_rule "$domain" "block"
}

# Get status and statistics
get_status() {
    get_session
    
    local stats query_log enabled
    stats=$(api_call GET "/stats")
    query_log=$(api_call GET "/querylog")
    enabled=$(api_call GET "/status" | grep -o '"protection_enabled":[a-z]*' | cut -d: -f2)
    
    local queries=$(echo "$stats" | grep -o '"num_dns_queries":[0-9]*' | cut -d: -f2)
    local blocked=$(echo "$stats" | grep -o '"num_blocked_filtering":[0-9]*' | cut -d: -f2)
    local safe_browsing=$(echo "$stats" | grep -o '"num_blocked_safebrowsing":[0-9]*' | cut -d: -f2)
    local replaced=$(echo "$stats" | grep -o '"num_replaced_safesearch":[0-9]*' | cut -d: -f2)
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "AdGuard Home Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Protection: $([ "$enabled" = "true" ] && echo "✓ ENABLED" || echo "✗ DISABLED")"
    echo ""
    echo "DNS Queries: ${queries:-0}"
    echo "Blocked by rules: ${blocked:-0}"
    echo "Blocked by safe browsing: ${safe_browsing:-0}"
    echo "Safe search replacements: ${replaced:-0}"
    
    if [ -n "$queries" ] && [ "$queries" -gt 0 ]; then
        local rate=$((blocked * 100 / queries))
        echo "Block rate: ${rate}%"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Toggle protection on/off
toggle_protection() {
    get_session
    
    local current_status
    current_status=$(api_call GET "/status")
    
    local current=$(echo "$current_status" | grep -o '"protection_enabled":[a-z]*' | cut -d: -f2)
    local new_state
    
    if [ "$current" = "true" ]; then
        new_state="false"
        echo "Disabling protection..."
    else
        new_state="true"
        echo "Enabling protection..."
    fi
    
    api_call POST "/protection" "{\"enabled\":${new_state}}"
    
    if [ $? -eq 0 ]; then
        echo "✓ Protection is now ${new_state}"
    else
        return 1
    fi
}

# Clear DNS cache
clear_cache() {
    get_session
    echo "Clearing DNS cache..."
    
    api_call POST "/cache_clear" ""
    
    if [ $? -eq 0 ]; then
        echo "✓ Cache cleared"
    else
        return 1
    fi
}

# Main command handler
case "${1:-status}" in
    check)
        check_env
        [ -z "$2" ] && { echo "Usage: adguard.sh check <domain>"; exit 1; }
        check_domain "$2"
        ;;
    allow|whitelist)
        check_env
        [ -z "$2" ] && { echo "Usage: adguard.sh allow <domain>"; exit 1; }
        allow_domain "$2"
        ;;
    block|blacklist)
        check_env
        [ -z "$2" ] && { echo "Usage: adguard.sh block <domain>"; exit 1; }
        block_domain "$2"
        ;;
    status|stats)
        check_env
        get_status
        ;;
    toggle|protection)
        check_env
        toggle_protection
        ;;
    cache-clear)
        check_env
        clear_cache
        ;;
    *)
        cat << 'EOF'
AdGuard Home CLI Manager

USAGE
    adguard.sh <command> [args]

COMMANDS
    check <domain>          Check if domain is blocked
    allow <domain>          Add domain to allowlist (whitelist)
    block <domain>          Add domain to blocklist (blacklist)
    status                  Show statistics and protection status
    toggle                  Enable/disable DNS protection
    cache-clear             Clear DNS cache
    help                    Show this help

ENVIRONMENT VARIABLES
    ADGUARD_URL             AdGuard Home URL (default: http://192.168.68.97:3000)
    ADGUARD_USERNAME        Admin username (default: admin)
    ADGUARD_PASSWORD        Admin password (REQUIRED)

CONFIGURATION
    Set up env vars in ~/.bashrc or ~/.zshrc:
    
    export ADGUARD_URL="http://192.168.1.100:3000"
    export ADGUARD_USERNAME="admin"
    export ADGUARD_PASSWORD="your_password_here"

EXAMPLES
    # Check if a domain is blocked
    adguard.sh check doubleclick.net

    # Add to allowlist
    adguard.sh allow broken-site.com

    # Add to blocklist  
    adguard.sh block malware-site.ru

    # View status
    adguard.sh status

    # Disable protection temporarily
    adguard.sh toggle

API DOCUMENTATION
    https://github.com/AdguardTeam/AdGuardHome/wiki/API

EOF
        exit 0
        ;;
esac
