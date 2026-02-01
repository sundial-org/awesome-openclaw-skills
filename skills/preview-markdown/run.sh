#!/usr/bin/env bash

#===============================================================================
# AUTO-GENERATED - DO NOT EDIT
#===============================================================================
# Source: src/preview-skills/run.sh
# To edit: Modify source file, then run: src/scripts/sync-skills.sh
#===============================================================================


# Universal Preview Tool
# Usage: ./run.sh <file> [-o output] [--no-browser]
#    OR: cat content | ./run.sh [name] [-o output] [--no-browser]
#
# Options:
#   -o, --output    Output file path or directory (default: /tmp/preview-skills/)
#   --no-browser    Skip opening browser, just output file path

set -euo pipefail

# Parse options
OUTPUT_PATH=""
NO_BROWSER=0
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        --no-browser)
            NO_BROWSER=1
            shift
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

set -- "${POSITIONAL_ARGS[@]:-}"

# Get directories (standalone skill)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$SCRIPT_DIR"
LIB_ROOT="$SKILL_ROOT"

# Source shared libraries
source "$LIB_ROOT/lib/content-utils.sh"
source "$LIB_ROOT/lib/browser-utils.sh"
source "$LIB_ROOT/lib/html-generator.sh"

# Load tool configuration
source "$SCRIPT_DIR/config.sh"

# Default functions (can be overridden in config.sh)
validate_content() {
    return 0  # No validation by default
}

preprocess_content() {
    echo "$1"  # Return content unchanged by default
}

get_additional_params() {
    echo ""  # No additional params by default
}

# Check if first argument is a file
if [ -f "${1:-}" ]; then
    SOURCE_FILE="$1"

    # Validate file path for security
    validate_file_path "$SOURCE_FILE" "$(pwd)" || exit 1

    # Extract filename (remove any of the configured extensions)
    FILENAME="$(basename "$SOURCE_FILE")"
    for ext in "${FILE_EXTENSIONS[@]}"; do
        FILENAME="${FILENAME%"$ext"}"
    done

    # Get additional parameters (background color, theme, etc.)
    shift
    ADDITIONAL_PARAMS=$(get_additional_params "$@")

    # Validate file size
    validate_file_size "$SOURCE_FILE" "$MAX_CONTENT_SIZE" || exit 1

    CONTENT=$(cat "$SOURCE_FILE")
else
    FILENAME="${1:-$DEFAULT_FILENAME}"

    # Get additional parameters
    shift || true
    ADDITIONAL_PARAMS=$(get_additional_params "$@")

    # Read stdin with size limit
    CONTENT=$(read_with_limit "$MAX_CONTENT_SIZE") || exit 1
fi

# Validate content (tool-specific)
validate_content "$CONTENT" || exit 1

# Preprocess content (tool-specific - may add metadata, detect types, etc.)
CONTENT=$(preprocess_content "$CONTENT")

# Encode content based on configuration
if [ "$CONTENT_ENCODING" = "base64" ]; then
    CONTENT_ENCODED=$(echo "$CONTENT" | base64_encode_utf8)
else
    CONTENT_ENCODED="$CONTENT"
fi

# Load renderer script and substitute variables
RENDER_SCRIPT=$(cat "$LIB_ROOT/$RENDERER_FILE")

