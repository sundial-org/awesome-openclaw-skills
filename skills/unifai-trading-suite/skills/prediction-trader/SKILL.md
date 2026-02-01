---
name: prediction-trader
description: AI-powered prediction market analysis across Polymarket and Kalshi with social signals
homepage: https://github.com/your-repo/trading
user-invocable: true
metadata: {"moltbot":{"emoji":"📈","requires":{"env":["UNIFAI_AGENT_API_KEY","GOOGLE_API_KEY"]},"primaryEnv":"UNIFAI_AGENT_API_KEY"}}
---

# Prediction Trader

AI-powered prediction market analysis assistant that aggregates data from multiple platforms and social signals.

## Supported Platforms

- **Polymarket**: Offshore prediction market on Polygon (crypto, politics, sports, world events)
- **Kalshi**: CFTC-regulated US prediction market (Fed rates, GDP, CPI, economics)

## Commands

### Compare Markets
```bash
python3 {baseDir}/scripts/trader.py compare "[topic]"
```
Compare prediction markets across both platforms for a given topic.

### Get Trending
```bash
python3 {baseDir}/scripts/trader.py trending
```
Get trending prediction markets from both platforms.

### Analyze Topic
```bash
python3 {baseDir}/scripts/trader.py analyze "[topic]"
```
Full analysis including market data and social signals.

### Platform-Specific

```bash
# Polymarket
python3 {baseDir}/scripts/trader.py polymarket trending
python3 {baseDir}/scripts/trader.py polymarket crypto
python3 {baseDir}/scripts/trader.py polymarket search "[query]"

# Kalshi
python3 {baseDir}/scripts/trader.py kalshi fed
python3 {baseDir}/scripts/trader.py kalshi economics
python3 {baseDir}/scripts/trader.py kalshi search "[query]"
```

## Output Format

Results include:
- Market question/title
- YES/NO prices (probability)
- Trading volume
- Platform source
- Resolution date (if available)

## Requirements

- `UNIFAI_AGENT_API_KEY` - UnifAI SDK key for Polymarket tools and social signals
- `GOOGLE_API_KEY` - Gemini API key for LLM analysis

## Example Usage

**User**: "Compare Bitcoin prediction markets"

**Assistant**: I'll compare Bitcoin markets across Polymarket and Kalshi.

```bash
python3 {baseDir}/scripts/trader.py compare "bitcoin"
```

**User**: "What are the Fed rate predictions?"

**Assistant**: Let me fetch the Federal Reserve interest rate markets from Kalshi.

```bash
python3 {baseDir}/scripts/trader.py kalshi fed
```

## Notes

- Polymarket data accessed via UnifAI tools (may have rate limits)
- Kalshi data accessed via direct public API (no auth for read)
- This tool is read-only; trading requires platform authentication
- All prices shown as decimals (0.75 = 75% probability)
