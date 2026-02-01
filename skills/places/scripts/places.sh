#!/bin/bash
# Camino AI Search API - Flexible Place Lookup
# Usage: ./search.sh '{"query": "Eiffel Tower"}' or ./search.sh '{"city": "Paris", "country": "France"}'

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
    echo "Usage: ./search.sh '{\"query\": \"Eiffel Tower\"}'" >&2
    echo "   or: ./search.sh '{\"street\": \"123 Main St\", \"city\": \"New York\"}'" >&2
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

# Check for at least one search parameter
QUERY=$(echo "$INPUT" | jq -r '.query // empty')
AMENITY=$(echo "$INPUT" | jq -r '.amenity // empty')
STREET=$(echo "$INPUT" | jq -r '.street // empty')
CITY=$(echo "$INPUT" | jq -r '.city // empty')
COUNTY=$(echo "$INPUT" | jq -r '.county // empty')
STATE=$(echo "$INPUT" | jq -r '.state // empty')
COUNTRY=$(echo "$INPUT" | jq -r '.country // empty')
POSTALCODE=$(echo "$INPUT" | jq -r '.postalcode // empty')

if [ -z "$QUERY" ] && [ -z "$AMENITY" ] && [ -z "$STREET" ] && [ -z "$CITY" ] && \
   [ -z "$COUNTY" ] && [ -z "$STATE" ] && [ -z "$COUNTRY" ] && [ -z "$POSTALCODE" ]; then
    echo "Error: At least one of 'query' or address components is required" >&2
    exit 1
fi

# Make API request
curl -s -X POST \
    -H "X-API-Key: $CAMINO_API_KEY" \
    -H "Content-Type: application/json" \
    -H "X-Client: claude-code-skill" \
    -d "$INPUT" \
    "https://api.getcamino.ai/search" | jq .
