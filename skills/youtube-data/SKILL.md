---
name: youtube-data
description: Access YouTube video data — transcripts, metadata, channel info, search, and playlists. A lightweight alternative to Google's YouTube Data API with no quota limits. Use when the user needs structured data from YouTube videos, channels, or playlists without dealing with Google API setup, OAuth, or daily quotas.
homepage: https://transcriptapi.com
metadata: {"moltbot":{"emoji":"📊","requires":{"env":["TRANSCRIPT_API_KEY"]},"primaryEnv":"TRANSCRIPT_API_KEY"}}
---

# YouTube Data

YouTube data access via [TranscriptAPI.com](https://transcriptapi.com) — lightweight alternative to Google's YouTube Data API.

## Setup

`TRANSCRIPT_API_KEY` required. Get one free (100 credits, no card):
- [transcriptapi.com/signup](https://transcriptapi.com/signup) → Dashboard → API Keys
- Store: `echo 'export TRANSCRIPT_API_KEY="sk_..."' >> ~/.zshenv && source ~/.zshenv`

Auth: `-H "Authorization: Bearer $TRANSCRIPT_API_KEY"`

## Video Data (transcript + metadata) — 1 credit

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_URL&format=json&include_timestamp=true&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "transcript": [
    {"text": "We're no strangers to love", "start": 18.0, "duration": 3.5}
  ],
  "metadata": {
    "title": "Rick Astley - Never Gonna Give You Up",
    "author_name": "Rick Astley",
    "author_url": "https://www.youtube.com/@RickAstley",
    "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
  }
}
```

## Search Data — 1 credit

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/search?q=QUERY&type=video&limit=20" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

**Video result fields:** `videoId`, `title`, `channelId`, `channelTitle`, `channelHandle`, `channelVerified`, `lengthText`, `viewCountText`, `publishedTimeText`, `hasCaptions`, `thumbnails`

**Channel result fields** (`type=channel`): `channelId`, `title`, `handle`, `url`, `description`, `subscriberCount`, `verified`, `rssUrl`, `thumbnails`

## Channel Data

**Resolve handle to ID (free):**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/resolve?input=@mkbhd" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```
Returns: `{"channel_id": "UCBcRF18a7Qf58cCRy5xuWwQ", "resolved_from": "@mkbhd"}`

**Latest 15 videos with exact stats (free):**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/latest?channel_id=UC_ID" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```
Returns: `channel` info, `results` array with `videoId`, `title`, `published` (ISO), `viewCount` (exact number), `description`, `thumbnail`

**All channel videos (paginated, 1 credit/page):**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/videos?channel_id=UC_ID" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```
Returns 100 videos per page + `continuation_token` for pagination.

**Search within channel (1 credit):**
```bash
curl -s "https://transcriptapi.com/api/v2/youtube/channel/search?channel_id=UC_ID&q=QUERY&limit=30" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

## Playlist Data — 1 credit/page

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/playlist/videos?playlist_id=PL_ID" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY"
```

Returns: `results` (videos), `playlist_info` (`title`, `numVideos`, `ownerName`, `viewCount`), `continuation_token`, `has_more`

## Credit Costs

| Endpoint | Cost | Data returned |
|----------|------|---------------|
| transcript | 1 | Full transcript + metadata |
| search | 1 | Video/channel details |
| channel/resolve | **free** | Channel ID mapping |
| channel/latest | **free** | 15 videos + exact stats |
| channel/videos | 1/page | 100 videos per page |
| channel/search | 1 | Videos matching query |
| playlist/videos | 1/page | 100 videos per page |

## Errors

| Code | Action |
|------|--------|
| 402 | No credits — transcriptapi.com/billing |
| 404 | Not found |
| 408 | Timeout — retry once |
| 422 | Invalid param format |

Free tier: 100 credits, 300 req/min.
