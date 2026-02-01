#!/bin/bash
# Delete Cloudflare tunnel

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

TUNNEL_NAME=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f) FORCE=true; shift ;;
        -h|--help)
            echo "Usage: tunnels/delete.sh <tunnel-name> [options]"
            echo ""
            echo "Options:"
            echo "  --force, -f  Skip confirmation"
            exit 0
            ;;
        *)
            if [ -z "$TUNNEL_NAME" ]; then
                TUNNEL_NAME="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$TUNNEL_NAME" ]; then
    echo "Usage: tunnels/delete.sh <tunnel-name>"
    exit 1
fi

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

# Get tunnel ID from name
TUNNELS=$(cf_get "/accounts/$ACCOUNT_ID/cfd_tunnel?name=$TUNNEL_NAME")
TUNNEL_ID=$(echo "$TUNNELS" | jq -r '.result[0].id // empty')

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Tunnel '$TUNNEL_NAME' not found"
    exit 1
fi

if [ "$FORCE" != "true" ]; then
    echo "Delete tunnel '$TUNNEL_NAME'?"
    echo "  ID: $TUNNEL_ID"
    read -p "Confirm (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

RESPONSE=$(cf_delete "/accounts/$ACCOUNT_ID/cfd_tunnel/$TUNNEL_ID")

if check_error "$RESPONSE"; then
    echo "✅ Tunnel deleted!"
else
    exit 1
fi