# Perform variable substitutions defined in config
# Convention:
#   - Variables ending in _ENCODED, _DATA, _CONTENT, _CODE → content variables
#   - Other variables → parameter variables (use shell var with same name if exists)
if [ ${#RENDERER_VARS[@]} -gt 0 ]; then
    for var in "${RENDERER_VARS[@]}"; do
        # Check if this is a content variable (ends with _ENCODED, _DATA, _CONTENT, or _CODE)
        if [[ "$var" =~ _(ENCODED|DATA|CONTENT|CODE)$ ]]; then
            # Content variable - use CONTENT_ENCODED or CONTENT based on encoding
            if [ "$CONTENT_ENCODING" = "base64" ]; then
                RENDER_SCRIPT="${RENDER_SCRIPT//$var/$CONTENT_ENCODED}"
            else
                RENDER_SCRIPT="${RENDER_SCRIPT//$var/$CONTENT}"
            fi
        else
            # Parameter variable - check if a shell variable with this name exists
            if [ -n "${!var:-}" ]; then
                # Use the value of the shell variable with the same name
                RENDER_SCRIPT="${RENDER_SCRIPT//$var/${!var}}"
            else
                # No shell variable found - leave as-is or use empty string
                echo "Warning: No value found for renderer variable: $var" >&2
            fi
        fi
    done
fi

# Generate output file path
OUTPUT_FILE=$(get_output_file_path "$TOOL_NAME" "$FILENAME" "$OUTPUT_PATH")

# Load common JavaScript libraries
UTILS_JS=$(cat "$LIB_ROOT/templates/scripts/utils.js")
COMMON_UI=$(cat "$LIB_ROOT/templates/scripts/common-ui.js")
COMMON_JS="${UTILS_JS}

${COMMON_UI}"

# Set up HTML generation environment
# Escape filename to prevent HTML injection via malicious filenames
SAFE_FILENAME=$(escape_filename_for_html "$FILENAME")
export HTML_TITLE="${TOOL_TITLE_PREFIX} - ${SAFE_FILENAME}"

# Handle CDN scripts array
if [ ${#CDN_SCRIPTS[@]} -gt 0 ]; then
    export HTML_CDN_SCRIPTS=("${CDN_SCRIPTS[@]}")
else
    export HTML_CDN_SCRIPTS=()
fi

export HTML_STYLE_FILES=("${STYLE_FILES[@]}")
export HTML_LAYOUT="$LAYOUT_TYPE"
export HTML_BACKGROUND="${BACKGROUND_COLOR}"
export HTML_COMMON_JS="$COMMON_JS"
export HTML_CUSTOM_JS="$RENDER_SCRIPT"
export HTML_OUTPUT="$OUTPUT_FILE"

# Handle user code template for interactive tools (D3, ThreeJS, Leaflet)
if [ "${NEEDS_USER_CODE_TEMPLATE:-0}" = "1" ]; then
    # Write user code to separate JavaScript file
    USER_CODE_FILE="${OUTPUT_FILE%.html}-user.js"

    cat > "$USER_CODE_FILE" <<'USERCODE'
/* eslint-disable no-unused-vars */
// User code - executes when dynamically loaded
USERCODE
    echo "$CONTENT" >> "$USER_CODE_FILE"
    chmod 644 "$USER_CODE_FILE"

    # Get filename for script src attribute
    USER_CODE_FILENAME=$(basename "$USER_CODE_FILE")

    # Generate metadata (empty by default, can be overridden in config)
    METADATA_JSON="${METADATA_JSON:-{}}"

    # Validate METADATA_JSON is valid JSON and escape for template safety
    # Prevent envsubst injection by ensuring no unescaped $ characters in values
    if ! echo "$METADATA_JSON" | grep -qE '^\s*\{.*\}\s*$'; then
        echo "Warning: Invalid METADATA_JSON format, using empty object" >&2
        METADATA_JSON="{}"
    fi

    # Export variables for envsubst template substitution
    export TOOL_NAME
    export METADATA_JSON
    export USER_CODE_SRC="$USER_CODE_FILENAME"

    # Generate HTML content using envsubst
    HTML_CONTENT=$(envsubst < "$LIB_ROOT/templates/user-code-template.html")
    export HTML_CONTENT
else
    export HTML_CONTENT='        <div id="content"></div>'
fi

# Generate HTML
generate_html

echo "Preview created: $OUTPUT_FILE"

# Open in browser (unless --no-browser flag is set)
if [ "$NO_BROWSER" != "1" ]; then
    open_in_browser "$OUTPUT_FILE"
fi
