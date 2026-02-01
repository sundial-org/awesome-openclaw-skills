# OpenClaw Starter Kit 🦞

> **The definitive starting point for autonomous agents. Powered by AIsa.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-brightgreen.svg)](https://openclaw.ai)

---

## Why OpenClaw Starter Kit?

Building autonomous agents shouldn't require juggling dozens of API keys. **OpenClaw Starter Kit** gives you unified access to everything your agent needs:

| Capability | What You Get |
|------------|--------------|
| 🐦 **Twitter/X** | Read timelines, search tweets, post, like, retweet |
| 🔍 **Web Search** | Real-time search results |
| 📚 **Scholar Search** | Academic papers and research |
| 📰 **News** | Company news by stock ticker |
| 🤖 **LLM Routing** | GPT-4, Claude, Gemini, Qwen, Deepseek, Grok |

**One API key. One integration. Infinite possibilities.**

---

## Quick Start (30 Seconds)

### 1. Get Your API Key

Sign up at [aisa.one](https://aisa.one) and grab your API key.

### 2. Set Environment Variable

```bash
export AISA_API_KEY="your-api-key-here"
```

### 3. Start Using

```bash
# Get Twitter user info
python scripts/aisa_client.py twitter user-info --username elonmusk

# Search the web
python scripts/aisa_client.py search web --query "autonomous agents 2024"

# Query an LLM
python scripts/aisa_client.py llm complete --model gpt-4 --prompt "Explain quantum computing"
```

---

## What Can Your Agent Do?

### Morning Briefing (Scheduled Task)
```
"Send me a daily briefing at 8am with:
- My portfolio performance (NVDA, TSLA, BTC)
- Twitter trends in AI
- Top news in my industry"
```

### Competitor Intelligence
```
"Monitor @OpenAI - alert me on new tweets, news mentions, and paper releases"
```

### Investment Research
```
"Full analysis on NVDA: price trends, insider trades, analyst estimates, 
SEC filings, and Twitter sentiment"
```

### Startup Validation
```
"Research the market for AI writing tools - find competitors, 
Twitter discussions, and academic papers on the topic"
```

---

## Installation

### Requirements

- Python 3.8+
- `curl` (for shell examples)

### Setup

```bash
# Clone the repository
git clone https://github.com/anthropic/openclaw-starter-kit.git
cd openclaw-starter-kit

# Set your API key
export AISA_API_KEY="your-api-key"

# Test the installation
python scripts/aisa_client.py twitter trends
```

---

## API Examples

### Twitter/X - Read

```bash
# User info
curl "https://api.aisa.one/apis/v1/twitter/user/info?userName=elonmusk" \
  -H "Authorization: Bearer $AISA_API_KEY"

# Advanced search
curl "https://api.aisa.one/apis/v1/twitter/tweet/advanced_search?query=AI+agents&queryType=Latest" \
  -H "Authorization: Bearer $AISA_API_KEY"

# Trending topics
curl "https://api.aisa.one/apis/v1/twitter/trends?woeid=1" \
  -H "Authorization: Bearer $AISA_API_KEY"
```

### Twitter/X - Write (Requires Login)

```bash
# Step 1: Login
curl -X POST "https://api.aisa.one/apis/v1/twitter/user_login_v3" \
  -H "Authorization: Bearer $AISA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_name":"myaccount","email":"me@example.com","password":"xxx","proxy":"http://user:pass@ip:port"}'

# Step 2: Post tweet
curl -X POST "https://api.aisa.one/apis/v1/twitter/send_tweet_v3" \
  -H "Authorization: Bearer $AISA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_name":"myaccount","text":"Hello from OpenClaw Starter Kit!"}'
```

### Web & Scholar Search

```bash
# Web search
curl -X POST "https://api.aisa.one/apis/v1/scholar/search/web?query=AI+frameworks&max_num_results=10" \
  -H "Authorization: Bearer $AISA_API_KEY"

# Academic papers
curl -X POST "https://api.aisa.one/apis/v1/scholar/search/scholar?query=transformer+models&max_num_results=10" \
  -H "Authorization: Bearer $AISA_API_KEY"
```

### LLM Routing (OpenAI Compatible)

```bash
curl -X POST "https://api.aisa.one/v1/chat/completions" \
  -H "Authorization: Bearer $AISA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4", "messages": [{"role": "user", "content": "Hello!"}]}'
```

**Supported Models:** GPT-4, Claude-3, Gemini, Qwen, Deepseek, Grok, and more.

---

## Python Client Reference

```bash
# Twitter
python scripts/aisa_client.py twitter user-info --username <username>
python scripts/aisa_client.py twitter tweets --username <username>
python scripts/aisa_client.py twitter search --query <query>
python scripts/aisa_client.py twitter trends

# Twitter Write (login required)
python scripts/aisa_client.py twitter login --username <u> --email <e> --password <p> --proxy <proxy>
python scripts/aisa_client.py twitter post --username <u> --text "Hello!"
python scripts/aisa_client.py twitter like --username <u> --tweet-id <id>

# Search
python scripts/aisa_client.py search web --query <query>
python scripts/aisa_client.py search scholar --query <query>
python scripts/aisa_client.py search smart --query <query>

# News
python scripts/aisa_client.py news --ticker AAPL

# LLM
python scripts/aisa_client.py llm complete --model gpt-4 --prompt "Your prompt"
python scripts/aisa_client.py llm chat --model claude-3-sonnet --messages '[{"role":"user","content":"Hi"}]'
```

---

## Pricing

| API | Cost |
|-----|------|
| Twitter query | ~$0.0004 |
| Twitter post/like | ~$0.001 |
| Web search | ~$0.001 |
| Scholar search | ~$0.002 |
| News | ~$0.001 |
| LLM | Token-based |

Every response includes `usage.cost` and `usage.credits_remaining`.

---

## OpenClaw Starter Kit vs. Alternatives

| Feature | OpenClaw Starter Kit | DIY API Integration |
|---------|---------------------|---------------------|
| Setup time | 30 seconds | Hours/Days |
| API keys needed | 1 | 5-10+ |
| Twitter read/write | ✅ | Complex |
| Web + Scholar search | ✅ | Multiple providers |
| LLM routing | ✅ | Separate integration |
| Server-friendly | ✅ | Varies |
| Pay-per-use | ✅ | Multiple billing |

---

## Documentation

- [SKILL.md](SKILL.md) - OpenClaw skill specification
- [API Reference](references/api-reference.md) - Complete endpoint documentation
- [AIsa Docs](https://aisa.mintlify.app) - Full API documentation

---

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

Apache 2.0 License - see [LICENSE](../LICENSE) for details.

---

## Links

- 🦞 [OpenClaw](https://openclaw.ai) - The autonomous agent framework
- ⚡ [AIsa](https://aisa.one) - Unified API backend
- 📖 [API Docs](https://aisa.mintlify.app) - Full documentation

---

<p align="center">
  <b>OpenClaw Starter Kit</b> - Built for the next generation of autonomous agents.
</p>
