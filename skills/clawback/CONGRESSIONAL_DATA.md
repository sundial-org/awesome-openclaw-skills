# Congressional Trade Data Collection System

## Overview

This system automatically collects, processes, and alerts on stock trades by US Senators and Representatives, integrating with the broker trading bot for automated trading based on congressional activity.

## Key Features

- **Automated Data Collection**: Fetches trade data from official government sources
- **Smart Alerting**: Sends alerts for significant trades (>$50K) via Telegram
- **Cron Job Scheduling**: Runs automatically on weekdays at 9 AM EST
- **Broker Integration**: Creates trading recommendations based on congressional trades
- **Comprehensive Tracking**: Monitors key politicians (Pelosi, Crenshaw, Tuberville, Greene)
- **Data Retention**: Stores 90 days of historical data with automatic cleanup

## Data Sources

### Official Government Sources:
1. **Senate Financial Disclosures**: `https://efdsearch.senate.gov/search/`
   - Scraped via Selenium headless browser
2. **House Financial Disclosures**: `https://disclosures-clerk.house.gov/FinancialDisclosure`
   - Parsed from official PDF filings with pdfplumber

## Configuration

### Main Configuration File: `config/congress_config.json`

```json
{
  "sources": {
    "senate": {
      "enabled": true,
      "check_interval_hours": 24,
      "min_trade_amount": 1000
    },
    "house": {
      "enabled": true,
      "check_interval_hours": 24,
      "min_trade_amount": 1000
    }
  },
  "politicians": {
    "track_all": false,
    "specific_politicians": [
      "Nancy Pelosi",
      "Dan Crenshaw",
      "Tommy Tuberville",
      "Marjorie Taylor Greene"
    ],
    "minimum_trade_size": 10000
  },
  "alerting": {
    "enabled": true,
    "minimum_trade_size_alert": 50000,
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID"
  },
  "cron": {
    "enabled": true,
    "schedule": "0 9 * * 1-5",
    "timezone": "America/New_York"
  }
}
```

## Quick Start

### 1. Install Dependencies
```bash
cd clawback
pip3 install -r requirements.txt
```

### 2. Configure the System
```bash
# Edit the configuration file
nano config/congress_config.json
```

### 3. Test the System
```bash
# Run interactive mode
python3 src/main.py interactive

# Or run a single check
python3 src/main.py run
```

### 4. Set Up Automation
```bash
# Set up cron jobs
./scripts/setup_cron.sh
```

## Cron Schedule

### Default Schedule: `0 9 * * 1-5`
- **Time**: 9:00 AM EST
- **Days**: Monday through Friday
- **Frequency**: Once per business day

### Why This Schedule?
- Government offices are open weekdays
- Trades are typically filed during business hours
- Morning check catches overnight filings
- Aligns with market hours for timely trading

## Alert System

### Alert Triggers:
1. **Trade Size**: > $50,000 (configurable)
2. **Politician**: Tracked politicians only (unless `track_all: true`)
3. **Recency**: Trades within last 7 days
4. **Transaction Type**: Buys and/or sells (configurable)

### Setting Up Telegram Alerts:
1. Create a bot via @BotFather on Telegram
2. Get your bot token
3. Get your chat ID (send message to @userinfobot)
4. Add to config in `config/secrets.json`

## Data Storage

### Directory Structure:
```
data/congress_trades/
├── senate/              # Senate trade data
├── house/               # House trade data
├── etrade_alerts/       # Alerts for broker integration
├── logs/                # Run history
└── alert_history.json   # Sent alerts tracking

data/trading_recommendations/
├── congress_*.json      # Individual recommendations
└── latest_congressional_recommendations.json
```

### Retention Policy:
- **Trade Data**: 90 days (configurable)
- **Log Files**: 30 days
- **Alert History**: 30 days

## Troubleshooting

### Common Issues:

1. **No Data Collected**
   - Check internet connection
   - Verify source URLs are accessible
   - Review logs for errors

2. **Cron Job Not Running**
   - Verify cron service is running: `systemctl status cron`
   - Check crontab: `crontab -l`
   - Test manual execution: `./scripts/run_bot.sh check`

3. **Alerts Not Sending**
   - Verify Telegram bot token and chat ID
   - Review alert thresholds
   - Check logs/trading.log for errors

## References

### Official Sources:
- [Senate Financial Disclosures](https://efdsearch.senate.gov/search/)
- [House Financial Disclosures](https://disclosures-clerk.house.gov/FinancialDisclosure)
- [STOCK Act Information](https://www.congress.gov/bill/112th-congress/house-bill/1148)

---

**Last Updated**: January 2026
**Version**: 1.0.0
**Compatibility**: Python 3.8+
