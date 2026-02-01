#!/bin/bash
# Get Cloudflare zone details

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

DOMAIN=""
OUTPUT="table"

while [[ $# -gt 0 ]]; do
    case $1 in
        --json) OUTPUT="json"; shift ;;
        -h|--help)
            echo "Usage: zones/get.sh <domain> [options]"
            echo ""
            echo "Options:"
            echo "  --json  Raw JSON output"
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
    echo "Usage: zones/get.sh <domain>"
    exit 1
fi

TOKEN=$(get_token)
if [ -z "$TOKEN" ]; then
    echo "❌ No API token. Run ./scripts/setup.sh first." >&2
    exit 1
fi

RESPONSE=$(cf_get "/zones?name=$DOMAIN")
check_error "$RESPONSE" || exit 1

ZONE=$(echo "$RESPONSE" | jq '.result[0]')

if [ "$ZONE" = "null" ]; then
    echo "❌ Zone '$DOMAIN' not found"
    exit 1
fi

if [ "$OUTPUT" = "json" ]; then
    echo "$ZONE" | jq '.'
else
    echo ""
    echo "Zone: $(echo "$ZONE" | jq -r '.name')"
    echo "ID: $(echo "$ZONE" | jq -r '.id')"
    echo "Status: $(echo "$ZONE" | jq -r '.status')"
    echo "Plan: $(echo "$ZONE" | jq -r '.plan.name')"
    echo "Nameservers:"
    echo "$ZONE" | jq -r '.name_servers[]' | while read ns; do
        echo "  - $ns"
    done
fi
