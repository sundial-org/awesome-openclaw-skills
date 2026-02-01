---
name: seo-dataforseo
description: "SEO keyword research using the DataForSEO API. Perform keyword analysis, YouTube keyword research, competitor analysis, SERP analysis, and trend tracking. Use when the user asks to: research keywords, analyze search volume/CPC/competition, find keyword suggestions, check keyword difficulty, analyze competitors, get trending topics, do YouTube SEO research, or optimize landing page keywords. Requires a DataForSEO API account and credentials in .env file."
---

# SEO Keyword Research (DataForSEO)

## Setup

Install dependencies:

```bash
pip install -r scripts/requirements.txt
```

Configure credentials by creating a `.env` file in the project root:

```
DATAFORSEO_LOGIN=your_email@example.com
DATAFORSEO_PASSWORD=your_api_password
```

Get credentials from: https://app.dataforseo.com/api-access

## Quick Start

| User says | Function to call |
|-----------|-----------------|
| "Research keywords for [topic]" | `keyword_research("topic")` |
| "YouTube keyword data for [idea]" | `youtube_keyword_research("idea")` |
| "Analyze competitor [domain.com]" | `competitor_analysis("domain.com")` |
| "What's trending?" | `trending_topics()` |
| "Keyword analysis for [list]" | `full_keyword_analysis(["kw1", "kw2"])` |
| "Landing page keywords for [topic]" | `landing_page_keyword_research(["kw1"], "competitor.com")` |

Execute functions by importing from `scripts/main.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("scripts")))
from main import *

result = keyword_research("AI website builders")
```

## Workflow Pattern

Every research task follows three phases:

### 1. Research
Run API functions. Each function call hits the DataForSEO API and returns structured data.

### 2. Auto-Save
All results automatically save as timestamped JSON files to `results/{category}/`. File naming pattern: `YYYYMMDD_HHMMSS__operation__keyword__extra_info.json`

### 3. Summarize
After research, read the saved JSON files and create a markdown summary in `results/summary/` with data tables, ranked opportunities, and strategic recommendations.

## High-Level Functions

These are the primary functions in `scripts/main.py`. Each orchestrates multiple API calls for a complete research workflow.

| Function | Purpose | What it gathers |
|----------|---------|----------------|
| `keyword_research(keyword)` | Single keyword deep-dive | Overview, suggestions, related keywords, difficulty |
| `youtube_keyword_research(keyword)` | YouTube content research | Overview, suggestions, YouTube SERP rankings, YouTube trends |
| `landing_page_keyword_research(keywords, competitor_domain)` | Landing page SEO | Overview, intent, difficulty, SERP analysis, competitor keywords |
| `full_keyword_analysis(keywords)` | Strategic content planning | Overview, difficulty, intent, keyword ideas, historical volume, Google Trends |
| `competitor_analysis(domain, keywords)` | Competitor intelligence | Domain keywords, Google Ads keywords, competitor domains |
| `trending_topics(location_name)` | Current trends | Currently trending searches |

### Parameters

All functions accept an optional `location_name` parameter (default: "United States"). Most functions also have boolean flags to skip specific sub-analyses (e.g., `include_suggestions=False`).

### Individual API Functions

For granular control, import specific functions from the API modules. See [references/api-reference.md](references/api-reference.md) for the complete list of 25 API functions with parameters, limits, and examples.

## Results Storage

Results auto-save to `results/` with this structure:

```
results/
├── keywords_data/    # Search volume, CPC, competition
├── labs/             # Suggestions, difficulty, intent
├── serp/             # Google/YouTube rankings
├── trends/           # Google Trends data
└── summary/          # Human-readable markdown summaries
```

### Managing Results

```python
from core.storage import list_results, load_result, get_latest_result

# List recent results
files = list_results(category="labs", limit=10)

# Load a specific result
data = load_result(files[0])

# Get most recent result for an operation
latest = get_latest_result(category="labs", operation="keyword_suggestions")
```

### Utility Functions

```python
from main import get_recent_results, load_latest

# List recent files across all categories
files = get_recent_results(limit=10)

# Load latest result for a category
data = load_latest("labs", "keyword_suggestions")
```

## Creating Summaries

After running research, create a markdown summary document in `results/summary/`. Include:

- **Data tables** with volumes, CPC, competition, difficulty
- **Ranked lists** of opportunities (sorted by volume or opportunity score)
- **SERP analysis** showing what currently ranks
- **Recommendations** for content strategy, titles, tags

Name the summary file descriptively (e.g., `results/summary/ai-tools-keyword-research.md`).

## Tips

1. **Be specific** — "Get keyword suggestions for 'AI website builders'" works better than "research AI stuff"
2. **Request summaries** — Always create a summary document after research, named specifically
3. **Batch related keywords** — Pass multiple related keywords at once for comparison
4. **Specify the goal** — "for a YouTube video" vs "for a landing page" changes which data matters most
5. **Ask for competition analysis** — "Show me what videos are ranking" helps identify content gaps

## Defaults

- **Location**: United States (code 2840)
- **Language**: English
- **API Limits**: 700 keywords for volume/overview, 1000 for difficulty/intent, 5 for trends, 200 for keyword ideas
