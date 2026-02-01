---
name: trakt
description: Interact with the Trakt API to manage your watchlist, collection, ratings, and discover content
metadata: {"openclaw": {"requires": {"env": ["TRAKT_CLIENT_ID", "TRAKT_CLIENT_SECRET", "TRAKT_ACCESS_TOKEN"]}, "primaryEnv": "TRAKT_ACCESS_TOKEN", "homepage": "https://trakt.tv"}}
---

# Trakt API Integration

Interact with Trakt.tv to manage your watchlist, track viewing history, maintain your collection, rate content, and discover new movies and shows.

## Authentication

Before using this skill, you need to set up Trakt API credentials:

1. Create a Trakt application at https://trakt.tv/oauth/applications
2. Get your Client ID and Client Secret
3. Complete OAuth flow to get an access token
4. Set environment variables in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "trakt": {
        "enabled": true,
        "env": {
          "TRAKT_CLIENT_ID": "your_client_id",
          "TRAKT_CLIENT_SECRET": "your_client_secret",
          "TRAKT_ACCESS_TOKEN": "your_access_token",
          "TRAKT_REFRESH_TOKEN": "your_refresh_token"
        }
      }
    }
  }
}
```

## Available Commands

### Watchlist Management

**Add to watchlist:**
```bash
curl -X POST https://api.trakt.tv/sync/watchlist \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID" \
  -d '{"movies":[{"title":"Inception","year":2010}]}'
```

**Get watchlist:**
```bash
curl https://api.trakt.tv/sync/watchlist/movies \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

**Remove from watchlist:**
```bash
curl -X POST https://api.trakt.tv/sync/watchlist/remove \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID" \
  -d '{"movies":[{"ids":{"trakt":12601}}]}'
```

### Search

**Search movies:**
```bash
curl "https://api.trakt.tv/search/movie?query=inception" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

**Search shows:**
```bash
curl "https://api.trakt.tv/search/show?query=breaking+bad" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

### History

**Get watch history:**
```bash
curl https://api.trakt.tv/sync/history \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

**Add to history (mark as watched):**
```bash
curl -X POST https://api.trakt.tv/sync/history \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID" \
  -d '{"movies":[{"title":"The Matrix","year":1999,"watched_at":"2024-01-15T20:00:00.000Z"}]}'
```

### Collection

**Get collection:**
```bash
curl https://api.trakt.tv/sync/collection/movies \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

**Add to collection:**
```bash
curl -X POST https://api.trakt.tv/sync/collection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID" \
  -d '{"movies":[{"title":"Blade Runner 2049","year":2017,"collected_at":"2024-01-15T20:00:00.000Z","media_type":"bluray","resolution":"uhd_4k"}]}'
```

### Ratings

**Get ratings:**
```bash
curl https://api.trakt.tv/sync/ratings/movies \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

**Add rating:**
```bash
curl -X POST https://api.trakt.tv/sync/ratings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID" \
  -d '{"movies":[{"title":"The Shawshank Redemption","year":1994,"rating":10}]}'
```

### Discovery

**Get recommendations:**
```bash
curl https://api.trakt.tv/recommendations/movies?limit=10 \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

**Get trending:**
```bash
curl https://api.trakt.tv/movies/trending \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

**Get popular:**
```bash
curl https://api.trakt.tv/movies/popular \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

## Data Format

### Movie Object
```json
{
  "title": "Inception",
  "year": 2010,
  "ids": {
    "trakt": 16662,
    "slug": "inception-2010",
    "imdb": "tt1375666",
    "tmdb": 27205
  }
}
```

### Show Object
```json
{
  "title": "Breaking Bad",
  "year": 2008,
  "ids": {
    "trakt": 1,
    "slug": "breaking-bad",
    "tvdb": 81189,
    "imdb": "tt0903747",
    "tmdb": 1396
  }
}
```

### Episode Object
```json
{
  "season": 1,
  "number": 1,
  "title": "Pilot",
  "ids": {
    "trakt": 73482,
    "tvdb": 349232,
    "imdb": "tt0959621",
    "tmdb": 62085
  }
}
```

## Usage Instructions

