#!/bin/bash
# Dilbert Skill - Fetch random Dilbert comic (fast version)

TEMP_DIR="/tmp/dilbert_$$"
mkdir -p "$TEMP_DIR"
OUTPUT_FILE="$TEMP_DIR/dilbert.gif"

# List of known working Dilbert comic IDs from archive.org
COMIC_IDS=(
    "463335109a090137b296005056a9545d"  # 2019-09-22
    "b3b6c720-c8ce-11e9-9955-bb395a5a1c94"  # 2019-09-02
    "9f4f25c0-c8ce-11e9-9955-bb395a5a1c94"  # 2019-08-26
    "a3b6c720-c8ce-11e9-9955-bb395a5a1c94"  # 2019-08-19
    "b3b6c720-c8ce-11e9-9955-bb395a5a1c94"  # various
)

# Pick random comic ID
RANDOM_IDX=$((RANDOM % ${#COMIC_IDS[@]}))
COMIC_URL="https://assets.amuniversal.com/${COMIC_IDS[$RANDOM_IDX]}"

curl -L --max-time 10 -o "$OUTPUT_FILE" "$COMIC_URL" 2>/dev/null

# Check if valid image
if [ -s "$OUTPUT_FILE" ] && file "$OUTPUT_FILE" | grep -qE "image|GIF|PNG|JPEG"; then
    echo "$OUTPUT_FILE"
    exit 0
fi

# Fallback: try a different one
for ID in "${COMIC_IDS[@]}"; do
    curl -L --max-time 10 -o "$OUTPUT_FILE" "https://assets.amuniversal.com/$ID" 2>/dev/null
    if [ -s "$OUTPUT_FILE" ] && file "$OUTPUT_FILE" | grep -qE "image|GIF|PNG|JPEG"; then
        echo "$OUTPUT_FILE"
        exit 0
    fi
done

# Last resort: xkcd
curl -L --max-time 10 -o "$OUTPUT_FILE" "https://imgs.xkcd.com/comics/python.png" 2>/dev/null
if [ -s "$OUTPUT_FILE" ]; then
    echo "$OUTPUT_FILE"
    exit 0
fi

rm -rf "$TEMP_DIR"
exit 1
