---
name: calctl
description: Manage Apple Calendar events via icalBuddy + AppleScript CLI
---

# calctl - Apple Calendar CLI

Manage Apple Calendar from the command line using icalBuddy (fast reads) and AppleScript (writes).

**Requirements:** `brew install ical-buddy`

## Commands

| Command | Description |
|---------|-------------|
| `calctl calendars` | List all calendars |
| `calctl show [filter]` | Show events (today, tomorrow, week, YYYY-MM-DD) |
| `calctl add <title>` | Create a new event |
| `calctl search <query>` | Search events by title (next 30 days) |

## Examples

```bash
# List calendars
calctl calendars

# Show today's events
calctl show today

# Show this week's events
calctl show week

# Show events from specific calendar
calctl show week --calendar Work

# Show events on specific date
calctl show 2026-01-25

# Add an event
calctl add "Meeting with John" --date 2026-01-22 --time 14:00

# Add event to specific calendar
calctl add "Team Standup" --calendar Work --date 2026-01-22 --time 09:00 --end 09:30

# Add all-day event
calctl add "Holiday" --date 2026-01-25 --all-day

# Add event with notes
calctl add "Project Review" --date 2026-01-22 --time 15:00 --notes "Bring quarterly report"

# Search for events
calctl search "meeting"
```

## Options for `add`

| Option | Description | Default |
|--------|-------------|---------|
| `-c, --calendar <name>` | Calendar to add event to | Privat |
| `-d, --date <YYYY-MM-DD>` | Event date | today |
| `-t, --time <HH:MM>` | Start time | 09:00 |
| `-e, --end <HH:MM>` | End time | 1 hour after start |
| `-n, --notes <text>` | Event notes | none |
| `--all-day` | Create all-day event | false |

## Available Calendars

Common calendars on this system:
- Privat (personal)
- Work
- Familien Kalender
- rainbat solutions GmbH
- TimeTrack
