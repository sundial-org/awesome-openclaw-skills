EOF
echo -e "${GREEN}✓ Automated trading controller created${NC}"

# Step 7: Create main automation script
echo -e "\n${BLUE}STEP 7: Creating main automation script...${NC}"
cat > run_automated_trading.py << 'EOF'
#!/usr/bin/env python3
"""
Main script for automated congressional trading system
"""
import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from automated_trading_controller import AutomatedTradingController

def main():
    parser = argparse.ArgumentParser(description='Automated Congressional Trading System')
    parser.add_argument('--mode', choices=['once', 'continuous', 'test', 'status'],
                       default='once', help='Execution mode')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without executing real trades')
    parser.add_argument('--interval', type=int, default=1,
                       help='Check interval in hours (continuous mode only)')
    parser.add_argument('--config', default='config/config.json',
                       help='Path to config file')
    
    args = parser.parse_args()
    
    # Initialize controller
    try:
        controller = AutomatedTradingController(args.config)
    except Exception as e:
        print(f"Error initializing controller: {e}")
        return 1
    
    # Execute based on mode
    if args.mode == 'once':
        print("Running single trading cycle...")
        success = controller.run_daily_cycle(dry_run=args.dry_run)
        if success:
            print("Trading cycle completed successfully")
            return 0
        else:
            print("Trading cycle failed")
            return 1
    
    elif args.mode == 'continuous':
        print(f"Starting continuous monitoring (check every {args.interval} hours)...")
        try:
            controller.run_continuous(interval_hours=args.interval)
        except KeyboardInterrupt:
            print("\nShutting down...")
            controller.stop()
        return 0
    
    elif args.mode == 'test':
        print("Testing system components...")
        
        # Test Telegram
        print("Testing Telegram notifications...")
        telegram_ok = controller.test_telegram()
        
        # Test broker connection
        print("Testing broker connection...")
        try:
            broker_ok = controller.broker.is_authenticated
        except Exception as e:
            print(f"Broker test failed: {e}")
            broker_ok = False
        
        # Test PDT tracker
        print("Testing PDT compliance tracker...")
        pdt_summary = controller.pdt_trader.get_trading_summary()
        
        print("\n=== TEST RESULTS ===")
        print(f"Telegram: {'✓ OK' if telegram_ok else '✗ FAILED'}")
        print(f"Broker: {'✓ OK' if broker_ok else '✗ FAILED'}")
        print(f"PDT Tracker: ✓ OK (Summary: {pdt_summary})")

        if telegram_ok and broker_ok:
            print("\nAll tests passed! System is ready.")
            return 0
        else:
            print("\nSome tests failed. Check configuration.")
            return 1
    
    elif args.mode == 'status':
        status = controller.get_status()
        print("\n=== SYSTEM STATUS ===")
        print(f"Status: {status['status'].upper()}")
        print(f"Last Execution: {status['last_execution'] or 'Never'}")
        print(f"Trades Today: {status['trades_today']}")
        print(f"Account Balance: ${status['account_balance']:,.2f}")
        print(f"Telegram: {'ENABLED' if status['telegram_enabled'] else 'DISABLED'}")
        
        pdt = status['pdt_compliance']
        print(f"\n=== PDT COMPLIANCE ===")
        print(f"Trades Today: {pdt['trades_today']}")
        print(f"Day Trades Today: {pdt['day_trades_today']}/{pdt['max_day_trades']}")
        print(f"Recent Day Trades: {pdt['recent_day_trades']}/{pdt['max_day_trades']}")
        print(f"PDT Compliant: {'✓ YES' if pdt['pdt_compliant'] else '✗ NO'}")
        
        return 0

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x run_automated_trading.py
echo -e "${GREEN}✓ Main automation script created${NC}"

# Step 8: Create cron job setup
echo -e "\n${BLUE}STEP 8: Setting up cron jobs...${NC}"
cat > scripts/setup_cron.sh << 'EOF'
#!/bin/bash

# Setup cron jobs for automated trading system

CRON_JOB="0 9 * * 1-5 cd $(pwd) && source venv/bin/activate && python3 run_automated_trading.py --mode once 2>&1 | logger -t congressional_trading"

