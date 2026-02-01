# Octolens API Usage Examples

This document provides real-world examples and workflows for common Octolens API use cases.

## Table of Contents

1. [Basic Queries](#basic-queries)
2. [Sentiment Analysis](#sentiment-analysis)
3. [Influencer Tracking](#influencer-tracking)
4. [Competitor Monitoring](#competitor-monitoring)
5. [Campaign Tracking](#campaign-tracking)
6. [Product Feedback Collection](#product-feedback-collection)
7. [Multi-Platform Analysis](#multi-platform-analysis)
8. [Pagination Workflows](#pagination-workflows)

---

## Basic Queries

### Example 1: Get Latest Mentions

Fetch the 20 most recent mentions:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 20
  }'
```

### Example 2: List All Keywords

```bash
curl "https://app.octolens.com/api/v1/keywords" \
  -H "Authorization: Bearer ${API_KEY}"
```

Response:
```json
{
  "data": [
    {"id": 1, "keyword": "MyProduct", "platforms": ["twitter", "reddit"]},
    {"id": 2, "keyword": "MyBrand", "platforms": ["twitter", "linkedin"]},
    {"id": 3, "keyword": "CompetitorA", "platforms": ["twitter"]}
  ]
}
```

### Example 3: List Saved Views

```bash
curl "https://app.octolens.com/api/v1/views" \
  -H "Authorization: Bearer ${API_KEY}"
```

---

## Sentiment Analysis

### Example 4: Positive Mentions Only

Get all positive sentiment mentions:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 50,
    "filters": {
      "sentiment": ["positive"]
    }
  }'
```

### Example 5: Negative Feedback Analysis

Get negative mentions to identify issues:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 30,
    "filters": {
      "sentiment": ["negative"],
      "engaged": false
    }
  }'
```

### Example 6: Sentiment Distribution

Get equal samples of each sentiment:

**Positive:**
```json
{"limit": 20, "filters": {"sentiment": ["positive"]}}
```

**Neutral:**
```json
{"limit": 20, "filters": {"sentiment": ["neutral"]}}
```

**Negative:**
```json
{"limit": 20, "filters": {"sentiment": ["negative"]}}
```

Then aggregate and analyze the distribution.

---

## Influencer Tracking

### Example 7: High-Follower Positive Mentions

Find positive mentions from accounts with 10k+ followers:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 25,
    "filters": {
      "sentiment": ["positive"],
      "minXFollowers": 10000,
      "source": ["twitter"]
    }
  }'
```

### Example 8: Micro-Influencer Engagement

Target micro-influencers (1k-10k followers):

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 50,
    "filters": {
      "minXFollowers": 1000,
      "maxXFollowers": 10000,
      "sentiment": ["positive", "neutral"],
      "engaged": false
    }
  }'
```

### Example 9: Macro-Influencer Mentions

Track macro-influencers (100k+ followers):

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 10,
    "filters": {
      "minXFollowers": 100000,
      "source": ["twitter", "linkedin"]
    }
  }'
```

---

## Competitor Monitoring

### Example 10: Track Competitor Mentions

Assuming keyword ID 5 is a competitor:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 30,
    "filters": {
      "keyword": [5],
      "sentiment": ["negative"]
    }
  }'
```

### Example 11: Compare Your Brand vs Competitor

**Your mentions:**
```json
{
  "limit": 50,
  "filters": {
    "keyword": [1],
    "sentiment": ["positive"]
  }
}
```

**Competitor mentions:**
```json
{
  "limit": 50,
  "filters": {
    "keyword": [5],
    "sentiment": ["positive"]
  }
}
```

Compare counts and sentiment distribution.

### Example 12: Exclude Competitor Noise

Get your mentions, excluding competitor discussions:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 40,
    "filters": {
      "keyword": [1, 2],
      "!keyword": [5, 6, 7]
    }
  }'
```

---

## Campaign Tracking

### Example 13: Product Launch Campaign

Track mentions during launch week:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 100,
    "filters": {
      "startDate": "2024-01-15T00:00:00Z",
      "endDate": "2024-01-21T23:59:59Z",
      "source": ["twitter", "linkedin", "hackernews"]
    }
  }'
```

### Example 14: Daily Campaign Monitoring

Get today's mentions (generate date dynamically):

```bash
#!/bin/bash
TODAY=$(date -u +"%Y-%m-%dT00:00:00Z")

curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"limit\": 50,
    \"filters\": {
      \"startDate\": \"$TODAY\"
    }
  }"
```

### Example 15: Weekly Digest

Get last 7 days of positive mentions:

```bash
#!/bin/bash
SEVEN_DAYS_AGO=$(date -u -v-7d +"%Y-%m-%dT%H:%M:%SZ")

curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"limit\": 100,
    \"filters\": {
      \"startDate\": \"$SEVEN_DAYS_AGO\",
      \"sentiment\": [\"positive\"]
    }
  }"
