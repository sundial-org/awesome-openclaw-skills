#!/bin/bash
# Create Cloudflare tunnel

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

TUNNEL_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Usage: tunnels/create.sh <tunnel-name>"
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
    echo "Usage: tunnels/create.sh <tunnel-name>"
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

echo "Creating tunnel: $TUNNEL_NAME"

# Generate tunnel secret
TUNNEL_SECRET=$(openssl rand -base64 32)

DATA=$(jq -n \
    --arg name "$TUNNEL_NAME" \
    --arg secret "$TUNNEL_SECRET" \
    '{name: $name, tunnel_secret: $secret}')

RESPONSE=$(cf_post "/accounts/$ACCOUNT_ID/cfd_tunnel" "$DATA")

if check_error "$RESPONSE"; then
    TUNNEL_ID=$(echo "$RESPONSE" | jq -r '.result.id')
    TUNNEL_TOKEN=$(echo "$RESPONSE" | jq -r '.result.token')
    
    echo "✅ Tunnel created!"
    echo ""
    echo "Tunnel ID: $TUNNEL_ID"
    echo "Tunnel Name: $TUNNEL_NAME"
    echo ""
    echo "Run token (save this!):"
    echo "$TUNNEL_TOKEN"
    echo ""
    echo "Next steps:"
    echo "  1. Configure ingress: ./scripts/tunnels/configure.sh $TUNNEL_NAME --hostname app.example.com --service http://localhost:3000"
    echo "  2. Add DNS record pointing to: ${TUNNEL_ID}.cfargotunnel.com"
    echo "  3. Run tunnel: cloudflared tunnel run --token <token>"
else
    exit 1
fi
