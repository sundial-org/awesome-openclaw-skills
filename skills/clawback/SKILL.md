---
name: clawback
description: Mirror congressional stock trades with automated broker execution and risk management. Use when you want to track and automatically trade based on congressional disclosures from House Clerk and Senate eFD sources.
version: 1.0.1
author: mainfraame
homepage: https://github.com/mainfraame/clawback
user-invocable: true
metadata:
  openclaw:
    emoji: "🦀"
    requires:
      bins:
        - python3
        - pip
      config:
        - channels.telegram.botToken
    install:
      pip: "{baseDir}"
    primaryEnv: BROKER_API_KEY
---

# ClawBack

**Mirror congressional stock trades with automated broker execution**

ClawBack tracks stock trades disclosed by members of Congress (House and Senate) and executes scaled positions in your brokerage account. Built on the premise that congressional leaders consistently outperform the market due to informational advantages.

## Features

- **Real-time disclosure tracking** from official House Clerk and Senate eFD sources
- **Automated trade execution** via broker API (E*TRADE adapter included)
- **Smart position sizing** - scales trades to your account size
- **Trailing stop-losses** - lock in profits, limit losses
- **Risk management** - drawdown limits, consecutive loss protection
- **Telegram notifications** - get alerts for new trades and stop-losses
- **Backtesting engine** - test strategies on historical data

## Performance (Backtest Results)

| Strategy | Win Rate | Return | Sharpe |
|----------|----------|--------|--------|
| 3-day delay, 30-day hold | 42.9% | +6.2% | 0.39 |
| 9-day delay, 90-day hold | 57.1% | +4.7% | 0.22 |

Congressional leaders have outperformed the S&P 500 by 47% annually according to NBER research.

## Quick Start

```bash
# Install via ClawHub (includes pip package)
clawhub install clawback

# Run setup wizard (credentials, auth, account selection, Telegram)
clawback setup

# Start the trading bot
clawback run
```

### Alternative: Install from GitHub

```bash
git clone https://github.com/mainfraame/clawback
cd clawback
pip install -e .
clawback setup
```

## Configuration

### Broker Credentials

ClawBack reads broker secrets from environment variables or `~/.clawback/secrets.json`:

```json
{
  "BROKER_API_KEY": "your-broker-api-key",
  "BROKER_API_SECRET": "your-broker-api-secret",
  "BROKER_ACCOUNT_ID": "your-account-id"
}
```

### Telegram Notifications

**When running as OpenClaw skill:** ClawBack uses OpenClaw's built-in Telegram channel. Configure once in `~/.openclaw/openclaw.json`:

```json
{
  "channels": {
    "telegram": {
      "botToken": "YOUR_BOT_TOKEN_FROM_BOTFATHER",
      "dmPolicy": "pairing"
    }
  }
}
```

Then pair your Telegram account:
1. Message `/start` to your bot
2. Run: `openclaw pairing approve telegram <code>`

**When running standalone:** Add Telegram credentials to your secrets:

```json
{
  "TELEGRAM_BOT_TOKEN": "your-bot-token",
  "TELEGRAM_CHAT_ID": "your-chat-id"
}
```

### Supported Brokers

ClawBack uses an adapter pattern for broker integration. Each broker implements a common interface defined in `broker_adapter.py`.

| Broker | Adapter | Status |
|--------|---------|--------|
| E*TRADE | `etrade_adapter.py` | Supported |
| Schwab | `schwab_adapter.py` | Planned |
| Fidelity | `fidelity_adapter.py` | Planned |

To specify which broker to use, set `broker.adapter` in your config:

```json
{
  "broker": {
    "adapter": "etrade",
    "credentials": {
      "apiKey": "${BROKER_API_KEY}",
      "apiSecret": "${BROKER_API_SECRET}"
    }
  }
}
```

## Data Sources

All data is scraped directly from official government sources:

| Source | Data | Method |
|--------|------|--------|
| House Clerk | House PTR filings | PDF parsing |
| Senate eFD | Senate PTR filings | Selenium scraping |

No third-party APIs required for congressional data.

## Strategy Settings

Edit `config/config.json` to customize:

```json
{
  "strategy": {
    "entryDelayDays": 3,
    "holdingPeriodDays": 30,
    "purchasesOnly": true,
    "minimumTradeSize": 50000
  },
  "riskManagement": {
    "positionStopLoss": 0.08,
    "trailingStopActivation": 0.10,
    "trailingStopPercent": 0.05,
    "maxDrawdown": 0.15
  }
}
```

## Commands

```bash
# Run setup wizard
clawback setup

# Start interactive trading mode
clawback run

# Run as background daemon (with token refresh)
clawback daemon

# Check system status
clawback status

# Test Telegram notifications
clawback test
```

## Automated Trading

The `clawback daemon` command runs continuously with:
- **Disclosure checks** at 10:00, 14:00, 18:00 ET (when filings are typically released)
- **Trade execution** at 9:35 AM ET (5 min after market open)
- **Token refresh** every 90 minutes (keeps broker session alive)
- **Market hours enforcement** (9:30 AM - 4:00 PM ET)

## Architecture

```
clawback/
├── src/clawback/
│   ├── cli.py               # CLI entry point (clawback command)
│   ├── main.py              # Trading bot controller
│   ├── congress_tracker.py  # Congressional data collection
│   ├── trade_engine.py      # Trade execution & risk management
│   ├── broker_adapter.py    # Abstract broker interface
│   ├── etrade_adapter.py    # E*TRADE broker implementation
│   ├── database.py          # SQLite state management (incl. tokens)
│   ├── telegram_notifier.py # Telegram notifications
│   └── config_loader.py     # Configuration handling
├── pyproject.toml           # Python package configuration
├── SKILL.md                 # OpenClaw skill definition
└── ~/.clawback/             # User config directory
    ├── config.json          # Main configuration
    ├── secrets.json         # API keys
    └── data/trading.db      # SQLite database
```

## Risk Disclaimer

This software is for educational purposes only. Trading stocks involves substantial risk of loss. Past performance of congressional trades does not guarantee future results. The authors are not financial advisors. Use at your own risk.

## License

MIT License - See LICENSE file

---

*Built for the OpenClaw community. Install via `clawhub install clawback` or `pip install clawback`.*
