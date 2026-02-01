---
name: toggl
description: Track time with Toggl via the toggl CLI. Use when the user wants to start/stop time tracking, check current timer, view today's or weekly reports, list recent entries, or manage time entries. Triggers on "toggl", "time tracking", "timer", "track time", "what am I working on", "log time", "timesheet".
---

# Toggl Time Tracking

Use the `toggl` CLI (@beauraines/toggl-cli) for Toggl Track integration.

## Prerequisites

Install the CLI:
```bash
npm install -g @beauraines/toggl-cli
```

Configure authentication (create `~/.toggl-cli.json`):
```json
{
  "api_token": "YOUR_TOGGL_API_TOKEN",
  "default_workspace_id": "YOUR_WORKSPACE_ID",
  "timezone": "Your/Timezone"
}
```

Get your API token from: https://track.toggl.com/profile
Get your workspace ID from your Toggl URL: `https://track.toggl.com/{workspace_id}/...`

Set permissions: `chmod 600 ~/.toggl-cli.json`

## Commands

### Status
```bash
toggl now                    # Show running timer
toggl me                     # Show user info
```

### Start/Stop
```bash
toggl start                  # Start timer (interactive)
toggl start -d "Task name"   # Start with description
toggl start -d "Task" -p "Project"  # With project
toggl stop                   # Stop current timer
```

### Continue Previous
```bash
toggl continue               # Restart most recent entry
toggl continue "keyword"     # Restart entry matching keyword
```

### Reports
```bash
toggl today                  # Today's time by project
toggl week                   # Weekly summary by day
```

### List Entries
```bash
toggl ls                     # Last 14 days
toggl ls -d 7                # Last 7 days
toggl ls --today             # Today only
toggl ls "search term"       # Search entries
```

### Add Completed Entry
```bash
toggl add "9:00AM" "10:30AM" "Meeting notes"
```

### Edit Current
```bash
toggl edit -s "10:00AM"      # Change start time
toggl edit -d "New desc"     # Change description
toggl edit -p "Project"      # Change project
```

### Delete
```bash
toggl rm <id>                # Remove entry by ID
```

### Projects
```bash
toggl project ls             # List projects
```

### Other
```bash
toggl web                    # Open Toggl in browser
toggl create-config          # Generate config template
```

## Notes

- Times must be parsable by dayjs (e.g., `4:50PM`, `12:00 AM`, `9:00`)
- Config file: `~/.toggl-cli.json`
- Environment variables override config: `TOGGL_API_TOKEN`, `TOGGL_DEFAULT_WORKSPACE_ID`, `TOGGL_TIMEZONE`
