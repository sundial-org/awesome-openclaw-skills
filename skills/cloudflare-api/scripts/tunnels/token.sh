#!/bin/bash
# Get tunnel run token

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

TUNNEL_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Usage: tunnels/token.sh <tunnel-name>"
            echo ""
            echo "Returns the token needed to run the tunnel with:"
            echo "  cloudflared tunnel run --token <token>"
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
    echo "Usage: tunnels/token.sh <tunnel-name>" >&2
    exit 1
fi

TOKEN=$(get_token)
if [ -z "$TOKEN" ]; then
    echo "❌ No API token. Run ./scripts/setup.sh first." >&2
    exit 1
fi

ACCOUNT_ID=$(get_account_id)
if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Could not get account ID" >&2
    exit 1
fi

# Get tunnel ID from name
TUNNELS=$(cf_get "/accounts/$ACCOUNT_ID/cfd_tunnel?name=$TUNNEL_NAME")
TUNNEL_ID=$(echo "$TUNNELS" | jq -r '.result[0].id // empty')
TUNNEL_TOKEN=$(echo "$TUNNELS" | jq -r '.result[0].token // empty')

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Tunnel '$TUNNEL_NAME' not found" >&2
    exit 1
fi

if [ -n "$TUNNEL_TOKEN" ]; then
    echo "$TUNNEL_TOKEN"
else
    # Token might be in credentials_file
    CREDS=$(echo "$TUNNELS" | jq -r '.result[0].credentials_file // empty')
    if [ -n "$CREDS" ] && [ "$CREDS" != "null" ]; then
        # Build token from credentials
        echo "$TUNNELS" | jq -r '.result[0].token // .result[0].id'
    else
        echo "❌ Token not available. You may need to recreate the tunnel." >&2
        exit 1
    fi
fi
