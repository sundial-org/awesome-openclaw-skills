#!/bin/bash

cd "$(dirname "$0")"

echo "📦 Installing Spacescan skill dependencies..."
npm install --production

if [ $? -eq 0 ]; then
  echo "✅ Spacescan skill installed successfully!"
  echo ""
  echo "⚠️  API Key Required:"
  echo "  Set SPACESCAN_API_KEY environment variable"
  echo "  Get your key at: https://www.spacescan.io/apis"
  echo ""
  echo "Usage:"
  echo "  CLI: scan <command>"
  echo "  Telegram: /scan <command>"
  echo ""
  echo "Run 'scan help' for command reference."
else
  echo "❌ Installation failed. Please check npm logs."
  exit 1
fi
