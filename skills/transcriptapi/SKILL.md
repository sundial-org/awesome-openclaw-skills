---
name: transcriptapi
description: Full TranscriptAPI toolkit — fetch YouTube transcripts, search videos and channels, browse channel uploads, get latest videos, and explore playlists. Use when the user wants to work with YouTube content programmatically, get transcripts for summarization or analysis, find videos, or monitor channels. Triggers on YouTube URLs, "transcript", "transcriptapi", "video summary", "what did they say", "find videos about", "search youtube".
homepage: https://transcriptapi.com
metadata: {"moltbot":{"emoji":"📺","requires":{"env":["TRANSCRIPT_API_KEY"]},"primaryEnv":"TRANSCRIPT_API_KEY"}}
---

# TranscriptAPI

Full YouTube data toolkit via [TranscriptAPI.com](https://transcriptapi.com). Transcripts, search, channels, playlists — one API key.

## Setup

If `$TRANSCRIPT_API_KEY` is not set:

```bash
# 1. Register (100 free credits, no card needed)
curl -s -X POST "https://transcriptapi.com/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "USER_EMAIL", "password": "SECURE_PASSWORD", "name": "USER_NAME"}'

# 2. Login to get access token
curl -s -X POST "https://transcriptapi.com/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=USER_EMAIL&password=SECURE_PASSWORD"

# 3. Get API key (auto-created on signup)
curl -s "https://transcriptapi.com/api/auth/api-keys" \
  -H "Authorization: Bearer ACCESS_TOKEN"

# 4. Store persistently
echo 'export TRANSCRIPT_API_KEY="sk_..."' >> ~/.zshenv && source ~/.zshenv
```

Manual: [transcriptapi.com/signup](https://transcriptapi.com/signup) → Dashboard → API Keys.

## Auth

All requests: `-H "Authorization: Bearer $TRANSCRIPT_API_KEY"`

## Endpoints

### GET /api/v2/youtube/transcript — 1 credit

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_URL&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Default | Validation |
|-------|----------|---------|------------|
| `video_url` | yes | — | YouTube URL or 11-char video ID |
| `format` | no | `json` | `json` or `text` |
| `include_timestamp` | no | `true` | `true` or `false` |
| `send_metadata` | no | `false` | `true` or `false` |

Accepts: `https://youtube.com/watch?v=ID`, `https://youtu.be/ID`, `youtube.com/shorts/ID`, or bare `ID`.

**Response** (`format=json`):
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "transcript": [{"text": "We're no strangers...", "start": 18.0, "duration": 3.5}],
  "metadata": {"title": "...", "author_name": "...", "author_url": "...", "thumbnail_url": "..."}
}
```

### GET /api/v2/youtube/search — 1 credit

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/search?q=QUERY&type=video&limit=20" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Default | Validation |
|-------|----------|---------|------------|
| `q` | yes | — | 1-200 chars (trimmed) |
| `type` | no | `video` | `video` or `channel` |
| `limit` | no | `20` | 1-50 |

**Response** (`type=video`):
```json
{
  "results": [{
    "type": "video",
    "videoId": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "channelTitle": "Rick Astley",
    "channelHandle": "@RickAstley",
    "channelVerified": true,
    "lengthText": "3:33",
    "viewCountText": "1.5B views",
    "publishedTimeText": "14 years ago",
    "hasCaptions": true,
    "thumbnails": [{"url": "...", "width": 120, "height": 90}]
  }],
  "result_count": 20
}
```

**Response** (`type=channel`):
```json
{
  "results": [{
    "type": "channel",
    "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "title": "Rick Astley",
    "handle": "@RickAstley",
    "subscriberCount": "4.2M subscribers",
    "verified": true,
    "rssUrl": "https://www.youtube.com/feeds/videos.xml?channel_id=UC..."
  }],
  "result_count": 5
}
```

### GET /api/v2/youtube/channel/resolve — FREE (0 credits)

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/resolve?input=@mkbhd" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Validation |
|-------|----------|------------|
| `input` | yes | 1-200 chars — @handle, URL, or UC... ID |

**Response:**
```json
{"channel_id": "UCBcRF18a7Qf58cCRy5xuWwQ", "resolved_from": "@mkbhd"}
```

Fast-path: If input is already a valid `UC[a-zA-Z0-9_-]{22}` ID, returns immediately without lookup.

### GET /api/v2/youtube/channel/videos — 1 credit/page

```bash
# First page (100 videos)
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"

# Next pages
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?continuation=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Validation |
|-------|----------|------------|
| `channel_id` | conditional | `^UC[a-zA-Z0-9_-]{22}$` (first page) |
| `continuation` | conditional | non-empty string (next pages) |

Provide exactly one of `channel_id` or `continuation`.

**Response:**
```json
{
  "results": [{
    "videoId": "abc123xyz00",
    "title": "Latest Video",
    "channelId": "UCBcRF18a7Qf58cCRy5xuWwQ",
    "channelTitle": "MKBHD",
    "channelHandle": "@mkbhd",
    "lengthText": "15:22",
    "viewCountText": "3.2M views",
    "thumbnails": [...],
    "index": "0"
  }],
  "playlist_info": {"title": "Uploads from MKBHD", "numVideos": "1893"},
  "continuation_token": "4qmFsgKlARIYVVV1...",
  "has_more": true
}
```

### GET /api/v2/youtube/channel/latest — FREE (0 credits)

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Validation |
|-------|----------|------------|
| `channel_id` | yes | `^UC[a-zA-Z0-9_-]{22}$` |

Returns last 15 videos via RSS with exact view counts and ISO timestamps.

**Response:**
```json
{
  "channel": {"channelId": "...", "title": "MKBHD", "author": "MKBHD", "url": "..."},
  "results": [{
    "videoId": "abc123xyz00",
    "title": "Latest Video",
    "published": "2026-01-30T16:00:00Z",
    "viewCount": "2287630",
    "description": "Full description...",
    "thumbnail": {"url": "...", "width": "480", "height": "360"}
  }],
  "result_count": 15
}
```

### GET /api/v2/youtube/channel/search — 1 credit

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/search?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ&q=review&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Validation |
|-------|----------|------------|
| `channel_id` | yes | `^UC[a-zA-Z0-9_-]{22}$` |
| `q` | yes | 1-200 chars |
| `limit` | no | 1-50 (default 30) |

### GET /api/v2/youtube/playlist/videos — 1 credit/page

```bash
# First page
curl -s "https://transcriptapi.com/api/v2/youtube/playlist/videos?playlist_id=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"

# Next pages
curl -s "https://transcriptapi.com/api/v2/youtube/playlist/videos?continuation=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Validation |
|-------|----------|------------|
| `playlist_id` | conditional | starts with PL/UU/LL/FL/OL |
| `continuation` | conditional | non-empty string |

## Credit Costs

| Endpoint | Cost | Cache |
|----------|------|-------|
| transcript | 1 | HIT or MISS |
| search | 1 | 10 min |
| channel/resolve | **free** | 24h (persistent) |
| channel/search | 1 | 15 min |
| channel/videos | 1/page | 1h first, 6h cont |
| channel/latest | **free** | 10 min |
| playlist/videos | 1/page | 2h first, 6h cont |

## Errors

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Bad API key | Check key, re-run setup |
| 402 | No credits | Top up at transcriptapi.com/billing |
| 404 | Not found | Video/channel/playlist doesn't exist or no captions |
| 408 | Timeout/retryable | Retry once after 2s |
| 422 | Validation error | Check param format |
| 429 | Rate limited | Wait, respect Retry-After |

## Tips

- When user shares YouTube URL with no instruction, fetch transcript and summarize key points.
- Use `channel/latest` (free) to check for new uploads before fetching transcripts.
- Combine `channel/resolve` → `channel/videos` for browsing channel uploads.
- For research: search → pick videos → fetch transcripts.
- Free tier: 100 credits, 300 req/min. Starter ($5/mo): 1,000 credits, 300 req/min.
