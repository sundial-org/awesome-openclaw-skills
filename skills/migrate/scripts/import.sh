#!/bin/bash
# Clawdbot Migration Import Script
# Restores workspace + config from export archive

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Defaults
WORKSPACE="${CLAWDBOT_WORKSPACE:-$HOME/clawd}"
CONFIG_DIR="$HOME/.clawdbot"
ARCHIVE=""
FORCE=false

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --workspace) WORKSPACE="$2"; shift 2 ;;
        --force|-f) FORCE=true; shift ;;
        --help|-h)
            echo "Usage: import.sh ARCHIVE [OPTIONS]"
            echo ""
            echo "Arguments:"
            echo "  ARCHIVE                Path to clawdbot export archive"
            echo ""
            echo "Options:"
            echo "  --workspace PATH       Target workspace directory (default: ~/clawd)"
            echo "  --force, -f            Overwrite existing files without prompting"
            exit 0
            ;;
        *)
            if [ -z "$ARCHIVE" ]; then
                ARCHIVE="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$ARCHIVE" ]; then
    echo -e "${RED}✗ No archive specified${NC}"
    echo "Usage: import.sh ARCHIVE [OPTIONS]"
    exit 1
fi

if [ ! -f "$ARCHIVE" ]; then
    echo -e "${RED}✗ Archive not found: $ARCHIVE${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Clawdbot Import${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create temp extraction directory
STAGING=$(mktemp -d)
trap "rm -rf $STAGING" EXIT

echo -e "${YELLOW}→ Extracting archive...${NC}"
tar -xzf "$ARCHIVE" -C "$STAGING"

# Check manifest
if [ -f "$STAGING/manifest.json" ]; then
    echo -e "${CYAN}Archive info:${NC}"
    cat "$STAGING/manifest.json" | grep -E '"exported_at"|"hostname"' | sed 's/[",]//g' | sed 's/^/  /'
    echo ""
fi

# Check for existing installations
if [ -d "$WORKSPACE" ] && [ "$FORCE" = false ]; then
    echo -e "${YELLOW}⚠ Workspace already exists: $WORKSPACE${NC}"
    read -p "  Merge/overwrite? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

if [ -d "$CONFIG_DIR" ] && [ "$FORCE" = false ]; then
    echo -e "${YELLOW}⚠ Config directory already exists: $CONFIG_DIR${NC}"
    read -p "  Merge/overwrite? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Restore workspace
if [ -d "$STAGING/workspace" ]; then
    echo -e "${YELLOW}→ Restoring workspace to $WORKSPACE...${NC}"
    mkdir -p "$WORKSPACE"
    cp -r "$STAGING/workspace"/* "$WORKSPACE/" 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Workspace restored"
fi

# Restore config
if [ -d "$STAGING/config" ]; then
    echo -e "${YELLOW}→ Restoring config to $CONFIG_DIR...${NC}"
    mkdir -p "$CONFIG_DIR"
    
    # Main config
    if [ -f "$STAGING/config/clawdbot.json" ]; then
        cp "$STAGING/config/clawdbot.json" "$CONFIG_DIR/"
        echo -e "  ${GREEN}✓${NC} Config file restored"
    fi
    
    # Skills
    if [ -d "$STAGING/config/skills" ]; then
        cp -r "$STAGING/config/skills" "$CONFIG_DIR/"
        echo -e "  ${GREEN}✓${NC} Managed skills restored"
    fi
    
    # WhatsApp session
    if [ -d "$STAGING/config/whatsapp" ]; then
        cp -r "$STAGING/config/whatsapp" "$CONFIG_DIR/"
        echo -e "  ${GREEN}✓${NC} WhatsApp session restored"
    fi
    
    # Sessions (if included)
    if [ -d "$STAGING/config/agents" ]; then
        cp -r "$STAGING/config/agents" "$CONFIG_DIR/"
        echo -e "  ${GREEN}✓${NC} Session transcripts restored"
    fi
    
    # Credentials (if included)
    if [ -d "$STAGING/config/credentials" ]; then
        cp -r "$STAGING/config/credentials" "$CONFIG_DIR/"
        echo -e "  ${GREEN}✓${NC} Credentials restored"
    fi
fi

# Update workspace path in config if different
if [ -f "$CONFIG_DIR/clawdbot.json" ]; then
    # Check if jq is available
    if command -v jq &> /dev/null; then
        CURRENT_WS=$(jq -r '.agent.workspace // empty' "$CONFIG_DIR/clawdbot.json" 2>/dev/null || true)
        if [ -n "$CURRENT_WS" ] && [ "$CURRENT_WS" != "$WORKSPACE" ]; then
            echo -e "${YELLOW}→ Updating workspace path in config...${NC}"
            jq --arg ws "$WORKSPACE" '.agent.workspace = $ws' "$CONFIG_DIR/clawdbot.json" > "$CONFIG_DIR/clawdbot.json.tmp"
            mv "$CONFIG_DIR/clawdbot.json.tmp" "$CONFIG_DIR/clawdbot.json"
        fi
    fi
fi

echo ""
echo -e "${GREEN}✓ Import complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Install Clawdbot (if not installed):"
echo "     npm install -g clawdbot"
echo ""
echo "  2. Start the gateway:"
echo "     cd $WORKSPACE && clawdbot gateway start"
echo ""
if [ -d "$STAGING/config/whatsapp" ]; then
    echo -e "  ${GREEN}✓${NC} WhatsApp session included - no re-scan needed!"
else
    echo "  3. Link WhatsApp (if needed):"
    echo "     clawdbot whatsapp link"
fi
