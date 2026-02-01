# Octolens Filter Reference Guide

This document provides comprehensive documentation on filtering mentions in the Octolens API.

## Filter Modes

The Octolens API supports two filtering modes: **Simple Mode** and **Advanced Mode**.

### Simple Mode (Implicit AND)

In simple mode, all filter conditions are combined with AND logic. Just place fields directly in the `filters` object.

**Structure:**
```json
{
  "filters": {
    "field1": ["value1", "value2"],
    "field2": ["value3"],
    "field3": value
  }
}
```

**Logic:** `field1 IN (value1, value2) AND field2 = value3 AND field3 = value`

**Example:**
```json
{
  "filters": {
    "source": ["twitter", "linkedin"],
    "sentiment": ["positive"],
    "minXFollowers": 1000
  }
}
```

This translates to:
```
source IN (twitter, linkedin)
AND sentiment = positive
AND follower_count >= 1000
```

### Advanced Mode (AND/OR Groups)

Advanced mode allows you to create complex nested logic with AND/OR operators.

**Structure:**
```json
{
  "filters": {
    "operator": "AND",
    "groups": [
      {
        "operator": "OR",
        "conditions": [
          { "field1": ["value1"] },
          { "field2": ["value2"] }
        ]
      },
      {
        "operator": "AND",
        "conditions": [
          { "field3": ["value3"] },
          { "field4": ["value4"] }
        ]
      }
    ]
  }
}
```

**Top-level operator**: Combines all groups (AND/OR)
**Group operator**: Combines conditions within a group (AND/OR)

**Example:**
```json
{
  "filters": {
    "operator": "AND",
    "groups": [
      {
        "operator": "OR",
        "conditions": [
          { "source": ["twitter"] },
          { "source": ["linkedin"] }
        ]
      },
      {
        "operator": "AND",
        "conditions": [
          { "sentiment": ["positive"] },
          { "!tag": ["spam"] }
        ]
      }
    ]
  }
}
```

This translates to:
```
(source = twitter OR source = linkedin)
AND
(sentiment = positive AND tag != spam)
```

## Exclusion Operator (!)

You can exclude values by prefixing the field name with `!`. This works in both simple and advanced mode.

**Examples:**

```json
// Exclude spam and irrelevant tags
{
  "filters": {
    "!tag": ["spam", "irrelevant"]
  }
}
```

```json
// Get Twitter mentions, excluding keywords 5 and 6
{
  "filters": {
    "source": ["twitter"],
    "!keyword": [5, 6]
  }
}
```

```json
// Everything except negative sentiment
{
  "filters": {
    "!sentiment": ["negative"]
  }
}
```

## Available Filter Fields

### source (string[])

Filter by platform/source of the mention.

**Values:**
- `twitter` - Twitter/X posts
- `reddit` - Reddit posts and comments
- `github` - GitHub issues, PRs, discussions
- `linkedin` - LinkedIn posts
- `youtube` - YouTube comments
- `hackernews` - Hacker News posts and comments
- `devto` - Dev.to articles and comments
- `stackoverflow` - Stack Overflow questions/answers
- `bluesky` - Bluesky posts
- `newsletter` - Newsletter mentions
- `podcast` - Podcast mentions

**Examples:**
```json
// Social media only
{"source": ["twitter", "linkedin", "bluesky"]}

// Developer platforms
{"source": ["github", "stackoverflow", "hackernews"]}

// Exclude Reddit
{"!source": ["reddit"]}
```

### sentiment (string[])

Filter by sentiment analysis result.

**Values:**
- `positive` - Positive sentiment
- `neutral` - Neutral sentiment
- `negative` - Negative sentiment

**Examples:**
```json
// Positive only
{"sentiment": ["positive"]}

// Positive or neutral
{"sentiment": ["positive", "neutral"]}

// Exclude negative
{"!sentiment": ["negative"]}
```

### keyword (string[])

Filter by specific keyword IDs. Use the `/keywords` endpoint to get available keyword IDs.

**Type:** Array of keyword IDs (numbers as strings or numbers)

**Examples:**
```json
// Mentions of keyword 1
{"keyword": [1]}

// Mentions of keywords 1, 2, or 3
{"keyword": [1, 2, 3]}

// Exclude keyword 5
{"!keyword": [5]}
```

**Workflow:**
1. First call `GET /api/v1/keywords` to get keyword IDs
2. Then use those IDs in your filter

### language (string[])

