#!/bin/bash
# LinkedIn Post Script
# Usage: ./post.sh "Your content here" [--image /path/to/image]

set -e

CONTENT="$1"
IMAGE=""

# Parse arguments
shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --image)
            IMAGE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$CONTENT" ]; then
    echo "Usage: ./post.sh \"Your content here\" [--image /path/to/image]"
    exit 1
fi

# Output instructions for the agent to execute via browser tool
cat << EOF
📝 LINKEDIN POST WORKFLOW
═══════════════════════════════════════

Content to post:
---
$CONTENT
---

Steps to execute via browser tool:

1. Navigate to https://www.linkedin.com/feed/

2. Wait for page load, then click "Start a post" button:
   - Selector: button[class*="share-box-feed-entry__trigger"]
   - Or look for text "Start a post"

3. In the modal, enter the content in the editor:
   - Selector: div.ql-editor[data-placeholder]
   - Type the content

4. $([ -n "$IMAGE" ] && echo "Click the image icon and upload: $IMAGE" || echo "No image to attach")

5. Click the "Post" button:
   - Selector: button.share-actions__primary-action
   - Or button with text "Post"

6. Wait for confirmation (post appears in feed)

⚠️  Rate limit: Max 2-3 posts per day
EOF
