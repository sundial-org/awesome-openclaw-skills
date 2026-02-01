# VibeTrader Skill for OpenClaw

Create and manage AI-powered trading bots directly from WhatsApp, Telegram, Slack, Discord, or any other OpenClaw channel.

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install vibetrader
```

### Manual Installation

Copy this folder to your OpenClaw skills directory:

```bash
cp -r openclaw-skill ~/.openclaw/skills/vibetrader
```

## Configuration

1. **Get your API key** from [vibetrader.markets/settings](https://vibetrader.markets/settings)

2. **Add to your OpenClaw config** (`~/.openclaw/openclaw.json`):

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

3. **Restart OpenClaw** to pick up the new skill

## Usage Examples

Once installed, just chat naturally with your OpenClaw assistant:

### Create Bots
> "Create a trading bot that buys AAPL when RSI drops below 30"

> "Make an NVDA momentum bot with a 5% trailing stop"

> "Build a crypto scalping bot for BTC/USD"

### Manage Portfolio
> "What's my portfolio value?"

> "Show my open positions"

> "Buy $500 of TSLA"

### Monitor Bots
> "Show me all my bots"

> "Pause my AAPL bot"

> "How did my bots perform today?"

### Market Data
> "What's the current price of Apple?"

> "Is the market open?"

## Features

- 🤖 **Natural Language Bot Creation** - Describe your strategy, AI builds the bot
- 📊 **Portfolio Tracking** - Real-time positions and P&L
- 📈 **Live & Paper Trading** - Practice risk-free or trade for real
- ⏱️ **Backtesting** - Test strategies on historical data
- 🔔 **Multi-Channel** - Manage from WhatsApp, Telegram, Slack, etc.

## Links

- **Website**: https://vibetrader.markets
- **Get API Key**: https://vibetrader.markets/settings
- **Documentation**: https://vibetrader.markets/docs

## License

MIT
