#!/bin/bash
# Publish LifePath to ClawdHub
# Run this after authenticating

echo "🎭 Publishing LifePath to ClawdHub..."
echo ""

# Check if logged in
clawdhub whoami > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Not authenticated. Please run:"
    echo "   clawdhub login"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Navigate to project
cd /home/ubuntu/clawd/projects/lifepath

# Publish
echo "📦 Publishing package..."
clawdhub publish . \
    --slug lifepath \
    --name "LifePath: AI Life Simulator" \
    --version "2.0.0" \
    --changelog "Multiplayer intersections, dynasty mode, challenges, image generation, Moltbook integration"

echo ""
echo "✅ Publication complete!"
echo ""
echo "Users can now install with:"
echo "   clawdhub install lifepath"
