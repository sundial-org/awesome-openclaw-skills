# AI Trader for Prediction Market

## Project Overview

An AI-powered trading agent for prediction markets that leverages LLMs (Google Gemini 3.0 Flash) to create and execute trading strategies based on social network signals and on-chain analysis.

## Project Phases

### Phase 1: UnifAI SDK Experimentation
- Evaluate UnifAI SDK for dynamic tool discovery and agent-to-agent communication
- Build trading strategy creation workflows using Google Gemini 3.0 Flash
- Integrate social network signal processing (Twitter/X, Discord, Telegram)
- Implement on-chain data analysis for market sentiment
- Create reusable toolkits for market data retrieval and trade execution

### Phase 2: Moltbot Skills Integration ✅
- Package trading strategies as Moltbot-compatible Skills
- Create SKILL.md files with proper YAML frontmatter
- Implement skill gating for API keys and dependencies
- Deploy skills to workspace or managed skill directories

**Implemented Skills:**
- `prediction-trader` - Main trading assistant across platforms
- `kalshi-trader` - Kalshi-specific prediction markets
- `polymarket-trader` - Polymarket-specific prediction markets
- `social-signals` - Social signal analysis (KOLs, sentiment, news)

## Technology Stack

- **LLM**: Google Gemini 3.0 Flash (via LiteLLM/OpenRouter)
- **Agent Framework**: UnifAI SDK (`unifai-sdk`)
- **Skills Platform**: Moltbot (AgentSkills-compatible)
- **Language**: Python 3.10+

## Directory Structure

```
trading/
├── CLAUDE.md              # This file
├── src/
│   ├── agents/            # UnifAI agent implementations
│   │   ├── trading_agent.py   # Main trading agent with social signals
│   │   └── basic_agent.py     # Simple agent example
│   ├── api/               # Web API and frontend
│   │   ├── server.py          # FastAPI server
│   │   └── static/            # HTML/JS frontend
│   ├── markets/           # Prediction market clients
│   │   ├── kalshi.py          # Kalshi API client
│   │   └── polymarket.py      # Polymarket via UnifAI
│   ├── toolkits/          # Custom UnifAI toolkits
│   ├── strategies/        # Trading strategy logic
│   ├── signals/           # Social & on-chain signal processors
│   │   └── social.py          # Social signal processor
│   └── utils/             # Shared utilities
├── skills/                # Moltbot skill definitions (Phase 2)
│   ├── prediction-trader/ # Main trading skill
│   │   ├── SKILL.md
│   │   └── scripts/trader.py
│   ├── kalshi-trader/     # Kalshi markets skill
│   │   ├── SKILL.md
│   │   └── scripts/kalshi.py
│   ├── polymarket-trader/ # Polymarket skill
│   │   ├── SKILL.md
│   │   └── scripts/polymarket.py
│   └── social-signals/    # Social analysis skill
│       ├── SKILL.md
│       └── scripts/signals.py
├── tests/
├── config/
│   └── settings.py        # Pydantic configuration
└── requirements.txt
```

## Key Dependencies

```
unifai-sdk>=0.3.3
litellm
google-generativeai
aiohttp
web3  # for on-chain analysis
```

## UnifAI SDK Usage Patterns

### Dynamic Tools for Strategy Discovery
```python
import unifai

tools = unifai.Tools(api_key=os.getenv('UNIFAI_AGENT_API_KEY'))
dynamic_tools = await tools.get_tools(dynamic_tools=True)
```

### Creating Trading Toolkits
```python
toolkit = unifai.Toolkit(api_key=os.getenv('UNIFAI_TOOLKIT_API_KEY'))

@toolkit.action(
    action="execute_trade",
    action_description='Execute a prediction market trade',
    payload_description={
        "market_id": {"type": "string"},
        "position": {"type": "string", "enum": ["yes", "no"]},
        "amount": {"type": "number"}
    },
)
async def execute_trade(ctx: unifai.ActionContext, payload={}):
    # Trade execution logic
    pass

await toolkit.run()
```

