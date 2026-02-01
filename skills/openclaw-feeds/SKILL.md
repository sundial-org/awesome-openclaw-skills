---
name: openclaw-feeds
description: >
  RSS news aggregator. Fetches headlines from curated feeds across three categories: news, games,
  and finance. Use when the user asks about current news, headlines, what's happening, what's going
  on, or says "what's up in news", "what's up in finance", "what's up in games", or the German
  equivalents "was geht mit nachrichten", "was geht mit money", "was geht mit gaming". Also
  activates for requests like "give me a news rundown", "latest headlines", "market news",
  "gaming news", "tech news", "finance roundup", or "briefing". Returns structured JSON from
  public RSS feeds — no API keys, no web search needed.
license: MIT
compatibility: Requires Python 3, feedparser (pip install feedparser), and network access to fetch RSS feeds.
allowed-tools: Bash(python3:*)
metadata:
  author: nesdeq
  version: "3.1.1"
  tags: "rss, news, feeds, headlines, aggregator"
---

# Feeds

RSS news aggregator. Fetches all current entries from curated feeds across three categories — news, games, and finance. Concurrent fetching, streamed JSON output. No API key needed.

## Constraint

Do NOT use web search, WebFetch, browser tools, or any other URL-fetching tool when this skill is active. The RSS feeds are the sole data source. Do not supplement, verify, or expand results with external searches. Do not fetch article URLs — summaries are already included in the output.

## Categories

Detect the category from the user's message:

- "news", "headlines", "nachrichten", "tech news" → `news`
- "finance", "markets", "money", "stocks", "economy" → `finance`
- "games", "gaming" → `games`

| Category | Feeds | Sources |
|----------|-------|---------|
| `news` | 21 | Ars Technica, Wired, TechCrunch, The Verge, NYT, Heise, Quanta, Aeon, Nautilus, and more |
| `games` | 10 | GameStar, GamesGlobal, PC Gamer, Polygon, Kotaku, IGN, Rock Paper Shotgun, GamesIndustry.biz |
| `finance` | 26 | Bloomberg, WSJ, FT, CNBC, MarketWatch, Seeking Alpha, The Economist, Forbes, CoinDesk, Fed, ECB |

Feed lists are defined in [scripts/lists.py](scripts/lists.py).

## How to Invoke

Run one invocation per category. Run multiple if the user asks for more than one.

```bash
python3 scripts/feeds.py --category news
python3 scripts/feeds.py --category games
python3 scripts/feeds.py --category finance
```

## Output Format

The script streams a JSON array. The first element is metadata, the rest are entries:

```json
[{"category": "news", "total_entries": 142, "sources": ["aeon.co", "arstechnica.com"], "fetched_at": "2026-01-31 22:00:00"}
,{"title": "Headline Here", "url": "https://example.com/article", "source": "arstechnica.com", "date": "Fri, 31 Jan 2026 12:00:00 GMT", "summary": "Brief summary text..."}
]
```

| Field | Description |
|-------|-------------|
| `title` | Headline text |
| `url` | Link to full article |
| `source` | Domain name of the feed source |
| `date` | Publication date as provided by the feed |
| `summary` | Brief description, HTML stripped, max 500 chars |

## CLI Reference

| Flag | Description |
|------|-------------|
| `-c, --category` | Feed category: `news`, `games`, or `finance` (required) |

## Presenting Results

After parsing the output, present a structured, concise rundown:

1. **Group by theme** — cluster related stories under headings (e.g. "Tech & Industry", "Science", "Markets", "Crypto")
2. **Keep it tight** — headline + one-line summary + source attribution per item
3. **Link to sources** — use markdown links so the user can read more
4. **Deduplicate** — if multiple feeds cover the same story, mention it once and note cross-source coverage
5. **Highlight big stories** — if a story appears across 3+ sources, call it out prominently

Example output:

```
### Tech & Industry
- **[Headline](url)** — One-line summary *(Source)*
- **[Headline](url)** — One-line summary *(Source)*

### Science
- **[Headline](url)** — One-line summary *(Source)*
```

## Edge Cases

- Failed or timed-out feeds (15s timeout) are silently skipped — remaining feeds still return results.
- If zero entries are returned, the script exits with `{"error": "No entries found", "category": "..."}`.
- Some entries may lack summaries — they will still have title, URL, and source.
