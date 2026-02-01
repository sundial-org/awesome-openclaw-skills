#!/bin/bash

# Feishu Document Blocks Reader - Shell wrapper
# Usage: ./get_blocks.sh <document_token>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/get_feishu_doc_blocks.py"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <document_token>"
    echo ""
    echo "Examples:"
    echo "  $0 docx_AbCdEfGhIjKlMnOpQrStUv"
    echo "  $0 doc_AbCdEfGhIjKlMnOpQrStUv"
    exit 1
fi

DOC_TOKEN="$1"

# Validate document token format
if [[ ! "$DOC_TOKEN" =~ ^(docx_|doc_)[a-zA-Z0-9]+$ ]]; then
    echo "Warning: Document token format may be invalid. Expected format: docx_xxxxx or doc_xxxxx" >&2
    echo "Continuing anyway..." >&2
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found: $PYTHON_SCRIPT" >&2
    exit 1
fi

# Execute the Python script
python3 "$PYTHON_SCRIPT" "$DOC_TOKEN"