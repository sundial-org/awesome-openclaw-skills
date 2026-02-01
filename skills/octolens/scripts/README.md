# Octolens API Scripts

These Node.js scripts provide quick access to the Octolens API. All scripts require Node.js 18+ (for fetch API support).

## Prerequisites

```bash
# Check Node.js version (requires 18+)
node --version

# Install Node.js if needed (macOS)
brew install node

# Install Node.js if needed (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Available Scripts

### 1. fetch-mentions.js

Fetch mentions with basic parameters.

```bash
node scripts/fetch-mentions.js YOUR_API_KEY [limit] [includeAll]
```

**Parameters:**
- `YOUR_API_KEY` (required): Your Octolens API key
- `limit` (optional, default: 20): Number of results to return (1-100)
- `includeAll` (optional, default: false): Include low-relevance posts

**Examples:**
```bash
# Fetch 20 mentions (default)
node scripts/fetch-mentions.js your_api_key_here

# Fetch 50 mentions
node scripts/fetch-mentions.js your_api_key_here 50

# Fetch 30 mentions including low-relevance posts
node scripts/fetch-mentions.js your_api_key_here 30 true
```

### 2. list-keywords.js

List all keywords configured for your organization.

```bash
node scripts/list-keywords.js YOUR_API_KEY
```

**Example:**
```bash
node scripts/list-keywords.js your_api_key_here
```

### 3. list-views.js

List all saved views (pre-configured filters).

```bash
node scripts/list-views.js YOUR_API_KEY
```

**Example:**
```bash
node scripts/list-views.js your_api_key_here
```

### 4. query-mentions.js

Query mentions with custom filter JSON.

```bash
node scripts/query-mentions.js YOUR_API_KEY '{"filter": "json"}' [limit]
```

**Examples:**
```bash
# Filter by source
node scripts/query-mentions.js your_api_key_here '{"source": ["twitter", "reddit"]}'

# Filter by sentiment
node scripts/query-mentions.js your_api_key_here '{"sentiment": ["positive"]}'

# Multiple filters (implicit AND)
node scripts/query-mentions.js your_api_key_here '{"source": ["twitter"], "sentiment": ["positive"], "minXFollowers": 1000}'

# With exclusion
node scripts/query-mentions.js your_api_key_here '{"source": ["twitter"], "!tag": ["spam"]}'

# Date range
node scripts/query-mentions.js your_api_key_here '{"startDate": "2024-01-01T00:00:00Z", "endDate": "2024-01-31T23:59:59Z"}'

# Combine multiple filters
node scripts/query-mentions.js your_api_key_here '{
  "source": ["twitter", "linkedin"],
  "sentiment": ["positive"],
  "minXFollowers": 500,
  "startDate": "2024-01-20T00:00:00Z"
}'
```

### 5. advanced-query.js

Query with complex AND/OR logic (demonstrates advanced filtering).

```bash
node scripts/advanced-query.js YOUR_API_KEY [limit]
```

**Default query**: `(Twitter OR Reddit) AND (Positive sentiment) AND NOT spam`

**Example:**
```bash
# Use default query with 20 results
node scripts/advanced-query.js your_api_key_here

# Use default query with 50 results
node scripts/advanced-query.js your_api_key_here 50
```

## Filter Fields Reference

| Field | Type | Values |
|-------|------|--------|
| `source` | array | twitter, reddit, github, linkedin, youtube, hackernews, devto, stackoverflow, bluesky, newsletter, podcast |
| `sentiment` | array | positive, neutral, negative |
| `keyword` | array | Keyword IDs (get from list-keywords.js) |
| `language` | array | en, es, fr, de, pt, it, nl, ja, ko, zh |
| `tag` | array | Tag names |
| `bookmarked` | boolean | true or false |
| `engaged` | boolean | true or false |
| `minXFollowers` | number | Minimum follower count |
| `maxXFollowers` | number | Maximum follower count |
| `startDate` | string | ISO 8601 format |
| `endDate` | string | ISO 8601 format |

## Exclusions

Prefix any array field with `!` to exclude values:

```bash
# Exclude spam tag
node scripts/query-mentions.js your_api_key_here '{"!tag": ["spam"]}'

# Exclude specific keywords
node scripts/query-mentions.js your_api_key_here '{"!keyword": [5, 6]}'

# Exclude negative sentiment
node scripts/query-mentions.js your_api_key_here '{"!sentiment": ["negative"]}'
```

## Advanced Filtering

For complex AND/OR logic, use the `operator` and `groups` structure:

```json
{
  "operator": "AND",
  "groups": [
    {
      "operator": "OR",
      "conditions": [
        { "source": ["twitter"] },
        { "source": ["reddit"] }
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
```

## Tips

1. **JSON formatting**: Scripts automatically format JSON output with proper indentation
2. **Save responses**: Pipe output to a file: `node scripts/fetch-mentions.js key > results.json`
3. **Chain with jq**: Extract specific fields: `node scripts/list-keywords.js key | jq '.data[].keyword'`
4. **Error handling**: Scripts exit with non-zero code on error, check exit codes in your workflows
5. **Node.js version**: Requires Node.js 18+ for native fetch API support

## Common Patterns

### Get positive mentions from high-follower accounts
```bash
node scripts/query-mentions.js your_api_key_here '{
  "sentiment": ["positive"],
  "minXFollowers": 10000
}'
```

### Get recent mentions (last 7 days)
```bash
# Calculate date 7 days ago (macOS)
START_DATE=$(date -u -v-7d +"%Y-%m-%dT%H:%M:%SZ")
node scripts/query-mentions.js your_api_key_here "{\"startDate\": \"$START_DATE\"}"

# Calculate date 7 days ago (Linux)
START_DATE=$(date -u -d '7 days ago' +"%Y-%m-%dT%H:%M:%SZ")
node scripts/query-mentions.js your_api_key_here "{\"startDate\": \"$START_DATE\"}"
```

### Filter by specific keyword
```bash
# First get keyword IDs
node scripts/list-keywords.js your_api_key_here | jq '.data[] | {id, keyword}'

# Then filter by keyword ID
node scripts/query-mentions.js your_api_key_here '{"keyword": [1]}'
```

### Exclude negative sentiment and spam
```bash
node scripts/query-mentions.js your_api_key_here '{
  "!sentiment": ["negative"],
  "!tag": ["spam", "irrelevant"]
}'
```

## Troubleshooting

### "fetch is not defined" or "fetch is not a function"
You need Node.js 18+. Check your version: `node --version`. Upgrade if needed.

### "unauthorized" error
Check your API key is correct and has proper permissions

### "rate_limit_exceeded" error
You've hit the 500 requests/hour limit. Wait for the rate limit to reset.

### Invalid JSON
Ensure your filter JSON is properly formatted. Test with: `echo '{"source": ["twitter"]}' | node -e "console.log(JSON.stringify(JSON.parse(require('fs').readFileSync(0, 'utf-8')), null, 2))"`
