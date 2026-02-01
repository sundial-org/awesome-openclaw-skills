# Finance News Skill for OpenClaw

AI-powered market news briefings with configurable language output and automated delivery.

## Features

- **Multi-source aggregation:** Reuters, WSJ, FT, Bloomberg, CNBC, Yahoo Finance, Tagesschau, Handelsblatt
- **Global markets:** US (S&P, Dow, NASDAQ), Europe (DAX, STOXX, FTSE), Japan (Nikkei)
- **AI summaries:** LLM-powered analysis in German or English
- **Automated briefings:** Morning (market open) and evening (market close)
- **WhatsApp/Telegram delivery:** Send briefings via openclaw
- **Portfolio tracking:** Personalized news for your stocks with price alerts
- **Lobster workflows:** Approval gates before sending

## Quick Start

### Docker (Recommended)

```bash
# Build the Docker image
docker build -t finance-news-briefing .

# Generate a briefing
docker run --rm -v "$PWD/config:/app/config:ro" \
  finance-news-briefing python3 scripts/briefing.py \
  --time morning --lang de --json --fast
```

### Lobster Workflow

```bash
# Set required environment variables
export FINANCE_NEWS_TARGET="your-group-jid@g.us"  # WhatsApp JID or Telegram chat ID
export FINANCE_NEWS_CHANNEL="whatsapp"            # or "telegram"

# Run workflow (halts for approval before sending)
lobster run workflows/briefing.yaml --args-json '{"time":"morning","lang":"de"}'
```

### CLI (Legacy)

```bash
# Generate a briefing
finance-news briefing --morning --lang de

# Use fast mode + deadline (recommended)
finance-news briefing --morning --lang de --fast --deadline 300
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FINANCE_NEWS_TARGET` | Delivery target (WhatsApp JID, group name, or Telegram chat ID) | `120363421796203667@g.us` |
| `FINANCE_NEWS_CHANNEL` | Delivery channel | `whatsapp` or `telegram` |
| `SKILL_DIR` | Path to skill directory (for Lobster) | `$HOME/projects/finance-news-openclaw-skill` |

## Installation

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/kesslerio/finance-news-openclaw-skill.git
cd finance-news-openclaw-skill
docker build -t finance-news-briefing .
```

### Option 2: Native Python

```bash
# Clone repository
git clone https://github.com/kesslerio/finance-news-openclaw-skill.git \
    ~/openclaw/skills/finance-news

# Create virtual environment
cd ~/openclaw/skills/finance-news
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create CLI symlink
ln -sf ~/openclaw/skills/finance-news/scripts/finance-news ~/.local/bin/finance-news
```

## Configuration

Configuration is stored in `config/config.json`:

- **RSS Feeds:** Enable/disable news sources per region
- **Markets:** Choose which indices to track
- **Delivery:** WhatsApp/Telegram settings
- **Language:** German (`de`) or English (`en`) output
- **Schedule:** Cron times for morning/evening briefings
- **LLM:** Model order preference for headlines, summaries, translations

Run the setup wizard for interactive configuration:

```bash
finance-news setup
```

## Lobster Workflow

The skill includes a Lobster workflow (`workflows/briefing.yaml`) that:

1. **Generates** briefing via Docker
2. **Translates** portfolio headlines (German only, via openclaw)
3. **Halts** for approval (shows preview)
4. **Sends** macro briefing to channel
5. **Sends** portfolio briefing to channel

### Workflow Arguments

| Arg | Default | Description |
|-----|---------|-------------|
| `time` | `morning` | Briefing type: `morning` or `evening` |
| `lang` | `de` | Language: `en` or `de` |
| `channel` | env var | `whatsapp` or `telegram` |
| `target` | env var | Group JID/name or chat ID |
| `fast` | `false` | Use fast mode (shorter timeouts) |

## Portfolio

Manage your stock watchlist in `config/portfolio.csv`:

```bash
finance-news portfolio-list              # View portfolio
finance-news portfolio-add NVDA          # Add stock
finance-news portfolio-remove TSLA       # Remove stock
finance-news portfolio-import stocks.csv # Import from CSV
```

Portfolio briefings show:
- Top gainers and losers from your holdings
- Relevant news articles with translations
- Shortened hyperlinks for easy access

## Dependencies

- Python 3.10+
- Docker (recommended)
- openclaw CLI (for message delivery and LLM)
- Lobster (for workflow automation)

### Optional

- OpenBB (`openbb-quote`) for enhanced market data

## License

Apache 2.0 - See [LICENSE](LICENSE) file for details.

## Related Skills

- **[task-tracker](https://github.com/kesslerio/task-tracker-openclaw-skill):** Personal task management with daily standups
