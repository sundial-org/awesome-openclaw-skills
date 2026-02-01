---
name: youtube-api
description: YouTube API access without the official API quota hassle — transcripts, search, channels, playlists, and metadata with no Google API key needed. Use when the user needs YouTube data programmatically, wants to avoid Google API quotas, or asks for "youtube api", "get video data", "youtube without api key", "no quota youtube".
homepage: https://transcriptapi.com
metadata: {"moltbot":{"emoji":"⚡","requires":{"env":["TRANSCRIPT_API_KEY"]},"primaryEnv":"TRANSCRIPT_API_KEY"}}
---

# YouTube API

YouTube data access via [TranscriptAPI.com](https://transcriptapi.com) — no Google API quota needed.

## Setup

`TRANSCRIPT_API_KEY` required. Get one free (100 credits, no card):
- [transcriptapi.com/signup](https://transcriptapi.com/signup) → Dashboard → API Keys
- Store: `echo 'export TRANSCRIPT_API_KEY="sk_..."' >> ~/.zshenv && source ~/.zshenv`

Auth: `-H "Authorization: Bearer $TRANSCRIPT_API_KEY"`

## Endpoint Reference

All endpoints: `https://transcriptapi.com/api/v2/youtube/...`

| Endpoint | Method | Cost | Cache |
|----------|--------|------|-------|
| `/transcript?video_url=ID` | GET | 1 | varies |
| `/search?q=QUERY&type=video` | GET | 1 | 10 min |
| `/channel/resolve?input=@handle` | GET | **free** | 24h |
| `/channel/latest?channel_id=UC_ID` | GET | **free** | 10 min |
| `/channel/videos?channel_id=UC_ID` | GET | 1/page | 1-6h |
| `/channel/search?channel_id=UC_ID&q=Q` | GET | 1 | 15 min |
| `/playlist/videos?playlist_id=PL_ID` | GET | 1/page | 2-6h |

## Quick Examples

**Search videos:**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/search?q=python+tutorial&type=video&limit=10" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

**Get transcript:**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=dQw4w9WgXcQ&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

**Resolve channel handle (free):**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/resolve?input=@mkbhd" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

**Latest videos (free):**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

**Browse channel uploads (paginated):**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
# Use continuation token from response for next pages
```

**Browse playlist (paginated):**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/playlist/videos?playlist_id=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

## Parameter Validation

| Field | Rule |
|-------|------|
| `channel_id` | `^UC[a-zA-Z0-9_-]{22}$` (24 chars total) |
| `playlist_id` | starts with `PL`, `UU`, `LL`, `FL`, or `OL` |
| `q` (search) | 1-200 chars |
| `limit` | 1-50 |
| `continuation` | non-empty string |

## Why Not Google's API?

| | Google YouTube Data API | TranscriptAPI |
|-|------------------------|---------------|
| Quota | 10,000 units/day (100 searches) | Credit-based, no daily cap |
| Setup | OAuth + API key + project | Single API key |
| Transcripts | Not available | Core feature |
| Pricing | $0.0015/unit overage | $5/1000 credits |

## Errors

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Bad API key | Check key |
| 402 | No credits | transcriptapi.com/billing |
| 404 | Not found | Resource doesn't exist |
| 408 | Timeout/retryable | Retry once after 2s |
| 422 | Validation error | Check param format |
| 429 | Rate limited | Wait, respect Retry-After |

Free tier: 100 credits, 300 req/min. Starter ($5/mo): 1,000 credits.
