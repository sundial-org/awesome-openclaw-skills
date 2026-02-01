---
name: youtube-channels
description: Work with YouTube channels — resolve handles to IDs, browse uploads, get latest videos, search within channels. Use when the user asks about a specific channel, wants to see recent uploads, or says "what has X posted lately", "latest from MKBHD", "show me their channel", "list channel videos", "browse channel uploads".
homepage: https://transcriptapi.com
metadata: {"moltbot":{"emoji":"📡","requires":{"env":["TRANSCRIPT_API_KEY"]},"primaryEnv":"TRANSCRIPT_API_KEY"}}
---

# YouTube Channels

YouTube channel tools via [TranscriptAPI.com](https://transcriptapi.com).

## Setup

`TRANSCRIPT_API_KEY` required. Get one free (100 credits, no card):
- [transcriptapi.com/signup](https://transcriptapi.com/signup) → Dashboard → API Keys
- Store: `echo 'export TRANSCRIPT_API_KEY="sk_..."' >> ~/.zshenv && source ~/.zshenv`

Auth: `-H "Authorization: Bearer $TRANSCRIPT_API_KEY"`

## GET /api/v2/youtube/channel/resolve — FREE

Convert @handle, URL, or UC... ID to canonical channel ID.

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

Fast-path: If input is already `UC[a-zA-Z0-9_-]{22}`, returns immediately. Cache: 24h.

## GET /api/v2/youtube/channel/latest — FREE

Latest 15 videos via RSS with exact stats.

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Validation |
|-------|----------|------------|
| `channel_id` | yes | `^UC[a-zA-Z0-9_-]{22}$` (24 chars total) |

**Response:**
```json
{
  "channel": {
    "channelId": "UCBcRF18a7Qf58cCRy5xuWwQ",
    "title": "MKBHD",
    "author": "MKBHD",
    "url": "https://www.youtube.com/channel/UCBcRF18a7Qf58cCRy5xuWwQ",
    "published": "2008-03-21T00:00:00Z"
  },
  "results": [{
    "videoId": "abc123xyz00",
    "title": "Latest Video Title",
    "channelId": "UCBcRF18a7Qf58cCRy5xuWwQ",
    "author": "MKBHD",
    "published": "2026-01-30T16:00:00Z",
    "updated": "2026-01-31T02:00:00Z",
    "link": "https://www.youtube.com/watch?v=abc123xyz00",
    "description": "Full video description...",
    "thumbnail": {"url": "https://i1.ytimg.com/vi/.../hqdefault.jpg", "width": "480", "height": "360"},
    "viewCount": "2287630",
    "starRating": {"average": "4.92", "count": "15000", "min": "1", "max": "5"}
  }],
  "result_count": 15
}
```

Great for monitoring channels — free and gives exact view counts + ISO timestamps. Cache: 10 min.

## GET /api/v2/youtube/channel/videos — 1 credit/page

Paginated list of ALL channel uploads (100 per page).

```bash
# First page
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"

# Next pages
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?continuation=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Validation |
|-------|----------|------------|
| `channel_id` | conditional | `^UC[a-zA-Z0-9_-]{22}$` (first page) |
| `continuation` | conditional | non-empty (next pages) |

Provide exactly one of `channel_id` or `continuation`, not both.

**Response:**
```json
{
  "results": [{
    "videoId": "abc123xyz00",
    "title": "Video Title",
    "channelId": "UCBcRF18a7Qf58cCRy5xuWwQ",
    "channelTitle": "MKBHD",
    "channelHandle": "@mkbhd",
    "lengthText": "15:22",
    "viewCountText": "3.2M views",
    "thumbnails": [...],
    "index": "0"
  }],
  "playlist_info": {"title": "Uploads from MKBHD", "numVideos": "1893", "ownerName": "MKBHD"},
  "continuation_token": "4qmFsgKlARIYVVV1...",
  "has_more": true
}
```

Keep calling with `continuation` until `has_more: false`. Cache: 1h first page, 6h continuations.

## GET /api/v2/youtube/channel/search — 1 credit

Search within a specific channel.

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/search?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ&q=iphone+review&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Validation |
|-------|----------|------------|
| `channel_id` | yes | `^UC[a-zA-Z0-9_-]{22}$` |
| `q` | yes | 1-200 chars |
| `limit` | no | 1-50 (default 30) |

## Typical workflow

```bash
# 1. Resolve handle to ID (free)
curl -s "https://transcriptapi.com/api/v2/youtube/channel/resolve?input=@mkbhd" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"

# 2. Check latest uploads (free)
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"

# 3. Get transcript of recent video
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_ID&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

## Errors

| Code | Action |
|------|--------|
| 400 | Invalid param combination (both or neither channel_id/continuation) |
| 402 | No credits — transcriptapi.com/billing |
| 404 | Channel not found |
| 408 | Timeout — retry once |
| 422 | Invalid channel_id format |

Free tier: 100 credits, 300 req/min. Free endpoints (resolve, latest) require auth but don't consume credits.
