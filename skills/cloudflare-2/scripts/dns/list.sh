#!/bin/bash
# List DNS records for a zone

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

DOMAIN=""
TYPE=""
NAME=""
OUTPUT="table"

while [[ $# -gt 0 ]]; do
    case $1 in
        --type) TYPE="$2"; shift 2 ;;
        --name) NAME="$2"; shift 2 ;;
        --json) OUTPUT="json"; shift ;;
        -h|--help)
            echo "Usage: dns/list.sh <domain> [options]"
            echo ""
            echo "Options:"
            echo "  --type TYPE  Filter by record type (A, CNAME, TXT, etc.)"
            echo "  --name NAME  Filter by record name"
            echo "  --json       Raw JSON output"
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

if [ -z "$DOMAIN" ]; then
    echo "Usage: dns/list.sh <domain>"
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

# Build query
QUERY="per_page=100"
[ -n "$TYPE" ] && QUERY="$QUERY&type=$TYPE"
[ -n "$NAME" ] && QUERY="$QUERY&name=$NAME.$DOMAIN"

RESPONSE=$(cf_get "/zones/$ZONE_ID/dns_records?$QUERY")
check_error "$RESPONSE" || exit 1

if [ "$OUTPUT" = "json" ]; then
    echo "$RESPONSE" | jq '.result'
else
    echo ""
    printf "%-8s | %-35s | %-40s | %s\n" "TYPE" "NAME" "CONTENT" "PROXIED"
    printf "%s\n" "---------|-------------------------------------|------------------------------------------|--------"
    
    echo "$RESPONSE" | jq -r '.result[] | [.type, .name, (.content | .[0:38]), (if .proxied then "✓" else "✗" end)] | @tsv' | \
    while IFS=$'\t' read -r type name content proxied; do
        printf "%-8s | %-35s | %-40s | %s\n" "$type" "$name" "$content" "$proxied"
    done
    
    COUNT=$(echo "$RESPONSE" | jq '.result | length')
    echo ""
    echo "Total: $COUNT record(s)"
fi
