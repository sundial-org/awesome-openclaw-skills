#!/bin/bash

# Setup script for Congressional Data → Broker Trading Integration

set -e

echo "🔗 Setting up Congressional Data to Broker Trading Integration"
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi
python_version=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $python_version found${NC}"

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
cd "$(dirname "$0")"
pip3 install -r src/requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create necessary directories
echo -e "\n${YELLOW}Creating data directories...${NC}"
mkdir -p data/congress_trades/etrade_alerts
mkdir -p data/trading_recommendations
mkdir -p logs/congress_data
mkdir -p logs/trading
echo -e "${GREEN}✓ Directories created${NC}"

# Check configuration files
echo -e "\n${YELLOW}Checking configuration files...${NC}"

if [ ! -f "config/config.json" ]; then
    echo -e "${RED}✗ Main config file not found: config/config.json${NC}"
    echo "Creating template config..."
    cat > config/config.json << 'EOF'
{
  "etrade": {
    "sandbox": {
      "consumer_key": "cde63877b06b844b59b5c23b0d3ad7f7",
      "consumer_secret": "ff190254629156cb6f9fc95adcb7eb73610aeda21b76864621e4752463c42aa4"
    },
    "production": {
      "consumer_key": "",
      "consumer_secret": ""
    },
    "use_sandbox": true,
    "account_id": ""
  },
  "trading": {
    "tradeScalePercentage": 0.01,
    "maxPositionPercentage": 0.05,
    "dailyLossLimit": 0.02,
    "marketHoursOnly": true,
    "maxTradesPerDay": 10,
    "minPelosiTradeSize": 10000
  },
  "logging": {
    "level": "INFO",
    "directory": "logs"
  }
}
EOF
    echo -e "${YELLOW}⚠ Created template config. Please edit with your settings.${NC}"
else
    echo -e "${GREEN}✓ Main config file found${NC}"
fi

if [ ! -f "config/congress_config.json" ]; then
    echo -e "${RED}✗ Congressional config file not found${NC}"
    echo "Creating default congressional config..."
    python3 -c "from src.congress_data.config import CongressConfig; config = CongressConfig('config/congress_config.json')"
    echo -e "${GREEN}✓ Congressional config created${NC}"
else
    echo -e "${GREEN}✓ Congressional config file found${NC}"
fi

# Set up cron job
echo -e "\n${YELLOW}Setting up cron job for automated data collection...${NC}"
python3 src/congress_data/setup_cron.py setup
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cron job scheduled (9 AM Monday-Friday)${NC}"
else
    echo -e "${YELLOW}⚠ Could not set up cron job automatically${NC}"
    echo "You can manually add to crontab:"
    echo "0 9 * * 1-5 cd $(pwd) && src/congress_data/run_cron.sh"
fi

# Test the integration
echo -e "\n${YELLOW}Testing the integration...${NC}"

echo "1. Testing congressional data collection..."
python3 src/congress_data/main.py once --verbose
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Congressional data collection working${NC}"
else
    echo -e "${YELLOW}⚠ Congressional data collection test had issues${NC}"
fi

echo -e "\n2. Testing alert system..."
python3 src/congress_data/main.py test-alerts
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Alert system working${NC}"
else
    echo -e "${YELLOW}⚠ Alert system test had issues${NC}"
fi

echo -e "\n3. Testing Broker integration..."
python3 src/congress_data/broker_integration.py process
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Broker integration working${NC}"
else
    echo -e "${YELLOW}⚠ Broker integration test had issues${NC}"
fi

# Create systemd service for continuous monitoring (optional)
echo -e "\n${YELLOW}Setting up continuous monitoring service...${NC}"
read -p "Set up systemd service for continuous monitoring? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 src/congress_data/setup_cron.py systemd
    echo -e "${GREEN}✓ Systemd service created${NC}"
    echo "To start: systemctl --user start congress-trade-collector.service"
    echo "To enable on boot: systemctl --user enable congress-trade-collector.service"
else
    echo -e "${YELLOW}⚠ Skipping systemd service setup${NC}"
fi

# Create automated trading script
echo -e "\n${YELLOW}Creating automated trading script...${NC}"
cat > run_automated_trading.sh << 'EOF'
#!/bin/bash

# Automated Trading Script
# Runs congressional data collection → Broker integration → Trading

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs/trading"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/automated_trading_${TIMESTAMP}.log"

echo "==========================================" | tee -a "$LOG_FILE"
echo "Automated Trading Run - $(date)" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"

# Step 1: Collect congressional data
echo "Step 1: Collecting congressional trade data..." | tee -a "$LOG_FILE"
cd "$SCRIPT_DIR"
python3 src/congress_data/main.py once 2>&1 | tee -a "$LOG_FILE"

# Step 2: Process alerts for trading
echo -e "\nStep 2: Processing alerts for trading..." | tee -a "$LOG_FILE"
python3 src/congress_data/broker_integration.py process 2>&1 | tee -a "$LOG_FILE"

# Step 3: Get trading recommendations
echo -e "\nStep 3: Checking for trading recommendations..." | tee -a "$LOG_FILE"
python3 src/congress_data/broker_integration.py recommendations --limit 5 2>&1 | tee -a "$LOG_FILE"

