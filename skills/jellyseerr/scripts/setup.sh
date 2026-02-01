#!/bin/bash
# Setup Jellyseerr credentials

CONFIG_DIR="$HOME/.config/jellyseerr"
CONFIG_FILE="$CONFIG_DIR/config.json"

mkdir -p "$CONFIG_DIR"

echo "=== Jellyseerr Setup ==="
echo ""

read -p "Enter your Jellyseerr server URL (e.g., https://jellyseerr.domain.com): " SERVER_URL
read -p "Enter your API key: " API_KEY

# Test connection
echo ""
echo "Testing connection..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "X-Api-Key: $API_KEY" "$SERVER_URL/api/v1/status" 2>/dev/null)

if [ "$STATUS" = "200" ]; then
    echo "✓ Connection successful!"
else
    echo "✗ Connection failed (HTTP $STATUS)"
    echo "Please check your URL and API key"
    exit 1
fi

# Save configuration
cat > "$CONFIG_FILE" << EOF
{
  "server_url": "$SERVER_URL",
  "api_key": "$API_KEY",
  "auto_approve": true
}
EOF

chmod 600 "$CONFIG_FILE"

echo ""
echo "✓ Configuration saved to $CONFIG_FILE"
echo ""
echo "You can now use:"
echo "  ./scripts/search.py \"Movie or TV Show\""
echo "  ./scripts/request_movie.py \"Movie Name\""
echo "  ./scripts/request_tv.py \"TV Show Name\""