```

---

## Product Feedback Collection

### Example 16: Feature Request Identification

Get mentions tagged as feature requests:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 50,
    "filters": {
      "tag": ["feature-request"],
      "source": ["twitter", "reddit", "github"]
    }
  }'
```

### Example 17: Bug Reports

Find potential bug reports (negative sentiment + specific sources):

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 30,
    "filters": {
      "sentiment": ["negative"],
      "source": ["github", "stackoverflow", "reddit"],
      "!tag": ["spam"]
    }
  }'
```

### Example 18: Unengaged High-Priority Feedback

Find important feedback you haven't responded to:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 20,
    "filters": {
      "engaged": false,
      "minXFollowers": 1000,
      "sentiment": ["positive", "neutral"],
      "!tag": ["spam", "irrelevant"]
    }
  }'
```

---

## Multi-Platform Analysis

### Example 19: Developer Community Mentions

Get mentions from developer platforms:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 50,
    "filters": {
      "source": ["github", "stackoverflow", "hackernews", "devto"],
      "language": ["en"]
    }
  }'
```

### Example 20: Social Media vs Forums

Compare social media and forum discussions:

**Social media:**
```json
{
  "limit": 50,
  "filters": {
    "source": ["twitter", "linkedin", "bluesky"]
  }
}
```

**Forums:**
```json
{
  "limit": 50,
  "filters": {
    "source": ["reddit", "hackernews", "stackoverflow"]
  }
}
```

### Example 21: Exclude Low-Quality Platforms

Focus on high-quality sources:

```bash
curl -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 40,
    "filters": {
      "source": ["twitter", "linkedin", "hackernews"],
      "!tag": ["spam", "bot"],
      "minXFollowers": 500
    }
  }'
```

---

## Pagination Workflows

### Example 22: Fetch All Results with Pagination

```bash
#!/bin/bash

API_KEY="your_api_key_here"
CURSOR=""
PAGE=1

