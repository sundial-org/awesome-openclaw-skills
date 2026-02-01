---
name: bbc-news
description: Fetch and display BBC News stories from various sections and regions via RSS feeds. Use when the user asks for BBC news, UK news headlines, world news from BBC, or news from specific BBC sections (technology, business, politics, science, health, entertainment, regional UK news, or world regions).
---

# BBC News

Fetch top stories from BBC News across different sections and regions.

## Quick Start

Fetch top stories:
```bash
python3 scripts/bbc_news.py
```

Fetch from specific section:
```bash
python3 scripts/bbc_news.py uk
python3 scripts/bbc_news.py world
python3 scripts/bbc_news.py technology
```

List all available sections:
```bash
python3 scripts/bbc_news.py --list
```

## Available Sections

### Main Sections
- `top` - Top stories (default)
- `uk` - UK news
- `world` - World news
- `business` - Business news
- `politics` - Politics
- `health` - Health news
- `education` - Education
- `science` - Science & Environment
- `technology` - Technology news
- `entertainment` - Entertainment & Arts

### UK Regional
- `england` - England news
- `scotland` - Scotland news
- `wales` - Wales news
- `northern-ireland` - Northern Ireland news

### World Regions
- `africa` - Africa news
- `asia` - Asia news
- `australia` - Australia news
- `europe` - Europe news
- `latin-america` - Latin America news
- `middle-east` - Middle East news
- `us-canada` - US & Canada news

## Options

**Limit number of stories:**
```bash
python3 scripts/bbc_news.py world --limit 5
```

**JSON output:**
```bash
python3 scripts/bbc_news.py technology --json
```

## Examples

Get top 5 UK stories:
```bash
python3 scripts/bbc_news.py uk --limit 5
```

Get Scotland news in JSON:
```bash
python3 scripts/bbc_news.py scotland --json
```

Get latest technology headlines:
```bash
python3 scripts/bbc_news.py technology --limit 3
```

## Dependencies

Requires `feedparser`:
```bash
pip3 install feedparser
```

## Resources

### scripts/bbc_news.py
Python CLI that fetches and displays BBC News stories from RSS feeds. Supports all major BBC sections and regions, with text and JSON output formats.

### references/feeds.md
Complete list of BBC News RSS feed URLs organized by section and region.
