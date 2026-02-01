#!/bin/bash

cd "$(dirname "$0")"

echo "📦 Installing Dexie skill dependencies..."
npm install --production

if [ $? -eq 0 ]; then
  echo "✅ Dexie skill installed successfully!"
  echo ""
  echo "Usage:"
  echo "  CLI: dex <command>"
  echo "  Telegram: /dex <command>"
  echo ""
  echo "Run 'dex help' for command reference."
else
  echo "❌ Installation failed. Please check npm logs."
  exit 1
fi