When the user asks to interact with Trakt:

1. **Always use curl** with proper headers including the access token
2. **Required headers** for all requests:
   - `trakt-api-version: 2`
   - `trakt-api-key: $TRAKT_CLIENT_ID`
   - `Authorization: Bearer $TRAKT_ACCESS_TOKEN` (for authenticated endpoints)
   - `Content-Type: application/json` (for POST/PUT/DELETE)

3. **Identify the item** using title and year, or IDs if available
4. **Use appropriate endpoint** based on the action:
   - Watchlist: `/sync/watchlist` (POST to add, `/sync/watchlist/remove` to remove)
   - History: `/sync/history` (GET for viewing, POST for adding)
   - Collection: `/sync/collection` (GET for viewing, POST for adding)
   - Ratings: `/sync/ratings` (GET for viewing, POST for adding)
   - Search: `/search/{type}?query={q}` (no auth required)
   - Trending: `/{type}/trending` (no auth required)
   - Popular: `/{type}/popular` (no auth required)
   - Recommendations: `/recommendations/{type}` (requires auth)

5. **Handle responses** appropriately:
   - Success: 200/201 status codes
   - Not found: 404
   - Unauthorized: 401 (token may need refresh)
   - Rate limited: 429

## Rate Limits

- **Authenticated**: 1000 GET requests per 5 minutes, 1 POST/PUT/DELETE per second
- **Unauthenticated**: 1000 GET requests per 5 minutes

## Getting OAuth Token

To get an access token, use this helper script:

```bash
#!/bin/bash
# Save as get_trakt_token.sh

CLIENT_ID="your_client_id"
CLIENT_SECRET="your_client_secret"
REDIRECT_URI="urn:ietf:wg:oauth:2.0:oob"

echo "1. Open this URL in your browser:"
echo "https://trakt.tv/oauth/authorize?response_type=code&client_id=$CLIENT_ID&redirect_uri=$REDIRECT_URI"
echo ""
echo "2. Authorize the app and copy the code"
echo -n "3. Paste the code here: "
read CODE

echo ""
echo "Exchanging code for token..."

RESPONSE=$(curl -s -X POST https://api.trakt.tv/oauth/token \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": \"$CODE\",
    \"client_id\": \"$CLIENT_ID\",
    \"client_secret\": \"$CLIENT_SECRET\",
    \"redirect_uri\": \"$REDIRECT_URI\",
    \"grant_type\": \"authorization_code\"
  }")

echo ""
echo "Response:"
echo "$RESPONSE" | jq .
echo ""
echo "Add these to your OpenClaw config:"
echo "TRAKT_ACCESS_TOKEN=$(echo $RESPONSE | jq -r .access_token)"
echo "TRAKT_REFRESH_TOKEN=$(echo $RESPONSE | jq -r .refresh_token)"
```

Make it executable: `chmod +x get_trakt_token.sh`

## Examples

**User:** "Add Dune to my Trakt watchlist"

**Assistant:** I'll add Dune to your Trakt watchlist.

```bash
curl -X POST https://api.trakt.tv/sync/watchlist \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID" \
  -d '{"movies":[{"title":"Dune","year":2021}]}'
```

---

**User:** "What movies are trending on Trakt?"

**Assistant:** Let me check the trending movies on Trakt.

```bash
curl "https://api.trakt.tv/movies/trending?limit=10" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID"
```

---

**User:** "Rate Breaking Bad 10/10 on Trakt"

**Assistant:** I'll rate Breaking Bad 10/10 on Trakt.

```bash
curl -X POST https://api.trakt.tv/sync/ratings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TRAKT_ACCESS_TOKEN" \
  -H "trakt-api-version: 2" \
  -H "trakt-api-key: $TRAKT_CLIENT_ID" \
  -d '{"shows":[{"title":"Breaking Bad","year":2008,"rating":10}]}'
```

## Notes

- Items are automatically removed from watchlist when marked as watched
- You can use IDs instead of title/year for more accuracy
- Extended info can be requested with `?extended=full` parameter
- All dates should be in UTC ISO 8601 format
- The API supports batch operations - you can add multiple items in one request
