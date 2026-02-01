#!/usr/bin/env bash
# Canva Connect API CLI
# Usage: canva.sh <command> [options]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="${CLAWDBOT_STATE_DIR:-$HOME/.clawdbot}"
TOKENS_FILE="$CONFIG_DIR/canva-tokens.json"
API_BASE="https://api.canva.com/rest"
OAUTH_PORT=3001

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load credentials from env or config
load_credentials() {
    if [[ -n "${CANVA_CLIENT_ID:-}" ]] && [[ -n "${CANVA_CLIENT_SECRET:-}" ]]; then
        CLIENT_ID="$CANVA_CLIENT_ID"
        CLIENT_SECRET="$CANVA_CLIENT_SECRET"
    elif [[ -f "$CONFIG_DIR/clawdbot.json" ]]; then
        CLIENT_ID=$(jq -r '.skills.entries.canva.clientId // empty' "$CONFIG_DIR/clawdbot.json" 2>/dev/null || echo "")
        CLIENT_SECRET=$(jq -r '.skills.entries.canva.clientSecret // empty' "$CONFIG_DIR/clawdbot.json" 2>/dev/null || echo "")
    fi
    
    if [[ -z "${CLIENT_ID:-}" ]] || [[ -z "${CLIENT_SECRET:-}" ]]; then
        echo -e "${RED}Error: Canva credentials not configured${NC}" >&2
        echo "Set CANVA_CLIENT_ID and CANVA_CLIENT_SECRET or configure in clawdbot.json" >&2
        exit 1
    fi
}

# Load access token
load_token() {
    if [[ ! -f "$TOKENS_FILE" ]]; then
        echo -e "${RED}Error: Not authenticated. Run: canva.sh auth${NC}" >&2
        exit 1
    fi
    
    ACCESS_TOKEN=$(jq -r '.access_token // empty' "$TOKENS_FILE" 2>/dev/null || echo "")
    EXPIRES_AT=$(jq -r '.expires_at // 0' "$TOKENS_FILE" 2>/dev/null || echo "0")
    
    # Check if token expired
    NOW=$(date +%s)
    if [[ "$NOW" -ge "$EXPIRES_AT" ]]; then
        refresh_token
    fi
}

# Refresh access token
refresh_token() {
    load_credentials
    REFRESH_TOKEN=$(jq -r '.refresh_token // empty' "$TOKENS_FILE" 2>/dev/null || echo "")
    
    if [[ -z "$REFRESH_TOKEN" ]]; then
        echo -e "${RED}Error: No refresh token. Run: canva.sh auth${NC}" >&2
        exit 1
    fi
    
    RESPONSE=$(curl -s -X POST "https://api.canva.com/rest/v1/oauth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=refresh_token" \
        -d "refresh_token=$REFRESH_TOKEN" \
        -d "client_id=$CLIENT_ID" \
        -d "client_secret=$CLIENT_SECRET")
    
    if echo "$RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
        save_tokens "$RESPONSE"
        ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
    else
        echo -e "${RED}Error refreshing token: $RESPONSE${NC}" >&2
        exit 1
    fi
}

# Save tokens to file
save_tokens() {
    local response="$1"
    local expires_in=$(echo "$response" | jq -r '.expires_in // 3600')
    local expires_at=$(($(date +%s) + expires_in - 60))
    
    echo "$response" | jq --arg exp "$expires_at" '. + {expires_at: ($exp | tonumber)}' > "$TOKENS_FILE"
    chmod 600 "$TOKENS_FILE"
}

