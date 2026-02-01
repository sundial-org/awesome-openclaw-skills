#!/usr/bin/env bash

#===============================================================================
# AUTO-GENERATED - DO NOT EDIT
#===============================================================================
# Source: src/core/lib/html-generator.sh
# To edit: Modify source file, then run: src/scripts/sync-skills.sh
#===============================================================================


# HTML Generator Library
# Core HTML generation functions

# Get the library root directory
if [ -z "$LIB_ROOT" ]; then
    LIB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

# Allowed CDN domains (whitelist)
readonly ALLOWED_CDN_DOMAINS=(
    "cdn.jsdelivr.net"
    "cdnjs.cloudflare.com"
    "unpkg.com"
    "fonts.googleapis.com"
    "fonts.gstatic.com"
)

# Security setting: require SRI hashes for all CDN resources
# Set to "1" to enforce SRI (recommended for production)
# Set to "0" to allow CDN resources without SRI (for development only)
REQUIRE_SRI_HASHES="${REQUIRE_SRI_HASHES:-1}"

#######################################
# Validate CDN URL against whitelist
# Arguments:
#   $1 - URL to validate
# Returns:
#   Exit code 0 if valid, 1 if invalid
#######################################
validate_cdn_url() {
    local url="$1"

    # Check if URL starts with https://
    if [[ ! "$url" =~ ^https:// ]]; then
        echo "Warning: CDN URL must use HTTPS: $url" >&2
        return 1
    fi

    # Extract domain from URL
    local domain
    domain=$(echo "$url" | sed -E 's|^https://([^/]+).*|\1|')

    # Check if domain is in whitelist
    for allowed_domain in "${ALLOWED_CDN_DOMAINS[@]}"; do
        if [[ "$domain" == "$allowed_domain" ]]; then
            return 0
        fi
    done

    echo "Warning: CDN domain not in whitelist: $domain" >&2
    return 1
}

#######################################
# Load CSS content from file or return import for CDN URL
# Arguments:
#   $1 - Path to CSS file (absolute, relative to LIB_ROOT, CDN URL, or URL::INTEGRITY)
# Returns:
#   CSS content or link tag for CDN with SRI
#######################################
load_css() {
    local css_entry="$1"

    # Check if it's a CDN URL with optional SRI hash
    if [[ "$css_entry" =~ ^https?:// ]]; then
        # Parse URL and optional integrity hash
        local css_url="${css_entry%%::*}"
        local integrity="${css_entry#*::}"

        # If no :: delimiter, integrity will equal css_url
        if [ "$integrity" == "$css_url" ]; then
            integrity=""
        fi

        # Validate and return appropriate format
        if [ -n "$integrity" ]; then
            # Return marker for later processing in generate_html
            echo "CDN_LINK::${css_url}::${integrity}"
        elif [ "$REQUIRE_SRI_HASHES" = "1" ]; then
            echo "Error: CDN stylesheet without SRI hash (REQUIRE_SRI_HASHES=1): $css_url" >&2
            echo "Add SRI hash using format: URL::sha384-HASH" >&2
            return 1
        else
            echo "Warning: CDN stylesheet without SRI hash: $css_url" >&2
            echo "@import url('$css_url');"
        fi
        return 0
    fi

    # Local file path
    local css_path="$css_entry"

    # Check if path is absolute
    if [[ "$css_path" != /* ]]; then
        css_path="$LIB_ROOT/$css_path"
    fi

    if [ -f "$css_path" ]; then
        cat "$css_path"
    else
        echo "/* Warning: CSS file not found: $css_path */" >&2
    fi
}

#######################################
# Load JavaScript content from file
# Arguments:
#   $1 - Path to JS file (absolute or relative to LIB_ROOT)
# Returns:
#   JavaScript content
#######################################
load_js() {
    local js_path="$1"

    # Check if path is absolute
    if [[ "$js_path" != /* ]]; then
        js_path="$LIB_ROOT/$js_path"
    fi

    if [ -f "$js_path" ]; then
        cat "$js_path"
    else
        echo "// Warning: JS file not found: $js_path" >&2
    fi
}

#######################################
# Merge multiple CSS files
# Arguments:
#   $@ - Paths to CSS files
# Returns:
#   Combined output with format:
#     CDN_LINKS_START
#     <link tags>
#     CDN_LINKS_END
#     <css content>
#######################################
merge_styles() {
    local imports=""
    local styles=""
    local cdn_links=""

    # Process all CSS files
    for css_file in "$@"; do
        if [ -n "$css_file" ]; then
            local css_content
            css_content=$(load_css "$css_file")

            # Check for CDN_LINK marker
            if [[ "$css_content" =~ ^CDN_LINK:: ]]; then
                # Extract URL and integrity
                local url="${css_content#CDN_LINK::}"
                local cdn_url="${url%%::*}"
                local integrity="${url#*::}"

                # Generate link tag
                cdn_links+="    <link rel=\"stylesheet\" href=\"${cdn_url}\" integrity=\"${integrity}\" crossorigin=\"anonymous\" referrerpolicy=\"no-referrer\">"
                cdn_links+=$'\n'
            # Separate @import rules from regular styles
            elif [[ "$css_content" =~ ^@import ]]; then
                imports+="$css_content"
                imports+=$'\n'
            else
                styles+="$css_content"
                styles+=$'\n'
            fi
        fi
    done

    # Return CDN links and styles in parseable format
    echo "CDN_LINKS_START"
    echo -n "$cdn_links"
    echo "CDN_LINKS_END"
    echo -n "${imports}${styles}"
}

#######################################
# Generate CDN script tags
# Arguments:
#   $@ - CDN URLs or URL::INTEGRITY pairs
# Returns:
#   HTML script tags with SRI hashes
# Format:
#   - Simple URL: https://cdn.example.com/lib.js
#   - With SRI: https://cdn.example.com/lib.js::sha384-HASH
#######################################
generate_cdn_scripts() {
    local scripts=""

    for cdn_entry in "$@"; do
        if [ -n "$cdn_entry" ]; then
            # Parse URL and optional integrity hash
            local cdn_url="${cdn_entry%%::*}"
            local integrity="${cdn_entry#*::}"

            # If no :: delimiter, integrity will equal cdn_url
            if [ "$integrity" == "$cdn_url" ]; then
                integrity=""
            fi

            # Validate CDN URL before adding
            if validate_cdn_url "$cdn_url"; then
                if [ -n "$integrity" ]; then
                    scripts+="    <script src=\"${cdn_url}\" integrity=\"${integrity}\" crossorigin=\"anonymous\" referrerpolicy=\"no-referrer\"></script>"
                    scripts+=$'\n'
                elif [ "$REQUIRE_SRI_HASHES" = "1" ]; then
                    echo "Error: CDN script without SRI hash (REQUIRE_SRI_HASHES=1): $cdn_url" >&2
                    echo "Add SRI hash using format: URL::sha384-HASH" >&2
                    return 1
                else
                    echo "Warning: CDN script without SRI hash: $cdn_url" >&2
                    scripts+="    <script src=\"${cdn_url}\" crossorigin=\"anonymous\" referrerpolicy=\"no-referrer\"></script>"
                    scripts+=$'\n'
                fi
            else
                echo "Error: Invalid CDN URL rejected: $cdn_url" >&2
                return 1
            fi
        fi
    done

    echo "$scripts"
}

#######################################
# Generate complete HTML document
# Uses environment variables:
#   HTML_TITLE - Page title
#   HTML_CDN_SCRIPTS - Array of CDN script URLs
#   HTML_STYLE_FILES - Array of CSS file paths
#   HTML_CUSTOM_STYLES - Inline CSS string
#   HTML_LAYOUT - Layout type (document, centered, full)
#   HTML_BACKGROUND - Background color
#   HTML_CONTENT - Content HTML
#   HTML_COMMON_JS - Common JavaScript
#   HTML_CUSTOM_JS - Custom JavaScript (render script)
#   HTML_OUTPUT - Output file path
# Returns:
#   Generates HTML file
#######################################
generate_html() {
    local title="${HTML_TITLE:-Preview}"
    local layout="${HTML_LAYOUT:-document}"
    local background="${HTML_BACKGROUND:-#f5f5f5}"
    local output="${HTML_OUTPUT:-/tmp/preview.html}"

    # Generate CDN script tags
    local cdn_scripts=""
    if [ ${#HTML_CDN_SCRIPTS[@]} -gt 0 ]; then
        cdn_scripts=$(generate_cdn_scripts "${HTML_CDN_SCRIPTS[@]}")
    fi

    # Merge CSS files and extract CDN links
    local combined_styles=""
    local cdn_css_links=""

    if [ ${#HTML_STYLE_FILES[@]} -gt 0 ]; then
        local merge_result
        merge_result=$(merge_styles "${HTML_STYLE_FILES[@]}")

        # Parse output to extract CDN links and styles
        if [[ "$merge_result" =~ CDN_LINKS_START ]]; then
            # Extract CDN links section
            cdn_css_links=$(echo "$merge_result" | sed -n '/CDN_LINKS_START/,/CDN_LINKS_END/p' | sed '1d;$d')
            # Extract styles section (everything after CDN_LINKS_END)
            combined_styles=$(echo "$merge_result" | sed -n '/CDN_LINKS_END/,$p' | tail -n +2)
        else
            # No CDN links, just styles
            combined_styles="$merge_result"
        fi
    fi

    # Add custom inline styles
    if [ -n "${HTML_CUSTOM_STYLES:-}" ]; then
        combined_styles+=$'\n'
        combined_styles+="$HTML_CUSTOM_STYLES"
    fi

    # Load common JavaScript
    local common_js=""
    if [ -n "${HTML_COMMON_JS:-}" ]; then
        common_js="$HTML_COMMON_JS"
    else
        common_js=$(load_js "templates/scripts/utils.js")
    fi

    # Custom JavaScript
    local custom_js="${HTML_CUSTOM_JS:-}"

    # Layout-specific body styles
    local body_styles="background: ${background}; margin: 0; padding: 0;"

    # Content wrapper
    local content="${HTML_CONTENT:-<div id=\"content\"></div>}"

    # Generate CSP header
    local csp_header="default-src 'self'; "
    csp_header+="script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
    csp_header+="style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://fonts.googleapis.com; "
    csp_header+="font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
    csp_header+="img-src 'self' data: https:; "
    csp_header+="connect-src 'self' https://cdn.jsdelivr.net https://unpkg.com; "
    csp_header+="object-src 'none'; "
    csp_header+="base-uri 'self'; "
    csp_header+="form-action 'self'; "
    csp_header+="frame-ancestors 'none';"

    # Set secure permissions before writing (owner read/write, others read-only)
    # 644 allows browser to read the file while preventing modification by others
    touch "$output"
    chmod 644 "$output" 2>/dev/null || true

    # Generate HTML
    cat > "$output" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="${csp_header}">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-Frame-Options" content="DENY">
    <title>${title}</title>
${cdn_scripts}
${cdn_css_links}
    <style>
${combined_styles}
        body {
            ${body_styles}
        }
    </style>
</head>
<body>
    <div id="container" class="layout-${layout}">
${content}
    </div>
    <script>
${common_js}

${custom_js}
    </script>
</body>
</html>
EOF

    return 0
}

#######################################
# Generate HTML with simple interface
# Arguments:
#   All arguments are key=value pairs
#   Supported keys:
#     title - Page title
#     cdn - CDN script URL (can be specified multiple times)
#     style - CSS file path (can be specified multiple times)
#     layout - Layout type (document, centered, full)
#     background - Background color
#     content - HTML content
#     js - Custom JavaScript
#     output - Output file path
# Example:
#   generate_html_simple \
#     title="My Page" \
#     cdn="https://cdn.example.com/lib.js" \
#     style="templates/styles/common.css" \
#     layout="document" \
#     output="/tmp/page.html"
#######################################
generate_html_simple() {
    # Reset environment variables
    unset HTML_TITLE HTML_CDN_SCRIPTS HTML_STYLE_FILES HTML_CUSTOM_STYLES
    unset HTML_LAYOUT HTML_BACKGROUND HTML_CONTENT HTML_COMMON_JS HTML_CUSTOM_JS HTML_OUTPUT

    # Arrays for multiple values
    HTML_CDN_SCRIPTS=()
    HTML_STYLE_FILES=()

    # Parse arguments
    for arg in "$@"; do
        local key="${arg%%=*}"
        local value="${arg#*=}"

        case "$key" in
            title)
                HTML_TITLE="$value"
                ;;
            cdn)
                HTML_CDN_SCRIPTS+=("$value")
                ;;
            style)
                HTML_STYLE_FILES+=("$value")
                ;;
            layout)
                HTML_LAYOUT="$value"
                ;;
            background)
                HTML_BACKGROUND="$value"
                ;;
            content)
                HTML_CONTENT="$value"
                ;;
            js)
                HTML_CUSTOM_JS="$value"
                ;;
            output)
                HTML_OUTPUT="$value"
                ;;
        esac
    done

    # Export for generate_html
    export HTML_TITLE HTML_LAYOUT HTML_BACKGROUND HTML_OUTPUT
    export HTML_CDN_SCRIPTS HTML_STYLE_FILES HTML_CUSTOM_STYLES
    export HTML_CONTENT HTML_COMMON_JS HTML_CUSTOM_JS

    # Generate HTML
    generate_html
}
