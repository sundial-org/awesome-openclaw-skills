#!/bin/bash
#
# AI Trading Skill - Quick Launch Script
#
# Usage:
#   ./run.sh analyze BTC/USDT
#   ./run.sh scan
#   ./run.sh interactive
#

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to skill directory
cd "$DIR"

# Set default balance if not set
export TRADING_BALANCE=${TRADING_BALANCE:-10000}

# Run the skill
python3 skill.py "$@"
