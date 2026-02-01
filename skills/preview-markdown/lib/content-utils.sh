#!/usr/bin/env bash

#===============================================================================
# AUTO-GENERATED - DO NOT EDIT
#===============================================================================
# Source: src/core/lib/content-utils.sh
# To edit: Modify source file, then run: src/scripts/sync-skills.sh
#===============================================================================


# Content Utilities Library
# Functions for encoding, escaping, and processing content

# Constants
readonly MAX_CONTENT_SIZE=$((10 * 1024 * 1024))  # 10MB limit
readonly MAX_FILE_SIZE=$((50 * 1024 * 1024))     # 50MB file size limit
readonly MAX_DIFF_FILE_SIZE=$((1 * 1024 * 1024)) # 1MB limit for individual files in diff

#######################################
# Encode content as UTF-8 safe base64
# Reads from stdin, writes to stdout
# Arguments:
#   None
# Returns:
#   Base64 encoded content
#######################################
base64_encode_utf8() {
    base64 | tr -d '\n'
}

#######################################
# Decode UTF-8 safe base64 content
# Arguments:
#   $1 - Base64 encoded string
# Returns:
#   Decoded content
#######################################
base64_decode_utf8() {
    local encoded="$1"
    echo "$encoded" | base64 -d
}

#######################################
# Escape content for use in JavaScript string literals
# Reads from stdin, writes to stdout
# Arguments:
#   None
# Returns:
#   Escaped content safe for JS strings
#######################################
escape_for_js() {
    # Escape content for JavaScript strings using sed
    sed -e 's/\\/\\\\/g' \
        -e 's/"/\\"/g' \
        -e "s/'/\\\\'/g" \
        -e ':a' -e 'N' -e '$!ba' \
        -e 's/\n/\\n/g'
}

#######################################
# Escape content for use in HTML
# Arguments:
#   $1 - Content to escape
# Returns:
#   HTML-safe content
#######################################
escape_for_html() {
    local content="$1"
    echo "$content" | sed \
        -e 's/&/\&amp;/g' \
        -e 's/</\&lt;/g' \
        -e 's/>/\&gt;/g' \
        -e 's/"/\&quot;/g' \
        -e "s/'/\&#39;/g"
}

#######################################
# Escape string for safe use in HTML attributes/titles
# More aggressive escaping for untrusted filenames
# Arguments:
#   $1 - String to escape
# Returns:
#   Safe string for HTML context
#######################################
escape_filename_for_html() {
    local input="$1"
    # Remove or escape potentially dangerous characters
    # Allow only alphanumeric, spaces, dots, dashes, underscores
    echo "$input" | sed \
        -e 's/&/\&amp;/g' \
        -e 's/</\&lt;/g' \
        -e 's/>/\&gt;/g' \
        -e 's/"/\&quot;/g' \
        -e "s/'/\&#39;/g" \
        -e 's/`/\&#96;/g' \
        -e 's/\$/\&#36;/g'
}

#######################################
# Read stdin with size limit
# Arguments:
#   $1 - Maximum size in bytes (optional, defaults to MAX_CONTENT_SIZE)
# Returns:
#   Content from stdin
#   Exit code 1 if content exceeds limit
#######################################
read_with_limit() {
    local limit="${1:-$MAX_CONTENT_SIZE}"
    local content
    local size

    # Read all content
    content=$(cat)
    size=${#content}

    if [ "$size" -gt "$limit" ]; then
        echo "Error: Content size ($size bytes) exceeds limit ($limit bytes)" >&2
        return 1
    fi

    echo "$content"
}

#######################################
# Validate that content is valid UTF-8
# Arguments:
#   $1 - Content to validate
# Returns:
#   Exit code 0 if valid, 1 if invalid
#######################################
validate_utf8() {
    local content="$1"

    # Use iconv to validate UTF-8
    if ! echo "$content" | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1; then
        echo "Error: Content is not valid UTF-8" >&2
        return 1
    fi

    return 0
}

#######################################
# Get MIME type for file extension
# Arguments:
#   $1 - File extension (e.g., "md", "json", "mmd")
# Returns:
#   MIME type string
#######################################
get_mime_type() {
    local extension="$1"

    case "$extension" in
        md|markdown)
            echo "text/markdown"
            ;;
        json)
            echo "application/json"
            ;;
        mmd|mermaid)
            echo "text/x-mermaid"
            ;;
        html|htm)
            echo "text/html"
            ;;
        txt)
            echo "text/plain"
            ;;
        csv)
            echo "text/csv"
            ;;
        *)
            echo "application/octet-stream"
            ;;
    esac
}

#######################################
# Validate file size before processing
# Arguments:
#   $1 - File path
#   $2 - Maximum size in bytes (optional, defaults to MAX_FILE_SIZE)
# Returns:
#   Exit code 0 if valid, 1 if exceeds limit
#######################################
validate_file_size() {
    local file_path="$1"
    local max_size="${2:-$MAX_FILE_SIZE}"

    if [ ! -f "$file_path" ]; then
        echo "Error: File not found: $file_path" >&2
        return 1
    fi

    # Get file size
    local file_size
    if [[ "$OSTYPE" == "darwin"* ]]; then
        file_size=$(stat -f%z "$file_path" 2>/dev/null) || file_size=0
    else
        file_size=$(stat -c%s "$file_path" 2>/dev/null) || file_size=0
    fi

    if [ "$file_size" -gt "$max_size" ]; then
        echo "Error: File size ($file_size bytes) exceeds limit ($max_size bytes)" >&2
        return 1
    fi

    return 0
}

#######################################
# Check if file is binary
# Arguments:
#   $1 - File path
# Returns:
#   Exit code 0 if binary, 1 if text
#######################################
is_binary_file() {
    local file_path="$1"

    if [ ! -f "$file_path" ]; then
        return 1
    fi

    # Use file command if available
    if command -v file >/dev/null 2>&1; then
        if file "$file_path" | grep -q "text"; then
            return 1  # Text file
        else
            return 0  # Binary file
        fi
    fi

    # Fallback: check for null bytes in first 8KB
    if head -c 8192 "$file_path" | grep -q $'\0'; then
        return 0  # Binary
    fi

    return 1  # Text
}

#######################################
# Read file safely with size and content validation
# Arguments:
#   $1 - File path
#   $2 - Maximum size in bytes (optional)
# Returns:
#   File content
#   Exit code 1 if file is invalid or too large
#######################################
read_file_safely() {
    local file_path="$1"
    local max_size="${2:-$MAX_FILE_SIZE}"

    # Validate file exists and size
    validate_file_size "$file_path" "$max_size" || return 1

    # Check if binary
    if is_binary_file "$file_path"; then
        echo "Error: File appears to be binary: $file_path" >&2
        return 1
    fi

    # Read file content
    cat "$file_path"
}
