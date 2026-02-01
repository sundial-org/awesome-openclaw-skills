#!/bin/bash

# Navigate to the directory of the script
SKILL_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
TRADING_TOOLS_DIR="/home/linuxuser/.openclaw/workspace/tools/trading"

echo "Starting background trading data collectors..."

# Start the smart money tracker in the background
cd "$TRADING_TOOLS_DIR"
nohup node smart-money-tracker.js > /tmp/tracker.log 2>&1 &
TRACKER_PID=$!
echo "  -> Smart money tracker started with PID $TRACKER_PID"

# Start the pair scanner in the background
nohup node pair-scanner.js > /tmp/scanner.log 2>&1 &
SCANNER_PID=$!
echo "  -> Pair scanner started with PID $SCANNER_PID"

# Navigate back to the skill's script directory
cd "$SKILL_DIR"

# Start the API server in the foreground
echo "Starting signal API server on port ${PORT:-7071}..."
node signal-api.js

# When the API server is stopped (e.g., Ctrl+C), kill the background jobs
echo "API server stopped. Cleaning up background processes..."
kill $TRACKER_PID
kill $SCANNER_PID
echo "Done."
