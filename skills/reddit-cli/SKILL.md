---
name: reddit-cli
version: 1.0.2
description: Reddit CLI using cookies for authentication. Read posts, search, and get subreddit info.
author: kelsia14
---

# Reddit CLI

Read Reddit using your session cookies. No API key needed.

## Quick start

```bash
reddit-cli posts programming 10       # Get 10 hot posts
reddit-cli posts gaming 5 top         # Get top 5 posts
reddit-cli search "python tutorial"   # Search all Reddit
reddit-cli search "help" --sub linux  # Search in subreddit
reddit-cli info AskReddit             # Subreddit info
reddit-cli check                      # Test connection
```

## Commands

### Get posts from subreddit
```bash
reddit-cli posts <subreddit> [limit] [sort]
```
- limit: number of posts (default: 10)
- sort: hot, new, top, rising (default: hot)

### Search Reddit
```bash
reddit-cli search <query> [--sub <subreddit>] [limit]
```

### Get subreddit info
```bash
reddit-cli info <subreddit>
```

### Check connection
```bash
reddit-cli check
```

## Environment

Set these in `~/.bashrc`:
```bash
export REDDIT_SESSION="your_reddit_session_cookie"
export TOKEN_V2="your_token_v2_cookie"  # optional
```

## Getting cookies

1. Go to reddit.com (logged in)
2. DevTools (F12) → Application → Cookies → reddit.com
3. Copy `reddit_session` value
4. Optionally copy `token_v2` value

## Notes

- Cookies expire, you may need to refresh them periodically
- Respects Reddit's rate limits
- For personal use only
