#!/bin/bash
# Tailscale API helper script
# Usage: ts-api.sh <command> [args...]

set -euo pipefail

CONFIG_FILE="${TS_CONFIG:-$HOME/.clawdbot/credentials/tailscale/config.json}"
API_BASE="https://api.tailscale.com/api/v2"

# Load config
if [[ -f "$CONFIG_FILE" ]]; then
    TS_API_KEY=$(jq -r '.apiKey // empty' "$CONFIG_FILE")
    TS_TAILNET=$(jq -r '.tailnet // "-"' "$CONFIG_FILE")
else
    TS_API_KEY="${TS_API_KEY:-}"
    TS_TAILNET="${TS_TAILNET:--}"
fi

if [[ -z "$TS_API_KEY" ]]; then
    echo '{"error": "No API key configured. Set TS_API_KEY or create '"$CONFIG_FILE"'"}' >&2
    exit 1
fi

# API call helper (Basic Auth with API key as username)
api() {
    local method="$1"
    local endpoint="$2"
    shift 2
    
    curl -sS -X "$method" \
        -u "${TS_API_KEY}:" \
        -H "Content-Type: application/json" \
        "$@" \
        "${API_BASE}${endpoint}"
}

usage() {
    cat <<EOF
Tailscale API CLI

Usage: $(basename "$0") <command> [options]

Device Commands:
  devices [--verbose]           List all devices in tailnet
  device <id|name>              Get device details
  online                        Show online status of all devices
  authorize <id>                Authorize a device
  delete <id>                   Delete a device from tailnet
  tags <id> <tags>              Set device tags (comma-separated)
  routes <id>                   Get device routes

Key Management:
  keys                          List auth keys
  create-key [options]          Create new auth key
    --reusable                  Key can be used multiple times
    --ephemeral                 Devices auto-remove when offline
    --tags <tags>               Comma-separated tags (e.g., tag:server)
    --expiry <duration>         Expiry (e.g., 1h, 7d, 90d)
  delete-key <id>               Delete an auth key

DNS Commands:
  dns                           Show DNS configuration
  dns-nameservers               List nameservers
  magic-dns <on|off>            Toggle MagicDNS

ACL Commands:
  acl                           Get current ACL policy
  acl-validate <file>           Validate an ACL file

Examples:
  $(basename "$0") devices
  $(basename "$0") online
  $(basename "$0") create-key --reusable --tags tag:ci --expiry 7d
  $(basename "$0") tags nodekey:abc123 tag:server,tag:prod
EOF
}

# Find device ID by name or return as-is if already an ID
resolve_device() {
    local input="$1"
    
    # If it looks like a device ID, return as-is
    if [[ "$input" =~ ^[0-9]+$ ]] || [[ "$input" =~ ^nodekey: ]]; then
        echo "$input"
        return
    fi
    
    # Search by hostname
    local devices
    devices=$(api GET "/tailnet/${TS_TAILNET}/devices")
    local id
    id=$(echo "$devices" | jq -r --arg name "$input" '.devices[] | select(.hostname == $name or .name == $name or (.name | split(".")[0]) == $name) | .id' | head -1)
    
    if [[ -n "$id" && "$id" != "null" ]]; then
        echo "$id"
    else
        echo "$input"  # Return as-is, let API error if invalid
    fi
}

cmd_devices() {
    local verbose=false
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --verbose|-v) verbose=true; shift ;;
            *) shift ;;
        esac
    done
    
    local result
    result=$(api GET "/tailnet/${TS_TAILNET}/devices")
    
    if [[ "$verbose" == "true" ]]; then
        echo "$result" | jq '.devices'
    else
        echo "$result" | jq '[.devices[] | {
            id: .id,
            name: .hostname,
            ip: .addresses[0],
            os: .os,
            online: (.lastSeen | if . then (now - (. | fromdateiso8601) < 300) else false end),
            lastSeen: .lastSeen
        }]'
    fi
}

cmd_device() {
    local id
    id=$(resolve_device "$1")
    api GET "/device/${id}"
}

cmd_online() {
    local result
    result=$(api GET "/tailnet/${TS_TAILNET}/devices")
    
    echo "$result" | jq '[.devices[] | {
        name: .hostname,
        ip: .addresses[0],
        online: (.lastSeen | if . then (now - (. | fromdateiso8601) < 300) else false end),
        lastSeen: (if .lastSeen then .lastSeen else "never" end)
    }] | sort_by(.online) | reverse'
}

cmd_authorize() {
    local id
    id=$(resolve_device "$1")
    api POST "/device/${id}/authorized" -d '{"authorized": true}'
    echo '{"status": "ok", "device": "'"$id"'", "authorized": true}'
}

