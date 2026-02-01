---
name: apple-music
description: Search Apple Music, add songs to library, manage playlists, control playback and AirPlay.
metadata: {"clawdbot":{"emoji":"🎵","os":["darwin"],"requires":{"bins":["node","curl"]}}}
---

# Apple Music

Control Apple Music via MusicKit API and AppleScript. Path: `~/.clawdbot/skills/apple-music/`

## Local (No Setup)

**Playback:** `./apple-music.sh player [now|play|pause|toggle|next|prev|shuffle|repeat|volume N|song "name"]`  
**AirPlay:** `./apple-music.sh airplay [list|select N|add N|remove N]`

## API (Setup Required)

Requires Apple Developer account ($99/yr) + MusicKit key.

### Setup

**Portal steps first:**
1. developer.apple.com → Keys → Create MusicKit key → Download .p8
2. Note your Key ID and Team ID

**Then run setup:**
```bash
./launch-setup.sh  # Opens Terminal for interactive setup
```

The launcher opens Terminal.app and runs the setup script there. Enter your .p8 path, Key ID, Team ID, then authorize in browser and paste the token.

**⚠️ Agents:** Always use `./launch-setup.sh` to open Terminal. Don't run setup.sh through chat (requires interactive input).

### Commands

- `search "query" [--type songs|albums|artists] [--limit N]`
- `library add <song-id>`
- `playlists [list|create "Name"|add <playlist-id> <song-id>]`

### Config

`config.json` stores tokens (valid ~6 months). Re-run `./setup.sh` if auth fails.

### Errors

- 401: Token expired, re-run setup
- 403: Check Apple Music subscription
- 404: Invalid ID or region-locked

### Setup Issues

- **404 on auth page:** Setup script auto-fixes with HTTP server verification
- **No token in browser:** Restart setup.sh
- **Browser won't open:** Manually open printed URL (Chrome recommended)