# Make API request
api_request() {
    local method="$1"
    local endpoint="$2"
    shift 2
    local data="${1:-}"
    
    load_token
    
    local curl_args=(-s -X "$method" "${API_BASE}${endpoint}" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json")
    
    if [[ -n "$data" ]]; then
        curl_args+=(-d "$data")
    fi
    
    local response
    response=$(curl "${curl_args[@]}")
    
    # Check for errors
    if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
        echo -e "${RED}API Error: $(echo "$response" | jq -r '.error.message // .error')${NC}" >&2
        exit 1
    fi
    
    echo "$response"
}

# Upload file (multipart)
api_upload() {
    local endpoint="$1"
    local file="$2"
    local metadata="$3"
    
    load_token
    
    curl -s -X POST "${API_BASE}${endpoint}" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Asset-Upload-Metadata: $metadata" \
        -H "Content-Type: application/octet-stream" \
        --data-binary "@$file"
}

# ==================== COMMANDS ====================

cmd_auth() {
    local subcmd="${1:-}"
    
    case "$subcmd" in
        status)
            if [[ -f "$TOKENS_FILE" ]]; then
                load_token
                echo -e "${GREEN}✓ Authenticated${NC}"
                api_request GET "/v1/users/me" | jq '{user: .display_name, team: .team_display_name}'
            else
                echo -e "${YELLOW}Not authenticated${NC}"
            fi
            ;;
        logout)
            rm -f "$TOKENS_FILE"
            echo -e "${GREEN}Logged out${NC}"
            ;;
        *)
            # Start OAuth flow with PKCE
            load_credentials
            
            local state=$(openssl rand -hex 16)
            local scopes="design:content:write design:content:read design:meta:read asset:write asset:read brandtemplate:meta:read brandtemplate:content:read profile:read folder:read folder:write"
            local encoded_scopes=$(echo "$scopes" | sed 's/ /%20/g')
            
            # Generate PKCE code_verifier (43-128 chars, URL-safe)
            local code_verifier=$(openssl rand -base64 32 | tr -d '=' | tr '+/' '-_' | cut -c1-43)
            # Generate code_challenge = base64url(sha256(code_verifier))
            local code_challenge=$(printf '%s' "$code_verifier" | openssl dgst -sha256 -binary | openssl base64 -A | tr -d '=' | tr '+/' '-_')
            
            local auth_url="https://www.canva.com/api/oauth/authorize?response_type=code&client_id=${CLIENT_ID}&redirect_uri=http://127.0.0.1:${OAUTH_PORT}/oauth/redirect&scope=${encoded_scopes}&state=${state}&code_challenge=${code_challenge}&code_challenge_method=S256"
            
            echo "Opening browser for Canva authorization..."
            echo "If browser doesn't open, visit: $auth_url"
            
            # Try to open browser
            if command -v xdg-open &> /dev/null; then
                xdg-open "$auth_url" 2>/dev/null &
            elif command -v open &> /dev/null; then
                open "$auth_url" 2>/dev/null &
            fi
            
            # Start simple HTTP server to catch callback
            echo "Waiting for OAuth callback on port $OAUTH_PORT..."
            
            # Save code_verifier to temp file for the callback handler
            local verifier_file=$(mktemp)
            local code_file=$(mktemp)
            echo "$code_verifier" > "$verifier_file"
            
            # Use Python for the callback server (simpler, more reliable)
            python3 << PYEOF
import http.server
import socketserver
import urllib.parse

code_file = "$code_file"
port = $OAUTH_PORT

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/oauth/redirect':
            params = urllib.parse.parse_qs(parsed.query)
            code = params.get('code', [None])[0]
            if code:
                with open(code_file, 'w') as f:
                    f.write(code)
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>Success!</h1><p>You can close this window.</p>')
                raise KeyboardInterrupt()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'No code received')
    def log_message(self, format, *args):
        pass  # Suppress logging

try:
    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.handle_request()
except KeyboardInterrupt:
    pass
PYEOF
            
            # Read auth code from file
            local auth_code=""
            if [ -f "$code_file" ]; then
                auth_code=$(cat "$code_file")
                rm -f "$code_file"
            fi
            
            if [ -n "$auth_code" ]; then
                local saved_verifier=$(cat "$verifier_file")
                rm -f "$verifier_file"
                
                # Debug output
                echo "Debug: code length=${#auth_code}, verifier length=${#saved_verifier}"
                
                # Exchange code for tokens (with PKCE code_verifier)
                local token_response=$(curl -s -X POST "https://api.canva.com/rest/v1/oauth/token" \
                    -H "Content-Type: application/x-www-form-urlencoded" \
                    -d "grant_type=authorization_code" \
                    -d "code=$auth_code" \
                    -d "redirect_uri=http://127.0.0.1:${OAUTH_PORT}/oauth/redirect" \
                    -d "code_verifier=$saved_verifier" \
                    -d "client_id=$CLIENT_ID" \
                    -d "client_secret=$CLIENT_SECRET")
                
                if echo "$token_response" | jq -e '.access_token' > /dev/null 2>&1; then
                    save_tokens "$token_response"
                    echo -e "${GREEN}✓ Successfully authenticated!${NC}"
                else
                    echo -e "${RED}Error: $token_response${NC}" >&2
                    exit 1
                fi
            else
                rm -f "$verifier_file"
                echo -e "${RED}Error: No authorization code received${NC}" >&2
                exit 1
            fi
            ;;
    esac
}

cmd_me() {
    api_request GET "/v1/users/me" | jq
}

cmd_designs() {
    local subcmd="${1:-list}"
    shift || true
    
    case "$subcmd" in
        list)
            local limit=10
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --limit) limit="$2"; shift 2 ;;
                    *) shift ;;
                esac
            done
            api_request GET "/v1/designs?ownership=owned&limit=$limit" | jq
            ;;
        get)
            local id="$1"
            api_request GET "/v1/designs/$id" | jq
            ;;
        create)
            local design_type="doc"
            local title="Untitled"
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --type) design_type="$2"; shift 2 ;;
                    --title) title="$2"; shift 2 ;;
                    *) shift ;;
                esac
            done
            api_request POST "/v1/designs" "{\"design_type\":\"$design_type\",\"title\":\"$title\"}" | jq
            ;;
        delete)
            local id="$1"
            api_request DELETE "/v1/designs/$id"
            echo -e "${GREEN}Design moved to trash${NC}"
            ;;
        *)
            echo "Usage: canva.sh designs [list|get|create|delete] [options]"
            ;;
    esac
}

