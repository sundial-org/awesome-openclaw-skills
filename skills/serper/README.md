# Serper

Google search via Serper API with full page content extraction. Fast API lookup, then concurrent page scraping (3s timeout per page) via trafilatura. Not just snippets — full article text from every result.

[![GitHub](https://img.shields.io/badge/GitHub-openclaw--serper-blue)](https://github.com/nesdeq/openclaw-serper)
[![Version](https://img.shields.io/badge/version-3.0.1-green)](https://github.com/nesdeq/openclaw-serper)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/nesdeq/openclaw-serper/blob/main/LICENSE)

---

## How It Works

1. **Serper API call** — fast Google search, returns result URLs instantly
2. **Concurrent page scraping** — all result pages fetched and extracted in parallel via trafilatura (3s timeout per page)
3. **Streamed output** — results print one at a time as each page finishes

One query returns 5 results (default mode) or up to 6 (current mode), each with full page content.

---

## Install

### 1. Clone

```bash
git clone https://github.com/nesdeq/openclaw-serper.git ~/.openclaw/skills/serper
```

### 2. Install trafilatura

trafilatura is the only dependency. It must be installed for the same Python that will run the script — install as your user, not with sudo.

```bash
# Install for your user
pip install --user trafilatura

# Or if you use pip3 explicitly
pip3 install --user trafilatura
```

If `python3` on your system points to a Homebrew/pyenv/asdf-managed Python, `pip install trafilatura` (without `--user`) is fine — those are already user-scoped. The `--user` flag matters on system Python (e.g. Debian/Ubuntu) where global installs require root.

**Verify it's importable by the Python that will run the script:**

```bash
python3 -c "import trafilatura; print('ok')"
```

### 3. API key

Get a free key at [serper.dev](https://serper.dev) (2,500 queries free). Add `SERPER_API_KEY` (or `SERP_API_KEY`) to `~/.openclaw/.env` or `~/.openclaw/skills/serper/.env`:

```bash
echo 'SERPER_API_KEY="your-key"' >> ~/.openclaw/.env
```

### 4. Search

```bash
python3 ~/.openclaw/skills/serper/scripts/search.py -q "how does HTTPS work"
```

---

## Search Modes

### `default` — General search (all-time)

All-time Google web search, **5 results**, each enriched with full page content.

Use for: general questions, research, how-to, evergreen topics, product info, technical docs, comparisons, tutorials.

```bash
python3 scripts/search.py -q "how does HTTPS work"
python3 scripts/search.py -q "best mechanical keyboards 2026"
```

### `current` — News and recent info

Past-week Google web search (3 results) + Google News (3 results), each enriched with full page content. Results are deduplicated by URL.

Use for: news, current events, recent developments, breaking news, announcements.

```bash
python3 scripts/search.py -q "OpenAI latest announcements" --mode current
python3 scripts/search.py -q "tech layoffs this week" --mode current
```

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

---

## Locale

**Default is global** — no country filter, English results.

Set `--gl` (country) and `--hl` (language) when the query is non-English or targets a specific region.

| Scenario | Flags |
|----------|-------|
| English query, no country target | *(omit --gl and --hl)* |
| German query or targeting DE/AT/CH | `--gl de --hl de` |
| French query or targeting France | `--gl fr --hl fr` |
| Any other language/country | `--gl XX --hl XX` (ISO codes) |

```bash
# German news
python3 scripts/search.py -q "Nachrichten aus Berlin" --mode current --gl de --hl de

# French product research
python3 scripts/search.py -q "meilleur smartphone 2026" --gl fr --hl fr
```

---

## Output Format

Streamed JSON array — elements print one at a time as each page is scraped:

```json
[{"query": "how does HTTPS work", "mode": "default", "locale": {"gl": "world", "hl": "en"}, "results": [{"title": "...", "url": "...", "source": "web"}]}
,{"title": "Page Title", "url": "https://example.com", "source": "web", "content": "Full extracted page text..."}
,{"title": "News Article", "url": "https://news.com", "source": "news", "date": "2 hours ago", "content": "Full article text..."}
]
```

The first element is search metadata. Each following element contains a result with full extracted content.

### Result Fields

| Field | Description |
|-------|-------------|
| `title` | Page title |
| `url` | Source URL |
| `source` | `"web"`, `"news"`, or `"knowledge_graph"` |
| `content` | Full extracted page text (falls back to snippet if extraction fails) |
| `date` | Present when available (news results always, web results sometimes) |

---

## CLI Reference

| Flag | Description |
|------|-------------|
| `-q, --query` | Search query (required) |
| `-m, --mode` | `default` (all-time, 5 results) or `current` (past week + news, 3 each) |
| `--gl` | Country code (e.g. `de`, `us`, `fr`, `at`, `ch`). Default: `world` |
| `--hl` | Language code (e.g. `en`, `de`, `fr`). Default: `en` |

---

## FAQ & Troubleshooting

**Q: Do I need a paid Serper account?**
> No. Serper offers 2,500 free queries at [serper.dev](https://serper.dev).

**Q: Why is content empty or just a snippet for some results?**
> Some sites block scraping. When trafilatura can't extract content, the skill falls back to the search snippet.

**Q: Does this work on Windows?**
> Yes. The script uses thread-based timeouts and works on all platforms.

**Error: "trafilatura is required but not installed"**
```bash
pip install --user trafilatura
# Then verify: python3 -c "import trafilatura; print('ok')"
```

**Error: "Missing Serper API key"**
```bash
# Add to ~/.openclaw/.env or ~/.openclaw/skills/serper/.env
echo 'SERPER_API_KEY="your-key"' >> ~/.openclaw/.env
```

**Error: "Invalid or expired API key" (401)**
> Generate a new key at [serper.dev](https://serper.dev).

**Error: "Rate limit exceeded" (429)**
> Wait and retry, or upgrade your Serper plan.

---

## License

MIT

---

## Links

- [Serper](https://serper.dev) — Google Search API (2,500 free queries)
- [ClawHub](https://www.clawhub.ai/nesdeq/serper) — Skill page
- [GitHub](https://github.com/nesdeq/openclaw-serper) — Source code & issues