cmd_delete() {
    local id
    id=$(resolve_device "$1")
    api DELETE "/device/${id}"
    echo '{"status": "ok", "device": "'"$id"'", "deleted": true}'
}

cmd_tags() {
    local id
    id=$(resolve_device "$1")
    local tags="$2"
    
    # Convert comma-separated to JSON array
    local tags_json
    tags_json=$(echo "$tags" | jq -R 'split(",") | map(select(length > 0))')
    
    api POST "/device/${id}/tags" -d "{\"tags\": ${tags_json}}"
    echo '{"status": "ok", "device": "'"$id"'", "tags": '"$tags_json"'}'
}

cmd_routes() {
    local id
    id=$(resolve_device "$1")
    api GET "/device/${id}/routes"
}

cmd_keys() {
    api GET "/tailnet/${TS_TAILNET}/keys" | jq '.keys'
}

cmd_create_key() {
    local reusable=false
    local ephemeral=false
    local tags=""
    local expiry=86400  # Default 1 day in seconds
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --reusable) reusable=true; shift ;;
            --ephemeral) ephemeral=true; shift ;;
            --tags) tags="$2"; shift 2 ;;
            --expiry)
                # Convert human-readable to seconds
                local val="$2"
                if [[ "$val" =~ ^([0-9]+)d$ ]]; then
                    expiry=$((${BASH_REMATCH[1]} * 86400))
                elif [[ "$val" =~ ^([0-9]+)h$ ]]; then
                    expiry=$((${BASH_REMATCH[1]} * 3600))
                else
                    expiry="$val"
                fi
                shift 2
                ;;
            *) shift ;;
        esac
    done
    
    local tags_json="[]"
    if [[ -n "$tags" ]]; then
        tags_json=$(echo "$tags" | jq -R 'split(",") | map(select(length > 0))')
    fi
    
    local body
    body=$(jq -n \
        --argjson reusable "$reusable" \
        --argjson ephemeral "$ephemeral" \
        --argjson tags "$tags_json" \
        --argjson expiry "$expiry" \
        '{
            capabilities: {
                devices: {
                    create: {
                        reusable: $reusable,
                        ephemeral: $ephemeral,
                        tags: $tags
                    }
                }
            },
            expirySeconds: $expiry
        }')
    
    api POST "/tailnet/${TS_TAILNET}/keys" -d "$body"
}

cmd_delete_key() {
    local id="$1"
    api DELETE "/tailnet/${TS_TAILNET}/keys/${id}"
    echo '{"status": "ok", "key": "'"$id"'", "deleted": true}'
}

cmd_dns() {
    echo "{"
    echo '  "nameservers": '
    api GET "/tailnet/${TS_TAILNET}/dns/nameservers"
    echo ','
    echo '  "searchPaths": '
    api GET "/tailnet/${TS_TAILNET}/dns/searchpaths"
    echo ','
    echo '  "preferences": '
    api GET "/tailnet/${TS_TAILNET}/dns/preferences"
    echo "}"
}

cmd_dns_nameservers() {
    api GET "/tailnet/${TS_TAILNET}/dns/nameservers"
}

cmd_magic_dns() {
    local state="$1"
    local enabled=false
    [[ "$state" == "on" || "$state" == "true" || "$state" == "1" ]] && enabled=true
    
    api POST "/tailnet/${TS_TAILNET}/dns/preferences" -d "{\"magicDNS\": $enabled}"
}

cmd_acl() {
    api GET "/tailnet/${TS_TAILNET}/acl" -H "Accept: application/hujson"
}

cmd_acl_validate() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo '{"error": "File not found: '"$file"'"}' >&2
        exit 1
    fi
    api POST "/tailnet/${TS_TAILNET}/acl/validate" -d @"$file"
}

# Main dispatch
case "${1:-}" in
    devices) shift; cmd_devices "$@" ;;
    device) shift; cmd_device "$@" ;;
    online) shift; cmd_online "$@" ;;
    authorize) shift; cmd_authorize "$@" ;;
    delete) shift; cmd_delete "$@" ;;
    tags) shift; cmd_tags "$@" ;;
    routes) shift; cmd_routes "$@" ;;
    keys) shift; cmd_keys "$@" ;;
    create-key) shift; cmd_create_key "$@" ;;
    delete-key) shift; cmd_delete_key "$@" ;;
    dns) shift; cmd_dns "$@" ;;
    dns-nameservers) shift; cmd_dns_nameservers "$@" ;;
    magic-dns) shift; cmd_magic_dns "$@" ;;
    acl) shift; cmd_acl "$@" ;;
    acl-validate) shift; cmd_acl_validate "$@" ;;
    -h|--help|help|"") usage ;;
    *) echo "Unknown command: $1" >&2; usage; exit 1 ;;
esac
