---
name: local-rag-search
description: Efficiently perform web searches using the mcp-local-rag server with semantic similarity ranking. Use this skill when you need to search the web for current information, research topics across multiple sources, or gather context from the internet without using external APIs. This skill teaches effective use of RAG-based web search with DuckDuckGo, Google, and multi-engine deep research capabilities.
---

# Local RAG Search Skill

This skill enables you to effectively use the mcp-local-rag MCP server for intelligent web searches with semantic ranking. The server performs RAG-like similarity scoring to prioritize the most relevant results without requiring any external APIs.

## Available Tools

### 1. `rag_search_ddgs` - DuckDuckGo Search
Use this for privacy-focused, general web searches.

**When to use:**
- User prefers privacy-focused searches
- General information lookup
- Default choice for most queries

**Parameters:**
- `query`: Natural language search query
- `num_results`: Initial results to fetch (default: 10)
- `top_k`: Most relevant results to return (default: 5)
- `include_urls`: Include source URLs (default: true)

### 2. `rag_search_google` - Google Search
Use this for comprehensive, technical, or detailed searches.

**When to use:**
- Technical or scientific queries
- Need comprehensive coverage
- Searching for specific documentation

### 3. `deep_research` - Multi-Engine Deep Research
Use this for comprehensive research across multiple search engines.

**When to use:**
- Researching complex topics requiring broad coverage
- Need diverse perspectives from multiple sources
- Gathering comprehensive information on a subject

**Available backends:**
- `duckduckgo`: Privacy-focused general search
- `google`: Comprehensive technical results
- `bing`: Microsoft's search engine
- `brave`: Privacy-first search
- `wikipedia`: Encyclopedia/factual content
- `yahoo`, `yandex`, `mojeek`, `grokipedia`: Alternative engines

**Default:** `["duckduckgo", "google"]`

### 4. `deep_research_google` - Google-Only Deep Research
Shortcut for deep research using only Google.

### 5. `deep_research_ddgs` - DuckDuckGo-Only Deep Research
Shortcut for deep research using only DuckDuckGo.

## Best Practices

### Query Formulation
1. **Use natural language**: Write queries as questions or descriptive phrases
   - Good: "latest developments in quantum computing"
   - Good: "how to implement binary search in Python"
   - Avoid: Single keywords like "quantum" or "Python"

2. **Be specific**: Include context and details
   - Good: "React hooks best practices for 2024"
   - Better: "React useEffect cleanup function best practices"

### Tool Selection Strategy

1. **Single Topic, Quick Answer** → Use `rag_search_ddgs` or `rag_search_google`
   ```
   rag_search_ddgs(
       query="What is the capital of France?",
       top_k=3
   )
   ```

2. **Technical/Scientific Query** → Use `rag_search_google`
   ```
   rag_search_google(
       query="Docker multi-stage build optimization techniques",
       num_results=15,
       top_k=7
   )
   ```

3. **Comprehensive Research** → Use `deep_research` with multiple search terms
   ```
   deep_research(
       search_terms=[
           "machine learning fundamentals",
           "neural networks architecture",
           "deep learning best practices 2024"
       ],
       backends=["google", "duckduckgo"],
       top_k_per_term=5
   )
   ```

4. **Factual/Encyclopedia Content** → Use `deep_research` with Wikipedia
   ```
   deep_research(
       search_terms=["World War II timeline", "WWII key battles"],
       backends=["wikipedia"],
       num_results_per_term=5
   )
   ```

### Parameter Tuning

**For quick answers:**
- `num_results=5-10`, `top_k=3-5`

**For comprehensive research:**
- `num_results=15-20`, `top_k=7-10`

**For deep research:**
- `num_results_per_term=10-15`, `top_k_per_term=3-5`
- Use 2-5 related search terms
- Use 1-3 backends (more = more comprehensive but slower)

## Workflow Examples

### Example 1: Current Events
```
Task: "What happened at the UN climate summit last week?"

1. Use rag_search_google for recent news coverage
2. Set top_k=7 for comprehensive view
3. Present findings with source URLs
```

### Example 2: Technical Deep Dive
```
Task: "How do I optimize PostgreSQL queries?"

1. Use deep_research with multiple specific terms:
   - "PostgreSQL query optimization techniques"
   - "PostgreSQL index best practices"
   - "PostgreSQL EXPLAIN ANALYZE tutorial"
2. Use backends=["google", "stackoverflow"] if available
3. Synthesize findings into actionable guide
```

### Example 3: Multi-Perspective Research
```
Task: "Research the impact of remote work on productivity"

1. Use deep_research with diverse search terms:
   - "remote work productivity statistics 2024"
   - "hybrid work model effectiveness studies"
   - "work from home challenges research"
2. Use backends=["google", "duckduckgo"] for broad coverage
3. Synthesize different perspectives and studies
```

## Guidelines

1. **Always cite sources**: When `include_urls=True`, reference the source URLs in your response
2. **Verify recency**: Check if the content appears current and relevant
3. **Cross-reference**: For important facts, use multiple search terms or engines
4. **Respect privacy**: Use DuckDuckGo for general queries unless specific needs require Google
5. **Batch related queries**: When researching a topic, create multiple related search terms for deep_research
6. **Semantic relevance**: Trust the RAG scoring - top results are semantically closest to the query
7. **Explain your choice**: Briefly mention which tool you're using and why

## Error Handling

If a search returns insufficient results:
1. Try rephrasing the query with different keywords
2. Switch to a different backend
3. Increase `num_results` parameter
4. Use `deep_research` with multiple related search terms

## Privacy Considerations

- DuckDuckGo: Privacy-focused, doesn't track users
- Google: Most comprehensive but tracks searches
- Recommend DuckDuckGo as default unless user specifically needs Google's coverage

## Performance Notes

- First search may be slower (model loading)
- Subsequent searches are faster (cached models)
- More backends = more comprehensive but slower
- Adjust `num_results` and `top_k` based on use case
