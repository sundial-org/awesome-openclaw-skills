---
name: spotify
description: Control Spotify playback on macOS. Play/pause, skip tracks, control volume, play artists/albums/playlists. Use when a user asks to play music, control Spotify, change songs, or adjust Spotify volume.
metadata: {"clawdbot":{"emoji":"🎵","requires":{"bins":["spotify"],"os":"darwin"},"install":[{"id":"brew","kind":"brew","packages":["shpotify"],"bins":["spotify"],"label":"Install spotify CLI (brew)"}]}}
---

# Spotify CLI

Control Spotify on macOS. No API key required.

## Commands

```bash
spotify play                     # Resume
spotify pause                    # Pause/toggle
spotify next                     # Next track
spotify prev                     # Previous track
spotify stop                     # Stop

spotify vol up                   # +10%
spotify vol down                 # -10%
spotify vol 50                   # Set to 50%

spotify status                   # Current track info
```

## Play by Name

1. Search web for Spotify URL: `"Daft Punk" site:open.spotify.com`
2. Get ID from URL: `open.spotify.com/artist/4tZwfgrHOc3mvqYlEYSvVi` → ID is `4tZwfgrHOc3mvqYlEYSvVi`
3. Play with AppleScript:

```bash
# Artist
osascript -e 'tell application "Spotify" to play track "spotify:artist:4tZwfgrHOc3mvqYlEYSvVi"'

# Album
osascript -e 'tell application "Spotify" to play track "spotify:album:4m2880jivSbbyEGAKfITCa"'

# Track
osascript -e 'tell application "Spotify" to play track "spotify:track:2KHRENHQzTIQ001nlP9Gdc"'
```

## Notes

- **macOS only** - uses AppleScript
- Spotify desktop app must be running
- Works with Sonos via Spotify Connect
