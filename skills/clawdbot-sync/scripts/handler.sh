#!/usr/bin/env bash
# Clawdbot Sync Handler
# Synchronize memory and skills between Clawdbot instances
# Usage: handler.sh <command> [args...] <workspace>

set -euo pipefail

# Check dependencies
command -v rsync >/dev/null 2>&1 || { echo '{"status":"error","message":"rsync required"}'; exit 1; }
command -v ssh >/dev/null 2>&1 || { echo '{"status":"error","message":"ssh required"}'; exit 1; }
command -v jq >/dev/null 2>&1 || { echo '{"status":"error","message":"jq required"}'; exit 1; }

CMD="${1:-status}"
shift || true

# Get workspace (always last argument)
WORKSPACE="${!#:-$(pwd)}"
DATA_DIR="$WORKSPACE/memory/clawdbot-sync"
CONFLICTS_DIR="$DATA_DIR/conflicts"

# Ensure directories exist
mkdir -p "$DATA_DIR" "$CONFLICTS_DIR"

# File paths
PEERS_FILE="$DATA_DIR/peers.json"
HISTORY_FILE="$DATA_DIR/history.json"
CONFIG_FILE="$DATA_DIR/config.json"

# Initialize files if they don't exist
[[ -f "$PEERS_FILE" ]] || echo '{"peers":{}}' > "$PEERS_FILE"
[[ -f "$HISTORY_FILE" ]] || echo '{"entries":[]}' > "$HISTORY_FILE"
[[ -f "$CONFIG_FILE" ]] || echo '{"autoSync":false,"syncSkills":false,"excludePatterns":["*.tmp","*.log",".git/","cache/","node_modules/"]}' > "$CONFIG_FILE"

# Paths to sync (relative to workspace)
SYNC_PATHS=(
    "memory/"
    "MEMORY.md"
    "USER.md"
    "HEARTBEAT.md"
)

# Paths to exclude
EXCLUDE_PATTERNS=(
    "*.tmp"
    "*.log"
    ".git/"
    "cache/"
    "node_modules/"
    "*.bak"
    "clawdbot-sync/"  # Don't sync the sync data itself
)

# ============================================
# Helper Functions
# ============================================

get_peer() {
    local name="$1"
    jq -r --arg n "$name" '.peers[$n] // empty' "$PEERS_FILE"
}

list_peers() {
    jq -r '.peers | keys[]' "$PEERS_FILE" 2>/dev/null
}

check_connection() {
    local host="$1"
    local user="${2:-clawdbot}"
    local timeout=5
    
    ssh -o ConnectTimeout=$timeout -o BatchMode=yes -o StrictHostKeyChecking=no \
        "${user}@${host}" "echo ok" 2>/dev/null && return 0
    return 1
}

add_history() {
    local action="$1"
    local peer="$2"
    local files="$3"
    local status="$4"
    
    jq --arg action "$action" --arg peer "$peer" --arg files "$files" --arg status "$status" \
        '.entries = [{"timestamp": (now | strftime("%Y-%m-%dT%H:%M:%SZ")), "action": $action, "peer": $peer, "files": ($files | tonumber), "status": $status}] + .entries[:99]' \
        "$HISTORY_FILE" > "$HISTORY_FILE.tmp" && mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
}

build_rsync_args() {
    local args="-avz --delete --itemize-changes"
    
    # Add excludes
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        args="$args --exclude='$pattern'"
    done
    
    echo "$args"
}

# ============================================
# Commands
# ============================================