Filter by language of the post (ISO 639-1 codes).

**Values:**
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `pt` - Portuguese
- `it` - Italian
- `nl` - Dutch
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese

**Examples:**
```json
// English only
{"language": ["en"]}

// English or Spanish
{"language": ["en", "es"]}

// Exclude Japanese
{"!language": ["ja"]}
```

### tag (string[])

Filter by tags applied to mentions.

**Type:** Array of tag names (strings)

**Examples:**
```json
// Feature requests only
{"tag": ["feature-request"]}

// High priority or bug tags
{"tag": ["high-priority", "bug"]}

// Exclude spam
{"!tag": ["spam"]}
```

### bookmarked (boolean)

Filter by bookmark status.

**Values:**
- `true` - Only bookmarked mentions
- `false` - Only non-bookmarked mentions

**Examples:**
```json
// Only bookmarked
{"bookmarked": true}

// Only non-bookmarked
{"bookmarked": false}
```

### engaged (boolean)

Filter by engagement status.

**Values:**
- `true` - Only engaged mentions (you've replied/interacted)
- `false` - Only non-engaged mentions

**Examples:**
```json
// Only engaged
{"engaged": true}

// Only non-engaged
{"engaged": false}
```

### minXFollowers (number)

Minimum Twitter/X follower count for the author.

**Type:** Number (integer)

**Examples:**
```json
// Authors with at least 1000 followers
{"minXFollowers": 1000}

// Influencers (10k+)
{"minXFollowers": 10000}
```

### maxXFollowers (number)

Maximum Twitter/X follower count for the author.

**Type:** Number (integer)

**Examples:**
```json
// Small accounts only (under 1000)
{"maxXFollowers": 1000}

// Range: 1000-10000 followers
{"minXFollowers": 1000, "maxXFollowers": 10000}
```

### startDate (string)

Only return mentions from this date onwards.

**Format:** ISO 8601 timestamp (e.g., `2024-01-15T00:00:00Z`)

**Examples:**
```json
// From January 1, 2024 onwards
{"startDate": "2024-01-01T00:00:00Z"}

// Last 7 days (calculate dynamically)
{"startDate": "2024-01-20T00:00:00Z"}
```

### endDate (string)

Only return mentions up to this date.

**Format:** ISO 8601 timestamp (e.g., `2024-01-31T23:59:59Z`)

**Examples:**
```json
// Up to January 31, 2024
{"endDate": "2024-01-31T23:59:59Z"}

// Specific date range
{
  "startDate": "2024-01-01T00:00:00Z",
  "endDate": "2024-01-31T23:59:59Z"
}
```

## Common Filter Patterns

### Pattern 1: Platform-Specific Sentiment Analysis

Get positive mentions from Twitter only:
```json
{
  "filters": {
    "source": ["twitter"],
    "sentiment": ["positive"]
  }
}
```

### Pattern 2: High-Value Engagement Opportunities

Positive or neutral mentions from high-follower accounts:
```json
{
  "filters": {
    "sentiment": ["positive", "neutral"],
    "minXFollowers": 5000,
    "engaged": false
  }
}
```

### Pattern 3: Quality Content Filter

Exclude low-quality content:
```json
{
  "filters": {
    "!tag": ["spam", "irrelevant", "bot"],
    "!sentiment": ["negative"]
  }
}
```

### Pattern 4: Developer Community Feedback

Get feedback from developer platforms:
```json
{
  "filters": {
    "source": ["github", "stackoverflow", "hackernews", "reddit"],
    "language": ["en"]
  }
}
```

### Pattern 5: Time-Bound Campaign Tracking

Track mentions during a specific campaign period:
```json
{
  "filters": {
    "startDate": "2024-01-15T00:00:00Z",
    "endDate": "2024-01-31T23:59:59Z",
    "sentiment": ["positive", "neutral"]
  }
}
```

### Pattern 6: Competitor Keyword Exclusion

Your keywords, but not competitors:
```json
{
  "filters": {
    "keyword": [1, 2],
    "!keyword": [10, 11],
    "source": ["twitter", "linkedin"]
  }
}
```

### Pattern 7: Multilingual Content

Content in specific languages:
```json
{
  "filters": {
    "language": ["en", "es", "pt"],
    "sentiment": ["positive"]
  }
}
```

## Advanced Filter Examples

### Example 1: Complex Platform Logic

Get mentions from (Twitter OR LinkedIn) AND (positive OR neutral) AND NOT spam:

```json
{
  "filters": {
    "operator": "AND",
    "groups": [
      {
        "operator": "OR",
        "conditions": [
          { "source": ["twitter"] },
          { "source": ["linkedin"] }
        ]
      },
      {
        "operator": "OR",
        "conditions": [
          { "sentiment": ["positive"] },
          { "sentiment": ["neutral"] }
        ]
      },
      {
        "operator": "AND",
        "conditions": [
          { "!tag": ["spam"] }
        ]
      }
    ]
  }
}
```

### Example 2: Multi-Source with Follower Tiers

Different follower requirements for different platforms:

This requires multiple queries, as you can't mix follower counts for different sources in one query:

**Query 1** - Twitter micro-influencers:
```json
{
  "filters": {
    "source": ["twitter"],
    "minXFollowers": 1000,
    "maxXFollowers": 10000
  }
}
```

**Query 2** - Reddit posts (no follower filter):
```json
{
  "filters": {
    "source": ["reddit"]
  }
}
```

### Example 3: Feature Request Pipeline

Unengaged positive feature requests from the last 30 days:

```json
{
  "filters": {
    "operator": "AND",
    "groups": [
      {
        "operator": "AND",
        "conditions": [
          { "tag": ["feature-request"] },
          { "engaged": false },
          { "sentiment": ["positive", "neutral"] }
        ]
      },
      {
        "operator": "AND",
        "conditions": [
          { "startDate": "2024-01-01T00:00:00Z" }
        ]
      }
    ]
  }
}
```

### Example 4: International Campaign

Multi-language positive mentions from social platforms:

```json
{
  "filters": {
    "operator": "AND",
    "groups": [
      {
        "operator": "OR",
        "conditions": [
          { "source": ["twitter"] },
          { "source": ["linkedin"] },
          { "source": ["bluesky"] }
        ]
      },
      {
        "operator": "OR",
        "conditions": [
          { "language": ["en"] },
          { "language": ["es"] },
          { "language": ["pt"] }
        ]
      },
      {
        "operator": "AND",
        "conditions": [
          { "sentiment": ["positive"] }
        ]
      }
    ]
  }
}
```

## Filter Optimization Tips

1. **Start Simple**: Begin with simple mode filters and add complexity only when needed
2. **Use Exclusions**: Often easier to exclude unwanted content than include everything wanted
3. **Layer Filters**: Apply broad filters first (source, date), then narrow down (sentiment, tags)
4. **Test Incrementally**: Add one filter at a time to see its effect
5. **Leverage Views**: Save common filter combinations as views for reuse
6. **Check Response Counts**: If you get zero results, remove filters one by one to find the issue
7. **Follower Filters**: Apply carefully - not all platforms have follower counts
8. **Date Formats**: Always use ISO 8601 format with timezone (Z for UTC)

## Troubleshooting Filters

### No Results Returned

1. Check each filter individually
2. Verify keyword IDs exist (call `/keywords`)
3. Ensure date ranges are valid (startDate < endDate)
4. Check for contradictory filters (e.g., `sentiment: ["positive"]` and `!sentiment: ["positive"]`)

### Too Many Results

1. Add more restrictive filters (minXFollowers, sentiment)
2. Narrow date range
3. Exclude low-quality tags
4. Use `includeAll: false` to filter out low-relevance mentions

### Unexpected Results

1. Check for case sensitivity in tag names
2. Verify source names are lowercase
3. Ensure language codes are ISO 639-1 (two-letter)
4. Check that keyword IDs match your organization's keywords

## API Request Examples

### cURL Example

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 20,
    "filters": {
      "source": ["twitter"],
      "sentiment": ["positive"],
      "minXFollowers": 1000,
      "!tag": ["spam"]
    }
  }'
```

### Python Example

```python
import requests

api_key = "YOUR_API_KEY"
url = "https://app.octolens.com/api/v1/mentions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "limit": 20,
    "filters": {
        "source": ["twitter", "linkedin"],
        "sentiment": ["positive"],
        "startDate": "2024-01-01T00:00:00Z"
    }
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()
```

### JavaScript Example

```javascript
const apiKey = 'YOUR_API_KEY';
const url = 'https://app.octolens.com/api/v1/mentions';

const response = await fetch(url, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    limit: 20,
    filters: {
      source: ['twitter'],
      sentiment: ['positive', 'neutral'],
      minXFollowers: 5000
    }
  })
});

const data = await response.json();
```
