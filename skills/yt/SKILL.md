---
name: yt
description: Quick YouTube utility — fetch transcripts, search videos, get latest from channels. Use when someone shares a YouTube link, asks about a video, or says "yt", "youtube", "check this video", "what's this video about", "find videos about", "latest from".
homepage: https://transcriptapi.com
metadata: {"moltbot":{"emoji":"▶️","requires":{"env":["TRANSCRIPT_API_KEY"]},"primaryEnv":"TRANSCRIPT_API_KEY"}}
---

# yt

Quick YouTube lookup via [TranscriptAPI.com](https://transcriptapi.com).

## Setup

Get a free API key (100 credits, no card) at [transcriptapi.com/signup](https://transcriptapi.com/signup).

Store: `echo 'export TRANSCRIPT_API_KEY="sk_..."' >> ~/.zshenv && source ~/.zshenv`

Auth: `-H "Authorization: Bearer $TRANSCRIPT_API_KEY"`

## Transcript — 1 credit

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_URL&format=text&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

## Search — 1 credit

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/search?q=QUERY&type=video&limit=10" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

| Param | Default | Values |
|-------|---------|--------|
| `q` | — | 1-200 chars (required) |
| `type` | `video` | `video`, `channel` |
| `limit` | `20` | 1-50 |

## Channel latest — FREE

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel_id=UC_ID" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

Returns last 15 videos with exact view counts and publish dates.

## Resolve handle — FREE

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/resolve?input=@mkbhd" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

Use to convert @handle to UC... channel ID.

## Errors

| Code | Action |
|------|--------|
| 402 | No credits — transcriptapi.com/billing |
| 404 | Not found / no captions |
| 408 | Timeout — retry once |

Free tier: 100 credits. Search and transcript cost 1 credit. Channel latest and resolve are free.
