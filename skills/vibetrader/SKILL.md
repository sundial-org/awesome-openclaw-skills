---
name: vibetrader
description: Create and manage AI-powered trading bots via natural language. Paper & live trading, portfolio monitoring, backtesting, stock quotes, and options chains.
homepage: https://vibetrader.markets
metadata: {"openclaw":{"homepage":"https://vibetrader.markets","category":"finance","requires":{"env":["VIBETRADER_API_KEY"]}}}
---

# VibeTrader - AI Trading Bots

Create and manage AI-powered trading bots using natural language. Trade stocks, ETFs, crypto, and options with automated strategies.

## What You Can Do

### 🤖 Bot Management
- **Create bots** from natural language: "Create a bot that buys AAPL when RSI drops below 30"
- **List, start, pause, delete** your bots
- **View bot performance** and trade history
- **Backtest strategies** before going live

### 📊 Portfolio & Trading
- **View positions** and account balance
- **Get real-time quotes** for stocks, ETFs, and crypto
- **Place manual orders** (buy/sell)
- **Switch between paper and live trading**

### 📈 Market Data
- Stock and ETF quotes
- Options chains with Greeks
- Market status checks

## Setup

1. **Get your API key** from [vibetrader.markets/settings](https://vibetrader.markets/settings)

2. **Set the environment variable** in your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "skills": {
    "entries": {
      "vibetrader": {
        "env": {
          "VIBETRADER_API_KEY": "vt_your_api_key_here"
        }
      }
    }
  }
}
```

Or export it in your shell:
```bash
export VIBETRADER_API_KEY="vt_your_api_key_here"
```

## Available Tools

| Tool | Description |
|------|-------------|
| `authenticate` | Connect with your API key (auto-uses env var if set) |
| `create_bot` | Create a trading bot from natural language |
| `list_bots` | List all your bots with status |
| `get_bot` | Get detailed bot info and strategy |
| `start_bot` | Start a paused bot |
| `pause_bot` | Pause a running bot |
| `delete_bot` | Delete a bot |
| `get_portfolio` | View positions and balance |
| `get_positions` | View current open positions |
| `get_account_summary` | Get account balance and buying power |
| `place_order` | Place a buy/sell order |
| `close_position` | Close an existing position |
| `get_quote` | Get stock/ETF/crypto quotes |
| `get_trade_history` | See recent trades |
| `run_backtest` | Backtest a bot's strategy |
| `get_market_status` | Check if markets are open |

## Example Prompts

### Create Trading Bots
- "Create a momentum bot that buys TSLA when RSI crosses below 30 and sells above 70"
- "Make an NVDA bot with a 5% trailing stop loss"
- "Create a crypto scalping bot for BTC/USD on the 5-minute chart"
- "Build an iron condor bot for SPY when IV rank is above 50"

### Manage Your Bots
- "Show me all my bots and how they're performing"
- "Pause my AAPL momentum bot"
- "What trades did my bots make today?"
- "Delete all my paused bots"

### Portfolio Management
- "What's my current portfolio value?"
- "Show my open positions with P&L"
- "Buy $500 worth of NVDA"
- "Close my TSLA position"

### Market Research
- "What's the current price of Apple stock?"
- "Get the options chain for SPY expiring this Friday"
- "Is the market open right now?"

### Backtesting
- "Backtest my RSI bot on the last 30 days"
- "How would a moving average crossover strategy have performed on QQQ?"

## Trading Modes

- **Paper Trading** (default): Practice with virtual money, no risk
- **Live Trading**: Real money trades via Alpaca brokerage

Switch modes with: "Switch to live trading mode" or "Use paper trading"

## MCP Server

This skill connects to the VibeTrader MCP server at:
```
https://vibetrader-mcp-289016366682.us-central1.run.app/mcp
```

## Support

- Website: [vibetrader.markets](https://vibetrader.markets)
- Documentation: [vibetrader.markets/docs](https://vibetrader.markets/docs)
