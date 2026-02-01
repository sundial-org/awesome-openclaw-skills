#!/bin/bash
# Clawdbot Migration Export Script
# Creates a portable archive of workspace + config

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Defaults
WORKSPACE="${CLAWDBOT_WORKSPACE:-$HOME/clawd}"
CONFIG_DIR="$HOME/.clawdbot"
OUTPUT_DIR="${1:-.}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="clawdbot-export-${TIMESTAMP}.tar.gz"
INCLUDE_SESSIONS=false
INCLUDE_CREDENTIALS=false

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --workspace) WORKSPACE="$2"; shift 2 ;;
        --output|-o) OUTPUT_DIR="$2"; shift 2 ;;
        --include-sessions) INCLUDE_SESSIONS=true; shift ;;
        --include-credentials) INCLUDE_CREDENTIALS=true; shift ;;
        --name) ARCHIVE_NAME="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: export.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --workspace PATH       Workspace directory (default: ~/clawd)"
            echo "  --output, -o PATH      Output directory (default: current dir)"
            echo "  --include-sessions     Include session transcripts"
            echo "  --include-credentials  Include credentials (DANGEROUS)"
            echo "  --name FILENAME        Custom archive name"
            exit 0
            ;;
        *) shift ;;
    esac
done

echo -e "${GREEN}🚀 Clawdbot Export${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Validate paths
if [ ! -d "$WORKSPACE" ]; then
    echo -e "${RED}✗ Workspace not found: $WORKSPACE${NC}"
    exit 1
fi

if [ ! -d "$CONFIG_DIR" ]; then
    echo -e "${RED}✗ Config directory not found: $CONFIG_DIR${NC}"
    exit 1
fi

# Create temp staging directory
STAGING=$(mktemp -d)
trap "rm -rf $STAGING" EXIT

echo -e "${YELLOW}→ Staging workspace...${NC}"
mkdir -p "$STAGING/workspace"

# Use rsync to exclude large/rebuilable directories
rsync -a --exclude='node_modules' \
         --exclude='.next' \
         --exclude='.open-next' \
         --exclude='.vercel' \
         --exclude='.wrangler' \
         --exclude='.git' \
         --exclude='dist' \
         --exclude='build' \
         --exclude='*.log' \
         --exclude='.DS_Store' \
         "$WORKSPACE/" "$STAGING/workspace/" 2>/dev/null || \
cp -r "$WORKSPACE"/* "$STAGING/workspace/" 2>/dev/null || true

# Cleanup if rsync wasn't available
rm -rf "$STAGING/workspace/.git" "$STAGING/workspace/node_modules" "$STAGING/workspace/.next" 2>/dev/null || true

echo -e "${YELLOW}→ Staging config...${NC}"
mkdir -p "$STAGING/config"

# Always include main config
[ -f "$CONFIG_DIR/clawdbot.json" ] && cp "$CONFIG_DIR/clawdbot.json" "$STAGING/config/"

# Include skills
if [ -d "$CONFIG_DIR/skills" ]; then
    cp -r "$CONFIG_DIR/skills" "$STAGING/config/"
fi

# Include WhatsApp session (for seamless migration)
if [ -d "$CONFIG_DIR/whatsapp" ]; then
    echo -e "${YELLOW}→ Including WhatsApp session...${NC}"
    cp -r "$CONFIG_DIR/whatsapp" "$STAGING/config/"
fi

# Optional: sessions
if [ "$INCLUDE_SESSIONS" = true ] && [ -d "$CONFIG_DIR/agents" ]; then
    echo -e "${YELLOW}→ Including session transcripts...${NC}"
    cp -r "$CONFIG_DIR/agents" "$STAGING/config/"
fi

# Optional: credentials (dangerous)
if [ "$INCLUDE_CREDENTIALS" = true ] && [ -d "$CONFIG_DIR/credentials" ]; then
    echo -e "${RED}⚠ Including credentials (handle with care!)${NC}"
    cp -r "$CONFIG_DIR/credentials" "$STAGING/config/"
fi

# Create manifest
cat > "$STAGING/manifest.json" << EOF
{
  "version": "1.0",
  "exported_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "hostname": "$(hostname)",
  "workspace_path": "$WORKSPACE",
  "includes": {
    "workspace": true,
    "config": true,
    "whatsapp_session": $([ -d "$CONFIG_DIR/whatsapp" ] && echo "true" || echo "false"),
    "sessions": $INCLUDE_SESSIONS,
    "credentials": $INCLUDE_CREDENTIALS
  }
}
EOF

# Create archive
echo -e "${YELLOW}→ Creating archive...${NC}"
mkdir -p "$OUTPUT_DIR"
tar -czf "$OUTPUT_DIR/$ARCHIVE_NAME" -C "$STAGING" .

# Summary
SIZE=$(du -h "$OUTPUT_DIR/$ARCHIVE_NAME" | cut -f1)
echo ""
echo -e "${GREEN}✓ Export complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  Archive: ${GREEN}$OUTPUT_DIR/$ARCHIVE_NAME${NC}"
echo -e "  Size: $SIZE"
echo ""
echo "To import on new machine:"
echo "  1. Copy archive to new machine"
echo "  2. Run: bash import.sh $ARCHIVE_NAME"