while true; do
  echo "Fetching page $PAGE..."

  if [ -z "$CURSOR" ]; then
    RESPONSE=$(curl -s -X POST "https://app.octolens.com/api/v1/mentions" \
      -H "Authorization: Bearer ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d '{
        "limit": 100,
        "filters": {"sentiment": ["positive"]}
      }')
  else
    RESPONSE=$(curl -s -X POST "https://app.octolens.com/api/v1/mentions" \
      -H "Authorization: Bearer ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d "{
        \"limit\": 100,
        \"cursor\": \"$CURSOR\",
        \"filters\": {\"sentiment\": [\"positive\"]}
      }")
  fi

  # Extract data
  echo "$RESPONSE" | jq '.data[]' >> all_mentions.json

  # Get next cursor
  NEXT_CURSOR=$(echo "$RESPONSE" | jq -r '.cursor // empty')

  if [ -z "$NEXT_CURSOR" ]; then
    echo "No more pages. Done!"
    break
  fi

  CURSOR="$NEXT_CURSOR"
  PAGE=$((PAGE + 1))

  # Rate limit protection
  sleep 1
done
```

### Example 23: Collect Until Date

Fetch mentions until reaching a specific date:

```bash
#!/bin/bash

API_KEY="your_api_key_here"
TARGET_DATE="2024-01-01T00:00:00Z"
CURSOR=""

while true; do
  if [ -z "$CURSOR" ]; then
    RESPONSE=$(curl -s -X POST "https://app.octolens.com/api/v1/mentions" \
      -H "Authorization: Bearer ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d '{"limit": 100}')
  else
    RESPONSE=$(curl -s -X POST "https://app.octolens.com/api/v1/mentions" \
      -H "Authorization: Bearer ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d "{\"limit\": 100, \"cursor\": \"$CURSOR\"}")
  fi

  # Get oldest timestamp in this page
  OLDEST=$(echo "$RESPONSE" | jq -r '.data[-1].timestamp // empty')

  if [ -z "$OLDEST" ]; then
    echo "No more data"
    break
  fi

  # Save data
  echo "$RESPONSE" | jq '.data[]' >> mentions.json

  # Check if we've reached target date
  if [[ "$OLDEST" < "$TARGET_DATE" ]]; then
    echo "Reached target date: $TARGET_DATE"
    break
  fi

  CURSOR=$(echo "$RESPONSE" | jq -r '.cursor // empty')
  if [ -z "$CURSOR" ]; then
    break
  fi

  sleep 1
done
```

---

## Advanced Workflows

### Example 24: Sentiment Analysis Report

Generate a sentiment report:

```bash
#!/bin/bash

API_KEY="your_api_key_here"

echo "Fetching sentiment data..."

POSITIVE=$(curl -s -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"limit": 100, "filters": {"sentiment": ["positive"]}}' \
  | jq '.data | length')

NEUTRAL=$(curl -s -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"limit": 100, "filters": {"sentiment": ["neutral"]}}' \
  | jq '.data | length')

NEGATIVE=$(curl -s -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"limit": 100, "filters": {"sentiment": ["negative"]}}' \
  | jq '.data | length')

TOTAL=$((POSITIVE + NEUTRAL + NEGATIVE))

echo "Sentiment Report:"
echo "================="
echo "Positive: $POSITIVE ($((POSITIVE * 100 / TOTAL))%)"
echo "Neutral:  $NEUTRAL ($((NEUTRAL * 100 / TOTAL))%)"
echo "Negative: $NEGATIVE ($((NEGATIVE * 100 / TOTAL))%)"
echo "Total:    $TOTAL"
```

### Example 25: Top Influencers Report

Find top influencers mentioning your brand:

```bash
#!/bin/bash

API_KEY="your_api_key_here"

curl -s -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 100,
    "filters": {
      "minXFollowers": 10000,
      "sentiment": ["positive", "neutral"]
    }
  }' | jq -r '.data[] | "\(.authorFollowers)\t\(.authorName)\t\(.url)"' \
  | sort -rn \
  | head -20
```

### Example 26: Daily Alert for Negative Mentions

Set up a daily alert:

```bash
#!/bin/bash

API_KEY="your_api_key_here"
TODAY=$(date -u +"%Y-%m-%dT00:00:00Z")

NEGATIVE_COUNT=$(curl -s -X POST "https://app.octolens.com/api/v1/mentions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"limit\": 100,
    \"filters\": {
      \"sentiment\": [\"negative\"],
      \"startDate\": \"$TODAY\"
    }
  }" | jq '.data | length')

if [ "$NEGATIVE_COUNT" -gt 0 ]; then
  echo "⚠️  Alert: $NEGATIVE_COUNT negative mentions today!"
  # Send notification (e.g., email, Slack, etc.)
else
  echo "✅ No negative mentions today"
fi
```

---

## Tips for Complex Queries

1. **Break down complex requirements**: Start with simple filters, then combine
2. **Test incrementally**: Add one filter at a time
3. **Use jq for analysis**: Pipe responses through jq for data extraction
4. **Cache keyword IDs**: Fetch once, reuse in filters
5. **Handle pagination**: Always check for cursor in responses
6. **Rate limit awareness**: Add delays between requests in loops
7. **Date calculations**: Use shell date utilities for dynamic date ranges
8. **Combine with views**: Start with a view, then add additional filters
