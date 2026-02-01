---
name: tabstack-extractor
description: Extract structured data from websites using Tabstack API. Use when you need to scrape job listings, news articles, product pages, or any structured web content. Provides JSON schema-based extraction and clean markdown conversion. Requires TABSTACK_API_KEY environment variable.
---

# Tabstack Extractor

## Overview

This skill enables structured data extraction from websites using the Tabstack API. It's ideal for web scraping tasks where you need consistent, schema-based data extraction from job boards, news sites, product pages, or any structured content.

## Quick Start

### 1. Install Babashka (if needed)
```bash
# Option A: From GitHub (recommended for sharing)
curl -s https://raw.githubusercontent.com/babashka/babashka/master/install | bash

# Option B: From Nix
nix-shell -p babashka

# Option C: From Homebrew
brew install borkdude/brew/babashka
```

### 2. Set up API Key

**Option A: Environment variable (recommended)**
```bash
export TABSTACK_API_KEY="your_api_key_here"
```

**Option B: Configuration file**
```bash
mkdir -p ~/.config/tabstack
echo '{:api-key "your_api_key_here"}' > ~/.config/tabstack/config.edn
```

**Get an API key:** Sign up at [Tabstack Console](https://console.tabstack.ai/signup)

### 3. Test Connection
```bash
bb scripts/tabstack.clj test
```

### 4. Extract Markdown (Simple)
```bash
bb scripts/tabstack.clj markdown "https://example.com"
```

### 5. Extract JSON (Start Simple)
```bash
# Start with simple schema (fast, reliable)
bb scripts/tabstack.clj json "https://example.com" references/simple_article.json

# Try more complex schemas (may be slower)
bb scripts/tabstack.clj json "https://news.site" references/news_schema.json
```

### 6. Advanced Features
```bash
# Extract with retry logic (3 retries, 1s delay)
bb scripts/tabstack.clj json-retry "https://example.com" references/simple_article.json

# Extract with caching (24-hour cache)
bb scripts/tabstack.clj json-cache "https://example.com" references/simple_article.json

# Batch extract from URLs file
echo "https://example.com" > urls.txt
echo "https://example.org" >> urls.txt
bb scripts/tabstack.clj batch urls.txt references/simple_article.json
```

## Core Capabilities

### 1. Markdown Extraction
Extract clean, readable markdown from any webpage. Useful for content analysis, summarization, or archiving.

**When to use:** When you need the textual content of a page without the HTML clutter.

**Example use cases:**
- Extract article content for summarization
- Archive webpage content
- Analyze blog post content

### 2. JSON Schema Extraction
Extract structured data using JSON schemas. Define exactly what data you want and get it in a consistent format.

**When to use:** When scraping job listings, product pages, news articles, or any structured data.

**Example use cases:**
- Scrape job listings from BuiltIn/LinkedIn
- Extract product details from e-commerce sites
- Gather news articles with consistent metadata

### 3. Schema Templates
Pre-built schemas for common scraping tasks. See `references/` directory for templates.

**Available schemas:**
- Job listing schema (see `references/job_schema.json`)
- News article schema
- Product page schema
- Contact information schema

## Workflow: Job Scraping Example

Follow this workflow to scrape job listings:

1. **Identify target sites** - BuiltIn, LinkedIn, company career pages
2. **Choose or create schema** - Use `references/job_schema.json` or customize
3. **Test extraction** - Run a single page to verify schema works
4. **Scale up** - Process multiple URLs
5. **Store results** - Save to database or file

**Example job schema:**
```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "company": {"type": "string"},
    "location": {"type": "string"},
    "description": {"type": "string"},
    "salary": {"type": "string"},
    "apply_url": {"type": "string"},
    "posted_date": {"type": "string"},
    "requirements": {"type": "array", "items": {"type": "string"}}
  }
}
```

## Integration with Other Skills

### Combine with Web Search
1. Use `web_search` to find relevant URLs
2. Use Tabstack to extract structured data from those URLs
3. Store results in Datalevin (future skill)

### Combine with Browser Automation
1. Use `browser` tool to navigate complex sites
2. Extract page URLs
3. Use Tabstack for structured extraction

## Error Handling

Common issues and solutions:

1. **Authentication failed** - Check `TABSTACK_API_KEY` environment variable
2. **Invalid URL** - Ensure URL is accessible and correct
3. **Schema mismatch** - Adjust schema to match page structure
4. **Rate limiting** - Add delays between requests

## Resources

### scripts/
- `tabstack.clj` - **Main API wrapper in Babashka** (recommended, has retry logic, caching, batch processing)
- `tabstack_curl.sh` - Bash/curl fallback (simple, no dependencies)
- `tabstack_api.py` - Python API wrapper (requires requests module)

### references/
- `job_schema.json` - Template schema for job listings
- `api_reference.md` - Tabstack API documentation

## Best Practices

1. **Start small** - Test with single pages before scaling
2. **Respect robots.txt** - Check site scraping policies
3. **Add delays** - Avoid overwhelming target sites
4. **Validate schemas** - Test schemas on sample pages
5. **Handle errors gracefully** - Implement retry logic for failed requests

## Teaching Focus: How to Create Schemas

This skill is designed to teach agents how to use Tabstack API effectively. The key is learning to create appropriate JSON schemas for different websites.

### Learning Path
1. **Start Simple** - Use `references/simple_article.json` (4 basic fields)
2. **Test Extensively** - Try schemas on multiple page types
3. **Iterate** - Add fields based on what the page actually contains
4. **Optimize** - Remove unnecessary fields for speed

See [Schema Creation Guide](references/schema_guide.md) for detailed instructions and examples.

### Common Mistakes to Avoid
- **Over-complex schemas** - Start with 2-3 fields, not 20
- **Missing fields** - Don't require fields that don't exist on the page
- **No testing** - Always test with example.com first, then target sites
- **Ignoring timeouts** - Complex schemas take longer (45s timeout)

## Babashka Advantages

Using Babashka for this skill provides:

1. **Single binary** - Easy to share/install (GitHub releases, brew, nix)
2. **Fast startup** - No JVM warmup, ~50ms startup time
3. **Built-in HTTP client** - No external dependencies
4. **Clojure syntax** - Familiar to you (Wes), expressive
5. **Retry logic & caching** - Built into the skill
6. **Batch processing** - Parallel extraction for multiple URLs

## Example User Requests

**For this skill to trigger:**
- "Scrape job listings from Docker careers page"
- "Extract the main content from this article"
- "Get structured product data from this e-commerce page"
- "Pull all the news articles from this site"
- "Extract contact information from this company page"
- "Batch extract job listings from these 20 URLs"
- "Get cached results for this page (avoid API calls)"
