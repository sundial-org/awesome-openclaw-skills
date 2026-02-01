#!/bin/bash
# Beanstalk Gateway Skill - Post-install setup

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           Beanstalk Gateway Skill Installed                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "To connect your Clawdbot to beans.talk:"
echo ""
echo "1. Get credentials from https://beans.talk"
echo "   - Sign up / log in"
echo "   - Click 'Add Gateway'"
echo "   - Copy your GATEWAY_URL and GATEWAY_TOKEN"
echo ""
echo "2. Create config file:"
echo "   mkdir -p ~/.clawdbot/.beanstalk"
echo "   cat > ~/.clawdbot/.beanstalk/gateway.json << EOF"
echo "   {"
echo '     "url": "wss://beanstalk.fly.dev/ws/gw_YOUR_ID",'
echo '     "token": "gt_YOUR_TOKEN"'
echo "   }"
echo "   EOF"
echo ""
echo "3. Start the gateway:"
echo "   node $SKILL_DIR/scripts/gateway-client.js"
echo ""
echo "Or set environment variables and run:"
echo "   GATEWAY_URL=wss://... GATEWAY_TOKEN=gt_... node $SKILL_DIR/scripts/gateway-client.js"
echo ""

# Make the client executable
chmod +x "$SKILL_DIR/scripts/gateway-client.js"

# Create a convenience symlink if possible
if [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
  ln -sf "$SKILL_DIR/scripts/gateway-client.js" /usr/local/bin/beanstalk-gateway 2>/dev/null && \
    echo "✓ Created /usr/local/bin/beanstalk-gateway"
fi

echo "Done! Visit https://beans.talk to get started."
