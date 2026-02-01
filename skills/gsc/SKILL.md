---
name: gsc
description: Query Google Search Console for SEO data - search queries, top pages, CTR opportunities, URL inspection, and sitemaps. Use when analyzing search performance, finding optimization opportunities, or checking indexing status.
---

# Google Search Console Skill

Query GSC for search analytics, indexing status, and SEO insights.

## Setup

1. **Credentials**: Uses same OAuth credentials as GA4 skill (stored in `.env`)
2. **Scopes**: Requires `webmasters.readonly` scope on your Google Cloud OAuth consent screen
3. **Access**: Your Google account must have access to the Search Console properties

## Commands

### List Available Sites
```bash
source /Users/admin/clawd/skills/gsc/.env && \
python /Users/admin/clawd/skills/gsc/scripts/gsc_query.py sites
```

### Top Search Queries
```bash
source /Users/admin/clawd/skills/gsc/.env && \
python /Users/admin/clawd/skills/gsc/scripts/gsc_query.py top-queries \
  --site "https://www.nutrient.io" \
  --days 28 \
  --limit 20
```

### Top Pages by Traffic
```bash
source /Users/admin/clawd/skills/gsc/.env && \
python /Users/admin/clawd/skills/gsc/scripts/gsc_query.py top-pages \
  --site "https://www.nutrient.io" \
  --days 28 \
  --limit 20
```

### Find Low-CTR Opportunities
High impressions but low click-through rate = optimization opportunities:
```bash
source /Users/admin/clawd/skills/gsc/.env && \
python /Users/admin/clawd/skills/gsc/scripts/gsc_query.py opportunities \
  --site "https://www.nutrient.io" \
  --days 28 \
  --min-impressions 100
```

### Inspect URL Indexing Status
```bash
source /Users/admin/clawd/skills/gsc/.env && \
python /Users/admin/clawd/skills/gsc/scripts/gsc_query.py inspect-url \
  --site "https://www.nutrient.io" \
  --url "/sdk/web"
```

### List Sitemaps
```bash
source /Users/admin/clawd/skills/gsc/.env && \
python /Users/admin/clawd/skills/gsc/scripts/gsc_query.py sitemaps \
  --site "https://www.nutrient.io"
```

### Raw Search Analytics (JSON)
```bash
source /Users/admin/clawd/skills/gsc/.env && \
python /Users/admin/clawd/skills/gsc/scripts/gsc_query.py search-analytics \
  --site "https://www.nutrient.io" \
  --days 28 \
  --dimensions query page \
  --limit 100
```

## Available Dimensions
- `query` - Search query
- `page` - Landing page URL
- `country` - Country code
- `device` - DESKTOP, MOBILE, TABLET
- `date` - Date

## Metrics Returned
- **clicks** - Number of clicks from search
- **impressions** - Number of times shown in search
- **ctr** - Click-through rate (clicks/impressions)
- **position** - Average ranking position

## SEO Use Cases

1. **Content Optimization**: Find high-impression/low-CTR pages → improve titles & descriptions
2. **Keyword Research**: See what queries bring traffic → create more content around them
3. **Technical SEO**: Check indexing status, find crawl issues
4. **Ranking Tracking**: Monitor position changes over time
5. **Sitemap Health**: Verify sitemaps are submitted and error-free

## Notes

- Data has ~3 day delay (GSC limitation)
- Credentials shared with GA4 skill
- URL inspection requires the page to be in the property
