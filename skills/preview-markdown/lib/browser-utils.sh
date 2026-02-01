#!/usr/bin/env bash

#===============================================================================
# AUTO-GENERATED - DO NOT EDIT
#===============================================================================
# Source: src/core/lib/browser-utils.sh
# To edit: Modify source file, then run: src/scripts/sync-skills.sh
#===============================================================================


# Browser Utilities Library
# Functions for opening browsers and managing temp files

# Constants
readonly TEMP_DIR="/tmp/preview-skills"
readonly TEMP_FILE_PREFIX="preview"

#######################################
# Initialize secure temp directory
# Creates /tmp/preview-skills with proper permissions
# Returns:
#   Exit code 0 on success, 1 on failure
#######################################
init_temp_dir() {
    # Create temp directory if it doesn't exist
    if [ ! -d "$TEMP_DIR" ]; then
        if ! mkdir -p "$TEMP_DIR" 2>/dev/null; then
            echo "Error: Failed to create temp directory: $TEMP_DIR" >&2
            return 1
        fi
        # Set restrictive permissions (owner only)
        chmod 700 "$TEMP_DIR" 2>/dev/null || true
    fi

    # Verify directory is secure
    if [ ! -d "$TEMP_DIR" ] || [ ! -w "$TEMP_DIR" ]; then
        echo "Error: Temp directory not accessible: $TEMP_DIR" >&2
        return 1
    fi

    return 0
}

#######################################
# Validate file path for security
# Prevents path traversal and ensures file is in allowed locations
# Arguments:
#   $1 - File path to validate
#   $2 - Optional base directory (defaults to current directory)
# Environment:
#   PREVIEW_ALLOW_EXTERNAL_FILES - Set to "1" to allow files outside base dir (default: 1)
#   PREVIEW_ALLOW_SYMLINKS - Set to "1" to allow symlinks (default: 0)
# Returns:
#   Exit code 0 if valid, 1 if invalid
#######################################
validate_file_path() {
    local file_path="$1"
    local base_dir="${2:-.}"
    local allow_external="${PREVIEW_ALLOW_EXTERNAL_FILES:-1}"
    local allow_symlinks="${PREVIEW_ALLOW_SYMLINKS:-0}"

    # Check if file exists
    if [ ! -f "$file_path" ]; then
        echo "Error: File not found: $file_path" >&2
        return 1
    fi

    # Check if file is a symbolic link
    if [ -L "$file_path" ]; then
        if [ "$allow_symlinks" != "1" ]; then
            echo "Error: Symbolic links are not allowed for security: $file_path" >&2
            echo "Set PREVIEW_ALLOW_SYMLINKS=1 to override this restriction." >&2
            return 1
        else
            echo "Warning: File is a symbolic link: $file_path" >&2
        fi
    fi

    # Get absolute paths and validate location
    if command -v realpath >/dev/null 2>&1; then
        local abs_file
        local abs_base

        abs_file=$(realpath "$file_path" 2>/dev/null) || return 1
        abs_base=$(realpath "$base_dir" 2>/dev/null) || abs_base="$base_dir"

        # Check if file is under base directory (prevent path traversal)
        if [[ "$abs_file" != "$abs_base"* ]]; then
            if [ "$allow_external" != "1" ]; then
                echo "Error: Access denied - file is outside allowed directory: $file_path" >&2
                echo "File location: $abs_file" >&2
                echo "Allowed base: $abs_base" >&2
                echo "Set PREVIEW_ALLOW_EXTERNAL_FILES=1 to override this restriction." >&2
                return 1
            fi
            # No warning when external files are explicitly allowed
        fi
    else
        # Fallback: check for path traversal patterns when realpath is unavailable
        # This is a basic check that catches common traversal attempts
        if [[ "$file_path" == *".."* ]]; then
            echo "Error: Path contains '..' which may indicate path traversal: $file_path" >&2
            return 1
        fi
        # Check for absolute paths outside base when external files not allowed
        if [ "$allow_external" != "1" ]; then
            if [[ "$file_path" == /* ]] && [[ "$file_path" != "$base_dir"* ]]; then
                echo "Warning: Cannot fully validate path without realpath command" >&2
            fi
        fi
    fi

    return 0
}

#######################################
# Open file in default browser
# Arguments:
#   $1 - Path to file to open
# Returns:
#   Exit code 0 on success
# Note: Tab reuse works automatically since we use same /tmp filename
#######################################
open_in_browser() {
    local file_path="$1"

    if [ ! -f "$file_path" ]; then
        echo "Error: File not found: $file_path" >&2
        return 1
    fi

    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$file_path"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "$file_path" 2>/dev/null || true
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        start "$file_path"
    else
        echo "Error: Unsupported operating system: $OSTYPE" >&2
        return 1
    fi

    return 0
}

#######################################
# Generate temp file path for preview
# Arguments:
#   $1 - Skill name (e.g., "markdown", "mermaid")
#   $2 - Filename (e.g., "document", "diagram")
# Returns:
#   Path to temp file (e.g., "/tmp/preview-skills/preview-markdown-document.html")
#######################################
get_temp_file_path() {
    local skill_name="$1"
    local filename="$2"

    # Initialize temp directory
    init_temp_dir || return 1

    # Sanitize skill name and filename (remove special chars, keep alphanumeric, dashes, underscores)
    local safe_skill
    local safe_filename
    safe_skill=$(echo "$skill_name" | sed 's/[^a-zA-Z0-9_-]/-/g' | cut -c1-50)
    safe_filename=$(echo "$filename" | sed 's/[^a-zA-Z0-9_-]/-/g' | cut -c1-100)

    # Ensure we don't have empty names
    [ -z "$safe_skill" ] && safe_skill="unknown"
    [ -z "$safe_filename" ] && safe_filename="file"

    echo "${TEMP_DIR}/${TEMP_FILE_PREFIX}-${safe_skill}-${safe_filename}.html"
}

#######################################
# Get output file path (custom or temp)
# Arguments:
#   $1 - Skill name (e.g., "markdown", "mermaid")
#   $2 - Filename (e.g., "document", "diagram")
#   $3 - Custom output path (optional, can be file or directory)
# Returns:
#   Path to output file
#######################################
get_output_file_path() {
    local skill_name="$1"
    local filename="$2"
    local custom_output="${3:-}"

    if [ -z "$custom_output" ]; then
        get_temp_file_path "$skill_name" "$filename"
        return
    fi

    local safe_filename
    safe_filename=$(echo "$filename" | sed 's/[^a-zA-Z0-9_-]/-/g' | cut -c1-100)
    [ -z "$safe_filename" ] && safe_filename="file"

    if [ -d "$custom_output" ]; then
        echo "${custom_output%/}/${safe_filename}.html"
        return
    fi

    if [[ "$custom_output" == */ ]]; then
        mkdir -p "$custom_output" 2>/dev/null || {
            echo "Error: Cannot create directory: $custom_output" >&2
            return 1
        }
        echo "${custom_output%/}/${safe_filename}.html"
        return
    fi

    local parent_dir
    parent_dir=$(dirname "$custom_output")
    if [ ! -d "$parent_dir" ]; then
        mkdir -p "$parent_dir" 2>/dev/null || {
            echo "Error: Cannot create directory: $parent_dir" >&2
            return 1
        }
    fi

    if [[ "$custom_output" != *.html ]]; then
        echo "${custom_output}.html"
    else
        echo "$custom_output"
    fi
}

