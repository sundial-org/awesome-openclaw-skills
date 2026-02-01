#!/bin/bash
# Glasses-to-Social: Check for new photos in Google Drive folder
# Usage: ./check-new-photos.sh [config.json]

set -e

export PATH="$HOME/.local/bin:$PATH"

# Load config
CONFIG_FILE="${1:-./glasses-to-social/config.json}"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    exit 1
fi

FOLDER_URL=$(jq -r '.googleDriveFolderUrl' "$CONFIG_FILE")
DOWNLOAD_DIR=$(jq -r '.downloadPath' "$CONFIG_FILE")
PROCESSED_FILE=$(jq -r '.processedFile' "$CONFIG_FILE")

# Ensure directories exist
mkdir -p "$DOWNLOAD_DIR"
mkdir -p "$(dirname "$PROCESSED_FILE")"

# Initialize processed file if missing
if [ ! -f "$PROCESSED_FILE" ]; then
    echo '{"processed": [], "pending": []}' > "$PROCESSED_FILE"
fi

# Create temp dir for new downloads
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Download folder contents to temp
echo "Checking for new photos in: $FOLDER_URL"
gdown --folder "$FOLDER_URL" -O "$TEMP_DIR" --remaining-ok 2>&1 || true

# Find image files
NEW_FILES=$(find "$TEMP_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.heic" -o -iname "*.webp" \) 2>/dev/null || true)

if [ -z "$NEW_FILES" ]; then
    echo "No photos found in folder"
    exit 0
fi

# Get list of already processed files
PROCESSED=$(jq -r '.processed[]' "$PROCESSED_FILE" 2>/dev/null || echo "")

FOUND_NEW=0

# Check each file
for FILE in $NEW_FILES; do
    FILENAME=$(basename "$FILE")
    
    # Skip if already processed
    if echo "$PROCESSED" | grep -qF "$FILENAME"; then
        continue
    fi
    
    echo "NEW PHOTO FOUND: $FILENAME"
    
    # Copy to downloads folder
    cp "$FILE" "$DOWNLOAD_DIR/"
    
    # Output the path for processing
    echo "NEW_PHOTO_PATH:$DOWNLOAD_DIR/$FILENAME"
    FOUND_NEW=1
done

if [ "$FOUND_NEW" -eq 0 ]; then
    echo "No new photos (all already processed)"
fi
