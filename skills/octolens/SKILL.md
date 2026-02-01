---
name: octolens
description: Query and analyze brand mentions from Octolens API. Use when the user wants to fetch mentions, track keywords, filter by source platforms (Twitter, Reddit, GitHub, LinkedIn, etc.), sentiment analysis, or analyze social media engagement. Supports complex filtering with AND/OR logic, date ranges, follower counts, and bookmarks.
license: MIT
metadata:
  author: octolens
  version: "1.0"
compatibility: Requires Node.js 18+ (for fetch API) and access to the internet
allowed-tools: Node Read
---

# Octolens API Skill

## When to use this skill

Use this skill when the user needs to:
- Fetch brand mentions from social media and other platforms
- Filter mentions by source (Twitter, Reddit, GitHub, LinkedIn, YouTube, HackerNews, DevTO, StackOverflow, Bluesky, newsletters, podcasts)
- Analyze sentiment (positive, neutral, negative)
- Filter by author follower count or engagement
- Search for specific keywords or tags
- Query mentions by date range
- List available keywords or saved views
- Apply complex filtering logic with AND/OR conditions

## API Authentication

The Octolens API requires a Bearer token for authentication. The user should provide their API key, which you'll use in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

**Important**: Always ask the user for their API key before making any API calls. Store it in a variable for subsequent requests.

## Base URL

All API endpoints use the base URL: `https://app.octolens.com/api/v1`

## Rate Limits

- **Limit**: 500 requests per hour
- **Check headers**: `X-RateLimit-*` headers indicate current usage

## Available Endpoints

### 1. POST /mentions

Fetch mentions matching keywords with optional filtering. Returns posts sorted by timestamp (newest first).

**Key Parameters:**
- `limit` (number, 1-100): Maximum results to return (default: 20)
- `cursor` (string): Pagination cursor from previous response
- `includeAll` (boolean): Include low-relevance posts (default: false)
- `view` (number): View ID to use for filtering
- `filters` (object): Filter criteria (see filtering section)

**Example Response:**
```json
{
  "data": [
    {
      "id": "abc123",
      "url": "https://twitter.com/user/status/123",
      "body": "Just discovered @YourProduct - this is exactly what I needed!",
      "source": "twitter",
      "timestamp": "2024-01-15T10:30:00Z",
      "author": "user123",
      "authorName": "John Doe",
      "authorFollowers": 5420,
      "relevance": "relevant",
      "sentiment": "positive",
      "language": "en",
      "tags": ["feature-request"],
      "keywords": [{ "id": 1, "keyword": "YourProduct" }],
      "bookmarked": false,
      "engaged": false
    }
  ],
  "cursor": "eyJsYXN0SWQiOiAiYWJjMTIzIn0="
}
```

### 2. GET /keywords

List all keywords configured for the organization.

**Example Response:**
```json
{
  "data": [
    {
      "id": 1,
      "keyword": "YourProduct",
      "platforms": ["twitter", "reddit", "github"],
      "color": "#6366f1",
      "paused": false,
      "context": "Our main product name"
    }
  ]
}
```

### 3. GET /views

List all saved views (pre-configured filters).

**Example Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "High Priority",
      "icon": "star",
      "filters": {
        "sentiment": ["positive", "negative"],
        "source": ["twitter"]
      },
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Filtering Mentions

The `/mentions` endpoint supports powerful filtering with two modes:

### Simple Mode (Implicit AND)

Put fields directly in filters. All conditions are ANDed together.

```json
{
  "filters": {
    "source": ["twitter", "linkedin"],
    "sentiment": ["positive"],
    "minXFollowers": 1000
  }
}
```
→ `source IN (twitter, linkedin) AND sentiment = positive AND followers ≥ 1000`

### Exclusions

Prefix any array field with ! to exclude values:

```json
{
  "filters": {
    "source": ["twitter"],
    "!keyword": [5, 6]
  }
}
```
→ `source = twitter AND keyword NOT IN (5, 6)`

### Advanced Mode (AND/OR Groups)

Use `operator` and `groups` for complex logic:

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
→ `(source = twitter OR source = linkedin) AND (sentiment = positive AND tag ≠ spam)`

### Available Filter Fields

| Field | Type | Description |
|-------|------|-------------|
| `source` | string[] | Platforms: twitter, reddit, github, linkedin, youtube, hackernews, devto, stackoverflow, bluesky, newsletter, podcast |
| `sentiment` | string[] | Values: positive, neutral, negative |
| `keyword` | string[] | Keyword IDs (get from /keywords endpoint) |
| `language` | string[] | ISO 639-1 codes: en, es, fr, de, pt, it, nl, ja, ko, zh |
| `tag` | string[] | Tag names |
| `bookmarked` | boolean | Filter bookmarked (true) or non-bookmarked (false) posts |
| `engaged` | boolean | Filter engaged (true) or non-engaged (false) posts |
| `minXFollowers` | number | Minimum Twitter follower count |
| `maxXFollowers` | number | Maximum Twitter follower count |
| `startDate` | string | ISO 8601 format (e.g., "2024-01-15T00:00:00Z") |
| `endDate` | string | ISO 8601 format |

## Using the Bundled Scripts

This skill includes helper scripts for common operations. Use them to quickly interact with the API:

### Fetch Mentions
```bash
node scripts/fetch-mentions.js YOUR_API_KEY [limit] [includeAll]
```

