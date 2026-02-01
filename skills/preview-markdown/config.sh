#!/usr/bin/env bash

# Markdown Preview Skill Configuration

# Skill metadata
TOOL_NAME="markdown"
TOOL_TITLE_PREFIX="Markdown"
DEFAULT_FILENAME="document"
FILE_EXTENSIONS=(".md" ".markdown")

# Layout configuration
LAYOUT_TYPE="document"  # document, centered, or full
BACKGROUND_COLOR="#f5f5f5"

# CDN Libraries with SRI hashes
# Format: URL::INTEGRITY_HASH
# To get SRI hash: curl -s URL | openssl dgst -sha384 -binary | openssl base64 -A
CDN_SCRIPTS=(
    "https://cdn.jsdelivr.net/npm/marked@11.2.0/marked.min.js::sha384-9Md4MlJk24bo2Ifubp0FbKhuES4/iAwyTGMeWpBG4RoHGTKygpEGEpOYhEQxbfa9"
    "https://cdn.jsdelivr.net/npm/dompurify@3.0.8/dist/purify.min.js::sha384-vdScihEZCfbPnBQf+lc7LgXUdJVYyhC3yWHUW5C5P5GpHRqVnaM6HJELJxT6IqwM"
    "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js::sha384-rbtjAdnIQE/aQJGEgXrVUlMibdfTSa4PQju4HDhN3sR2PmaKFzhEafuePsl9H/9I"
)

# CSS Files (relative to LIB_ROOT or absolute paths)
STYLE_FILES=(
    "templates/styles/layout.css"
    "templates/styles/markdown.css"
)

# Content processing
CONTENT_ENCODING="base64"

# Renderer configuration
RENDERER_FILE="templates/scripts/markdown-renderer.js"
RENDERER_VARS=(
    "MARKDOWN_CONTENT"  # Will be substituted with base64 content
)
