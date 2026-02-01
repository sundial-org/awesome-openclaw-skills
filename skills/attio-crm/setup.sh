#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCPORTER_DIR="${HOME}/.config/mcporter/servers/attio"
SKILLS_DIR="${HOME}/.clawdbot/skills"

echo "================================"
echo "Attio Moltbot Skill Setup"
echo "================================"
echo

# Step 1: Check for attio-mcp
echo -e "${YELLOW}Step 1: Checking for attio-mcp...${NC}"
if command -v attio-mcp &> /dev/null; then
    VERSION=$(attio-mcp --version 2>/dev/null || echo "unknown")
    echo -e "${GREEN}Found attio-mcp: ${VERSION}${NC}"
else
    echo -e "${YELLOW}attio-mcp not found. Installing...${NC}"
    npm install -g attio-mcp
    echo -e "${GREEN}Installed attio-mcp${NC}"
fi
echo

# Step 2: Get credentials
echo -e "${YELLOW}Step 2: Configuring credentials...${NC}"

# Try to load from .env file first
if [[ -f "${SCRIPT_DIR}/.env" ]]; then
    echo "Loading credentials from .env file..."
    set -a
    source "${SCRIPT_DIR}/.env"
    set +a
fi

# Prompt for missing credentials
if [[ -z "${ATTIO_ACCESS_TOKEN:-}" ]]; then
    echo "Get your API token from: https://app.attio.com/settings/api-tokens"
    read -rp "Enter ATTIO_ACCESS_TOKEN: " ATTIO_ACCESS_TOKEN
fi

if [[ -z "${ATTIO_WORKSPACE_ID:-}" ]]; then
    echo "Find your workspace ID in Attio workspace settings"
    read -rp "Enter ATTIO_WORKSPACE_ID: " ATTIO_WORKSPACE_ID
fi

if [[ -z "${ATTIO_ACCESS_TOKEN}" || -z "${ATTIO_WORKSPACE_ID}" ]]; then
    echo -e "${RED}Error: Both ATTIO_ACCESS_TOKEN and ATTIO_WORKSPACE_ID are required${NC}"
    exit 1
fi

echo -e "${GREEN}Credentials configured${NC}"
echo

# Step 3: Configure mcporter
echo -e "${YELLOW}Step 3: Configuring mcporter...${NC}"
mkdir -p "${MCPORTER_DIR}"

# Create config with substituted values
cat > "${MCPORTER_DIR}/config.json" << EOF
{
  "name": "attio",
  "type": "stdio",
  "command": "attio-mcp",
  "args": ["start:stdio"],
  "env": {
    "ATTIO_ACCESS_TOKEN": "${ATTIO_ACCESS_TOKEN}",
    "ATTIO_WORKSPACE_ID": "${ATTIO_WORKSPACE_ID}"
  },
  "healthCheck": {
    "type": "stdio",
    "command": "attio-mcp",
    "args": ["--help"]
  }
}
EOF

echo -e "${GREEN}Created ${MCPORTER_DIR}/config.json${NC}"
echo

# Step 4: Install skill
echo -e "${YELLOW}Step 4: Installing Moltbot skill...${NC}"
mkdir -p "${SKILLS_DIR}"

# Remove existing symlink/directory if present
if [[ -L "${SKILLS_DIR}/attio" || -d "${SKILLS_DIR}/attio" ]]; then
    rm -rf "${SKILLS_DIR}/attio"
fi

# Create symlink
ln -sf "${SCRIPT_DIR}" "${SKILLS_DIR}/attio"
echo -e "${GREEN}Linked skill to ${SKILLS_DIR}/attio${NC}"
echo

# Step 5: Validate
echo -e "${YELLOW}Step 5: Validating setup...${NC}"

# Check mcporter
if command -v mcporter &> /dev/null; then
    if mcporter list attio &> /dev/null; then
        echo -e "${GREEN}mcporter: attio server configured${NC}"
    else
        echo -e "${YELLOW}mcporter: server not responding (may need daemon restart)${NC}"
    fi
else
    echo -e "${YELLOW}mcporter not found - install it to use MCP tools${NC}"
fi

# Check skill
if [[ -f "${SKILLS_DIR}/attio/SKILL.md" ]]; then
    echo -e "${GREEN}Skill installed at ${SKILLS_DIR}/attio${NC}"
else
    echo -e "${RED}Error: Skill not properly installed${NC}"
    exit 1
fi

echo
echo "================================"
echo -e "${GREEN}Setup complete!${NC}"
echo "================================"
echo
echo "Next steps:"
echo "  1. Restart Moltbot to load the skill"
echo "  2. Test with: mcporter call attio.search_records resource_type=companies"
echo "  3. In Moltbot: 'Search for companies in Attio'"
echo
echo "Documentation: ${SCRIPT_DIR}/README.md"
