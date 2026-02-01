# Feeds

RSS news aggregator skill. Fetches headlines from curated feeds across three categories — news, games, finance. Concurrent fetching, structured JSON output. No API key needed.

[![GitHub](https://img.shields.io/badge/GitHub-openclaw--feeds-blue)](https://github.com/nesdeq/openclaw-feeds)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/nesdeq/openclaw-feeds)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/nesdeq/openclaw-feeds/blob/main/LICENSE)

---

## How It Works

1. **Pick a category** — news, games, or finance
2. **Concurrent feed fetching** — all RSS feeds for that category fetched in parallel (15s timeout per feed)
3. **Streamed output** — results print as a JSON array, one element per entry

One call returns all current entries from every feed in the selected category.

---

## Install

### 1. Clone

```bash
git clone https://github.com/nesdeq/openclaw-feeds.git ~/.openclaw/skills/feeds
```

### 2. Install feedparser

feedparser is the only dependency.

```bash
pip install --user feedparser

# Or if you use pip3 explicitly
pip3 install --user feedparser
```

**Verify it's importable:**

```bash
python3 -c "import feedparser; print('ok')"
```

### 3. Run

```bash
python3 ~/.openclaw/skills/feeds/scripts/feeds.py --category news
```

---

## Categories

### `news` — General news (21 feeds)

Tech, science, culture, essays. Sources include Ars Technica, Wired, TechCrunch, The Verge, NYT, Heise, Quanta Magazine, Aeon, Nautilus, and more.

```bash
python3 scripts/feeds.py --category news
```

### `games` — Gaming news (10 feeds)

German and US gaming press. Sources include GameStar, GamesGlobal, PC Gamer, Polygon, Kotaku, IGN, Rock Paper Shotgun, GamesIndustry.biz.

```bash
python3 scripts/feeds.py --category games
```

### `finance` — Finance & markets (26 feeds)

Markets, business, economy, crypto, central banks. Sources include Bloomberg, WSJ, FT, CNBC, MarketWatch, Seeking Alpha, The Economist, Forbes, CoinDesk, Fed, ECB.

```bash
python3 scripts/feeds.py --category finance
```

---

## Output Format

Streamed JSON array — first element is metadata, rest are entries:

```json
[{"category": "news", "total_entries": 142, "sources": ["aeon.co", "arstechnica.com", ...], "fetched_at": "2026-01-31 22:00:00"}
,{"title": "Headline Here", "url": "https://...", "source": "arstechnica.com", "date": "Fri, 31 Jan 2026 ...", "summary": "Brief summary text..."}
,{"title": "Another Headline", "url": "https://...", "source": "wired.com", "date": "...", "summary": "..."}
]
```

### Entry Fields

| Field | Description |
|-------|-------------|
| `title` | Headline text |
| `url` | Link to full article |
| `source` | Domain name of the feed source |
| `date` | Publication date (as provided by the feed) |
| `summary` | Brief summary/description (HTML stripped, max 500 chars) |

---

## CLI Reference

| Flag | Description |
|------|-------------|
| `-c, --category` | Feed category: `news`, `games`, or `finance` (required) |

---

## FAQ & Troubleshooting

**Q: Do I need an API key?**
> No. This skill reads public RSS feeds directly.

**Q: Why are some entries missing summaries?**
> Some feeds don't include summary/description fields. The entry will still have title, URL, and source.

**Q: Can I add my own feeds?**
> Edit `scripts/lists.py` — three lists: `NEWS_FEEDS`, `GAMES_FEEDS`, `FINANCE_FEEDS`.

**Error: "feedparser is required but not installed"**
```bash
pip install --user feedparser
# Then verify: python3 -c "import feedparser; print('ok')"
```

---

## License

MIT

---

## Links

- [ClawHub](https://www.clawhub.ai/nesdeq/feeds) — Skill page
- [GitHub](https://github.com/nesdeq/openclaw-feeds) — Source code & issues
