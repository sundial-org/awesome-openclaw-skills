---
name: apple-calendar
description: Apple Calendar.app integration for macOS. CRUD operations for events, search, and multi-calendar support.
metadata: {"clawdbot":{"emoji":"📅","os":["darwin"]}}
---

# Apple Calendar

Interact with Calendar.app via AppleScript. Run scripts from: `cd {baseDir}`

## Commands

| Command | Usage |
|---------|-------|
| List calendars | `scripts/cal-list.sh` |
| List events | `scripts/cal-events.sh [days_ahead] [calendar_name]` |
| Read event | `scripts/cal-read.sh <event-uid> [calendar_name]` |
| Create event | `scripts/cal-create.sh <calendar> <summary> <start> <end> [location] [description] [allday] [recurrence]` |
| Update event | `scripts/cal-update.sh <event-uid> [--summary X] [--start X] [--end X] [--location X] [--description X]` |
| Delete event | `scripts/cal-delete.sh <event-uid> [calendar_name]` |
| Search events | `scripts/cal-search.sh <query> [days_ahead] [calendar_name]` |

## Date Format

- Timed: `YYYY-MM-DD HH:MM`
- All-day: `YYYY-MM-DD`

## Recurrence

| Pattern | RRULE |
|---------|-------|
| Daily 10x | `FREQ=DAILY;COUNT=10` |
| Weekly M/W/F | `FREQ=WEEKLY;BYDAY=MO,WE,FR` |
| Monthly 15th | `FREQ=MONTHLY;BYMONTHDAY=15` |

## Output

- Events/search: `UID | Summary | Start | End | AllDay | Location | Calendar`
- Read: Full details with description, URL, recurrence

## Notes

- Read-only calendars (Birthdays, Holidays) can't be modified
- Calendar names are case-sensitive
- Deleting recurring events removes entire series
