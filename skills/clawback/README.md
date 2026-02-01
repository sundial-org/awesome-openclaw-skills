# ClawBack - Congressional Trade Mirror Bot

## Overview
Automated trading application that mirrors congressional stock trades using broker APIs, scaling trade amounts relative to account size. Includes comprehensive congressional trade data collection from official government sources.

## Architecture

### Core Trading Components:
1. **Congressional Tracker** - Fetches trade data from Senate and House official disclosures
2. **Broker Adapter** - Handles authentication and trading operations (E*TRADE adapter included)
3. **Account Monitor** - Tracks account balance and positions
4. **Trade Calculator** - Scales congressional trades to user's account size
5. **Execution Engine** - Places and manages orders
6. **Safety Controller** - Implements risk management and failsafes

### Congressional Data System:
7. **Data Sources** - Official Senate eFD and House Clerk disclosures
8. **Alert Manager** - Sends alerts for significant trades via Telegram
9. **Cron Scheduler** - Automated daily data collection (9 AM weekdays)
10. **Broker Integration** - Creates trading recommendations from alerts

### Data Flow:
1. **Daily Collection** (9 AM weekdays):
   - Fetch congressional trade data from official sources
   - Parse PDFs (House Clerk) and scrape Senate eFD
   - Generate alerts for significant trades (>$50K)

2. **Trading Pipeline**:
   - Process congressional trade alerts
   - Calculate scaled trade amounts based on account balance
   - Validate trades (risk checks, market hours)
   - Place orders via broker API
   - Monitor execution and update positions

## Configuration

### Main Configuration (`config/config.json`):
- Broker API credentials (generic naming supports multiple brokers)
- Trade scaling ratio (percentage of account to allocate)
- Risk limits (max position size, stop losses)
- Trading hours restrictions

### Congressional Data Configuration (`config/congress_config.json`):
- Data source settings (Senate, House)
- Politician tracking list (Pelosi, Crenshaw, Tuberville, Greene)
- Alert thresholds and Telegram settings
- Cron schedule and data retention

## Safety Features
- Maximum position size limits
- Daily loss limits
- Market hours validation
- Manual override capability
- Comprehensive logging and monitoring
- Alert system for significant trades

## Congressional Data System Features

### Automated Data Collection:
- **Schedule**: Weekdays at 9 AM EST (configurable)
- **Sources**: Official Senate eFD and House Clerk disclosures
- **Politicians**: Track specific politicians or all
- **Thresholds**: Minimum trade size filtering

### Alert System:
- **Telegram Integration**: Instant notifications
- **Broker Integration**: Automated trading recommendations
- **Thresholds**: Configurable trade size alerts (>$50K default)

## OpenClaw Skill Integration

ClawBack is also available as an OpenClaw skill for easy installation and management:

### Install as OpenClaw Skill:
```bash
# Install from local directory
clawhub install ./clawback

# Or copy to skills directory
cp -r . ~/.openclaw/skills/clawback
cd ~/.openclaw/skills/clawback
./setup.sh
```

### Skill Features:
- **Automated setup** with virtual environment
- **Environment-based configuration** (.env file)
- **OpenClaw metadata** for automatic skill loading
- **Comprehensive testing** suite
- **Skill-specific documentation** (SKILL_README.md)

## Quick Start

### Option 1: Standard Installation
```bash
cd clawback
pip3 install -r requirements.txt
```

### Option 2: OpenClaw Skill Installation
```bash
# Install and setup
clawhub install ./clawback
cd ~/.openclaw/skills/clawback
./setup.sh
```

### Configure Secrets:
```bash
# Run interactive setup
python3 src/config_loader.py setup

# Or manually edit secrets
nano config/secrets.json

# For OpenClaw skill, edit .env file
nano .env
```

### Authenticate with Broker:
```bash
# Run interactive mode
python3 src/main.py interactive
# Select option 1 to authenticate
```

### Set Up Automation:
```bash
# Install cron jobs
./scripts/setup_cron.sh
```

### Run the System:
```bash
# Check for new trades
./scripts/run_bot.sh check

# Monitor stop-losses
./scripts/run_bot.sh monitor

# Run both
./scripts/run_bot.sh full
```

## Documentation
- **Congressional Data System**: [docs/CONGRESSIONAL_DATA.md](docs/CONGRESSIONAL_DATA.md)
- **Skill Documentation**: [SKILL.md](SKILL.md)

## Monitoring & Maintenance

### Logs:
- `logs/trading.log` - Main trading log
- `data/congress_trades/` - Congressional trade data

### Maintenance:
- Daily: Check logs and alerts
- Weekly: Review statistics and performance
- Monthly: Clean up old data and update configurations

## Security Considerations
- API keys stored in `config/secrets.json` (git-ignored)
- Environment variable substitution for sensitive values
- No personal information beyond public disclosures
- Rate limiting for web scraping

## Supported Brokers

ClawBack uses an adapter pattern for broker integration. Each broker implements the interface defined in `broker_adapter.py`.

| Broker | Adapter | Status |
|--------|---------|--------|
| E*TRADE | `etrade_adapter.py` | Supported |
| Schwab | `schwab_adapter.py` | Planned |
| Fidelity | `fidelity_adapter.py` | Planned |

## Support & Troubleshooting
- Check logs in `logs/` directory
- Review configuration files
- Test individual components
- Consult documentation

---

**Version**: 1.0.0
**Last Updated**: January 2026
**Compatibility**: Python 3.8+