cmd_export() {
    local subcmd="$1"
    shift || true
    
    if [[ "$subcmd" == "status" ]]; then
        local job_id="$1"
        api_request GET "/v1/exports/$job_id" | jq
    else
        # subcmd is design_id
        local design_id="$subcmd"
        local format="pdf"
        local output=""
        
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --format) format="$2"; shift 2 ;;
                --output) output="$2"; shift 2 ;;
                *) shift ;;
            esac
        done
        
        local response=$(api_request POST "/v1/exports" "{\"design_id\":\"$design_id\",\"format\":{\"type\":\"$format\"}}")
        echo "$response" | jq
        
        # If output specified, poll until complete and download
        if [[ -n "$output" ]]; then
            local job_id=$(echo "$response" | jq -r '.job.id')
            echo "Export job started: $job_id"
            
            while true; do
                sleep 2
                local status_response=$(api_request GET "/v1/exports/$job_id")
                local status=$(echo "$status_response" | jq -r '.job.status')
                
                case "$status" in
                    success)
                        local url=$(echo "$status_response" | jq -r '.job.result.urls[0]')
                        curl -s -o "$output" "$url"
                        echo -e "${GREEN}Downloaded to: $output${NC}"
                        break
                        ;;
                    failed)
                        echo -e "${RED}Export failed${NC}" >&2
                        echo "$status_response" | jq >&2
                        exit 1
                        ;;
                    *)
                        echo "Status: $status..."
                        ;;
                esac
            done
        fi
    fi
}

cmd_assets() {
    local subcmd="${1:-list}"
    shift || true
    
    case "$subcmd" in
        list)
            api_request GET "/v1/assets" | jq
            ;;
        get)
            local id="$1"
            api_request GET "/v1/assets/$id" | jq
            ;;
        upload)
            local file="$1"
            local name="${2:-$(basename "$file")}"
            
            if [[ ! -f "$file" ]]; then
                echo -e "${RED}File not found: $file${NC}" >&2
                exit 1
            fi
            
            local metadata="{\"name_base64\":\"$(echo -n "$name" | base64)\"}"
            api_upload "/v1/asset-uploads" "$file" "$metadata" | jq
            ;;
        delete)
            local id="$1"
            api_request DELETE "/v1/assets/$id"
            echo -e "${GREEN}Asset deleted${NC}"
            ;;
        *)
            echo "Usage: canva.sh assets [list|get|upload|delete] [options]"
            ;;
    esac
}

cmd_templates() {
    local subcmd="${1:-list}"
    shift || true
    
    case "$subcmd" in
        list)
            api_request GET "/v1/brand-templates" | jq
            ;;
        get)
            local id="$1"
            api_request GET "/v1/brand-templates/$id" | jq
            ;;
        *)
            echo "Usage: canva.sh templates [list|get]"
            ;;
    esac
}

cmd_autofill() {
    local template_id="$1"
    shift || true
    
    local data="{}"
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --data) data="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    api_request POST "/v1/autofills" "{\"brand_template_id\":\"$template_id\",\"data\":$data}" | jq
}

cmd_folders() {
    local subcmd="${1:-list}"
    shift || true
    
    case "$subcmd" in
        list)
            api_request GET "/v1/folders" | jq
            ;;
        get)
            local id="$1"
            api_request GET "/v1/folders/$id/items" | jq
            ;;
        create)
            local name="$1"
            api_request POST "/v1/folders" "{\"name\":\"$name\"}" | jq
            ;;
        *)
            echo "Usage: canva.sh folders [list|get|create]"
            ;;
    esac
}

cmd_help() {
    cat << 'EOF'
Canva Connect CLI

Usage: canva.sh <command> [options]

Commands:
  auth [status|logout]           Authenticate with Canva
  me                             Get current user profile
  designs [list|get|create|delete]  Manage designs
  export <design_id> [--format]  Export a design
  assets [list|get|upload|delete]  Manage assets
  templates [list|get]           List brand templates
  autofill <template_id> --data  Autofill a template
  folders [list|get|create]      Manage folders
  help                           Show this help

Examples:
  canva.sh auth                  # Authenticate
  canva.sh designs list          # List designs
  canva.sh designs create --type poster --title "My Poster"
  canva.sh export DAF... --format png --output poster.png
  canva.sh assets upload ./image.png --name "My Image"

For more info: https://canva.dev/docs/connect/
EOF
}

# ==================== MAIN ====================

mkdir -p "$CONFIG_DIR"

COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    auth) cmd_auth "$@" ;;
    me) cmd_me "$@" ;;
    designs) cmd_designs "$@" ;;
    export) cmd_export "$@" ;;
    assets) cmd_assets "$@" ;;
    templates) cmd_templates "$@" ;;
    autofill) cmd_autofill "$@" ;;
    folders) cmd_folders "$@" ;;
    help|--help|-h) cmd_help ;;
    *)
        echo "Unknown command: $COMMAND"
        cmd_help
        exit 1
        ;;
esac
