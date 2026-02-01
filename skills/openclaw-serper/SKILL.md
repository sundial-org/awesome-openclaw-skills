---
name: openclaw-serper
description: >
  Searches Google and extracts full page content from every result via trafilatura.
  Returns clean readable text, not just snippets.
  Use when the user needs web search, research, current events, news, factual lookups,
  product comparisons, technical documentation, or any question requiring up-to-date
  information from the internet.
license: MIT
compatibility: Requires Python 3, trafilatura (pip install trafilatura), and network access.
allowed-tools: Bash(python3:*)
metadata:
  author: nesdeq
  version: "3.1.1"
  tags: "search, web-search, serper, google, content-extraction"
---

# Serper

Google search via Serper API. Fetches results AND reads the actual web pages to extract clean full-text content via trafilatura. Not just snippets — full article text.

## Constraint

This skill already fetches and extracts full page content. Do NOT use WebFetch, web_fetch, WebSearch, browser tools, or any other URL-fetching/browsing tool on the URLs returned by this skill. The content is already included in the output. Never follow up with a separate fetch — everything you need is in the results.

## Query Discipline

Craft ONE good search query. That is almost always enough.

Each call returns multiple results with full page text — you get broad coverage from a single query. Do not run multiple searches to "explore" a topic. One well-chosen query with the right mode covers it.

**At most two calls** if the user's request genuinely spans two distinct topics (e.g. "compare X vs Y" where X and Y need separate searches, or one `default` + one `current` call for different aspects). Never more than two.

**Do NOT:**
- Run the same query with different wording to "get more results"
- Run sequential searches to "dig deeper" — the full page content is already deep
- Run one search to find something, then another to follow up — read the content you already have

## Two Search Modes

There are exactly two modes. Pick the right one based on the query:

### `default` — General search (all-time)

- All-time Google web search, **5 results**, each enriched with full page content
- Use for: general questions, research, how-to, evergreen topics, product info, technical docs, comparisons, tutorials, anything NOT time-sensitive

### `current` — News and recent info

- Past-week Google web search (3 results) + Google News (3 results), each enriched with full page content
- Use for: news, current events, recent developments, breaking news, announcements, anything time-sensitive

### Mode Selection Guide

| Query signals | Mode |
|---------------|------|
| "how does X work", "what is X", "explain X" | `default` |
| Product research, comparisons, tutorials | `default` |
| Technical documentation, guides | `default` |
| Historical topics, evergreen content | `default` |
| "news", "latest", "today", "this week", "recent" | `current` |
| "what happened", "breaking", "announced", "released" | `current` |
| Current events, politics, sports scores, stock prices | `current` |

## Locale

**Default is global** — no country filter, English results. This ONLY works for English queries.

**You MUST ALWAYS set `--gl` and `--hl` when ANY of these are true:**
- The user's message is in a non-English language
- The search query you construct is in a non-English language
- The user mentions a specific country, city, or region
- The user asks for local results (prices, news, stores, etc.) in a non-English context

**If the user writes in German, you MUST pass `--gl de --hl de`. No exceptions.**

| Scenario | Flags |
|----------|-------|
| English query, no country target | *(omit --gl and --hl)* |
| German query OR user writes in German OR targeting DE/AT/CH | `--gl de --hl de` |
| French query OR user writes in French OR targeting France | `--gl fr --hl fr` |
| Any other non-English language/country | `--gl XX --hl XX` (ISO codes) |

**Rule of thumb:** If the query string contains non-English words, set `--gl` and `--hl` to match that language.

## How to Invoke

```bash
python3 scripts/search.py -q "QUERY" [--mode MODE] [--gl COUNTRY] [--hl LANG]
```

### Examples

```bash
# English, general research
python3 scripts/search.py -q "how does HTTPS work"

# English, time-sensitive
python3 scripts/search.py -q "OpenAI latest announcements" --mode current

# German query — set locale + current mode for news/prices
python3 scripts/search.py -q "aktuelle Preise iPhone" --mode current --gl de --hl de

# German news
python3 scripts/search.py -q "Nachrichten aus Berlin" --mode current --gl de --hl de

# French product research
python3 scripts/search.py -q "meilleur smartphone 2026" --gl fr --hl fr
```

## Output Format

The script streams a JSON array. The first element is metadata, the rest are results with full extracted content:

```json
[{"query": "...", "mode": "default", "locale": {"gl": "world", "hl": "en"}, "results": [{"title": "...", "url": "...", "source": "web"}]}
,{"title": "Page Title", "url": "https://example.com", "source": "web", "content": "Full extracted page text..."}
,{"title": "News Article", "url": "https://news.com", "source": "news", "date": "2 hours ago", "content": "Full article text..."}
]
```

| Field | Description |
|-------|-------------|
| `title` | Page title |
| `url` | Source URL |
| `source` | `"web"`, `"news"`, or `"knowledge_graph"` |
| `content` | Full extracted page text (falls back to search snippet if extraction fails) |
| `date` | Present when available (news results always, web results sometimes) |

## CLI Reference

| Flag | Description |
|------|-------------|
| `-q, --query` | Search query (required) |
| `-m, --mode` | `default` (all-time, 5 results) or `current` (past week + news, 3 each) |
| `--gl` | Country code (e.g. `de`, `us`, `fr`, `at`, `ch`). Default: `world` |
| `--hl` | Language code (e.g. `en`, `de`, `fr`). Default: `en` |

## Edge Cases

- If trafilatura cannot extract content from a page, the result falls back to the search snippet.
- Some sites block scraping entirely — the snippet is all you get.
- If zero results are returned, the script exits with `{"error": "No results found", "query": "..."}`.
- The Serper API key is loaded from `.env` in the skill directory. If missing, the script exits with setup instructions.