case "$CMD" in
    # ----------------------------------------
    # STATUS
    # ----------------------------------------
    status)
        peers_json=$(jq -c '.peers' "$PEERS_FILE")
        peer_count=$(jq '.peers | length' "$PEERS_FILE")
        
        # Check each peer's connection
        peer_status="[]"
        while IFS= read -r peer_name; do
            [[ -z "$peer_name" ]] && continue
            peer_data=$(get_peer "$peer_name")
            host=$(echo "$peer_data" | jq -r '.host')
            user=$(echo "$peer_data" | jq -r '.user // "clawdbot"')
            
            if check_connection "$host" "$user" 2>/dev/null; then
                conn_status="online"
            else
                conn_status="offline"
            fi
            
            peer_status=$(echo "$peer_status" | jq --arg name "$peer_name" --arg host "$host" --arg status "$conn_status" \
                '. + [{"name": $name, "host": $host, "status": $status}]')
        done < <(list_peers)
        
        auto_sync=$(jq -r '.autoSync // false' "$CONFIG_FILE")
        last_sync=$(jq -r '.entries[0].timestamp // "never"' "$HISTORY_FILE")
        
        jq -n \
            --argjson peers "$peer_status" \
            --argjson peerCount "$peer_count" \
            --arg autoSync "$auto_sync" \
            --arg lastSync "$last_sync" \
            '{
                status: "ok",
                peerCount: $peerCount,
                peers: $peers,
                autoSync: ($autoSync == "true"),
                lastSync: $lastSync,
                commands: {
                    "/sync now [peer]": "Sync with peer",
                    "/sync push <peer>": "Push to peer",
                    "/sync pull <peer>": "Pull from peer",
                    "/sync diff <peer>": "Show differences",
                    "/sync add <name> <host> [user] [path]": "Add peer",
                    "/sync remove <name>": "Remove peer",
                    "/sync history": "Show sync history"
                }
            }'
        ;;
        
    # ----------------------------------------
    # ADD PEER
    # ----------------------------------------
    add)
        name="${1:-}"
        host="${2:-}"
        user="${3:-clawdbot}"
        remote_path="${4:-/home/clawdbot/clawd}"
        
        [[ -z "$name" ]] && { echo '{"status":"error","message":"Peer name required"}'; exit 1; }
        [[ -z "$host" ]] && { echo '{"status":"error","message":"Host required"}'; exit 1; }
        
        # Test connection
        if check_connection "$host" "$user" 2>/dev/null; then
            conn_test="success"
        else
            conn_test="failed"
        fi
        
        # Add peer
        jq --arg name "$name" --arg host "$host" --arg user "$user" --arg path "$remote_path" \
            '.peers[$name] = {"host": $host, "user": $user, "path": $path, "addedAt": (now | strftime("%Y-%m-%dT%H:%M:%SZ"))}' \
            "$PEERS_FILE" > "$PEERS_FILE.tmp" && mv "$PEERS_FILE.tmp" "$PEERS_FILE"
        
        jq -n --arg name "$name" --arg host "$host" --arg conn "$conn_test" \
            '{status: "ok", message: "Peer added", peer: $name, host: $host, connectionTest: $conn}'
        ;;
        
    # ----------------------------------------
    # REMOVE PEER
    # ----------------------------------------
    remove)
        name="${1:-}"
        [[ -z "$name" ]] && { echo '{"status":"error","message":"Peer name required"}'; exit 1; }
        
        jq --arg name "$name" 'del(.peers[$name])' "$PEERS_FILE" > "$PEERS_FILE.tmp" && mv "$PEERS_FILE.tmp" "$PEERS_FILE"
        
        echo '{"status":"ok","message":"Peer removed","peer":"'"$name"'"}'
        ;;
        
    # ----------------------------------------
    # DIFF (show what would change)
    # ----------------------------------------
    diff)
        peer_name="${1:-}"
        [[ -z "$peer_name" ]] && { echo '{"status":"error","message":"Peer name required"}'; exit 1; }
        
        peer_data=$(get_peer "$peer_name")
        [[ -z "$peer_data" ]] && { echo '{"status":"error","message":"Peer not found: '"$peer_name"'"}'; exit 1; }
        
        host=$(echo "$peer_data" | jq -r '.host')
        user=$(echo "$peer_data" | jq -r '.user // "clawdbot"')
        remote_path=$(echo "$peer_data" | jq -r '.path // "/home/clawdbot/clawd"')
        
        # Build exclude args
        exclude_args=""
        for pattern in "${EXCLUDE_PATTERNS[@]}"; do
            exclude_args="$exclude_args --exclude=$pattern"
        done
        
        changes_out="[]"
        changes_in="[]"
        
        for sync_path in "${SYNC_PATHS[@]}"; do
            local_path="$WORKSPACE/$sync_path"
            remote="$user@$host:$remote_path/$sync_path"
            
            [[ ! -e "$local_path" ]] && continue
            
            # Check outgoing (local → remote)
            out_diff=$(rsync -avzn --delete $exclude_args "$local_path" "$remote" 2>/dev/null | grep -E "^[<>ch]" | head -10 || echo "")
            if [[ -n "$out_diff" ]]; then
                while IFS= read -r line; do
                    changes_out=$(echo "$changes_out" | jq --arg f "$line" '. + [$f]')
                done <<< "$out_diff"
            fi
            
            # Check incoming (remote → local)
            in_diff=$(rsync -avzn --delete $exclude_args "$remote" "$local_path" 2>/dev/null | grep -E "^[<>ch]" | head -10 || echo "")
            if [[ -n "$in_diff" ]]; then
                while IFS= read -r line; do
                    changes_in=$(echo "$changes_in" | jq --arg f "$line" '. + [$f]')
                done <<< "$in_diff"
            fi
        done
        
        jq -n --argjson out "$changes_out" --argjson in "$changes_in" --arg peer "$peer_name" \
            '{status: "ok", peer: $peer, outgoing: $out, incoming: $in, outCount: ($out | length), inCount: ($in | length)}'
        ;;
        
    # ----------------------------------------
    # PUSH (local → remote)
    # ----------------------------------------
    push)
        peer_name="${1:-}"
        [[ -z "$peer_name" ]] && { echo '{"status":"error","message":"Peer name required"}'; exit 1; }
        
        peer_data=$(get_peer "$peer_name")
        [[ -z "$peer_data" ]] && { echo '{"status":"error","message":"Peer not found: '"$peer_name"'"}'; exit 1; }
        
        host=$(echo "$peer_data" | jq -r '.host')
        user=$(echo "$peer_data" | jq -r '.user // "clawdbot"')
        remote_path=$(echo "$peer_data" | jq -r '.path // "/home/clawdbot/clawd"')
        
        # Build exclude args
        exclude_args=""
        for pattern in "${EXCLUDE_PATTERNS[@]}"; do
            exclude_args="$exclude_args --exclude=$pattern"
        done
        
        total_files=0
        errors=""
        
        for sync_path in "${SYNC_PATHS[@]}"; do
            local_path="$WORKSPACE/$sync_path"
            remote="$user@$host:$remote_path/$sync_path"
            
            [[ ! -e "$local_path" ]] && continue
            
            # Ensure remote directory exists
            if [[ "$sync_path" == */ ]]; then
                ssh -o BatchMode=yes "$user@$host" "mkdir -p $remote_path/$sync_path" 2>/dev/null || true
            fi
            
            # Sync
            result=$(rsync -avz $exclude_args "$local_path" "$remote" 2>&1) || errors="$errors\n$result"
            count=$(echo "$result" | grep -cE "^[<>ch]" || echo "0")
            total_files=$((total_files + count))
        done
        
        add_history "push" "$peer_name" "$total_files" "success"
        
        jq -n --arg peer "$peer_name" --argjson files "$total_files" \
            '{status: "ok", action: "push", peer: $peer, filesSynced: $files}'
        ;;
        
    # ----------------------------------------
    # PULL (remote → local)
    # ----------------------------------------
    pull)
        peer_name="${1:-}"
        [[ -z "$peer_name" ]] && { echo '{"status":"error","message":"Peer name required"}'; exit 1; }
        
        peer_data=$(get_peer "$peer_name")
        [[ -z "$peer_data" ]] && { echo '{"status":"error","message":"Peer not found: '"$peer_name"'"}'; exit 1; }
        
        host=$(echo "$peer_data" | jq -r '.host')
        user=$(echo "$peer_data" | jq -r '.user // "clawdbot"')
        remote_path=$(echo "$peer_data" | jq -r '.path // "/home/clawdbot/clawd"')
        
        # Build exclude args
        exclude_args=""
        for pattern in "${EXCLUDE_PATTERNS[@]}"; do
            exclude_args="$exclude_args --exclude=$pattern"
        done
        
        total_files=0
        
        for sync_path in "${SYNC_PATHS[@]}"; do
            local_path="$WORKSPACE/$sync_path"
            remote="$user@$host:$remote_path/$sync_path"
            
            # Ensure local directory exists
            if [[ "$sync_path" == */ ]]; then
                mkdir -p "$local_path"
            fi
            
            # Sync
            result=$(rsync -avz $exclude_args "$remote" "$local_path" 2>&1) || true
            count=$(echo "$result" | grep -cE "^[<>ch]" || echo "0")
            total_files=$((total_files + count))
        done
        
        add_history "pull" "$peer_name" "$total_files" "success"
        
        jq -n --arg peer "$peer_name" --argjson files "$total_files" \
            '{status: "ok", action: "pull", peer: $peer, filesSynced: $files}'
        ;;
        
    # ----------------------------------------
    # SYNC (bi-directional)
    # ----------------------------------------
    sync|now)
        peer_name="${1:-}"
        
        # If no peer specified, sync all
        if [[ -z "$peer_name" || "$peer_name" == "$WORKSPACE" ]]; then
            peers=$(list_peers)
            [[ -z "$peers" ]] && { echo '{"status":"error","message":"No peers configured. Use /sync add first."}'; exit 1; }
            peer_name=$(echo "$peers" | head -1)
        fi
        
        peer_data=$(get_peer "$peer_name")
        [[ -z "$peer_data" ]] && { echo '{"status":"error","message":"Peer not found: '"$peer_name"'"}'; exit 1; }
        
        host=$(echo "$peer_data" | jq -r '.host')
        user=$(echo "$peer_data" | jq -r '.user // "clawdbot"')
        remote_path=$(echo "$peer_data" | jq -r '.path // "/home/clawdbot/clawd"')
        
        # Check connection first
        if ! check_connection "$host" "$user" 2>/dev/null; then
            echo '{"status":"error","message":"Cannot connect to peer: '"$peer_name"' ('"$host"')"}'
            exit 1
        fi
        
        # Build exclude args
        exclude_args=""
        for pattern in "${EXCLUDE_PATTERNS[@]}"; do
            exclude_args="$exclude_args --exclude=$pattern"
        done
        
        pushed=0
        pulled=0
        
        for sync_path in "${SYNC_PATHS[@]}"; do
            local_path="$WORKSPACE/$sync_path"
            remote="$user@$host:$remote_path/$sync_path"
            
            # Ensure directories exist
            if [[ "$sync_path" == */ ]]; then
                mkdir -p "$local_path" 2>/dev/null || true
                ssh -o BatchMode=yes "$user@$host" "mkdir -p $remote_path/$sync_path" 2>/dev/null || true
            fi
            
            # Push newer local files
            if [[ -e "$local_path" ]]; then
                result=$(rsync -avzu $exclude_args "$local_path" "$remote" 2>&1) || true
                count=$(echo "$result" | grep -cE "^[<>ch]" || echo "0")
                pushed=$((pushed + count))
            fi
            
            # Pull newer remote files
            result=$(rsync -avzu $exclude_args "$remote" "$local_path" 2>&1) || true
            count=$(echo "$result" | grep -cE "^[<>ch]" || echo "0")
            pulled=$((pulled + count))
        done
        
        total=$((pushed + pulled))
        add_history "sync" "$peer_name" "$total" "success"
        
        jq -n --arg peer "$peer_name" --arg host "$host" --argjson pushed "$pushed" --argjson pulled "$pulled" --argjson total "$total" \
            '{status: "ok", action: "sync", peer: $peer, host: $host, pushed: $pushed, pulled: $pulled, totalFiles: $total}'
        ;;
        
    # ----------------------------------------
    # HISTORY
    # ----------------------------------------
    history)
        limit="${1:-10}"
        [[ "$limit" == "$WORKSPACE" ]] && limit=10
        
        jq --argjson limit "$limit" '{
            status: "ok",
            total: (.entries | length),
            entries: .entries[:$limit]
        }' "$HISTORY_FILE"
        ;;
        
    # ----------------------------------------
    # AUTO (enable/disable auto-sync)
    # ----------------------------------------
    auto)
        setting="${1:-}"
        
        case "$setting" in
            on|true|enable)
                jq '.autoSync = true' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
                echo '{"status":"ok","message":"Auto-sync enabled","autoSync":true}'
                ;;
            off|false|disable)
                jq '.autoSync = false' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
                echo '{"status":"ok","message":"Auto-sync disabled","autoSync":false}'
                ;;
            *)
                auto_sync=$(jq -r '.autoSync' "$CONFIG_FILE")
                echo '{"status":"ok","autoSync":'"$auto_sync"'}'
                ;;
        esac
        ;;
        
    # ----------------------------------------
    # HELP
    # ----------------------------------------
    help)
        echo '{"status":"ok","commands":["status","add","remove","diff","push","pull","sync","now","history","auto"]}'
        ;;
        
    *)
        echo '{"status":"error","message":"Unknown command: '"$CMD"'"}'
        exit 1
        ;;
esac
