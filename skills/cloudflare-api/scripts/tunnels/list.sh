#!/bin/bash
# List Cloudflare tunnels

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

OUTPUT="table"
NAME_FILTER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --json) OUTPUT="json"; shift ;;
        --quiet) OUTPUT="quiet"; shift ;;
        --name) NAME_FILTER="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: tunnels/list.sh [options]"
            echo ""
            echo "Options:"
            echo "  --name NAME  Filter by tunnel name"
            echo "  --json       Raw JSON output"
            echo "  --quiet      Tunnel IDs only"
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

ACCOUNT_ID=$(get_account_id)
if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Could not get account ID"
    exit 1
fi

QUERY=""
[ -n "$NAME_FILTER" ] && QUERY="?name=$NAME_FILTER"

RESPONSE=$(cf_get "/accounts/$ACCOUNT_ID/cfd_tunnel$QUERY")
check_error "$RESPONSE" || exit 1

case $OUTPUT in
    json)
        echo "$RESPONSE" | jq '.result'
        ;;
    quiet)
        if [ -n "$NAME_FILTER" ]; then
            echo "$RESPONSE" | jq -r '.result[0].id // empty'
        else
            echo "$RESPONSE" | jq -r '.result[].id'
        fi
        ;;
    table)
        echo ""
        printf "%-36s | %-25s | %-10s | %s\n" "TUNNEL ID" "NAME" "STATUS" "CREATED"
        printf "%s\n" "--------------------------------------|---------------------------|------------|------------"
        
        echo "$RESPONSE" | jq -r '.result[] | [.id, .name, .status, (.created_at | split("T")[0])] | @tsv' | \
        while IFS=$'\t' read -r id name status created; do
            printf "%-36s | %-25s | %-10s | %s\n" "$id" "$name" "$status" "$created"
        done
        
        COUNT=$(echo "$RESPONSE" | jq '.result | length')
        echo ""
        echo "Total: $COUNT tunnel(s)"
        ;;
esac