echo "Setting up cron job for automated trading..."
echo "Schedule: 9:00 AM Monday-Friday"
echo "Command: $CRON_JOB"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "congressional_trading"; then
    echo "Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "congressional_trading" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "# Congressional Trading System - Runs at 9 AM weekdays"; echo "$CRON_JOB") | crontab -

echo "Cron job added successfully!"
echo ""
echo "Current crontab:"
crontab -l 2>/dev/null | grep -A2 -B2 "congressional_trading"
EOF

chmod +x scripts/setup_cron.sh
echo -e "${GREEN}✓ Cron setup script created${NC}"

# Step 9: Create monitoring dashboard
echo -e "\n${BLUE}STEP 9: Creating monitoring dashboard...${NC}"
cat > monitor_trading.sh << 'EOF'
#!/bin/bash

# Trading System Monitoring Dashboard

echo "📊 CONGRESSIONAL TRADING SYSTEM DASHBOARD"
echo "=========================================="
echo ""

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if system is running
if pgrep -f "run_automated_trading.py" > /dev/null; then
    echo "✅ System Status: RUNNING"
    PROCESS_INFO=$(ps aux | grep "run_automated_trading.py" | grep -v grep)
    echo "   Process: $(echo "$PROCESS_INFO" | awk '{print $2, $11, $12}')"
else
    echo "❌ System Status: STOPPED"
fi

echo ""

# Check logs
echo "📋 RECENT LOGS:"
if [ -f "logs/trading.log" ]; then
    tail -20 logs/trading.log | while read line; do
        echo "   $line"
    done
else
    echo "   No log file found"
fi

echo ""

# Check trade history
echo "💰 TRADE HISTORY:"
if [ -f "data/trade_history.json" ]; then
    TRADE_COUNT=$(jq '.trades | length' data/trade_history.json 2>/dev/null || echo "0")
    echo "   Total Trades Recorded: $TRADE_COUNT"
    
    TODAY=$(date +%Y-%m-%d)
    TODAY_TRADES=$(jq --arg today "$TODAY" '.trades | map(select(.date == $today)) | length' data/trade_history.json 2>/dev/null || echo "0")
    echo "   Trades Today: $TODAY_TRADES"
else
    echo "   No trade history file"
fi

echo ""

# Check congressional data
echo "🏛️ CONGRESSIONAL DATA:"
if [ -d "data/congress_trades" ]; then
    DATA_FILES=$(find data/congress_trades -name "*.json" -o -name "*.csv" | wc -l)
    echo "   Data Files: $DATA_FILES"
    
    if [ -f "data/congress_trades/latest_trades.json" ]; then
        LATEST_TRADES=$(jq 'length' data/congress_trades/latest_trades.json 2>/dev/null || echo "0")
        echo "   Latest Trades: $LATEST_TRADES"
    fi
else
    echo "   No congressional data directory"
fi

echo ""

# Check cron jobs
echo "⏰ SCHEDULED JOBS:"
if crontab -l 2>/dev/null | grep -q "congressional_trading"; then
    echo "✅ Cron job is scheduled"
    crontab -l 2>/dev/null | grep "congressional_trading"
else
    echo "❌ No cron job found"
fi

echo ""
echo "=========================================="
echo "Quick Commands:"
echo "  ./run_automated_trading.py --mode status  # System status"
echo "  ./run_automated_trading.py --mode test    # Test all components"
echo "  ./scripts/setup_cron.sh                   # Setup cron job"
echo "  tail -f logs/trading.log                  # View live logs"
EOF

chmod +x monitor_trading.sh
echo -e "${GREEN}✓ Monitoring dashboard created${NC}"

# Step 10: Create quick start guide
echo -e "\n${BLUE}STEP 10: Creating quick start guide...${NC}"
cat > QUICK_START_AUTOMATED.md << 'EOF'
# Quick Start - Automated Congressional Trading System

## 🚀 System Overview
Automated system that:
1. Pulls congressional trading data daily (Pelosi + Senate)
2. Generates trade recommendations
3. Executes trades via E*TRADE API
4. Sends Telegram notifications
5. Maintains PDT compliance for $50K account

## 📋 Prerequisites
1. E*TRADE account with API access
2. Telegram bot (from @BotFather)
3. Python 3.8+ and virtual environment

## ⚡ Quick Start

