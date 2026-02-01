---
name: gram
description: Instagram CLI for viewing feeds, posts, profiles, and engagement via cookies.
homepage: https://github.com/arein/gram
metadata: {"clawdbot":{"emoji":"📸","requires":{"bins":["gram"]},"install":[{"id":"npm","kind":"node","package":"@cyberdrk/gram","bins":["gram"],"label":"Install gram (npm)"}]}}
---

# gram 📸

Instagram CLI using REST/GraphQL API + cookie auth.

## Install

```bash
# npm/pnpm/bun
npm install -g @cyberdrk/gram

# One-shot (no install)
bunx @cyberdrk/gram whoami
```

## Authentication

`gram` uses cookie-based auth from your Instagram web session.

Use `--session-id`, `--csrf-token`, and `--ds-user-id` to pass cookies directly, or `--cookie-source` for browser cookies.

Run `gram check` to see which source is active. For Arc/Brave, use `--chrome-profile-dir <path>`.

## Commands

### Account & Auth

```bash
gram whoami                    # Show logged-in account
gram check                     # Show credential sources
gram query-ids --refresh       # Refresh GraphQL query ID cache
```

### Reading Posts

```bash
gram post <shortcode-or-url>   # View a post
gram <shortcode-or-url>        # Shorthand for post
gram comments <shortcode> -n 20 # View comments on a post
gram likers <shortcode>        # View users who liked a post
```

### Feeds

```bash
gram feed -n 20                # Home feed
gram explore -n 20             # Explore/discover feed
```

### User Profiles

```bash
gram user <username>           # View user profile
gram user @instagram --json    # JSON output
gram posts <username> -n 20    # User's posts
gram following [username]      # Users someone follows (defaults to you)
gram followers [username]      # Someone's followers (defaults to you)
```

### Search

```bash
gram search "query"            # Search users, hashtags, places
gram search "coffee" --type users
gram search "nyc" --type places
gram search "#photography" --type hashtags
```

### Engagement Actions

```bash
gram like <shortcode>          # Like a post
gram unlike <shortcode>        # Unlike a post
gram save <shortcode>          # Save/bookmark a post
gram unsave <shortcode>        # Unsave a post
gram comment <shortcode> "nice!" # Comment on a post
gram follow <username>         # Follow a user
gram unfollow <username>       # Unfollow a user
```

## Output Options

```bash
--json          # JSON output
--json-full     # JSON with raw API response in _raw field
--plain         # No emoji, no color (script-friendly)
--no-emoji      # Disable emoji
--no-color      # Disable ANSI colors (or set NO_COLOR=1)
```

## Global Options

```bash
--session-id <token>           # Instagram sessionid cookie
--csrf-token <token>           # Instagram csrftoken cookie
--ds-user-id <id>              # Instagram ds_user_id cookie
--cookie-source <source>       # Cookie source for browser cookies (repeatable)
--chrome-profile <name>        # Chrome profile name
--chrome-profile-dir <path>    # Chrome/Chromium profile dir or cookie DB path
--firefox-profile <name>       # Firefox profile
--timeout <ms>                 # Request timeout
--cookie-timeout <ms>          # Cookie extraction timeout
```

## Config File

`~/.config/gram/config.json5` (global) or `./.gramrc.json5` (project):

```json5
{
  cookieSource: ["safari", "chrome"],
  chromeProfile: "Profile 1",
  timeoutMs: 60000
}
```

Environment variables: `GRAM_TIMEOUT_MS`, `GRAM_COOKIE_TIMEOUT_MS`

## Troubleshooting

### Query IDs stale (404 errors)
```bash
gram query-ids --refresh
```

### Cookie extraction fails
- Check browser is logged into Instagram
- Try different `--cookie-source`
- For Arc/Brave: use `--chrome-profile-dir`
- Provide cookies manually: `--session-id`, `--csrf-token`, `--ds-user-id`

### User-agent mismatch errors
- The CLI uses desktop user-agent by default
- If your session was created on mobile, it may fail
- Create a new session by logging in via desktop browser

---

**TL;DR**: View feeds, profiles, search, and engage with Instagram via CLI. 📸
