#!/bin/bash
# Graphiti Environment Discovery

# Try Clawdbot config first
GRAPHITI_URL=$(clawdbot config get skills.graphiti.baseUrl 2>/dev/null || echo "")

# Fallback to environment variable
GRAPHITI_URL=${GRAPHITI_URL:-"http://localhost:8001"}

# Verify service is reachable
if curl -sf "$GRAPHITI_URL/health" > /dev/null 2>&1; then
    echo "$GRAPHITI_URL"
    exit 0
else
    echo "ERROR: Graphiti not reachable at $GRAPHITI_URL" >&2
    exit 1
fi
