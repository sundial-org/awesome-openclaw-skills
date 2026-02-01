#!/bin/bash
#
# Congressional Trade Mirror Bot - Automated Runner
# This script is designed to be run by cron
#
# Usage:
#   ./scripts/run_bot.sh [command]
#
# Commands:
#   check     - Check for new trades and execute (default)
#   monitor   - Monitor positions and check stop-losses
#   full      - Run full cycle (check + monitor)
#   status    - Just print status
#

# Configuration
BOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$BOT_DIR/venv"
LOG_DIR="$BOT_DIR/logs"
LOCK_FILE="/tmp/congress_bot.lock"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/cron.log"
}

# Check for lock file (prevent concurrent runs)
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE")
    if ps -p "$pid" > /dev/null 2>&1; then
        log "ERROR: Bot already running (PID: $pid)"
        exit 1
    else
        log "WARN: Stale lock file found, removing"
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock file
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# Activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    log "ERROR: Virtual environment not found at $VENV_DIR"
    exit 1
fi

# Change to bot directory
cd "$BOT_DIR"

# Get command (default: check)
COMMAND="${1:-check}"

log "Starting bot with command: $COMMAND"

case "$COMMAND" in
    check)
        # Check for new congressional trades and execute
        python3 -c "
import sys
sys.path.insert(0, 'src')
from main import TradingBot
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading.log'),
        logging.StreamHandler()
    ]
)

bot = TradingBot('config/config.json')
if bot.broker.is_authenticated:
    bot.check_and_process_trades()
else:
    print('ERROR: Not authenticated. Run interactive mode first.')
    sys.exit(1)
"
        ;;

    monitor)
        # Monitor positions and check stop-losses
        python3 -c "
import sys
sys.path.insert(0, 'src')
from main import TradingBot
import logging

logging.basicConfig(level=logging.INFO)

bot = TradingBot('config/config.json')
if bot.broker.is_authenticated:
    # Check stop-losses
    triggered = bot.trade_engine.run_stop_loss_monitor()
    if triggered:
        print(f'Executed {len(triggered)} stop-loss orders')

    # Check holding periods
    expired = bot.trade_engine.check_holding_periods()
    if expired:
        print(f'{len(expired)} positions exceeded holding period')

    # Check portfolio risk
    risk = bot.trade_engine.check_portfolio_risk()
    if risk['status'] == 'halt':
        print('WARNING: Trading halted due to risk limits')
        for w in risk.get('warnings', []):
            print(f'  - {w}')
else:
    print('ERROR: Not authenticated')
    sys.exit(1)
"
        ;;

    full)
        # Run full cycle
        log "Running full cycle..."
        $0 check
        sleep 5
        $0 monitor
        ;;

    status)
        # Print status
        python3 -c "
import sys
sys.path.insert(0, 'src')
from main import TradingBot
import json

bot = TradingBot('config/config.json')
status = bot.get_status()
print(json.dumps(status, indent=2, default=str))
"
        ;;

    *)
        echo "Unknown command: $COMMAND"
        echo "Usage: $0 [check|monitor|full|status]"
        exit 1
        ;;
esac

log "Bot finished with command: $COMMAND"
