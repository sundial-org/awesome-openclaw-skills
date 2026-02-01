#!/bin/bash
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"
TOKEN_SCRIPT="$SKILL_DIR/lib/generate-token.js"

# Minimal output helpers
err() { echo "✗ $1" >&2; }
ok() { echo "✓ $1"; }
info() { echo "→ $1"; }

check_requirements() {
    command -v node &>/dev/null || { err "Node.js required (brew install node)"; exit 1; }
    command -v curl &>/dev/null || { err "curl required"; exit 1; }
    ok "Requirements met"
}

check_existing_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        read -p "Config exists. Reconfigure? [y/N] " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] || exit 0
    fi
}

show_requirements() {
    echo ""
    echo "Apple Music Setup (requires Developer account)"
    echo "Need: .p8 key, Key ID, Team ID"
    echo "Get at: developer.apple.com → Keys → MusicKit"
    echo ""
    read -p "Press Enter when ready (Ctrl+C to cancel)... "
}

get_credentials() {
    echo ""
    # Get .p8 key path
    while true; do
        read -e -p "Path to .p8 key: " KEY_PATH
        KEY_PATH="${KEY_PATH/#\~/$HOME}"
        [[ -f "$KEY_PATH" ]] && break
        err "File not found"
    done
    ok "Key found"
    
    # Auto-detect Key ID from filename
    FILENAME=$(basename "$KEY_PATH")
    if [[ "$FILENAME" =~ ^AuthKey_([A-Z0-9]{8,12})\.p8$ ]]; then
        KEY_ID="${BASH_REMATCH[1]}"
        info "Key ID: $KEY_ID (auto-detected)"
    else
        read -p "Key ID: " KEY_ID
    fi
    
    read -p "Team ID: " TEAM_ID
    read -p "Storefront [us]: " STOREFRONT
    STOREFRONT="${STOREFRONT:-us}"
}

generate_developer_token() {
    info "Generating developer token..."
    DEVELOPER_TOKEN=$(node "$TOKEN_SCRIPT" "$KEY_PATH" "$KEY_ID" "$TEAM_ID" 180 2>&1)
    [[ $? -eq 0 && $(echo "$DEVELOPER_TOKEN" | tr '.' '\n' | wc -l) -eq 3 ]] || { err "Token generation failed"; exit 1; }
    ok "Developer token created (6 month validity)"
}

get_user_authorization() {
    echo ""
    info "Starting auth server..."
    
    # Find available port
    AUTH_PORT=8765
    while lsof -i:$AUTH_PORT &>/dev/null; do AUTH_PORT=$((AUTH_PORT + 1)); done
    
    # Start HTTP server
    python3 -c "
import http.server, socketserver, os
os.chdir('$SKILL_DIR')
with socketserver.TCPServer(('127.0.0.1', $AUTH_PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    httpd.serve_forever()
" &>/dev/null &
    HTTP_SERVER_PID=$!
    sleep 2
    
    # Verify server started
    curl -s "http://localhost:$AUTH_PORT/auth.html" >/dev/null || { err "Server failed"; kill $HTTP_SERVER_PID 2>/dev/null; exit 1; }
    
    AUTH_URL="http://localhost:$AUTH_PORT/auth.html?token=$DEVELOPER_TOKEN"
    
    # Open browser (Chrome preferred on macOS)
    if command -v open &>/dev/null; then
        [[ -d "/Applications/Google Chrome.app" ]] && open -a "Google Chrome" "$AUTH_URL" || open "$AUTH_URL"
    elif command -v xdg-open &>/dev/null; then
        xdg-open "$AUTH_URL"
    else
        echo "Open manually: $AUTH_URL"
    fi
    
    info "Sign in with Apple Music, then paste the token below"
    echo ""
    read -p "Music User Token: " MUSIC_USER_TOKEN
    
    [[ -n "$MUSIC_USER_TOKEN" ]] || { err "Token required"; exit 1; }
    
    kill $HTTP_SERVER_PID 2>/dev/null || true
    ok "Token received"
}

test_tokens() {
    info "Testing API..."
    HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null \
        -H "Authorization: Bearer $DEVELOPER_TOKEN" \
        -H "Music-User-Token: $MUSIC_USER_TOKEN" \
        "https://api.music.apple.com/v1/me/library/playlists?limit=1")
    
    case "$HTTP_CODE" in
        200) ok "API test passed" ;;
        401) err "Auth failed - check Key ID/Team ID" ;;
        403) err "Invalid token or no Apple Music subscription" ;;
        *) err "Unexpected: HTTP $HTTP_CODE" ;;
    esac
}

save_config() {
    cat > "$CONFIG_FILE" << EOF
{
  "developer_token": "$DEVELOPER_TOKEN",
  "music_user_token": "$MUSIC_USER_TOKEN",
  "key_id": "$KEY_ID",
  "team_id": "$TEAM_ID",
  "storefront": "$STOREFRONT",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
    chmod 600 "$CONFIG_FILE"
    ok "Config saved"
}

show_completion() {
    echo ""
    ok "Setup complete!"
    echo ""
    echo "Usage: ./apple-music.sh [command]"
    echo "Tokens valid for ~6 months. Re-run setup.sh if auth fails."
    echo ""
}

main() {
    echo "🎵 Apple Music Setup"
    check_requirements
    check_existing_config
    show_requirements
    get_credentials
    generate_developer_token
    get_user_authorization
    test_tokens
    save_config
    show_completion
}

main
