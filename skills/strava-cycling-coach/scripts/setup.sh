#!/bin/bash
# Setup Strava API OAuth

CONFIG_DIR="$HOME/.config/strava"
CONFIG_FILE="$CONFIG_DIR/config.json"

mkdir -p "$CONFIG_DIR"

echo "=== Strava API Setup ==="
echo ""
echo "First, create a Strava API application:"
echo "Visit: https://www.strava.com/settings/api"
echo ""
echo "Application settings:"
echo "  - Name: Clawdbot"
echo "  - Category: Data Importer"  
echo "  - Website: http://localhost"
echo "  - Authorization Callback Domain: localhost"
echo ""

read -p "Enter your Client ID: " CLIENT_ID
read -p "Enter your Client Secret: " CLIENT_SECRET

# Save initial config
cat > "$CONFIG_FILE" << EOF
{
  "client_id": "$CLIENT_ID",
  "client_secret": "$CLIENT_SECRET",
  "redirect_uri": "http://localhost:8080/callback"
}
EOF

chmod 600 "$CONFIG_FILE"

# Generate OAuth URL
OAUTH_URL="https://www.strava.com/oauth/authorize?client_id=${CLIENT_ID}&redirect_uri=http://localhost:8080/callback&response_type=code&scope=activity:read_all,profile:read_all"

echo ""
echo "✓ Configuration initialized"
echo ""
echo "Next step: Authorize the application"
echo ""
echo "Visit this URL in your browser:"
echo "$OAUTH_URL"
echo ""
echo "After authorizing, you'll be redirected to localhost:8080/callback?code=..."
echo "Copy the 'code' parameter from the URL and run:"
echo ""
echo "  scripts/complete_auth.py YOUR_CODE_HERE"
echo ""
