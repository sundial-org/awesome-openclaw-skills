#!/bin/bash
# List Cloudflare zones (domains)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

OUTPUT="table"

while [[ $# -gt 0 ]]; do
    case $1 in
        --json) OUTPUT="json"; shift ;;
        --quiet) OUTPUT="quiet"; shift ;;
        -h|--help)
            echo "Usage: zones/list.sh [options]"
            echo ""
            echo "Options:"
            echo "  --json   Raw JSON output"
            echo "  --quiet  Zone IDs only"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

TOKEN=$(get_token)
if [ -z "$TOKEN" ]; then
    echo "❌ No API token. Run ./scripts/setup.sh first." >&2
    exit 1
fi

RESPONSE=$(cf_get "/zones?per_page=50")
check_error "$RESPONSE" || exit 1

case $OUTPUT in
    json)
        echo "$RESPONSE" | jq '.result'
        ;;
    quiet)
        echo "$RESPONSE" | jq -r '.result[].id'
        ;;
    table)
        echo ""
        printf "%-36s | %-30s | %-10s | %s\n" "ZONE ID" "DOMAIN" "STATUS" "PLAN"
        printf "%s\n" "--------------------------------------|--------------------------------|------------|--------"
        
        echo "$RESPONSE" | jq -r '.result[] | [.id, .name, .status, .plan.name] | @tsv' | \
        while IFS=$'\t' read -r id name status plan; do
            printf "%-36s | %-30s | %-10s | %s\n" "$id" "$name" "$status" "$plan"
        done
        
        TOTAL=$(echo "$RESPONSE" | jq -r '.result_info.total_count // 0')
        echo ""
        echo "Total: $TOTAL zone(s)"
        ;;
esac
