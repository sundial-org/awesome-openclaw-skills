#!/usr/bin/env bash
# Tabstack API wrapper using curl (no Python dependencies)
# Usage: ./tabstack_curl.sh <command> [args]

set -euo pipefail

TABSTACK_BASE_URL="https://api.tabstack.ai/v1"
API_KEY="${TABSTACK_API_KEY:-}"

if [[ -z "$API_KEY" ]]; then
    echo "Error: TABSTACK_API_KEY environment variable not set"
    echo "Set it with: export TABSTACK_API_KEY=\"your_key_here\""
    exit 1
fi

test_connection() {
    echo "Testing Tabstack API connection..."
    if curl -s -X GET "${TABSTACK_BASE_URL}/" \
        -H "Authorization: Bearer ${API_KEY}" \
        -H "Content-Type: application/json" \
        --max-time 10 > /dev/null 2>&1; then
        echo "✅ Tabstack API connection successful"
        return 0
    else
        echo "❌ Tabstack API connection failed"
        return 1
    fi
}

extract_markdown() {
    local url="$1"
    echo "Extracting markdown from: $url"
    
    curl -s -X POST "${TABSTACK_BASE_URL}/extract/markdown" \
        -H "Authorization: Bearer ${API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$url\"}" \
        --max-time 30
}

extract_json() {
    local url="$1"
    local schema_file="$2"
    
    echo "Extracting JSON from: $url"
    echo "Using schema: $schema_file"
    
    # Read schema file
    if [[ ! -f "$schema_file" ]]; then
        echo "Error: Schema file not found: $schema_file"
        exit 1
    fi
    
    local schema
    schema=$(cat "$schema_file")
    
    curl -s -X POST "${TABSTACK_BASE_URL}/extract/json" \
        -H "Authorization: Bearer ${API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$url\", \"json_schema\": $schema}" \
        --max-time 30
}

# Main command handling
case "${1:-}" in
    "test")
        test_connection
        ;;
    "markdown")
        if [[ $# -lt 2 ]]; then
            echo "Usage: $0 markdown <url>"
            exit 1
        fi
        extract_markdown "$2"
        ;;
    "json")
        if [[ $# -lt 3 ]]; then
            echo "Usage: $0 json <url> <schema_file.json>"
            exit 1
        fi
        extract_json "$2" "$3"
        ;;
    *)
        echo "Usage: $0 <command> [args]"
        echo "Commands:"
        echo "  test                 - Test API connection"
        echo "  markdown <url>       - Extract markdown from URL"
        echo "  json <url> <schema>  - Extract JSON using schema file"
        exit 1
        ;;
esac