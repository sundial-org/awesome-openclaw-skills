---
name: transcript
description: Get transcripts from any YouTube video — for summarization, research, translation, quoting, or content analysis. Use when the user shares a video link or asks "what did they say", "get the transcript", "transcribe this video", "summarize this video", or wants to analyze spoken content.
homepage: https://transcriptapi.com
metadata: {"moltbot":{"emoji":"📝","requires":{"env":["TRANSCRIPT_API_KEY"]},"primaryEnv":"TRANSCRIPT_API_KEY"}}
---

# Transcript

Fetch video transcripts via [TranscriptAPI.com](https://transcriptapi.com).

## Setup

`TRANSCRIPT_API_KEY` required. Get one free (100 credits, no card):
- [transcriptapi.com/signup](https://transcriptapi.com/signup) → Dashboard → API Keys
- Store: `echo 'export TRANSCRIPT_API_KEY="sk_..."' >> ~/.zshenv && source ~/.zshenv`

## GET /api/v2/youtube/transcript

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

Accepts: full URLs (`youtube.com/watch?v=ID`), short URLs (`youtu.be/ID`), shorts (`youtube.com/shorts/ID`), or bare video IDs.

**Default:** Always use `format=text&include_timestamp=true&send_metadata=true` unless user specifies otherwise.

**Response** (`format=json`):
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "transcript": [
    {"text": "We're no strangers to love", "start": 18.0, "duration": 3.5},
    {"text": "You know the rules and so do I", "start": 21.5, "duration": 2.8}
  ],
  "metadata": {
    "title": "Rick Astley - Never Gonna Give You Up",
    "author_name": "Rick Astley",
    "author_url": "https://www.youtube.com/@RickAstley",
    "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
  }
}
```

**Response** (`format=text`):
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "transcript": "[00:00:18] We're no strangers to love\n[00:00:21] You know the rules...",
  "metadata": {...}
}
```

## Errors

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Bad API key | Check key or re-setup |
| 402 | No credits | Top up at transcriptapi.com/billing |
| 404 | No transcript | Video may not have captions enabled |
| 408 | Timeout | Retry once after 2s |
| 429 | Rate limited | Wait and retry |

## Tips

- For long videos, summarize key points first, offer full transcript on request.
- Use `format=json` when you need precise timestamps for quoting specific moments.
- Use `include_timestamp=false` for clean text suitable for translation or analysis.
- 1 credit per successful request. Errors don't cost credits.
- Free tier: 100 credits, 300 req/min.
