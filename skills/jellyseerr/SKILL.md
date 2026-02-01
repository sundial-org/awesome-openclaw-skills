---
name: jellyseerr
description: Request movies and TV shows through Jellyseerr. Use when the user wants to add media to their Plex/Jellyfin server, search for content availability, or manage media requests.
---

# Jellyseerr

Request movies and TV shows through your Jellyseerr server for automated downloading to Plex/Jellyfin.

## Setup

Configure your Jellyseerr server:

```bash
scripts/setup.sh
```

You'll need:
- Jellyseerr server URL
- API key (from Jellyseerr Settings > General)

## Usage

Request a movie:
```bash
scripts/request_movie.py "Movie Name"
```

Request a TV show:
```bash
scripts/request_tv.py "TV Show Name"
```

Search for content:
```bash
scripts/search.py "Content Name"
```

## Examples

Request a movie:
```bash
scripts/request_movie.py "The Matrix"
```

Request a TV show (entire series):
```bash
scripts/request_tv.py "Breaking Bad"
```

Request specific TV season:
```bash
scripts/request_tv.py "Breaking Bad" --season 1
```

## Automatic Availability Notifications

Get notified when your requested content becomes available.

### Webhooks (Recommended)

For instant notifications, set up webhook integration. See [references/WEBHOOK_SETUP.md](references/WEBHOOK_SETUP.md) for the complete guide.

Quick setup:
```bash
scripts/install_service.sh  # Run with sudo
```

Then configure Jellyseerr to send webhooks to `http://YOUR_IP:8384/`

### Polling (Alternative)

For environments where webhooks aren't available, use cron-based polling:

```bash
crontab -l > /tmp/cron_backup.txt
echo "* * * * * $(pwd)/scripts/auto_monitor.sh" >> /tmp/cron_backup.txt
crontab /tmp/cron_backup.txt
```

Check pending requests:
```bash
scripts/track_requests.py
```

## Configuration

Edit `~/.config/jellyseerr/config.json`:
```json
{
  "server_url": "https://jellyseerr.yourdomain.com",
  "api_key": "your-api-key",
  "auto_approve": true
}
```

## API Reference

See [references/api.md](references/api.md) for Jellyseerr API documentation.