# Step 4: Execute trades (if in production mode)
echo -e "\nStep 4: Checking if trades should be executed..." | tee -a "$LOG_FILE"

# Check if we should execute trades
CONFIG_FILE="$SCRIPT_DIR/config/config.json"
if [ -f "$CONFIG_FILE" ]; then
    USE_SANDBOX=$(python3 -c "import json; data=json.load(open('$CONFIG_FILE')); print(data.get('etrade', {}).get('use_sandbox', True))")
    
    if [ "$USE_SANDBOX" = "False" ]; then
        echo "PRODUCTION MODE: Would execute trades here" | tee -a "$LOG_FILE"
        # Uncomment to actually execute trades:
        # python3 src/main.py execute --recommendations
    else
        echo "SANDBOX MODE: Trade execution simulated" | tee -a "$LOG_FILE"
        echo "To enable production trading, set 'use_sandbox': false in config.json" | tee -a "$LOG_FILE"
    fi
else
    echo "Config file not found, running in simulation mode" | tee -a "$LOG_FILE"
fi

echo -e "\n==========================================" | tee -a "$LOG_FILE"
echo "Automated Trading Complete" | tee -a "$LOG_FILE"
echo "Log saved to: $LOG_FILE" | tee -a "$LOG_FILE"
echo "==========================================" | tee -a "$LOG_FILE"
EOF

chmod +x run_automated_trading.sh
echo -e "${GREEN}✓ Created automated trading script: ./run_automated_trading.sh${NC}"

# Create monitoring dashboard script
echo -e "\n${YELLOW}Creating monitoring dashboard...${NC}"
cat > monitor_dashboard.sh << 'EOF'
#!/bin/bash

# Monitoring Dashboard for Congressional Trading System

while true; do
    clear
    echo "📊 CONGRESSIONAL TRADING SYSTEM DASHBOARD"
    echo "=========================================="
    echo "Last Updated: $(date)"
    echo ""
    
    # Congressional System Status
    echo "🔍 CONGRESSIONAL DATA SYSTEM"
    echo "----------------------------"
    python3 src/congress_data/main.py stats 2>/dev/null | grep -A20 "CONGRESSIONAL DATA COLLECTION STATISTICS" | tail -n +3
    
    echo ""
    echo "💼 Broker INTEGRATION"
    echo "----------------------"
    python3 src/congress_data/broker_integration.py stats 2>/dev/null | grep -A10 "Broker Integration Statistics" | tail -n +3
    
    echo ""
    echo "📈 RECENT TRADING RECOMMENDATIONS"
    echo "---------------------------------"
    python3 src/congress_data/broker_integration.py recommendations --limit 3 2>/dev/null | grep -A30 "Congressional Trading Recommendations" | tail -n +3
    
    echo ""
    echo "⏰ Next cron run: 9:00 AM $(date -d 'tomorrow' +%A) (weekdays only)"
    echo ""
    echo "Press Ctrl+C to exit. Refreshing in 60 seconds..."
    
    sleep 60
done
EOF

chmod +x monitor_dashboard.sh
echo -e "${GREEN}✓ Created monitoring dashboard: ./monitor_dashboard.sh${NC}"

# Final instructions
echo -e "\n${GREEN}✅ INTEGRATION SETUP COMPLETE${NC}"
echo "================================================================"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. ${YELLOW}Configure Alert Channels:${NC}"
echo "   - Edit config/congress_config.json"
echo "   - Add Telegram bot token for instant alerts"
echo "   - Configure email alerts if desired"
echo ""
echo "2. ${YELLOW}Test Broker Authentication:${NC}"
echo "   python3 src/main.py auth"
echo "   (Follow the OAuth flow in your browser)"
echo ""
echo "3. ${YELLOW}Run Manual Test:${NC}"
echo "   ./run_automated_trading.sh"
echo "   (This tests the complete pipeline)"
echo ""
echo "4. ${YELLOW}Monitor the System:${NC}"
echo "   ./monitor_dashboard.sh"
echo "   (Live dashboard showing system status)"
echo ""
echo "5. ${YELLOW}Schedule Automated Runs:${NC}"
echo "   The cron job is already set for 9 AM weekdays"
echo "   You can also add to crontab:"
echo "   30 9 * * 1-5 $(pwd)/run_automated_trading.sh"
echo ""
echo "6. ${YELLOW}Enable Production Trading:${NC}"
echo "   - Set 'use_sandbox': false in config/config.json"
echo "   - Add production Broker API keys"
echo "   - Test extensively in sandbox first!"
echo ""
echo "📁 IMPORTANT DIRECTORIES:"
echo "   - data/congress_trades/etrade_alerts/ - Congressional trade alerts"
echo "   - data/trading_recommendations/ - Generated trading recommendations"
echo "   - logs/ - System logs"
echo ""
echo "🔧 TROUBLESHOOTING:"
echo "   - Check logs in logs/congress_data/ and logs/trading/"
echo "   - Run tests: python3 src/congress_data/main.py test-alerts"
echo "   - View stats: python3 src/congress_data/main.py stats"
echo ""
echo "================================================================"
echo "🚀 System ready for automated congressional trade mirroring!"
echo "================================================================"