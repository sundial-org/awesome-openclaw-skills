#!/bin/bash
# Camino AI Journey API - Multi-Stop Planning
# Usage: ./journey.sh '{"waypoints": [{"lat": 40.7128, "lon": -74.0060, "purpose": "Start"}, {"lat": 40.7484, "lon": -73.9857, "purpose": "Empire State"}]}'

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
    echo "Usage: ./journey.sh '{\"waypoints\": [{\"lat\": 40.7128, \"lon\": -74.0060, \"purpose\": \"Start\"}, {\"lat\": 40.7484, \"lon\": -73.9857, \"purpose\": \"End\"}]}'" >&2
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

# Check for required field
WAYPOINTS=$(echo "$INPUT" | jq '.waypoints // empty')
WAYPOINT_COUNT=$(echo "$INPUT" | jq '.waypoints | length // 0')

if [ "$WAYPOINTS" = "null" ] || [ -z "$WAYPOINTS" ]; then
    echo "Error: 'waypoints' array is required" >&2
    exit 1
fi

if [ "$WAYPOINT_COUNT" -lt 2 ]; then
    echo "Error: At least 2 waypoints are required" >&2
    exit 1
fi

# Make API request
curl -s -X POST \
    -H "X-API-Key: $CAMINO_API_KEY" \
    -H "Content-Type: application/json" \
    -H "X-Client: claude-code-skill" \
    -d "$INPUT" \
    "https://api.getcamino.ai/journey" | jq .