#######################################
# Clean up old preview files
# Arguments:
#   $1 - Skill name (optional, cleans all if not specified)
#   $2 - Age in minutes (optional, defaults to 60)
# Returns:
#   Number of files removed
#######################################
cleanup_old_previews() {
    local skill_name="${1:-*}"
    local age_minutes="${2:-60}"
    local pattern="${TEMP_DIR}/${TEMP_FILE_PREFIX}-${skill_name}-*.html"
    local count=0

    # Find and remove files older than specified age
    if command -v find >/dev/null 2>&1; then
        # Use find command if available (more precise)
        while IFS= read -r file; do
            rm -f "$file"
            ((count++))
        done < <(find "$TEMP_DIR" -name "${TEMP_FILE_PREFIX}-${skill_name}-*.html" -type f -mmin "+${age_minutes}" 2>/dev/null)
    fi

    echo "$count"
}

#######################################
# Get list of active preview files
# Arguments:
#   $1 - Skill name (optional, lists all if not specified)
# Returns:
#   List of preview file paths
#######################################
list_preview_files() {
    local skill_name="${1:-*}"
    local pattern="${TEMP_DIR}/${TEMP_FILE_PREFIX}-${skill_name}-*.html"

    # List matching files
    # shellcheck disable=SC2086
    ls -t $pattern 2>/dev/null || true
}

#######################################
# Check if browser command is available
# Returns:
#   Exit code 0 if browser can be opened, 1 otherwise
#######################################
check_browser_available() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        command -v open >/dev/null 2>&1
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        command -v xdg-open >/dev/null 2>&1
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        command -v start >/dev/null 2>&1
    else
        return 1
    fi
}

#######################################
# Future: Start live server for preview
# Arguments:
#   $1 - Port number (default: 8765)
#   $2 - Source file to watch
# Returns:
#   Server PID
# Note: Not yet implemented, placeholder for future enhancement
#######################################
start_live_server() {
    local port="${1:-8765}"
    local source_file="$2"

    echo "Error: Live server not yet implemented" >&2
    return 1
}

#######################################
# Future: Watch file for changes
# Arguments:
#   $1 - File to watch
#   $2 - Callback command to execute on change
# Returns:
#   Watcher PID
# Note: Not yet implemented, placeholder for future enhancement
#######################################
watch_file() {
    local file="$1"
    local callback="$2"

    echo "Error: File watching not yet implemented" >&2
    return 1
}
