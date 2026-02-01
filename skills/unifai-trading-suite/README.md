# AI Trader for Prediction Markets

An AI-powered trading agent for prediction markets that leverages LLMs to create and execute trading strategies based on social network signals and on-chain analysis.

## Features

- **Multi-Platform Support**: Trade on Polymarket and Kalshi prediction markets
- **Social Signal Analysis**: Track KOL mentions, sentiment, and trending tokens
- **LLM-Powered Strategies**: Uses Google Gemini 3.0 Flash for intelligent analysis
- **UnifAI Integration**: Dynamic tool discovery and agent-to-agent communication
- **Web Interface**: Simple chat-based frontend for trading queries
- **Moltbot Skills**: Packaged as reusable skills for AI agents

## Quick Start

### Prerequisites

- Python 3.10+
- UnifAI API key (for social signals and Polymarket)
- Google API key (for Gemini LLM)

### Installation

```bash
# Clone the repository
git clone https://github.com/zbruceli/trading.git
cd trading

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

```bash
export UNIFAI_AGENT_API_KEY="your-unifai-key"
export GOOGLE_API_KEY="your-google-key"
export LLM_MODEL="gemini/gemini-3-flash-preview"
```

### Running

```bash
# Run the trading agent demo
python -m src.agents.trading_agent --demo

# Interactive mode
python -m src.agents.trading_agent

# Start web interface
uvicorn src.api.server:app --port 8080
```

## Usage

### Trading Agent

```python
from src.agents import TradingAgent

agent = TradingAgent()

# Analyze a token with price + social + news signals
analysis = await agent.analyze_token("SOL")

# Get trending tokens from KOL discussions
trending = await agent.get_trending_signals()

# Natural language queries
response = await agent.chat("Get ETH price and recent news")
```

### Kalshi Markets

```python
from src.markets import KalshiClient

client = KalshiClient()

# Get Fed interest rate markets
fed_markets = await client.get_fed_markets(limit=10)

# Search markets
results = await client.search_markets("bitcoin", limit=5)
```

### Social Signals

```python
from src.signals import SocialSignalProcessor

processor = SocialSignalProcessor()

# Get token sentiment
sentiment = await processor.get_token_sentiment("ETH")

# Get trending tokens from KOLs
trending = await processor.get_trending_tokens(time_window="24h")
```

## Prediction Market Integrations

| Platform | Integration | Market Types |
|----------|-------------|--------------|
| **Polymarket** | UnifAI SDK | Crypto, politics, sports |
| **Kalshi** | Direct API | Economics, politics, events |

## Project Structure

```
trading/
├── src/
│   ├── agents/        # Trading agents
│   ├── api/           # Web API & frontend
│   ├── markets/       # Market clients (Kalshi, Polymarket)
│   ├── signals/       # Social signal processors
│   └── strategies/    # Trading strategies
├── skills/            # Moltbot skill definitions
└── tests/
```

## Moltbot Skills

Pre-packaged skills for AI agent platforms:

- `prediction-trader` - Cross-platform trading assistant
- `kalshi-trader` - Kalshi market queries
- `polymarket-trader` - Polymarket integration
- `social-signals` - Social signal analysis

See [CLAUDE.md](CLAUDE.md) for detailed skill documentation.

## Technology Stack

- **LLM**: Google Gemini 3.0 Flash (via LiteLLM)
- **Agent Framework**: UnifAI SDK
- **Skills Platform**: Moltbot (AgentSkills-compatible)
- **Language**: Python 3.10+

## License

MIT

## References

- [UnifAI SDK](https://github.com/unifai-network/unifai-sdk-py)
- [LiteLLM](https://docs.litellm.ai/)
- [Kalshi API](https://docs.kalshi.com)
- [Polymarket](https://docs.polymarket.com)
