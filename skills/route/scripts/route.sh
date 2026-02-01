#!/bin/bash
# Camino AI Route API - Point-to-Point Navigation
# Usage: ./route.sh '{"start_lat": 40.7128, "start_lon": -74.0060, "end_lat": 40.7589, "end_lon": -73.9851}'

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
    echo "Usage: ./route.sh '{\"start_lat\": 40.7128, \"start_lon\": -74.0060, \"end_lat\": 40.7589, \"end_lon\": -73.9851}'" >&2
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
START_LAT=$(echo "$INPUT" | jq -r '.start_lat // empty')
START_LON=$(echo "$INPUT" | jq -r '.start_lon // empty')
END_LAT=$(echo "$INPUT" | jq -r '.end_lat // empty')
END_LON=$(echo "$INPUT" | jq -r '.end_lon // empty')

if [ -z "$START_LAT" ] || [ -z "$START_LON" ]; then
    echo "Error: 'start_lat' and 'start_lon' are required" >&2
    exit 1
fi

if [ -z "$END_LAT" ] || [ -z "$END_LON" ]; then
    echo "Error: 'end_lat' and 'end_lon' are required" >&2
    exit 1
fi

# Build query string from JSON input
build_query_string() {
    local params="start_lat=${START_LAT}&start_lon=${START_LON}&end_lat=${END_LAT}&end_lon=${END_LON}"

    # Optional parameters
    local mode=$(echo "$INPUT" | jq -r '.mode // empty')
    local include_geometry=$(echo "$INPUT" | jq -r '.include_geometry // empty')
    local include_imagery=$(echo "$INPUT" | jq -r '.include_imagery // empty')

    [ -n "$mode" ] && params="${params}&mode=${mode}"
    [ -n "$include_geometry" ] && params="${params}&include_geometry=${include_geometry}"
    [ -n "$include_imagery" ] && params="${params}&include_imagery=${include_imagery}"

    echo "$params"
}

QUERY_STRING=$(build_query_string)

# Make API request
curl -s -X GET \
    -H "X-API-Key: $CAMINO_API_KEY" \
    -H "X-Client: claude-code-skill" \
    "https://api.getcamino.ai/route?${QUERY_STRING}" | jq .
