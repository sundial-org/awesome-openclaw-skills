#!/bin/bash
# Mark a photo as processed
# Usage: ./mark-processed.sh <filename> [config.json]

set -e

FILENAME="$1"
CONFIG_FILE="${2:-./glasses-to-social/config.json}"

if [ -z "$FILENAME" ]; then
    echo "Usage: $0 <filename> [config.json]"
    exit 1
fi

PROCESSED_FILE=$(jq -r '.processedFile' "$CONFIG_FILE")

# Add to processed list
jq --arg f "$FILENAME" '.processed += [$f]' "$PROCESSED_FILE" > "${PROCESSED_FILE}.tmp"
mv "${PROCESSED_FILE}.tmp" "$PROCESSED_FILE"

echo "Marked as processed: $FILENAME"
