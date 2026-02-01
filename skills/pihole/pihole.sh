#!/bin/bash

# Pi-hole Skill - CLI script for Pi-hole v6 API control
# Usage: ./pihole.sh [command] [args]

set -o pipefail

# Configuration from env or fallback
PIHOLE_API_URL="${PIHOLE_API_URL:-http://pi-hole.local/admin/api.php}"
PIHOLE_API_TOKEN="${PIHOLE_API_TOKEN:-}"
PIHOLE_INSECURE="${PIHOLE_INSECURE:-false}"

# Get API URL from clawdbot config if env not set
if [[ -z "$PIHOLE_API_TOKEN" ]]; then
    CONFIG_FILE="$HOME/.clawdbot/clawdbot.json"
    if [[ -f "$CONFIG_FILE" ]]; then
        PIHOLE_API_URL=$(jq -r '.skills.entries.pihole.apiUrl // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
        PIHOLE_API_TOKEN=$(jq -r '.skills.entries.pihole.apiToken // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
        PIHOLE_INSECURE=$(jq -r '.skills.entries.pihole.insecure // "false"' "$CONFIG_FILE" 2>/dev/null || echo "false")
    fi
fi

# Validate API URL and token
if [[ -z "$PIHOLE_API_URL" ]] || [[ "$PIHOLE_API_URL" == "empty" ]]; then
    echo "⚠️  Pi-hole API URL not configured"
    echo "Set PIHOLE_API_URL environment variable or configure in clawdbot.json"
    exit 1
fi

if [[ -z "$PIHOLE_API_TOKEN" ]] || [[ "$PIHOLE_API_TOKEN" == "empty" ]]; then
    echo "⚠️  Pi-hole API token not configured"
    echo "Set PIHOLE_API_TOKEN environment variable or configure in clawdbot.json"
    exit 1
fi

# Build curl flags based on insecure setting
CURL_FLAGS="-s --fail --max-time 30"
if [[ "$PIHOLE_INSECURE" == "true" ]]; then
    CURL_FLAGS="$CURL_FLAGS -k"
fi

# Validate numeric input
validate_number() {
    local value="$1"
    local name="$2"
    local min="${3:-0}"

    if ! [[ "$value" =~ ^[0-9]+$ ]]; then
        echo "⚠️  ${name} must be a number"
        exit 1
    fi

    if (( value < min )); then
        echo "⚠️  ${name} must be at least ${min}"
        exit 1
    fi
    return 0
}

# Validate domain input
validate_domain() {
    local domain="$1"

    if [[ -z "$domain" ]]; then
        echo "⚠️  Domain cannot be empty"
        exit 1
    fi

    # Basic domain validation
    if ! [[ "$domain" =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$ ]]; then
        echo "⚠️  Invalid domain format: $domain"
        exit 1
    fi
    return 0
}

# Get session token (Pi-hole v6 API requires this)
get_session() {
    local response
    response=$(curl $CURL_FLAGS \
        -H "Content-Type: application/json" \
        -d "{\"password\":\"$PIHOLE_API_TOKEN\"}" \
        "${PIHOLE_API_URL}/auth" 2>/dev/null)

    if ! echo "$response" | jq -e '.session.sid' >/dev/null 2>&1; then
        echo "⚠️  Failed to authenticate with Pi-hole"
        echo "Response: $response"
        exit 1
    fi

    echo "$response" | jq -r '.session.sid'
}

# Helper: Make authenticated API request
api_request() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="$3"
    local session

    session=$(get_session) || exit 1

    if [[ -n "$data" ]]; then
        curl $CURL_FLAGS \
            -H "sid: $session" \
            -H "Content-Type: application/json" \
            -X "$method" \
            -d "$data" \
            "${PIHOLE_API_URL}${endpoint}" 2>/dev/null
    else
        curl $CURL_FLAGS \
            -H "sid: $session" \
            "${PIHOLE_API_URL}${endpoint}" 2>/dev/null
    fi
}

# Parse command
COMMAND="${1:-help}"

case "$COMMAND" in
    status)
        # Get Pi-hole blocking status
        RESULT=$(api_request "/dns/blocking")
        if ! echo "$RESULT" | jq -e '.blocking' >/dev/null 2>&1; then
            echo "⚠️  Could not determine status"
            echo "Response: $RESULT"
            exit 1
        fi

        BLOCKING=$(echo "$RESULT" | jq -r '.blocking')
        TIMER=$(echo "$RESULT" | jq -r '.timer // "none"')

        if [[ "$BLOCKING" == "true" ]]; then
            echo "🟢 Pi-hole is ENABLED"
            if [[ "$TIMER" != "none" ]] && [[ "$TIMER" != "null" ]]; then
                echo "⏱️  Temporarily disabled for $TIMER seconds"
            fi
        else
            echo "🔴 Pi-hole is DISABLED"
            if [[ "$TIMER" != "none" ]] && [[ "$TIMER" != "null" ]]; then
                echo "⏱️  Will re-enable in $TIMER seconds"
            fi
        fi
        ;;

    on|enable)
        # Enable Pi-hole blocking
        echo "Enabling Pi-hole..."
        RESULT=$(api_request "/dns/blocking" "POST" '{"blocking":true}')
        BLOCKING=$(echo "$RESULT" | jq -r '.blocking')
        if [[ "$BLOCKING" == "true" ]] || [[ "$BLOCKING" == "enabled" ]]; then
            echo "✅ Pi-hole is now ENABLED"
        else
            echo "⚠️  Failed to enable Pi-hole"
            echo "Response: $RESULT"
            exit 1
        fi
        ;;

    off|disable)
        # Disable Pi-hole blocking (indefinitely)
        echo "Disabling Pi-hole..."
        RESULT=$(api_request "/dns/blocking" "POST" '{"blocking":false}')
        BLOCKING=$(echo "$RESULT" | jq -r '.blocking')
        if [[ "$BLOCKING" == "false" ]] || [[ "$BLOCKING" == "disabled" ]]; then
            echo "✅ Pi-hole is now DISABLED"
        else
            echo "⚠️  Failed to disable Pi-hole"
            echo "Response: $RESULT"
            exit 1
        fi
        ;;

    5m|5min)
        # Disable for 5 minutes
        echo "Disabling Pi-hole for 5 minutes..."
        RESULT=$(api_request "/dns/blocking" "POST" '{"blocking":false,"timer":300}')
        BLOCKING=$(echo "$RESULT" | jq -r '.blocking')
        if [[ "$BLOCKING" == "false" ]] || [[ "$BLOCKING" == "disabled" ]]; then
            echo "✅ Pi-hole disabled for 5 minutes"
        else
            echo "⚠️  Failed to disable Pi-hole"
            echo "Response: $RESULT"
            exit 1
        fi
        ;;

    disable)
        # Disable for custom duration (in minutes)
        DURATION="${2:-5}"
        if ! validate_number "$DURATION" "Duration" "1"; then
            exit 1
        fi
        SECONDS=$((DURATION * 60))
        echo "Disabling Pi-hole for ${DURATION} minutes..."
        RESULT=$(api_request "/dns/blocking" "POST" "{\"blocking\":false,\"timer\":$SECONDS}")
        BLOCKING=$(echo "$RESULT" | jq -r '.blocking')
        if [[ "$BLOCKING" == "false" ]] || [[ "$BLOCKING" == "disabled" ]]; then
            echo "✅ Pi-hole disabled for ${DURATION} minutes"
        else
            echo "⚠️  Failed to disable Pi-hole"
            echo "Response: $RESULT"
            exit 1
        fi
        ;;

    blocked|recent-blocked|blocked-last-5m)
        # Show what was blocked recently (last 30 minutes by default)
        DURATION="${2:-1800}"
        if ! validate_number "$DURATION" "Duration" "1"; then
            exit 1
        fi

        echo "🔍 Checking blocked queries in last $((DURATION / 60)) minutes..."
        RESULT=$(api_request "/queries?start=-${DURATION}")

        if ! echo "$RESULT" | jq -e '.queries' >/dev/null 2>&1; then
            echo "⚠️  Could not fetch blocked queries"
            echo "Response: $RESULT"
            exit 1
        fi

        BLOCKED=$(echo "$RESULT" | jq -r '.queries | map(select(.status=="GRAVITY")) | .[] | .domain' | sort | uniq -c | sort -rn | head -20)

        if [[ -z "$BLOCKED" ]]; then
            echo "✅ No domains blocked in last $((DURATION / 60)) minutes"
        else
            echo "🚫 Blocked domains (count in time window):"
            echo "$BLOCKED" | awk '{printf "%4dx %s\n", $1, $2}'
        fi
        ;;

    stats|summary)
        # Show Pi-hole stats
        echo "📊 Pi-hole Stats:"
        RESULT=$(api_request "/stats/summary")

        if ! echo "$RESULT" | jq -e '.queries' >/dev/null 2>&1; then
            echo "⚠️  Could not fetch statistics"
            echo "Response: $RESULT"
            exit 1
        fi

        QUERIES=$(echo "$RESULT" | jq -r '.queries.total // 0')
        BLOCKED=$(echo "$RESULT" | jq -r '.queries.blocked // 0')
        DOMAINS=$(echo "$RESULT" | jq -r '.gravity.domains_being_blocked // 0')
        CLIENTS=$(echo "$RESULT" | jq -r '.clients.active // 0')

        if (( QUERIES > 0 )); then
            PERCENT=$(awk "BEGIN {printf \"%.1f\", ($BLOCKED / $QUERIES) * 100}" <<< "$QUERIES $BLOCKED")
        else
            PERCENT="0.0"
        fi

        echo "Queries: $QUERIES"
        echo "Blocked: $BLOCKED (${PERCENT}%)"
        echo "Blocked domains: $DOMAINS"
        echo "Active clients: $CLIENTS"
        ;;

    top-domains)
        # Show top domains
        LIMIT="${2:-10}"
        if ! validate_number "$LIMIT" "Limit" "1"; then
            exit 1
        fi

        echo "📊 Top $LIMIT domains:"
        RESULT=$(api_request "/stats/query_types?start=-86400")

        if ! echo "$RESULT" | jq -e '.top_domains' >/dev/null 2>&1; then
            echo "⚠️  Could not fetch top domains"
            echo "Response: $RESULT"
            exit 1
        fi

        echo "$RESULT" | jq -r ".top_domains[0:$LIMIT] | .[] | \"\(.count) \(.domain)\""
        ;;

    whitelist|add-whitelist)
        # Add domain to whitelist (via DNSMASQ config in v6)
        DOMAIN="${2}"
        if ! validate_domain "$DOMAIN"; then
            exit 1
        fi

        echo "⚠️  Whitelist functionality requires DNSMASQ config in Pi-hole v6"
        echo "Domain: $DOMAIN"
        echo "This feature is not implemented via API yet"
        exit 1
        ;;

    help|--help|-h)
        cat << EOF
Pi-hole Skill - Control Pi-hole DNS blocker (v6 API)

Commands:
  status                    Show if Pi-hole is enabled/disabled
  on / enable               Enable ad blocking
  off / disable             Disable ad blocking
  5m / 5min              Disable for 5 minutes
  disable <minutes>         Disable for custom duration
  blocked [seconds]          Show blocked domains (default: 30 min)
  stats / summary           Show Pi-hole statistics
  top-domains [limit]        Show top domains (default: 10)

Examples:
  ./pihole.sh status
  ./pihole.sh disable 5
  ./pihole.sh blocked 600  (show blocked in last 10 min)
  ./pihole.sh stats

Configuration:
  Set PIHOLE_API_URL and PIHOLE_API_TOKEN in clawdbot.json skills.entries.pihole
  Set insecure: true to bypass SSL cert validation

EOF
        ;;

    *)
        echo "Unknown command: $COMMAND"
        echo "Run './pihole.sh help' for usage"
        exit 1
        ;;
esac
