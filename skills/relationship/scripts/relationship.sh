#!/bin/bash
# Camino AI Relationship API - Spatial Calculations
# Usage: ./relationship.sh '{"start": {"lat": 40.7128, "lon": -74.0060}, "end": {"lat": 40.7589, "lon": -73.9851}}'

set -e

# Check dependencies
for cmd in jq curl; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: '$cmd' is required but not installed" >&2
        exit 1
    fi
done

# Check if input is provided
if [ -z "$1" ]; then
    echo "Error: JSON input required" >&2
    echo "Usage: ./relationship.sh '{\"start\": {\"lat\": 40.7128, \"lon\": -74.0060}, \"end\": {\"lat\": 40.7589, \"lon\": -73.9851}}'" >&2
    exit 1
fi

INPUT="$1"

# Validate JSON
if ! echo "$INPUT" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON input" >&2
    exit 1
fi

# Check for API key
if [ -z "$CAMINO_API_KEY" ]; then
    echo "Error: CAMINO_API_KEY environment variable not set" >&2
    echo "Get your API key at https://app.getcamino.ai" >&2
    exit 1
fi

# Check for required fields
START=$(echo "$INPUT" | jq '.start // empty')
END=$(echo "$INPUT" | jq '.end // empty')

if [ "$START" = "null" ] || [ -z "$START" ]; then
    echo "Error: 'start' field with lat/lon is required" >&2
    exit 1
fi

if [ "$END" = "null" ] || [ -z "$END" ]; then
    echo "Error: 'end' field with lat/lon is required" >&2
    exit 1
fi

# Make API request
curl -s -X POST \
    -H "X-API-Key: $CAMINO_API_KEY" \
    -H "Content-Type: application/json" \
    -H "X-Client: claude-code-skill" \
    -d "$INPUT" \
    "https://api.getcamino.ai/relationship" | jq .
