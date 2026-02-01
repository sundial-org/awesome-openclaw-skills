# Web Search by Exa

Real-time web search using Exa for fresh sources, citations, and quick content extraction without running a browser.

## Setup
Connect MCP server:
`https://mcp.exa.ai/mcp`

No API key needed.

## Tool
`web_search_exa`

## What it does
Searches the public web and returns the most relevant sources plus a condensed
context string for the top results. Useful for fast research, fact checking,
and getting up-to-date links.

## Inputs
- `query` (string, required): The search query. Natural language works best.
- `numResults` (int, optional): How many results to return (keep small for speed).
- `type` (string, optional): Search strategy: `auto`, `fast`, `deep`.
- `livecrawl` (string, optional): `fallback` or `preferred`.
- `contextMaxCharacters` (int, optional): Limit size of returned context string.

## Examples
Basic search (5-10 results):
```
web_search_exa { "query": "latest MCP tooling trends 2026" }
```

Focused search, faster:
```
web_search_exa {
  "query": "What is the latest news in techcrunch",
  "numResults": 5,
  "type": "fast"
}
```

Deep research with more context:
```
web_search_exa {
  "query": "Top AI productivity tools for startups in 2026",
  "numResults": 8,
  "type": "deep",
  "contextMaxCharacters": 8000
}
```

## When to Use
- Looking up recent info beyond model training data
- Finding official docs, blog posts, or changelogs
- Quick source lists for fact checking or citations
- Light content extraction for summaries or analysis

## Notes
- Provide precise queries and include domain hints for better results.
- If you need full-page extraction for a specific URL, use Exa "contents" tools
  (outside this web_search_exa-only skill).

## References
- Exa MCP: https://exa.ai/docs/reference/exa-mcp
- Exa Search API: https://exa.ai/docs/reference/search