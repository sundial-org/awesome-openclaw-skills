#!/bin/bash
# Memory Bridge: Fetch Graphiti context for council topic

TOPIC="$1"
MAX_FACTS="${2:-10}"

if [ -z "$TOPIC" ]; then
    echo "Usage: graphiti-bridge.sh <topic> [max_facts]" >&2
    exit 1
fi

# Get Graphiti URL from env-check
source "$(dirname "$0")/env-check.sh"

# Search Graphiti for relevant facts
FACTS=$(curl -s -X POST "$GRAPHITI_URL/facts/search" \
  -H 'Content-Type: application/json' \
  -d "{\"query\": \"$TOPIC\", \"max_facts\": $MAX_FACTS}")

# Format facts for injection into system prompt
if [ -n "$FACTS" ]; then
    echo "=== Relevant Context from Knowledge Graph ==="
    echo "$FACTS" | jq -r '.facts[]? | "- " + .fact' 2>/dev/null || echo "$FACTS"
    echo "============================================="
else
    echo "No relevant context found in knowledge graph."
fi
