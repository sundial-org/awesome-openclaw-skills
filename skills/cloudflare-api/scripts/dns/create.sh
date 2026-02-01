#!/bin/bash
# Create DNS record

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

DOMAIN=""
TYPE=""
NAME=""
CONTENT=""
PROXIED=false
TTL=1

while [[ $# -gt 0 ]]; do
    case $1 in
        --type) TYPE="$2"; shift 2 ;;
        --name) NAME="$2"; shift 2 ;;
        --content) CONTENT="$2"; shift 2 ;;
        --proxied) PROXIED=true; shift ;;
        --ttl) TTL="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: dns/create.sh <domain> --type TYPE --name NAME --content CONTENT [options]"
            echo ""
            echo "Required:"
            echo "  --type TYPE       Record type (A, AAAA, CNAME, TXT, MX, etc.)"
            echo "  --name NAME       Record name (subdomain, or @ for root)"
            echo "  --content CONTENT Record value"
            echo ""
            echo "Options:"
            echo "  --proxied         Enable Cloudflare proxy (orange cloud)"
            echo "  --ttl SECONDS     TTL (default: 1 = auto)"
            exit 0
            ;;
        *)
            if [ -z "$DOMAIN" ]; then
                DOMAIN="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$DOMAIN" ] || [ -z "$TYPE" ] || [ -z "$NAME" ] || [ -z "$CONTENT" ]; then
    echo "Usage: dns/create.sh <domain> --type TYPE --name NAME --content CONTENT"
    echo "Run with -h for help"
    exit 1
fi

TOKEN=$(get_token)
if [ -z "$TOKEN" ]; then
    echo "❌ No API token. Run ./scripts/setup.sh first." >&2
    exit 1
fi

ZONE_ID=$(get_zone_id "$DOMAIN")
if [ -z "$ZONE_ID" ]; then
    echo "❌ Zone '$DOMAIN' not found"
    exit 1
fi

# Build full name
if [ "$NAME" = "@" ]; then
    FULL_NAME="$DOMAIN"
else
    FULL_NAME="$NAME.$DOMAIN"
fi

echo "Creating $TYPE record: $FULL_NAME → $CONTENT"

DATA=$(jq -n \
    --arg type "$TYPE" \
    --arg name "$FULL_NAME" \
    --arg content "$CONTENT" \
    --argjson proxied "$PROXIED" \
    --argjson ttl "$TTL" \
    '{type: $type, name: $name, content: $content, proxied: $proxied, ttl: $ttl}')

RESPONSE=$(cf_post "/zones/$ZONE_ID/dns_records" "$DATA")

if check_error "$RESPONSE"; then
    echo "✅ Record created!"
    RECORD_ID=$(echo "$RESPONSE" | jq -r '.result.id')
    echo "   ID: $RECORD_ID"
else
    exit 1
fi