### LLM Integration with Gemini 3
```python
# Model is configurable via LLM_MODEL environment variable
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-3-flash-preview")

response = await litellm.acompletion(
    model=DEFAULT_MODEL,
    messages=[{"content": query, "role": "user"}],
    tools=await tools.get_tools(),
    temperature=1.0,  # Required for Gemini 3 to avoid looping
)
results = await tools.call_tools(response.choices[0].message.tool_calls)
```

### Gemini 3 Requirements

**Thought Signatures**: Gemini 3 requires "thought signatures" for multi-turn function calling. LiteLLM 1.80.5+ handles this automatically by:
- Storing signatures in `tool_call.id` (format: `call_xxx__thought__<signature>`)
- Preserving signatures when using `message.model_dump()` in conversation history

**Temperature**: Always use `temperature=1.0` (default for Gemini 3). Lower values can cause infinite loops or degraded reasoning.

**LiteLLM Version**: Requires LiteLLM >= 1.80.5 for Gemini 3 thought signature support.

## Moltbot Skill Structure

Skills should follow this format in `skills/<skill-name>/SKILL.md`:

```markdown
---
name: prediction-trader
description: AI-powered prediction market trading assistant
homepage: https://github.com/zbruceli/trading
user-invocable: true
---

# Prediction Trader Skill

Instructions for the agent on how to use trading tools...
```

### Skill Metadata (JSON in SKILL.md)
```json
{
  "moltbot": {
    "requires": {
      "env": ["UNIFAI_AGENT_API_KEY", "PREDICTION_MARKET_API_KEY"]
    },
    "primaryEnv": "UNIFAI_AGENT_API_KEY"
  }
}
```

## Environment Variables

```bash
# UnifAI
UNIFAI_AGENT_API_KEY=       # For using toolkits in agents
UNIFAI_TOOLKIT_API_KEY=     # For creating toolkits

# LLM
LLM_MODEL=gemini/gemini-3-flash-preview  # LiteLLM model identifier
GOOGLE_API_KEY=             # Gemini API key
OPENROUTER_API_KEY=         # Alternative: OpenRouter

# Prediction Markets
POLYMARKET_API_KEY=         # If using Polymarket
MANIFOLD_API_KEY=           # If using Manifold Markets

# On-chain
ALCHEMY_API_KEY=            # Or Infura for blockchain data
```

## Development Guidelines

### Code Style
- Use async/await for all I/O operations
- Type hints required for all function signatures
- Follow PEP 8 with 100 char line limit
- Use pydantic for data validation

### Testing
- Unit tests for strategy logic
- Integration tests for API interactions
- Mock external services in tests

### Error Handling
- Graceful degradation when signals unavailable
- Retry logic for transient API failures
- Position limits to prevent runaway losses

## Current Implementation

### Trading Agent (`src/agents/trading_agent.py`)
Two-phase workflow agent with social signal integration:

```python
from src.agents import TradingAgent

agent = TradingAgent()

# Comprehensive token analysis (price + social + news)
analysis = await agent.analyze_token("SOL")

# Get trending tokens from KOL discussions
trending = await agent.get_trending_signals()

# Market sentiment for a topic
sentiment = await agent.get_market_sentiment("Bitcoin ETF")

# Custom queries
response = await agent.chat("Get ETH price and recent news")
```

### Social Signal Processor (`src/signals/social.py`)
Dedicated processor for social signals via UnifAI:

```python
from src.signals import SocialSignalProcessor

processor = SocialSignalProcessor()

# Get token sentiment
sentiment = await processor.get_token_sentiment("ETH")

# Get trending tokens from KOLs
trending = await processor.get_trending_tokens(time_window="24h")

# Search crypto news
news = await processor.get_crypto_news("Polymarket prediction")

# Get event summary from social mentions
events = await processor.get_event_summary("Bitcoin", time_window="24h")
```

