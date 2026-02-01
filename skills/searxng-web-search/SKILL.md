---
name: searxng-web-search
description: Search the web using SearXNG. Use when you need current information, research topics, find documentation, verify facts, or look up anything beyond your knowledge. Returns ranked results with titles, URLs, and content snippets.
metadata:
  openclaw:
    requires:
      bins: ["bb"]
      env: ["SEARXNG_URL"]
    emoji: "🔍"
    nix:
      plugin: "babashka"
---

# SearXNG Web Search

Search the web using a self-hosted SearXNG instance. This skill provides access to web search results through the SearXNG JSON API, with built-in rate limiting, error handling, and result formatting.

## When to Use

Use this skill when you need to:
- Find current information or recent news
- Research topics beyond your knowledge cutoff
- Look up documentation or technical references
- Verify facts or check current status
- Find URLs or resources on specific topics
- Search for code examples or solutions

## Configuration

Set the `SEARXNG_URL` environment variable to your SearXNG instance:

```bash
export SEARXNG_URL="http://localhost:8888"
```

Or use the default (http://localhost:8888) if not set.

## Usage

Execute the search script with your query:

```bash
bb scripts/search.clj "your search query"
```

### Advanced Options

Pass additional parameters as JSON:

```bash
bb scripts/search.clj "your query" '{"category": "news", "time_range": "day", "num_results": 10}'
```

Available options:
- `category` - Filter by category: general, news, images, videos, it, science
- `time_range` - Time filter: day, week, month, year
- `language` - Language code (default: en)
- `num_results` - Number of results to return (default: 5)

## Output Format

The script returns formatted search results as text:

```
Search Results for "your query"
Found 42 total results

1. Result Title [Score: 1.85]
   URL: https://example.com/page
   Description snippet from the page...
   Engines: google, bing

2. Another Result [Score: 1.62]
   ...
```

## Error Handling

The script handles common errors gracefully:
- Network timeouts (30s timeout)
- SearXNG unavailable (clear error message)
- Invalid queries (error details)
- Rate limiting (429 responses)
- Empty results (informative message)

## Rate Limiting

The script implements basic rate limiting:
- Minimum 1 second between requests
- Uses filesystem-based state (`.searxng-last-request`)
- Prevents accidental spam

## Examples

### Basic Search
```bash
bb scripts/search.clj "NixOS configuration"
```

### News Search
```bash
bb scripts/search.clj "AI developments" '{"category": "news", "time_range": "week"}'
```

### Technical Search
```bash
bb scripts/search.clj "babashka http client" '{"category": "it", "num_results": 3}'
```

### Recent Results Only
```bash
bb scripts/search.clj "product launch" '{"time_range": "day"}'
```

## Troubleshooting

**"SEARXNG_URL not set"**
- Set the environment variable: `export SEARXNG_URL="http://localhost:8888"`

**Connection timeout**
- Check that SearXNG is running: `curl $SEARXNG_URL/search?q=test&format=json`
- Verify firewall settings
- Check service status: `systemctl status searx`

**Empty results**
- Try a broader query
- Remove filters and try again
- Check SearXNG logs: `journalctl -u searx -n 50`

**Rate limit errors**
- Wait a few seconds between searches
- The script enforces minimum 1s delay automatically

## Implementation Notes

The search script (`scripts/search.clj`) uses:
- `babashka.http-client` for HTTP requests
- Clojure's `cheshire.core` for JSON parsing
- Filesystem-based rate limiting
- 30-second timeout with proper error messages
- Result scoring and sorting for best results first

For detailed API documentation, see `references/api-guide.md`.
