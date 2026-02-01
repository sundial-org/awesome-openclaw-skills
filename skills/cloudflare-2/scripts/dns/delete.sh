#!/bin/bash
# Delete DNS record

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

DOMAIN=""
TYPE=""
NAME=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --type) TYPE="$2"; shift 2 ;;
        --name) NAME="$2"; shift 2 ;;
        --force|-f) FORCE=true; shift ;;
        -h|--help)
            echo "Usage: dns/delete.sh <domain> --name NAME --type TYPE [options]"
            echo ""
            echo "Required:"
            echo "  --name NAME  Record name to delete"
            echo "  --type TYPE  Record type"
            echo ""
            echo "Options:"
            echo "  --force, -f  Skip confirmation"
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
    echo "Usage: dns/delete.sh <domain> --name NAME --type TYPE"
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
CONTENT=$(echo "$RECORDS" | jq -r '.result[0].content // empty')

if [ -z "$RECORD_ID" ]; then
    echo "❌ Record not found: $FULL_NAME ($TYPE)"
    exit 1
fi

if [ "$FORCE" != "true" ]; then
    echo "Delete $TYPE record?"
    echo "  Name: $FULL_NAME"
    echo "  Content: $CONTENT"
    read -p "Confirm (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

RESPONSE=$(cf_delete "/zones/$ZONE_ID/dns_records/$RECORD_ID")

if check_error "$RESPONSE"; then
    echo "✅ Record deleted!"
else
    exit 1
fi
