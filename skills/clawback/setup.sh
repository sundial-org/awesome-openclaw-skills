#!/bin/bash

# ClawBack Congressional Trading System - Setup Script
# This script sets up the complete system for OpenClaw skill installation

set -e

echo "🚀 ClawBack Congressional Trading System Setup"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Must run from ClawBack project directory"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Install with: brew install python3"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install additional dependencies for PDF parsing
echo "📄 Installing PDF parsing dependencies..."
pip install pdfplumber

# Check for ChromeDriver (for Senate scraping)
if ! command -v chromedriver &> /dev/null; then
    echo "⚠️  ChromeDriver not found. Senate data scraping may not work."
    echo "Install with: brew install --cask chromedriver"
fi

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p logs data config

# Copy sample config if it doesn't exist
if [ ! -f "config/config.json" ]; then
    if [ -f "config/config.template.json" ]; then
        cp config/config.template.json config/config.json
        echo "✅ Created config/config.json from template"
    else
        echo "⚠️  Config template not found, creating basic config..."
        cat > config/config.json << 'EOF'
{
  "broker": {
    "adapter": "etrade",
    "environment": "sandbox",
    "credentials": {
      "apiKey": "${ETRADE_API_KEY}",
      "apiSecret": "${ETRADE_API_SECRET}"
    }
  },
  "trading": {
    "accountId": "${ETRADE_ACCOUNT_ID}",
    "initialCapital": 50000,
    "tradeScalePercentage": 0.02,
    "maxPositionPercentage": 0.10,
    "maxPositions": 10,
    "dailyLossLimit": 0.01,
    "portfolioStopLoss": 0.15,
    "positionStopLoss": 0.08,
    "tradeDelayDays": 3,
    "holdingPeriodDays": 30,
    "marketHoursOnly": true,
    "marketOpen": "09:30",
    "marketClose": "16:00"
  }
}
EOF
        echo "✅ Created basic config/config.json"
    fi
fi

# Create .env.example file
echo "📝 Creating environment configuration..."
cat > .env.example << 'EOF'
# ClawBack Congressional Trading System
# Copy to .env and fill in your credentials
# NEVER commit .env to version control!

# E*TRADE API Credentials (required)
# Get from https://developer.etrade.com
ETRADE_API_KEY=your_api_key_here
ETRADE_API_SECRET=your_api_secret_here
ETRADE_ACCOUNT_ID=your_account_id_here

# Telegram Bot (optional)
# Create bot via @BotFather, get token
# Get chat ID via @userinfobot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Financial Modeling Prep API (optional)
# Get from https://financialmodelingprep.com/developer
FMP_API_KEY=your_fmp_api_key_here
EOF

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file (edit with your credentials)"
    echo "⚠️  IMPORTANT: Edit .env file with your API keys before running!"
else
    echo "✅ .env file already exists"
fi

# Run basic tests
echo "🧪 Running basic system checks..."
if python3 -c "import pdfplumber; import selenium; import yfinance; print('✅ Python dependencies OK')"; then
    echo "✅ Python dependencies verified"
else
    echo "❌ Python dependency check failed"
    exit 1
fi

# Test config loading
echo "🔧 Testing configuration loading..."
if python3 -c "
import sys
import os
sys.path.append('src')
try:
    # Try to import config_loader from clawback package
    from clawback.config_loader import load_config
    config = load_config('config/config.json')
    print('✅ Config loading works (clawback package)')
except ImportError as e:
    try:
        # Fallback: check if config_loader.py exists directly
        import importlib.util
        spec = importlib.util.spec_from_file_location('config_loader', 'src/clawback/config_loader.py')
        if spec is not None:
            config_loader = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_loader)
            config = config_loader.load_config('config/config.json')
            print('✅ Config loading works (direct import)')
        else:
            print(f'⚠️  Config loader not found: {e}')
    except Exception as e2:
        print(f'⚠️  Config loading test: {e2}')
        print('   (This is expected if config_loader has unmet dependencies)')
except Exception as e:
    print(f'⚠️  Config loading error: {e}')
    print('   (This may be due to missing environment variables)')
"; then
    echo "✅ Configuration test completed"
else
    echo "⚠️  Configuration test had issues"
fi

echo ""
echo "🎉 Setup Complete!"
echo "================="
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Test the system:"
echo "   python3 src/main.py interactive"
echo ""
echo "3. Set up automation (optional):"
echo "   ./scripts/setup_cron.sh"
echo ""
echo "4. Run backtest to validate strategy:"
echo "   python3 src/backtester.py"
echo ""
echo "Documentation:"
echo "- Read QUICK_START.md for quick start guide"
echo "- Read AUTOMATED_SYSTEM_SUMMARY.md for system overview"
echo "- Read CONGRESSIONAL_DATA.md for data source details"
echo ""
echo "For OpenClaw skill installation:"
echo "1. Install skill: clawhub install ./clawback"
echo "2. Or copy to skills directory: cp -r . ~/.openclaw/skills/clawback"
echo ""
echo "⚠️  Remember: This is for educational purposes only."
echo "    Trading involves risk. Use at your own discretion."