### 1. Initial Setup
```bash
# Run the setup script
./setup_automated_trading.sh

# Follow prompts to enter Telegram credentials
```

### 2. Test the System
```bash
# Test all components
./run_automated_trading.py --mode test

# Run a dry-run trading cycle
./run_automated_trading.py --mode once --dry-run
```

### 3. Set Up Automation
```bash
# Setup cron job (runs at 9 AM weekdays)
./scripts/setup_cron.sh

# Or run continuous monitoring
./run_automated_trading.py --mode continuous --interval 1
```

### 4. Monitor the System
```bash
# View dashboard
./monitor_trading.sh

# Check system status
./run_automated_trading.py --mode status

# View logs
tail -f logs/trading.log
```

## 🔧 Configuration

### Main Config (`config/config.json`)
- `accountBalance`: $50,000 (adjust as needed)
- `tradeScalePercentage`: 0.01 (1% per trade)
- `maxTradesPerDay`: 3 (PDT-safe limit)
- `telegram`: Configure bot token and chat ID

### PDT Compliance
- Max 2 day trades in 5 rolling days (conservative)
- Position limits: 5% of account per symbol
- Trade limits: $2,500 max per trade

## 📱 Telegram Notifications
The system sends:
- ✅ Trade execution alerts
- 📊 Congressional trade alerts
- ⚠️ Error notifications
- 📋 Daily trading summaries

## 🛡️ Safety Features
1. **Dry-run mode**: Test without real trades
2. **PDT compliance**: Avoids day-trader classification
3. **Position limits**: Prevents over-concentration
4. **Stop-loss protection**: 10% automatic stop loss
5. **Market hours only**: Only trades during market hours

## 🔄 Daily Workflow
1. **9:00 AM**: Cron job triggers data collection
2. **9:05 AM**: Process congressional trades
3. **9:10 AM**: Generate trade recommendations
4. **9:15 AM**: Execute PDT-compliant trades
5. **9:20 AM**: Send Telegram notifications
6. **4:00 PM**: Send daily summary

## 🚨 Emergency Stop
```bash
# Find and kill the process
pkill -f "run_automated_trading.py"

# Or use the controller (if running in continuous mode)
# Send Ctrl+C to the running process
```

## 📊 Monitoring
- **Logs**: `logs/trading.log`
- **Trade History**: `data/trade_history.json`
- **Congressional Data**: `data/congress_trades/`
- **Dashboard**: `./monitor_trading.sh`

## 🔍 Troubleshooting
1. **Telegram not working**: Check bot token and chat ID
2. **E*TRADE auth failed**: Verify API keys and OAuth setup
3. **No trades executing**: Check PDT compliance and market hours
4. **Cron job not running**: Verify cron setup and permissions

## 📈 Going Live
1. Test thoroughly in sandbox mode
2. Start with small position sizes
3. Monitor for 1-2 weeks
4. Gradually increase trade scale
5. Enable real trading by setting `environment: "production"` in config

## 🆘 Support
- Check logs: `tail -f logs/trading.log`
- Run tests: `./run_automated_trading.py --mode test`
- View status: `./run_automated_trading.py --mode status`
EOF

echo -e "${GREEN}✓ Quick start guide created${NC}"

# Step 11: Final setup and test
echo -e "\n${BLUE}STEP 11: Final setup and testing...${NC}"

# Make scripts executable
chmod +x setup_automated_trading.sh
chmod +x monitor_trading.sh

echo -e "\n${GREEN}✅ SETUP COMPLETE!${NC}"
echo -e "\n${YELLOW}=== NEXT STEPS ===${NC}"
echo "1. Review configuration files:"
echo "   - config/config.json (trading settings)"
echo "   - config/congress_config.json (data sources)"
echo ""
echo "2. Test the system:"
echo "   ./run_automated_trading.py --mode test"
echo ""
echo "3. Run a dry-run trading cycle:"
echo "   ./run_automated_trading.py --mode once --dry-run"
echo ""
echo "4. Set up automation:"
echo "   ./scripts/setup_cron.sh"
echo ""
echo "5. Monitor the system:"
echo "   ./monitor_trading.sh"
echo ""
echo "📖 Detailed instructions: QUICK_START_AUTOMATED.md"
echo ""
echo "${GREEN}Your automated congressional trading system is ready!${NC}"