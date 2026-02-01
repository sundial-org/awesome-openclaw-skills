#!/bin/bash
#
# local-whisper CLI
# Fast speech-to-text transcription for Clawdbot
#
# Usage:
#   transcribe.sh <audio_file> [--translate] [--language XX]
#
# Tries daemon first (fast), falls back to direct Python if unavailable.

set -e

DAEMON_URL="${CLAWD_WHISPER_URL:-http://localhost:8787}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
AUDIO_FILE=""
TRANSLATE="false"
LANGUAGE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --translate|-t)
            TRANSLATE="true"
            shift
            ;;
        --language|-l)
            LANGUAGE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: transcribe.sh <audio_file> [--translate] [--language XX]"
            echo ""
            echo "Options:"
            echo "  --translate, -t    Translate to English"
            echo "  --language, -l XX  Source language (ISO-639-1 code)"
            echo "  --help, -h         Show this help"
            exit 0
            ;;
        *)
            if [[ -z "$AUDIO_FILE" ]]; then
                AUDIO_FILE="$1"
            else
                echo "Error: Unexpected argument: $1" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$AUDIO_FILE" ]]; then
    echo "Error: No audio file specified" >&2
    echo "Usage: transcribe.sh <audio_file> [--translate] [--language XX]" >&2
    exit 1
fi

if [[ ! -f "$AUDIO_FILE" ]]; then
    echo "Error: File not found: $AUDIO_FILE" >&2
    exit 1
fi

# Convert to absolute path
AUDIO_FILE="$(cd "$(dirname "$AUDIO_FILE")" && pwd)/$(basename "$AUDIO_FILE")"

# Try daemon first (fast path)
try_daemon() {
    local json_payload
    json_payload=$(cat <<EOF
{"file": "$AUDIO_FILE", "translate": $TRANSLATE${LANGUAGE:+, "language": "$LANGUAGE"}}
EOF
)
    
    local response
    response=$(curl -s -X POST "$DAEMON_URL/transcribe" \
        -H "Content-Type: application/json" \
        -d "$json_payload" \
        --connect-timeout 2 \
        --max-time 120 2>/dev/null) || return 1
    
    # Check for error
    if echo "$response" | grep -q '"error"'; then
        local error
        error=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('error','Unknown error'))" 2>/dev/null)
        echo "Daemon error: $error" >&2
        return 1
    fi
    
    # Extract text
    echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('text',''))" 2>/dev/null
    return 0
}

# Fallback to mlx_whisper CLI with local models
try_direct() {
    export PATH="$PATH:$HOME/Library/Python/3.9/bin"
    local MODEL_PATH="$SCRIPT_DIR/mlx_models/medium"
    
    # Check for local model
    if [[ ! -d "$MODEL_PATH" ]]; then
        MODEL_PATH="$SCRIPT_DIR/mlx_models/medium"
    fi
    
    if [[ ! -d "$MODEL_PATH" ]]; then
        echo "Error: No local MLX model found in $SCRIPT_DIR/mlx_models/" >&2
        return 1
    fi
    
    local args=("$AUDIO_FILE" "--model" "$MODEL_PATH" "--output-format" "txt")
    
    if [[ "$TRANSLATE" == "true" ]]; then
        args+=("--task" "translate")
    fi
    
    if [[ -n "$LANGUAGE" ]]; then
        args+=("--language" "$LANGUAGE")
    fi
    
    # Run mlx_whisper and extract just the text
    local output
    output=$(mlx_whisper "${args[@]}" 2>&1)
    
    # Extract transcription lines (format: [00:00.000 --> 00:00.000] text)
    echo "$output" | sed -n 's/^\[.*\] //p' | tr '\n' ' ' | sed 's/  */ /g;s/^ *//;s/ *$//'
}

# Main
if try_daemon; then
    exit 0
fi

echo "Daemon unavailable, trying direct transcription..." >&2
try_direct
