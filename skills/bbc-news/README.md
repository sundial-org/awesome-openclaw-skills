# BBC News Skill

A Clawdbot skill for fetching BBC News stories from various sections and regions via RSS feeds.

## Features

- 📰 **Multiple Sections**: Top stories, UK, World, Business, Politics, Health, Education, Science, Technology, Entertainment
- 🌍 **UK Regional News**: England, Scotland, Wales, Northern Ireland
- 🗺️ **World Regions**: Africa, Asia, Australia, Europe, Latin America, Middle East, US & Canada
- 📊 **Flexible Output**: Text or JSON format
- ⚙️ **Customizable**: Limit number of stories

## Installation

### Via ClawdHub

```bash
clawdhub install bbc-news
```

### Manual Installation

```bash
# Clone the repo
git clone https://github.com/ddrayne/bbc-news-skill.git ~/.clawdbot/skills/bbc-news

# Install dependencies
pip3 install feedparser
```

## Usage

### With Clawdbot

Ask your agent:
- "What's the latest BBC news?"
- "Show me UK technology news from BBC"
- "Get top 5 Scotland stories"

### Direct Script Usage

```bash
# Top stories (default)
python3 ~/.clawdbot/skills/bbc-news/scripts/bbc_news.py

# Specific section
python3 ~/.clawdbot/skills/bbc-news/scripts/bbc_news.py technology

# Limit results
python3 ~/.clawdbot/skills/bbc-news/scripts/bbc_news.py uk --limit 5

# JSON output
python3 ~/.clawdbot/skills/bbc-news/scripts/bbc_news.py world --json

# List all sections
python3 ~/.clawdbot/skills/bbc-news/scripts/bbc_news.py --list
```

## Available Sections

### Main Sections
`top`, `uk`, `world`, `business`, `politics`, `health`, `education`, `science`, `technology`, `entertainment`

### UK Regional
`england`, `scotland`, `wales`, `northern-ireland`

### World Regions
`africa`, `asia`, `australia`, `europe`, `latin-america`, `middle-east`, `us-canada`

## Dependencies

- Python 3
- feedparser (`pip3 install feedparser`)

## License

MIT
