#!/bin/bash
# Configure tunnel ingress

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../_lib.sh"

TUNNEL_NAME=""
HOSTNAME=""
SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --hostname) HOSTNAME="$2"; shift 2 ;;
        --service) SERVICE="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: tunnels/configure.sh <tunnel-name> --hostname HOST --service URL"
            echo ""
            echo "Required:"
            echo "  --hostname HOST  Public hostname (e.g., app.example.com)"
            echo "  --service URL    Local service URL (e.g., http://localhost:3000)"
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

if [ -z "$TUNNEL_NAME" ] || [ -z "$HOSTNAME" ] || [ -z "$SERVICE" ]; then
    echo "Usage: tunnels/configure.sh <tunnel-name> --hostname HOST --service URL"
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

echo "Configuring tunnel: $TUNNEL_NAME ($TUNNEL_ID)"
echo "  Hostname: $HOSTNAME"
echo "  Service: $SERVICE"

DATA=$(jq -n \
    --arg hostname "$HOSTNAME" \
    --arg service "$SERVICE" \
    '{config: {ingress: [{hostname: $hostname, service: $service}, {service: "http_status:404"}]}}')

RESPONSE=$(cf_put "/accounts/$ACCOUNT_ID/cfd_tunnel/$TUNNEL_ID/configurations" "$DATA")

if check_error "$RESPONSE"; then
    echo "✅ Tunnel configured!"
    echo ""
    echo "Don't forget to add DNS record:"
    echo "  Type: CNAME"
    echo "  Name: $(echo $HOSTNAME | cut -d. -f1)"
    echo "  Content: ${TUNNEL_ID}.cfargotunnel.com"
    echo "  Proxied: ON"
else
    exit 1
fi