### List Keywords
```bash
node scripts/list-keywords.js YOUR_API_KEY
```

### List Views
```bash
node scripts/list-views.js YOUR_API_KEY
```

### Custom Filter Query
```bash
node scripts/query-mentions.js YOUR_API_KEY '{"source": ["twitter"], "sentiment": ["positive"]}' [limit]
```

### Advanced Query
```bash
node scripts/advanced-query.js YOUR_API_KEY [limit]
```

## Best Practices

1. **Always ask for the API key** before making requests
2. **Use views** when possible to leverage pre-configured filters
3. **Start with simple filters** and add complexity as needed
4. **Check rate limits** in response headers (`X-RateLimit-*`)
5. **Use pagination** with cursor for large result sets
6. **Dates must be ISO 8601** format (e.g., "2024-01-15T00:00:00Z")
7. **Get keyword IDs** from `/keywords` endpoint before filtering by keyword
8. **Use exclusions** (!) to filter out unwanted content
9. **Combine includeAll=false** with relevance filtering for quality results

## Common Use Cases

### Find positive Twitter mentions with high followers
```json
{
  "limit": 20,
  "filters": {
    "source": ["twitter"],
    "sentiment": ["positive"],
    "minXFollowers": 1000
  }
}
```

### Exclude spam and get Reddit + GitHub mentions
```json
{
  "limit": 50,
  "filters": {
    "source": ["reddit", "github"],
    "!tag": ["spam", "irrelevant"]
  }
}
```

### Complex query: (Twitter OR LinkedIn) AND positive sentiment, last 7 days
```json
{
  "limit": 30,
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
          { "startDate": "2024-01-20T00:00:00Z" }
        ]
      }
    ]
  }
}
```

## Error Handling

| Status | Error | Description |
|--------|-------|-------------|
| 401 | unauthorized | Missing or invalid API key |
| 403 | forbidden | Valid key but no permission |
| 404 | not_found | Resource (e.g., view ID) not found |
| 429 | rate_limit_exceeded | Too many requests |
| 400 | invalid_request | Malformed request body |
| 500 | internal_error | Server error, retry later |

## Step-by-Step Workflow

When a user asks to query Octolens data:

1. **Ask for API key** if not already provided
2. **Understand the request**: What are they looking for?
3. **Determine filters needed**: Source, sentiment, date range, etc.
4. **Check if a view applies**: List views first if user mentions saved filters
5. **Build the query**: Use simple mode first, advanced mode for complex logic
6. **Execute the request**: Use bundled Node.js scripts or fetch API directly
7. **Parse results**: Extract key information (author, body, sentiment, source)
8. **Handle pagination**: If more results needed, use cursor from response
9. **Present findings**: Summarize insights, highlight patterns

## Examples

### Example 1: Simple Query
**User**: "Show me positive mentions from Twitter in the last 7 days"

**Action** (using bundled script):
```bash
node scripts/query-mentions.js YOUR_API_KEY '{"source": ["twitter"], "sentiment": ["positive"], "startDate": "2024-01-20T00:00:00Z"}'
```

**Alternative** (using fetch API directly):
```javascript
const response = await fetch('https://app.octolens.com/api/v1/mentions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    limit: 20,
    filters: {
      source: ['twitter'],
      sentiment: ['positive'],
      startDate: '2024-01-20T00:00:00Z',
    },
  }),
});
const data = await response.json();
```

### Example 2: Advanced Query
**User**: "Find mentions from Reddit or GitHub, exclude spam tag, with positive or neutral sentiment"

**Action** (using bundled script):
```bash
node scripts/query-mentions.js YOUR_API_KEY '{"operator": "AND", "groups": [{"operator": "OR", "conditions": [{"source": ["reddit"]}, {"source": ["github"]}]}, {"operator": "OR", "conditions": [{"sentiment": ["positive"]}, {"sentiment": ["neutral"]}]}, {"operator": "AND", "conditions": [{"!tag": ["spam"]}]}]}'
```

**Alternative** (using fetch API directly):
```javascript
const response = await fetch('https://app.octolens.com/api/v1/mentions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    limit: 30,
    filters: {
      operator: 'AND',
      groups: [
        {
          operator: 'OR',
          conditions: [
            { source: ['reddit'] },
            { source: ['github'] },
          ],
        },
        {
          operator: 'OR',
          conditions: [
            { sentiment: ['positive'] },
            { sentiment: ['neutral'] },
          ],
        },
        {
          operator: 'AND',
          conditions: [
            { '!tag': ['spam'] },
          ],
        },
      ],
    },
  }),
});
const data = await response.json();
```

### Example 3: Get Keywords First
**User**: "Show mentions for our main product keyword"

**Actions**:
1. First, list keywords:
```bash
node scripts/list-keywords.js YOUR_API_KEY
```

2. Then query mentions with the keyword ID:
```bash
node scripts/query-mentions.js YOUR_API_KEY '{"keyword": [1]}'
```

## Tips for Agents

- **Use bundled scripts**: The Node.js scripts handle JSON parsing automatically
- **Cache keywords**: After fetching keywords once, remember them for the session
- **Explain filters**: When using complex filters, explain the logic to the user
- **Show examples**: When users are unsure, show example filter structures
- **Paginate wisely**: Ask if user wants more results before fetching next page
- **Summarize insights**: Don't just dump data, provide analysis (sentiment trends, top authors, platform distribution)
