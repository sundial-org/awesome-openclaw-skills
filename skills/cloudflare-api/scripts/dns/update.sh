#!/bin/bash
# Update DNS record

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

DOMAIN=""
TYPE=""
NAME=""
CONTENT=""
PROXIED=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --type) TYPE="$2"; shift 2 ;;
        --name) NAME="$2"; shift 2 ;;
        --content) CONTENT="$2"; shift 2 ;;
        --proxied) PROXIED=true; shift ;;
        --no-proxy) PROXIED=false; shift ;;
        -h|--help)
            echo "Usage: dns/update.sh <domain> --name NAME --type TYPE [options]"
            echo ""
            echo "Required:"
            echo "  --name NAME       Record name to update"
            echo "  --type TYPE       Record type"
            echo ""
            echo "Options:"
            echo "  --content VALUE   New content value"
            echo "  --proxied         Enable proxy"
            echo "  --no-proxy        Disable proxy"
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

if [ -z "$DOMAIN" ] || [ -z "$NAME" ] || [ -z "$TYPE" ]; then
    echo "Usage: dns/update.sh <domain> --name NAME --type TYPE --content VALUE"
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

# Find the record
FULL_NAME="$NAME.$DOMAIN"
[ "$NAME" = "@" ] && FULL_NAME="$DOMAIN"

RECORDS=$(cf_get "/zones/$ZONE_ID/dns_records?name=$FULL_NAME&type=$TYPE")
RECORD_ID=$(echo "$RECORDS" | jq -r '.result[0].id // empty')

if [ -z "$RECORD_ID" ]; then
    echo "❌ Record not found: $FULL_NAME ($TYPE)"
    exit 1
fi

# Get current values
CURRENT=$(echo "$RECORDS" | jq '.result[0]')
CURRENT_CONTENT=$(echo "$CURRENT" | jq -r '.content')
CURRENT_PROXIED=$(echo "$CURRENT" | jq -r '.proxied')

# Use new values or keep current
[ -z "$CONTENT" ] && CONTENT="$CURRENT_CONTENT"
[ -z "$PROXIED" ] && PROXIED="$CURRENT_PROXIED"

echo "Updating $TYPE record: $FULL_NAME"

DATA=$(jq -n \
    --arg type "$TYPE" \
    --arg name "$FULL_NAME" \
    --arg content "$CONTENT" \
    --argjson proxied "$PROXIED" \
    '{type: $type, name: $name, content: $content, proxied: $proxied, ttl: 1}')

RESPONSE=$(cf_put "/zones/$ZONE_ID/dns_records/$RECORD_ID" "$DATA")

if check_error "$RESPONSE"; then
    echo "✅ Record updated!"
else
    exit 1
fi
