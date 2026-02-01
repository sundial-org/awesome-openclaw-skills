---
name: brave-images
description: Search for images using Brave Search API. Use when you need to find images, pictures, photos, or visual content on any topic. Requires BRAVE_API_KEY environment variable.
---

# Brave Image Search

Search images via Brave Search API.

## Usage

```bash
curl -s "https://api.search.brave.com/res/v1/images/search?q=QUERY&count=COUNT" \
  -H "X-Subscription-Token: $BRAVE_API_KEY"
```

## Parameters

| Param | Required | Description |
|-------|----------|-------------|
| `q` | yes | Search query (URL-encoded) |
| `count` | no | Results count (1-100, default 20) |
| `country` | no | 2-letter code (US, DE, IL) for region bias |
| `search_lang` | no | Language code (en, de, he) |
| `safesearch` | no | off, moderate, strict (default: moderate) |

## Response Parsing

Key fields in each result:
- `results[].title` — Image title
- `results[].properties.url` — Full image URL
- `results[].thumbnail.src` — Thumbnail URL  
- `results[].source` — Source website
- `results[].properties.width/height` — Dimensions

## Example

Search for "sunset beach" images in Israel:
```bash
curl -s "https://api.search.brave.com/res/v1/images/search?q=sunset%20beach&count=5&country=IL" \
  -H "X-Subscription-Token: $BRAVE_API_KEY"
```

Then extract from JSON response:
- Thumbnail: `.results[0].thumbnail.src`
- Full image: `.results[0].properties.url`

## Delivering Results

When presenting image search results:
1. Send images directly to the user (don't just list URLs)
2. Use `results[].properties.url` for full images or `results[].thumbnail.src` for thumbnails
3. Include image title as caption
4. If more results exist than shown, tell the user (e.g., "Found 20 images, showing 3 — want more?")

Example flow:
```
User: "find me pictures of sunsets"
→ Search with count=10
→ Send 3-5 images with captions
→ "Found 10 sunset images, showing 5. Want to see more?"
```

## Notes

- URL-encode query strings (spaces → `%20`)
- API key from env: `$BRAVE_API_KEY`
- Respect rate limits per subscription tier
