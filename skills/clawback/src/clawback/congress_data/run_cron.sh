#!/bin/bash

# Congressional Trade Data Collection Cron Job
# Run this script via cron to automatically collect congressional trade data

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/../config/congress_config.json"
LOG_DIR="$PROJECT_ROOT/../../logs/congress_data"
PYTHON_CMD="python3"

# Create log directory
mkdir -p "$LOG_DIR"

# Log file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/cron_${TIMESTAMP}.log"

echo "==========================================" >> "$LOG_FILE"
echo "Congressional Data Collection Cron Job" >> "$LOG_FILE"
echo "Start Time: $(date)" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found: $CONFIG_FILE" >> "$LOG_FILE"
    echo "Creating default config..." >> "$LOG_FILE"
    
    # Create config directory if it doesn't exist
    mkdir -p "$(dirname "$CONFIG_FILE")"
    
    # Run Python to create default config
    "$PYTHON_CMD" -c "
import json
import os
from congress_data.config import CongressConfig

config = CongressConfig('$CONFIG_FILE')
print('Default config created at: $CONFIG_FILE')
" >> "$LOG_FILE" 2>&1
fi

# Run the data collection
echo "Running data collection..." >> "$LOG_FILE"
cd "$PROJECT_ROOT" && \
"$PYTHON_CMD" -m congress_data.main once --config "$CONFIG_FILE" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo "" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"
echo "Cron Job Completed" >> "$LOG_FILE"
echo "End Time: $(date)" >> "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"

# Clean up old log files (keep last 30 days)
find "$LOG_DIR" -name "cron_*.log" -mtime +30 -delete

exit $EXIT_CODE