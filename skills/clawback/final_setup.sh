#!/bin/bash

# FINAL SETUP - Complete Congressional Trading System
# Integrates all improvements from Claude with automated execution

set -e

echo "🚀 COMPLETE CONGRESSIONAL TRADING SYSTEM SETUP"
echo "================================================"
echo "Features:"
echo "• Senate + House data collection"
echo "• Backtested optimal strategy (3-day delay, 30-day hold)"
echo "• Trailing stop-loss system"
echo "• Cron job automation"
echo "• Telegram notifications"
echo "• $50K PDT-compliant account"
echo "================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check directory
if [ ! -f "src/main.py" ]; then
    echo -e "${RED}Error: Must run from etrade-pelosi-bot directory${NC}"
    exit 1
fi

# Step 1: Activate virtual environment
echo -e "\n${BLUE}STEP 1: Setting up environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r src/requirements.txt
pip install yfinance python-telegram-bot==20.7 selenium webdriver-manager
echo -e "${GREEN}✓ Environment ready${NC}"

# Step 2: Configure Telegram
echo -e "\n${BLUE}STEP 2: Telegram notifications setup...${NC}"
read -p "Enable Telegram notifications? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter Telegram Bot Token (from @BotFather): " TELEGRAM_TOKEN
    read -p "Enter Telegram Chat ID (from @userinfobot): " TELEGRAM_CHAT_ID
    
    if [ -z "$TELEGRAM_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
        echo -e "${YELLOW}⚠ Telegram not configured. You can add later.${NC}"
        TELEGRAM_TOKEN=""
        TELEGRAM_CHAT_ID=""
    else
        echo -e "${GREEN}✓ Telegram configured${NC}"
    fi
else
    TELEGRAM_TOKEN=""
    TELEGRAM_CHAT_ID=""
fi

# Step 3: Update configuration with optimal strategy
echo -e "\n${BLUE}STEP 3: Applying optimal trading strategy...${NC}"

# Create optimal config based on backtest results
cat > config/config.json << EOF
{
  "broker": {
    "adapter": "etrade",
    "environment": "sandbox",
    "apiKey": "\${BROKER_API_KEY}",
    "apiSecret": "\${BROKER_API_SECRET}",
    "baseUrl": "https://apisb.etrade.com",
    "oauth": {
      "requestTokenUrl": "https://apisb.etrade.com/oauth/request_token",
      "accessTokenUrl": "https://apisb.etrade.com/oauth/access_token",
      "authorizeUrl": "https://us.etrade.com/e/t/etws/authorize"
    }
  },
  "trading": {
    "accountId": "\${BROKER_ACCOUNT_ID}",
    "initialCapital": 50000,
    "tradeScalePercentage": 0.05,
    "maxPositionPercentage": 0.05,
    "maxPositions": 20,
    "dailyLossLimit": 0.03,
    "portfolioStopLoss": 0.15,
    "positionStopLoss": 0.08,
    "tradeDelayDays": 3,
    "holdingPeriodDays": 30,
    "marketHoursOnly": true,
    "marketOpen": "09:30",
    "marketClose": "16:00"
  },
  "strategy": {
    "entryDelayDays": 3,
    "holdingPeriodDays": 30,
    "purchasesOnly": true,
    "minimumTradeSize": 50000,
    "maxSectorExposure": 0.25,
    "prioritizeLeadership": true,
    "multiMemberBonus": true
  },
  "congress": {
    "dataSource": "official",
    "pollIntervalHours": 24,
    "minimumTradeSize": 50000,
    "tradeTypes": ["purchase"],
    "includeSenate": true,
    "targetPoliticians": [
      {"name": "Nancy Pelosi", "chamber": "house", "priority": 1},
      {"name": "Dan Crenshaw", "chamber": "house", "priority": 2},
      {"name": "Tommy Tuberville", "chamber": "senate", "priority": 2},
      {"name": "Marjorie Taylor Greene", "chamber": "house", "priority": 3}
    ]
  },
  "riskManagement": {
    "maxDrawdown": 0.15,
    "dailyLossLimit": 0.03,
    "positionStopLoss": 0.08,
    "trailingStopActivation": 0.10,
    "trailingStopPercent": 0.05,
    "consecutiveLossLimit": 3
  },
  "notifications": {
    "telegram": {
      "enabled": ${TELEGRAM_TOKEN:+true},
      "botToken": "${TELEGRAM_TOKEN}",
      "chatId": "${TELEGRAM_CHAT_ID}"
    }
  },
  "logging": {
    "level": "info",
    "file": "logs/trading.log",
    "maxSize": "10MB",
    "maxFiles": 10
  },
  "database": {
    "path": "data/trading.db"
  }
}
EOF

echo -e "${GREEN}✓ Configuration updated with optimal strategy${NC}"

# Step 4: Create data directories
echo -e "\n${BLUE}STEP 4: Creating data structure...${NC}"
mkdir -p data/congress_trades
mkdir -p data/backups
mkdir -p logs/trading
mkdir -p logs/cron
mkdir -p scripts
echo -e "${GREEN}✓ Directories created${NC}"

# Step 5: Test the system
echo -e "\n${BLUE}STEP 5: Testing system components...${NC}"

# Test database
echo "Testing database..."
python3 -c "
from src.database import get_database
db = get_database()
print('✓ Database initialized')
stats = db.get_trade_stats()
print(f'  Stats: {stats}')
"

# Test PDF parser
echo "Testing PDF parser..."
python3 -c "
from src.congress_tracker import CongressTracker
import json
config = json.load(open('config/config.json'))
tracker = CongressTracker(config)
print('✓ Congress tracker initialized')
print('  Note: PDF parsing requires actual PDFs to test')
"

# Test backtester
echo "Testing backtester..."
python3 -c "
try:
    from src.backtester import Backtester
    print('✓ Backtester available')
except ImportError as e:
    print(f'⚠ Backtester not available: {e}')
"

echo -e "${GREEN}✓ System tests completed${NC}"

# Step 6: Set up cron jobs
echo -e "\n${BLUE}STEP 6: Setting up automated execution...${NC}"
chmod +x scripts/*.sh

echo "Setting up cron jobs..."
./scripts/setup_cron.sh

echo -e "${GREEN}✓ Cron jobs configured${NC}"

# Step 7: Create monitoring dashboard
echo -e "\n${BLUE}STEP 7: Creating monitoring tools...${NC}"

cat > monitor.sh << 'EOF'
#!/bin/bash

# Congressional Trading System Monitor

echo "📊 CONGRESSIONAL TRADING SYSTEM MONITOR"
echo "========================================"
echo ""

# System status
echo "🖥️ SYSTEM STATUS:"
if pgrep -f "run_bot.sh" > /dev/null; then
    echo "✅ Bot is running"
    PROCESSES=$(pgrep -f "run_bot.sh" | wc -l)
    echo "   Processes: $PROCESSES"
else
    echo "❌ Bot is stopped"
fi

echo ""

# Database stats
echo "🗄️ DATABASE STATS:"
if [ -f "data/trading.db" ]; then
    python3 -c "
import sqlite3
conn = sqlite3.connect('data/trading.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM congressional_trades')
total = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM congressional_trades WHERE processed = 0')
unprocessed = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM executed_trades')
executed = c.fetchone()[0]
print(f'  Total trades: {total}')
print(f'  Unprocessed: {unprocessed}')
print(f'  Executed: {executed}')
conn.close()
"
else
    echo "  No database found"
fi

echo ""

# Recent logs
echo "📝 RECENT ACTIVITY:"
if [ -f "logs/trading.log" ]; then
    tail -5 logs/trading.log | while read line; do
        echo "  $line"
    done
else
    echo "  No log file"
fi

echo ""

# Cron jobs
echo "⏰ SCHEDULED JOBS:"
if crontab -l 2>/dev/null | grep -q "congressional_trading"; then
    echo "✅ Cron jobs active"
    crontab -l 2>/dev/null | grep "congressional_trading" | while read job; do
        echo "  $job"
    done
else
    echo "❌ No cron jobs found"
fi

echo ""
echo "========================================"
echo "Quick Commands:"
echo "  ./scripts/run_bot.sh check    - Run trade check"
echo "  ./scripts/run_bot.sh monitor  - Run stop-loss monitor"
echo "  ./scripts/run_bot.sh status   - System status"
echo "  tail -f logs/trading.log      - View live logs"
echo "  ./scripts/setup_cron.sh       - Reconfigure cron jobs"
EOF

chmod +x monitor.sh
echo -e "${GREEN}✓ Monitoring dashboard created${NC}"

# Step 8: Create startup script
echo -e "\n${BLUE}STEP 8: Creating startup script...${NC}"

cat > start_trading.sh << 'EOF'
#!/bin/bash

# Start Congressional Trading System

echo "🤖 STARTING CONGRESSIONAL TRADING SYSTEM"
echo "========================================"

source venv/bin/activate

# Check if already running
if pgrep -f "run_bot.sh" > /dev/null; then
    echo "System is already running"
    exit 1
fi

# Start the bot in background
echo "Starting automated trading..."
nohup ./scripts/run_bot.sh full > logs/startup.log 2>&1 &

echo "System started in background"
echo "Check logs: tail -f logs/startup.log"
echo "Monitor: ./monitor.sh"
EOF

chmod +x start_trading.sh

cat > stop_trading.sh << 'EOF'
#!/bin/bash

# Stop Congressional Trading System

echo "🛑 STOPPING CONGRESSIONAL TRADING SYSTEM"
echo "========================================"

# Find and kill processes
pkill -f "run_bot.sh"
pkill -f "python.*main.py"

echo "System stopped"
echo "Note: Cron jobs will restart at scheduled times"
EOF

chmod +x stop_trading.sh
echo -e "${GREEN}✓ Control scripts created${NC}"

# Step 9: Create Telegram test
if [ -n "$TELEGRAM_TOKEN" ]; then
    echo -e "\n${BLUE}STEP 9: Testing Telegram notifications...${NC}"
    
    cat > test_telegram.py << EOF
#!/usr/bin/env python3
import json
import requests

config = json.load(open('config/config.json'))
token = config['notifications']['telegram']['botToken']
chat_id = config['notifications']['telegram']['chatId']

if token and chat_id:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    message = "✅ Congressional Trading System Test\\n\\nSystem is online and ready for automated trading!"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Telegram test message sent successfully!")
        else:
            print(f"Telegram test failed: {response.status_code}")
    except Exception as e:
        print(f"Telegram test error: {e}")
else:
    print("Telegram not configured in config.json")
EOF

    python3 test_telegram.py
    rm test_telegram.py
fi

# Step 10: Final instructions
echo -e "\n${GREEN}✅ SETUP COMPLETE!${NC}"
echo -e "\n${YELLOW}=== NEXT STEPS ===${NC}"
echo ""
echo "1. 🔐 AUTHENTICATE WITH E*TRADE:"
echo "   source venv/bin/activate"
echo "   python3 src/main.py interactive"
echo "   Select option 1 to authenticate"
echo ""
echo "2. 🧪 TEST THE SYSTEM:"
echo "   ./scripts/run_bot.sh check    # Check for trades"
echo "   ./scripts/run_bot.sh monitor  # Test stop-loss"
echo "   ./monitor.sh                  # View system status"
echo ""
echo "3. 🚀 START AUTOMATED TRADING:"
echo "   ./start_trading.sh            # Start background trading"
echo "   OR"
echo "   Let cron jobs handle it (already scheduled)"
echo ""
echo "4. 📱 TELEGRAM NOTIFICATIONS:"
if [ -n "$TELEGRAM_TOKEN" ]; then
    echo "   ✅ Configured - you'll receive alerts for:"
    echo "     • New congressional trades"
    echo "     • Trade executions"
    echo "     • Stop-loss triggers"
    echo "     • Daily summaries"
else
    echo "   ⚠ Not configured - edit config/config.json to add:"
    echo "     'botToken': 'YOUR_TOKEN',"
    echo "     'chatId': 'YOUR_CHAT_ID'"
fi
echo ""
echo "5. 📊 MONITOR PERFORMANCE:"
echo "   ./monitor.sh                  # System dashboard"
echo "   tail -f logs/trading.log      # Live logs"
echo "   python3 src/main.py interactive  # Manual control"
echo ""
echo "6. ⚙️ CRON SCHEDULE:"
echo "   8 AM Mon-Fri: Morning trade check"
echo "   6 PM Mon-Fri: Evening trade check"
echo "   10AM-4PM hourly: Stop-loss monitoring"
echo ""
echo "${GREEN}Your automated congressional trading system is ready!${NC}"
echo ""
echo "📖 For more details:"
echo "   • Run backtests: python3 src/backtester.py"
echo "   • View strategy: config/config.json"
echo "   • Check logs: logs/trading.log"
echo ""