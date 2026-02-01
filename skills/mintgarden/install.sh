#!/bin/bash

cd "$(dirname "$0")"

echo "📦 Installing MintGarden skill dependencies..."
npm install --production

if [ $? -eq 0 ]; then
  echo "✅ MintGarden skill installed successfully!"
  echo ""
  echo "Usage:"
  echo "  CLI: mg <command>"
  echo "  Telegram: /mg <command>"
  echo ""
  echo "Run 'mg help' for command reference."
else
  echo "❌ Installation failed. Please check npm logs."
  exit 1
fi