### Available UnifAI Tools for Signals

| Tool | Description |
|------|-------------|
| `Birdeye--174--RetrieveTheLatestPrice` | Token prices on Solana, Ethereum, BSC, etc. |
| `TokenAnalysis--25--analyzeToken` | Comprehensive analysis with social metrics |
| `Elfa--18--getTrendingTokens` | Trending tokens from KOL discussions on X |
| `Elfa--18--getEventSummary` | Event summaries from social mentions |
| `SerpAPI--21--newsSearch` | Google News search for crypto topics |
| `polymarket--127--getEventsByCategory` | Prediction market events |

## Key Concepts

### Signal Sources
1. **Social Signals**: KOL mentions (Elfa), token sentiment (TokenAnalysis)
2. **News Signals**: Google News via SerpAPI
3. **Market Signals**: Price data (Birdeye), prediction markets (Polymarket)
4. **On-chain Signals**: Wallet movements, smart contract interactions (planned)

### Agent Workflow
1. **Tool Discovery**: Search UnifAI for relevant tools
2. **Signal Collection**: Fetch price, social, and news data
3. **Signal Synthesis**: LLM combines signals into analysis
4. **Response**: Structured output with signal sources

### Strategy Components
1. **Signal Aggregator**: Combines multiple signal sources
2. **Risk Manager**: Position sizing and stop-loss logic
3. **Executor**: Trade execution with slippage protection

## Prediction Market Integrations

### Polymarket (via UnifAI)

Polymarket tools are available through UnifAI SDK with full trading capabilities:

```python
from src.agents.trading_agent import TradingAgent

agent = TradingAgent()

# Get trending prediction markets
response = await agent.chat("Get trending events on Polymarket")

# Search for specific markets
response = await agent.chat("Search Polymarket for Bitcoin price predictions")

# Get crypto markets
response = await agent.chat("Get crypto prediction markets on Polymarket")
```

**Available Polymarket Tools (via UnifAI):**

| Tool | Description |
|------|-------------|
| `polymarket--127--search` | Search markets by text query |
| `polymarket--127--searchPolymarketMarkets` | Filter markets with options |
| `polymarket--127--searchPolymarketEvents` | Search events with filters |
| `polymarket--127--getEventsByCategory` | Get events: trending, politics, crypto, etc. |
| `polymarket--127--getPrices` | Get prices for token IDs |
| `polymarket--127--getOrderBooks` | Get orderbook data |
| `polymarket--127--limitOrderBuy/Sell` | Place limit orders |
| `polymarket--127--marketOrderBuy/Sell` | Place market orders |

### Kalshi (Direct API)

Kalshi is a CFTC-regulated prediction market. We have a direct API client since UnifAI doesn't have Kalshi tools:

```python
from src.markets import KalshiClient

client = KalshiClient()

# Get Fed interest rate markets
fed_markets = await client.get_fed_markets(limit=10)

# Get GDP/economics markets
econ_markets = await client.get_economics_markets(limit=10)

# Search markets
results = await client.search_markets("bitcoin", limit=5)

# Get all available series
series = await client.get_all_series()

await client.close()
```

**Kalshi API Endpoints:**
- Base URL: `https://api.elections.kalshi.com/trade-api/v2`
- Public endpoints (no auth): `/markets`, `/events`, `/series`, `/orderbook`
- Trading endpoints require API key

**Key Kalshi Series:**
| Series | Description |
|--------|-------------|
| `KXFED` | Federal Reserve interest rate decisions |
| `KXGDP` | US GDP predictions |
| `KXCPI` | Consumer Price Index |
| `KXBTC` | Bitcoin price markets |

### Comparison

