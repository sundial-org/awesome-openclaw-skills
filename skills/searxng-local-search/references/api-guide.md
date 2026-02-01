# SearXNG API Reference

This document provides detailed information about the SearXNG JSON API used by the search skill.

## Endpoint

```
GET /search
```

## Query Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | The search query |
| `format` | string | Response format (use `json`) |

### Optional

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `language` | string | Language code (en, es, de, fr, etc.) | `en` |
| `pageno` | integer | Page number for pagination | `1` |
| `time_range` | string | Time filter: `day`, `week`, `month`, `year` | None |
| `category_X` | string | Filter by category (set to `1` to enable) | None |

### Categories

Enable specific categories by setting `category_NAME=1`:

- `category_general` - General web search
- `category_images` - Image search
- `category_videos` - Video search
- `category_news` - News articles
- `category_map` - Maps and locations
- `category_music` - Music search
- `category_files` - File search
- `category_it` - IT/technical content
- `category_science` - Scientific articles
- `category_social` - Social media

## Response Format

```json
{
  "query": "search query",
  "number_of_results": 42,
  "results": [
    {
      "url": "https://example.com/page",
      "title": "Page Title",
      "content": "Description snippet...",
      "engine": "google",
      "engines": ["google", "bing"],
      "category": "general",
      "score": 1.85,
      "pretty_url": "https://example.com/page",
      "parsed_url": ["https", "example.com", "/page", "", "", ""],
      "publishedDate": "2024-01-15T12:00:00"
    }
  ],
  "answers": [],
  "corrections": [],
  "infoboxes": [],
  "suggestions": ["related query 1", "related query 2"],
  "unresponsive_engines": []
}
```

## Result Fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Full URL of the result |
| `title` | string | Page title |
| `content` | string | Description or snippet |
| `engine` | string | Primary search engine |
| `engines` | array | All engines that returned this result |
| `score` | float | Relevance score (higher is better) |
| `category` | string | Result category |
| `publishedDate` | string | Publication date (ISO 8601) |

## Example Requests

### Basic Search

```bash
curl "http://localhost:8888/search?q=NixOS&format=json"
```

### Category Filter

```bash
curl "http://localhost:8888/search?q=python&category_it=1&format=json"
```

### Time Range Filter

```bash
curl "http://localhost:8888/search?q=news&time_range=day&format=json"
```

### Multiple Filters

```bash
curl "http://localhost:8888/search?q=AI&category_news=1&time_range=week&language=en&format=json"
```

### Pagination

```bash
curl "http://localhost:8888/search?q=rust&pageno=2&format=json"
```

## Rate Limiting

SearXNG implements rate limiting to prevent abuse. The default configuration allows:

- IP-based rate limiting
- Bot detection via various heuristics
- Link token verification

If you receive a 429 (Too Many Requests) response:
- Wait a few seconds before retrying
- Implement exponential backoff
- Cache frequently-accessed results

## Error Responses

### 400 Bad Request

Missing required parameters or invalid format.

```json
{
  "error": "Missing required parameter: q"
}
```

### 429 Too Many Requests

Rate limit exceeded.

```json
{
  "error": "Rate limit exceeded"
}
```

### 500 Internal Server Error

SearXNG server error. Check logs:

```bash
journalctl -u searx -n 50
```

## Best Practices

### 1. Query Construction

- Keep queries concise (1-6 words is optimal)
- Use quotes for exact phrases: `"exact phrase"`
- Use boolean operators: `term1 OR term2`
- Exclude terms with minus: `query -excluded`

### 2. Result Handling

- Sort by score for best results
- Check multiple engines for reliability
- Handle empty results gracefully
- Respect `unresponsive_engines` field

### 3. Performance

- Cache results locally when possible
- Use appropriate timeouts (30s recommended)
- Implement retry logic with exponential backoff
- Monitor response times

### 4. Categories

Choose appropriate categories for your query:

| Query Type | Best Category |
|------------|---------------|
| Current events | `news` |
| Code/documentation | `it` |
| Research papers | `science` |
| How-to guides | `general` |
| Media content | `videos` or `images` |

### 5. Time Ranges

Use time filters for time-sensitive queries:

- `day` - Breaking news, stock prices
- `week` - Recent updates, current events
- `month` - Trends, ongoing stories
- `year` - Annual reports, yearly summaries

## Engine-Specific Notes

SearXNG aggregates results from multiple search engines. Common engines:

- **Google** - Broad coverage, good relevance
- **Bing** - Good for recent content
- **DuckDuckGo** - Privacy-focused
- **Wikipedia** - Encyclopedic content
- **Stack Overflow** - Programming Q&A
- **GitHub** - Code repositories
- **arXiv** - Scientific papers

Each result may come from multiple engines, indicated in the `engines` array.

## Troubleshooting

### No Results

1. Check query is not too specific
2. Remove filters and try again
3. Verify engines are responding:
   ```bash
   journalctl -u searx | grep -i error
   ```

### Slow Responses

1. Check `unresponsive_engines` field
2. Increase timeout in client
3. Disable slow engines in SearXNG config

### Inconsistent Results

1. Results vary by engine availability
2. Check which engines responded: `engines` field
3. Consider using score for ranking

## Advanced Configuration

For custom SearXNG configurations, edit the NixOS module:

```nix
services.searx.settings.engines = [
  {
    name = "google";
    weight = 1.5;  # Boost Google results
  }
  {
    name = "duckduckgo";
    disabled = true;  # Disable DDG
  }
];
```

## Resources

- [SearXNG Documentation](https://docs.searxng.org/)
- [SearXNG GitHub](https://github.com/searxng/searxng)
- [Engine Configuration](https://docs.searxng.org/admin/engines/index.html)
- [API Documentation](https://docs.searxng.org/dev/search_api.html)
