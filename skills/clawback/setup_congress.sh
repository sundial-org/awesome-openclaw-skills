#!/bin/bash
# Setup script for Congressional Trade Data Collection System

echo "================================================"
echo "ClawBack - Congressional Trade Data Setup"
echo "================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create directories
echo ""
echo "Creating directories..."
mkdir -p config data/{congress_trades,senate,house,backups} logs

# Create default congressional config
echo ""
echo "Creating default congressional configuration..."
python3 -c "
import json
import os

config = {
    'sources': {
        'senate': {
            'enabled': True,
            'url': 'https://efdsearch.senate.gov/search/',
            'check_interval_hours': 24,
            'min_trade_amount': 1000,
            'data_dir': 'data/senate'
        },
        'house': {
            'enabled': True,
            'url': 'https://disclosures-clerk.house.gov/FinancialDisclosure',
            'check_interval_hours': 24,
            'min_trade_amount': 1000,
            'data_dir': 'data/house'
        }
    },
    'politicians': {
        'track_all': False,
        'specific_politicians': [
            'Nancy Pelosi',
            'Dan Crenshaw',
            'Tommy Tuberville',
            'Marjorie Taylor Greene'
        ],
        'minimum_trade_size': 10000,
        'tracked_positions': ['Senator', 'Representative', 'Speaker']
    },
    'alerting': {
        'enabled': False,
        'telegram_bot_token': '',
        'telegram_chat_id': '',
        'minimum_trade_size_alert': 50000,
        'alert_on_buys': True,
        'alert_on_sells': True
    },
    'storage': {
        'data_directory': 'data/congress_trades',
        'max_days_to_keep': 90,
        'backup_enabled': True,
        'backup_directory': 'data/backups'
    },
    'cron': {
        'enabled': True,
        'schedule': '0 9 * * 1-5',
        'timezone': 'America/New_York',
        'run_on_startup': True
    }
}

config_path = 'config/congress_config.json'
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f'Default config created at {config_path}')
"

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next Steps:"
echo "1. Configure secrets: python3 src/config_loader.py setup"
echo "2. Run interactive mode: python3 src/main.py interactive"
echo "3. Set up cron jobs: ./scripts/setup_cron.sh"
echo ""
echo "Data Sources:"
echo "   - House Clerk: PDF parsing with pdfplumber"
echo "   - Senate eFD: Web scraping with Selenium"
echo ""
echo "Documentation: See docs/CONGRESSIONAL_DATA.md"
echo "================================================"