| Feature | Polymarket | Kalshi |
|---------|------------|--------|
| Regulation | Offshore (Polygon) | CFTC-regulated (US) |
| UnifAI Support | Full tools available | No (direct API) |
| Market Types | Crypto, politics, sports | Economics, politics, events |
| Trading | USDC.e on Polygon | USD |
| API Auth | Required for trading | Required for trading |

## Running the Agent

```bash
# Activate virtual environment
source venv/bin/activate

# Run demo with social signals
python -m src.agents.trading_agent --demo

# Interactive mode
python -m src.agents.trading_agent

# Test social signal processor
python -m src.signals.social

# Test Kalshi client
python -m src.markets.kalshi

# Start web frontend (port 8080)
uvicorn src.api.server:app --port 8080
```

## Web Frontend

A simple web interface is available at `http://localhost:8080`:

```bash
uvicorn src.api.server:app --port 8080
```

Features:
- Chat interface for trading queries
- Quick actions: trending tokens, available tools
- Token analyzer with price and social signals
- Example queries for common use cases

## Moltbot Skills (Phase 2)

Skills are packaged as AgentSkills-compatible SKILL.md files with Python scripts.

### Installation

Copy skills to your Moltbot skills directory:
```bash
# Per-workspace
cp -r skills/* <workspace>/skills/

# Shared (all workspaces)
cp -r skills/* ~/.clawdbot/skills/
```

### Available Skills

#### prediction-trader
Main trading assistant with cross-platform analysis.
```bash
# Compare markets across platforms
python3 skills/prediction-trader/scripts/trader.py compare "bitcoin"

# Get trending markets
python3 skills/prediction-trader/scripts/trader.py trending

# Full topic analysis
python3 skills/prediction-trader/scripts/trader.py analyze "Fed rates"
```

#### kalshi-trader
CFTC-regulated prediction market queries.
```bash
# Fed interest rate markets
python3 skills/kalshi-trader/scripts/kalshi.py fed

# Economics (GDP, CPI)
python3 skills/kalshi-trader/scripts/kalshi.py economics

# Search markets
python3 skills/kalshi-trader/scripts/kalshi.py search "inflation"
```

#### polymarket-trader
Polymarket prediction market queries.
```bash
# Trending events
python3 skills/polymarket-trader/scripts/polymarket.py trending

# Crypto markets
python3 skills/polymarket-trader/scripts/polymarket.py crypto

# Search markets
python3 skills/polymarket-trader/scripts/polymarket.py search "election"
```

#### social-signals
Social signal analysis for crypto.
```bash
# Trending tokens from KOLs
python3 skills/social-signals/scripts/signals.py trending

# Token sentiment
python3 skills/social-signals/scripts/signals.py sentiment "SOL"

# Crypto news
python3 skills/social-signals/scripts/signals.py news "Bitcoin ETF"
```

### Skill Requirements

| Skill | Required Env Vars |
|-------|-------------------|
| prediction-trader | UNIFAI_AGENT_API_KEY, GOOGLE_API_KEY |
| kalshi-trader | (none - public API) |
| polymarket-trader | UNIFAI_AGENT_API_KEY, GOOGLE_API_KEY |
| social-signals | UNIFAI_AGENT_API_KEY, GOOGLE_API_KEY |

### SKILL.md Format

Skills follow the AgentSkills specification:
```markdown
---
name: skill-name
description: Brief description
homepage: https://github.com/zbruceli/trading
user-invocable: true
metadata: {"moltbot":{"emoji":"📈","requires":{"env":["API_KEY"]},"primaryEnv":"API_KEY"}}
---

# Skill Name

Instructions and command documentation...
```

## References

- [UnifAI SDK Documentation](https://github.com/unifai-network/unifai-sdk-py)
- [Moltbot Skills Documentation](https://docs.molt.bot/tools/skills)
- [AgentSkills Specification](https://github.com/agentskills/agentskills)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Kalshi API Documentation](https://docs.kalshi.com)
- [Polymarket Documentation](https://docs.polymarket.com)
