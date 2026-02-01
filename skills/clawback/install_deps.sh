#!/bin/bash
# Install dependencies for E*TRADE Pelosi Trade Mirror Bot

echo "Installing Python dependencies..."
pip3 install -r src/requirements.txt

echo "Creating necessary directories..."
mkdir -p logs data

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Verify config/config.json has your API keys"
echo "2. Run: python3 src/main.py auth"
echo "3. Follow authentication prompts"
echo "4. Test with: python3 src/main.py interactive"