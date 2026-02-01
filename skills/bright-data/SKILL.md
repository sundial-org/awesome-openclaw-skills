---
name: brightdata
description: Web scraping and search via Bright Data API. Requires BRIGHTDATA_API_KEY and BRIGHTDATA_UNLOCKER_ZONE. Use for scraping any webpage as markdown (bypassing bot detection/CAPTCHA) or searching Google with structured results.
---

# Bright Data - Web Scraping & Search

Direct API access to Bright Data's Web Unlocker and SERP APIs.

## Setup

**1. Get your API Key:**
Get a key from [Bright Data Dashboard](https://brightdata.com/cp).

**2. Create a Web Unlocker zone:**
Create a zone at brightdata.com/cp by clicking "Add" (top-right), selecting "Unlocker zone".

**3. Set environment variables:**
```bash
export BRIGHTDATA_API_KEY="your-api-key"
export BRIGHTDATA_UNLOCKER_ZONE="your-zone-name"
```

## Usage

### Google Search
Search Google and get structured JSON results (title, link, description).
```bash
bash scripts/search.sh "query" [cursor]
```
- `cursor`: Optional page number for pagination (0-indexed, default: 0)

### Web Scraping
Scrape any webpage as markdown. Bypasses bot detection and CAPTCHA.
```bash
bash scripts/scrape.sh "url"
```

## Output Formats

### Search Results
Returns JSON with structured `organic` array:
```json
{
  "organic": [
    {"link": "...", "title": "...", "description": "..."}
  ]
}
```

### Scrape Results
Returns clean markdown content from the webpage.
