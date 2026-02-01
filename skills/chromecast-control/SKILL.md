---
name: chromecast
description: Control Chromecast devices on your local network - discover, cast media, control playback, manage queues, and save/restore states
homepage: https://github.com/skorokithakis/catt
metadata: {"clawdbot":{"emoji":"📺","requires":{"bins":["catt"]},"install":[{"id":"pip","kind":"uv","package":"catt","bins":["catt"],"label":"Install via pip/uv"}]}}
---

# Chromecast Control

Control Chromecast and Google Cast-enabled devices on your local network using `catt` (Cast All The Things).

## Quick Reference

| Command | Description |
|---------|-------------|
| `catt scan` | Find all Chromecasts on network |
| `catt cast <url>` | Cast video/audio |
| `catt pause` / `play` | Pause/resume |
| `catt stop` | Stop playback |
| `catt status` | Current playback info |
| `catt volume <0-100>` | Set volume |

Use `-d <device>` to target a specific device by name or IP.

## Discovery & Device Management

```bash
# Find all devices
catt scan

# Set a default device (saves to config)
catt -d "Living Room TV" set_default

# Create an alias for easier access
catt -d 192.168.1.163 set_alias tv

# Remove alias or default
catt -d tv del_alias
catt del_default
```

## Casting Media

### Basic Casting
```bash
# Cast from URL (YouTube, Vimeo, and hundreds of yt-dlp supported sites)
catt cast "https://www.youtube.com/watch?v=VIDEO_ID"

# Cast local file
catt cast ./video.mp4

# Cast a website (displays webpage on TV)
catt cast_site "https://example.com"
```

### Advanced Cast Options
```bash
# Cast with subtitles
catt cast -s ./subtitles.srt ./video.mp4

# Start at specific timestamp
catt cast -t 01:30:00 "https://youtube.com/watch?v=VIDEO_ID"

# Play random item from playlist
catt cast -r "https://youtube.com/playlist?list=PLAYLIST_ID"

# Play only video (ignore playlist in URL)
catt cast -n "https://youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID"

# Disable automatic subtitle loading
catt cast --no-subs ./video.mp4

# Pass yt-dlp options (e.g., select format)
catt cast -y format=best "https://youtube.com/watch?v=VIDEO_ID"

# Block until playback ends (useful for scripts)
catt cast -b "https://example.com/video.mp4"
```

## Playback Control

```bash
catt play              # Resume playback
catt pause             # Pause playback
catt play_toggle       # Toggle play/pause
catt stop              # Stop playback completely
catt skip              # Skip to end of content

# Seeking
catt seek 300          # Jump to 5 minutes (seconds)
catt seek 01:30:00     # Jump to 1h 30m (HH:MM:SS)
catt ffwd 30           # Fast forward 30 seconds
catt rewind 30         # Rewind 30 seconds
```

## Volume Control

```bash
catt volume 50         # Set volume to 50%
catt volumeup 10       # Increase by 10
catt volumedown 10     # Decrease by 10
catt volumemute on     # Mute
catt volumemute off    # Unmute
```

## Queue Management (YouTube)

```bash
# Add video to end of queue
catt add "https://youtube.com/watch?v=VIDEO_ID"

# Add video to play next
catt add -n "https://youtube.com/watch?v=VIDEO_ID"

# Remove video from queue
catt remove "https://youtube.com/watch?v=VIDEO_ID"

# Clear entire queue
catt clear
```

## State Management

```bash
# Save current state (position, volume, what's playing)
catt save

# Restore saved state later
catt restore
```

## Device Information

```bash
catt status    # Brief: time, volume, mute status
catt info      # Full: title, URL, player state, media type, etc.
```

## Configuration

Config file: `~/.config/catt/catt.cfg`

```ini
[options]
device = Living Room TV

[aliases]
tv = Living Room TV
bedroom = Bedroom Speaker
```

## Network Requirements

- Chromecast and computer must be on same network
- For local file casting: TCP ports 45000-47000 must be open
- Some networks block mDNS - use IP address directly if `catt scan` fails

## Supported Sources

Catt uses yt-dlp internally, supporting:
- YouTube (videos, playlists, live streams)
- Vimeo, Dailymotion, Twitch
- Direct video URLs (MP4, MKV, WebM, etc.)
- Local files (video, audio, images)
- Hundreds more sites (see yt-dlp supported sites)
