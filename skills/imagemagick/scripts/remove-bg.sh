#!/usr/bin/env bash
#
# Remove solid background color from image to create transparent PNG
#
# Usage: ./remove-bg.sh <input.png> <output.png> [tolerance] [target_color]
#
# Args:
#   input.png      - Source image
#   output.png     - Output transparent PNG
#   tolerance      - Color matching tolerance (default: 20, range: 0-255)
#   target_color   - Color to remove (default: white "#FFFFFF")
#
# Examples:
#   ./remove-bg.sh icon.png icon-clean.png                    # remove white
#   ./remove-bg.sh icon.png icon-clean.png 30                 # loose tolerance
#   ./remove-bg.sh icon.png icon-clean.png 10 "#000000"       # remove black

set -euo pipefail

INPUT="${1:-}"
OUTPUT="${2:-}"
TOLERANCE="${3:-20}"
TARGET_COLOR="${4:-#FFFFFF}"

if [[ -z "$INPUT" || -z "$OUTPUT" ]]; then
    echo "Usage: $0 <input.png> <output.png> [tolerance] [target_color]"
    echo ""
    echo "Args:"
    echo "  input.png       Source image"
    echo "  output.png      Output transparent PNG"
    echo "  tolerance       Color matching tolerance (default: 20, range: 0-255)"
    echo "  target_color    Color to remove (default: white #FFFFFF)"
    echo ""
    echo "Examples:"
    echo "  $0 icon.png icon-clean.png"
    echo "  $0 icon.png icon-clean.png 30"
    echo "  $0 icon.png icon-clean.png 10 \"#000000\""
    exit 1
fi

if ! command -v convert &> /dev/null; then
    echo "Error: ImageMagick 'convert' not found."
    echo "Install with: brew install imagemagick (macOS) or apt install imagemagick (Linux)"
    exit 1
fi

if [[ ! -f "$INPUT" ]]; then
    echo "Error: Input file '$INPUT' not found"
    exit 1
fi

echo "Removing background color: $TARGET_COLOR with tolerance $TOLERANCE"
echo "Input: $INPUT → Output: $OUTPUT"

convert "$INPUT" \
    -fuzz "${TOLERANCE}%" \
    -fill none \
    -draw "color 0,0 floodfill" \
    "$OUTPUT"

echo "Done! Transparency saved to $OUTPUT"

# Show file size comparison
INPUT_SIZE=$(stat -f%z "$INPUT" 2>/dev/null || stat -c%s "$INPUT" 2>/dev/null)
OUTPUT_SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null)
echo "Size: $(($INPUT_SIZE / 1024))KB → $(($OUTPUT_SIZE / 1024))KB"
