---
name: social-signals
description: Analyze crypto social signals - KOL mentions, sentiment, trending tokens, and news
homepage: https://github.com/your-repo/trading
user-invocable: true
metadata: {"moltbot":{"emoji":"📡","requires":{"env":["UNIFAI_AGENT_API_KEY","GOOGLE_API_KEY"]},"primaryEnv":"UNIFAI_AGENT_API_KEY"}}
---

# Social Signals

Analyze cryptocurrency social signals from Twitter/X, news sources, and KOL (Key Opinion Leader) discussions.

## Data Sources

- **Elfa**: Trending tokens from web3 KOLs on X/Twitter
- **TokenAnalysis**: Comprehensive token analysis with social metrics
- **SerpAPI**: Google News search for crypto topics
- **Twitter**: Direct tweet search and user timelines

## Commands

### Get Trending Tokens
```bash
python3 {baseDir}/scripts/signals.py trending
```
Get tokens currently trending among crypto KOLs.

### Token Sentiment
```bash
python3 {baseDir}/scripts/signals.py sentiment "<token>"
```
Get social sentiment analysis for a specific token (e.g., BTC, ETH, SOL).

### Search News
```bash
python3 {baseDir}/scripts/signals.py news "<query>"
```
Search recent crypto news for a topic.

### Event Summary
```bash
python3 {baseDir}/scripts/signals.py events "<keyword>"
```
Get event summary from social mentions for a keyword.

### Full Analysis
```bash
python3 {baseDir}/scripts/signals.py analyze "<token>"
```
Comprehensive analysis combining price, social, and news signals.

## Output Format

Results include:
- Token symbol and current metrics
- Sentiment score (-1 to 1) and label (bullish/bearish/neutral)
- Mention counts and social volume
- Key discussion topics
- Recent news headlines

## Requirements

- `UNIFAI_AGENT_API_KEY` - UnifAI SDK key for social signal tools
- `GOOGLE_API_KEY` - Gemini API key for analysis

## Example Usage

**User**: "What's the social sentiment on Solana?"

**Assistant**: I'll analyze the social signals for SOL.

```bash
python3 {baseDir}/scripts/signals.py sentiment "SOL"
```

**User**: "What tokens are KOLs talking about?"

**Assistant**: Let me check what's trending among crypto KOLs.

```bash
python3 {baseDir}/scripts/signals.py trending
```

## Signal Types

| Signal | Source | Description |
|--------|--------|-------------|
| Sentiment | TokenAnalysis | Overall social sentiment score |
| Trending | Elfa | KOL-driven trending tokens |
| News | SerpAPI | Recent news articles |
| Mentions | Twitter | Tweet volume and engagement |

## Notes

- Social signals are lagging indicators - use with caution
- KOL sentiment can shift rapidly
- News sentiment may not reflect market direction
- Best used in combination with market data
