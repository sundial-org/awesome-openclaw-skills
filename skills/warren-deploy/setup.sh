#!/bin/bash
# Warren Deploy - Quick Setup
# Run: bash setup.sh

cd "$(dirname "$0")"
npm init -y > /dev/null 2>&1
npm install ethers
echo ""
echo "✅ Setup complete! Usage:"
echo "  PRIVATE_KEY=0x... node deploy.js --html '<h1>Hello</h1>' --name 'My Site'"
echo ""
echo "Prerequisites:"
echo "  1. Get testnet ETH: https://docs.megaeth.com/faucet"
echo "  2. Genesis Key NFT auto-mints (free on testnet)"
