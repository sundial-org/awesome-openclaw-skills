---
name: youtube-full
description: Complete YouTube toolkit — transcripts, search, channels, playlists, and metadata all in one skill. Use when you need comprehensive YouTube access, want to search and then get transcripts, browse channel content, work with playlists, or need the full suite of YouTube data endpoints. The all-in-one YouTube skill for agents.
homepage: https://transcriptapi.com
metadata: {"moltbot":{"emoji":"🎯","requires":{"env":["TRANSCRIPT_API_KEY"]},"primaryEnv":"TRANSCRIPT_API_KEY"}}
---

# YouTube Full

Complete YouTube toolkit via [TranscriptAPI.com](https://transcriptapi.com). Everything in one skill.

## Setup

`TRANSCRIPT_API_KEY` required. Get one free (100 credits, no card):
- [transcriptapi.com/signup](https://transcriptapi.com/signup) → Dashboard → API Keys
- Store: `echo 'export TRANSCRIPT_API_KEY="sk_..."' >> ~/.zshenv && source ~/.zshenv`

Auth: `-H "Authorization: Bearer $TRANSCRIPT_API_KEY"`

---

## Transcript — 1 credit

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_URL&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Default | Values |
|-------|----------|---------|--------|
| `video_url` | yes | — | YouTube URL or 11-char video ID |
| `format` | no | `json` | `json`, `text` |
| `include_timestamp` | no | `true` | `true`, `false` |
| `send_metadata` | no | `false` | `true`, `false` |

**Response** (`format=json`):
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "transcript": [{"text": "...", "start": 18.0, "duration": 3.5}],
  "metadata": {"title": "...", "author_name": "...", "author_url": "...", "thumbnail_url": "..."}
}
```

---

## Search — 1 credit

```bash
# Videos
curl -s "https://transcriptapi.com/api/v2/youtube/search?q=QUERY&type=video&limit=20" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"

# Channels
curl -s "https://transcriptapi.com/api/v2/youtube/search?q=QUERY&type=channel&limit=10" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Required | Default | Validation |
|-------|----------|---------|------------|
| `q` | yes | — | 1-200 chars |
| `type` | no | `video` | `video`, `channel` |
| `limit` | no | `20` | 1-50 |

---

## Channels

### Resolve handle — FREE

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/resolve?input=@mkbhd" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```
Response: `{"channel_id": "UC...", "resolved_from": "@mkbhd"}`

### Latest 15 videos — FREE

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel_id=UC_ID" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

Requires `channel_id` matching `^UC[a-zA-Z0-9_-]{22}$`. Returns exact `viewCount` and ISO `published` timestamps.

### All channel videos — 1 credit/page

```bash
# First page (100 videos)
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?channel_id=UC_ID" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"

# Next pages
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?continuation=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

Provide exactly one of `channel_id` or `continuation`. Response includes `continuation_token` and `has_more`.

### Search within channel — 1 credit

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/search?channel_id=UC_ID&q=QUERY&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

---

## Playlists — 1 credit/page

```bash
# First page
curl -s "https://transcriptapi.com/api/v2/youtube/playlist/videos?playlist_id=PL_ID" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"

# Next pages
curl -s "https://transcriptapi.com/api/v2/youtube/playlist/videos?continuation=TOKEN" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

Valid prefixes: `PL`, `UU`, `LL`, `FL`, `OL`. Response includes `playlist_info`, `results`, `continuation_token`, `has_more`.

---

## Credit Costs

| Endpoint | Cost | Cache |
|----------|------|-------|
| transcript | 1 | varies |
| search | 1 | 10 min |
| channel/resolve | **free** | 24h |
| channel/latest | **free** | 10 min |
| channel/videos | 1/page | 1-6h |
| channel/search | 1 | 15 min |
| playlist/videos | 1/page | 2-6h |

---

## Validation Rules

| Field | Rule |
|-------|------|
| `channel_id` | `^UC[a-zA-Z0-9_-]{22}$` |
| `playlist_id` | starts with `PL`/`UU`/`LL`/`FL`/`OL` |
| `q` | 1-200 chars |
| `limit` | 1-50 |

---

## Errors

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Bad API key | Check key |
| 402 | No credits | transcriptapi.com/billing |
| 404 | Not found | Resource doesn't exist or no captions |
| 408 | Timeout | Retry once after 2s |
| 422 | Validation error | Check param format |
| 429 | Rate limited | Wait, respect Retry-After |

---

## Typical Workflows

**Research workflow:** search → pick videos → fetch transcripts
```bash
# 1. Search
curl -s "https://transcriptapi.com/api/v2/youtube/search?q=machine+learning+explained&limit=5" -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
# 2. Transcript
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_ID&format=text&include_timestamp=true&send_metadata=true" -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

**Channel monitoring:** resolve → latest (free) → transcript
```bash
# 1. Resolve handle (free)
curl -s "https://transcriptapi.com/api/v2/youtube/channel/resolve?input=@mkbhd" -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
# 2. Latest uploads (free)
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel_id=UCBcRF18a7Qf58cCRy5xuWwQ" -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
# 3. Transcript of latest
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_ID&format=text&include_timestamp=true&send_metadata=true" -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

Free tier: 100 credits, 300 req/min. Starter ($5/mo): 1,000 credits.
