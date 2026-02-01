---
name: gcalcli
description: Interact with Google Calendar via gcalcli
---

# Calendar Reference

This document provides details on using `gcalcli` to view and manage calendar events.

## Installation

`gcalcli` is a Python CLI for Google Calendar that works with `uvx` for one-time execution.

**IMPORTANT: Always use the custom fork with attachment support:**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli
```

This custom version includes attachments in TSV and JSON output, which is essential for accessing meeting notes and other event attachments.

## Authentication

First time running `gcalcli`, it will:
1. Open a browser for Google OAuth authentication
2. Cache credentials for future use
3. Request calendar read permissions

## Common Commands

### View Upcoming Agenda

**Recommended: JSON format with full details (structured data with attachments):**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --details all --json
```

**Alternative: TSV format (tab-separated, parseable):**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --details all --tsv
```

**Human-readable format (may truncate long descriptions):**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --details all
```

**Basic agenda view (minimal details):**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com
```

### Date Ranges

**Important: `gcalcli agenda` shows events from NOW onwards by default.**

When you run `gcalcli agenda "today"` at 2pm, it shows events from 2pm onwards for today and into the future. Past events from earlier today won't appear.

**Specific date range:**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com "tomorrow" "2 weeks"
```

**Today only (from current time onwards):**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com "today"
```

**See earlier today's events (use absolute dates):**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com "2025-10-07" "2025-10-07"
```

**Next week:**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com "monday" "friday"
```

### Search Calendar

**Search for events by text:**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli search --calendar smcdonal@redhat.com "MCP Server"
```

### Access Meeting Attachments and Gemini Notes

**IMPORTANT: The custom gcalcli fork includes `attachments` array in JSON/TSV output.**

Each event's `attachments` array contains objects with:
- `attachment_title`: Title of the attachment (e.g., "Notes by Gemini", "Recording", "Chat")
- `attachment_url`: Direct link to Google Drive file or Google Doc

**Common attachment types:**
- **"Notes by Gemini"**: AI-generated meeting notes from Google Meet
- **Recording**: Meeting recordings (video files)
- **Chat**: Meeting chat transcripts
- **Shared docs**: Agendas, planning docs, presentations

**Search for events with Gemini notes:**
```bash
# Find all events with Gemini notes
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli search "MCP" --calendar smcdonal@redhat.com --details all --json | jq '.[] | select(.attachments[]? | .attachment_title | contains("Notes by Gemini")) | {title, attachments: [.attachments[] | select(.attachment_title | contains("Notes by Gemini"))]}'

# Get just the titles and Gemini note URLs
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli search "MCP" --calendar smcdonal@redhat.com --details all --json | jq -r '.[] | select(.attachments[]? | .attachment_title | contains("Notes by Gemini")) | "\(.title): \(.attachments[] | select(.attachment_title | contains("Notes by Gemini")) | .attachment_url)"'
```

**Filter events by attachment type:**
```bash
# Events with recordings
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --json | jq '.[] | select(.attachments[]? | .attachment_title | contains("Recording"))'

# Events with any attachments
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --json | jq '.[] | select(.attachments | length > 0)'
```

**Export Gemini notes using gcmd:**

Single meeting export:
```bash
# 1. Find meeting with Gemini notes
GEMINI_URL=$(uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli search "MCP proposals" --calendar smcdonal@redhat.com --json | jq -r '.[0].attachments[] | select(.attachment_title | contains("Notes by Gemini")) | .attachment_url' | head -1)

# 2. Export to markdown using gcmd
cd /var/home/shanemcd/github/shanemcd/gcmd
uv run gcmd export "$GEMINI_URL" -o ~/Downloads/
```

**Bulk export ALL Gemini notes from search results (parallel):**
```bash
# Extract Gemini note URLs and export in parallel (8 concurrent processes)
cd /var/home/shanemcd/github/shanemcd/gcmd
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli search "MCP" --calendar smcdonal@redhat.com --details all --json "2 months ago" "today" | jq -r '.[] | select(.attachments[]? | .attachment_title | contains("Notes by Gemini")) | .attachments[] | select(.attachment_title | contains("Notes by Gemini")) | .attachment_url' | sort -u | xargs -P 8 -I {} sh -c 'uv run gcmd export "{}" -o ~/Downloads/meeting-notes/'
```

This efficiently:
- Searches calendar for meetings matching your query
- Filters to only meetings with Gemini notes
- Exports all notes in parallel (8 at a time) to organized directory
- Uses direct pipeline (no intermediate files)
- Deduplicates URLs with sort -u

**Common workflow - Review recent meeting notes:**
```bash
# Search for recent meetings on a topic
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli search "ANSTRAT-1567" --calendar smcdonal@redhat.com --json

# Filter to show only events with Gemini notes
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli search "ANSTRAT-1567" --calendar smcdonal@redhat.com --json | jq '.[] | select(.attachments[]? | .attachment_title | contains("Notes by Gemini")) | {title, date: .s, gemini_notes: [.attachments[] | select(.attachment_title | contains("Notes by Gemini")) | .attachment_url]}'

# Export the most recent Gemini notes for review
# (extract URL, then use gcmd export)
```

## Output Formats

### --json (JSON Format) **RECOMMENDED**
- Structured JSON output with complete event data
- Includes attachments array with title and fileUrl for each attachment
- All event fields preserved
- Easy to parse programmatically with `jq` or Python
- No truncation of any fields
- Best for accessing meeting notes and attachments

### --tsv (Tab-Separated Values)
- One event per line
- Tab-separated fields:
  - id
  - start_date, start_time
  - end_date, end_time
  - html_link
  - hangout_link
  - conference details
  - title
  - location
  - description (full, no truncation)
  - calendar
  - email
  - attachments (pipe-separated: title|url|title|url...)
  - action
- Ideal for parsing with standard Unix tools (grep, awk, cut)
- No ANSI color codes or formatting

### Default Format
- Human-readable colored output
- Shows time, title, basic details
- May truncate long descriptions with "..." indicator

### --details all
- Includes full descriptions
- Shows all attendees with response status
- Conference/meeting links
- Location information
- Attachments (in human-readable format)

## Use Cases

### 1. Morning Review
Check what's on today's schedule (shows from current time onwards):
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --json "today"
```

Note: This shows events from NOW onwards. To see the full day including past events, use the specific date:
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --json "2025-10-07" "2025-10-07"
```

### 2. Weekly Planning
See upcoming week to plan deep work time:
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --json "monday" "friday"
```

### 3. Meeting Preparation
Check details for upcoming meetings:
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --details all --json "today" "tomorrow"
```

### 4. Find Meeting Links and Notes
Get conference links and meeting notes for a meeting:
```bash
# Using JSON (recommended for accessing attachments)
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --details all --json | jq '.[] | select(.title | contains("Meeting Name"))'

# Using TSV
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --details all --tsv | grep "Meeting Name"
```

### 5. Context Before Work
Before working on a feature, check if there are relevant sync meetings:
```bash
uvx gcalcli search --calendar smcdonal@redhat.com "ANSTRAT-1673"
```

## Integration with Work Tracking

### Calendar-Aware Planning

When planning your day's agenda:
1. Check calendar for upcoming related meetings
2. Note if meetings happen before important deadlines (e.g., sync 2 days before release)
3. Plan work to prepare for discussions
4. Identify good time blocks for focused work (between meetings)

### Examples

**ANSTRAT-1673 Scenario:**
- Oct 8: Sync meeting with Demetrius Lima
- Oct 10: Expected llama-stack release
- Action: Check calendar to confirm timing, prepare talking points

**Pre-Meeting Prep:**
```bash
# See what's coming up this week with attachments
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --json "monday" "friday"

# Check specific meeting details
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli search --calendar smcdonal@redhat.com --json "ANSTRAT"
```

## Tips

1. **Always use custom fork with constraint**: Use `uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0"` for attachment support
2. **Always use `--json` flag**: Default to JSON format for structured data with attachments
3. **Use `jq` for parsing**: JSON output works perfectly with `jq` for filtering and extracting data
4. **Check calendar at session start**: Part of standard workflow
5. **Time-box focused work**: Look for gaps between meetings
6. **Prepare for syncs**: Check calendar 1-2 days before important meetings
7. **Access meeting notes**: Use `jq` to filter for Gemini notes, then export with gcmd
8. **Search before export**: Use `gcalcli search` to find relevant meetings, then filter attachments array
9. **Understand time ranges**: `"today"` shows from NOW onwards, not the full day. Use specific dates for complete day view.

## Limitations

- Read-only (no event creation/modification via CLI documented here)
- Requires OAuth authentication
- May need periodic re-authentication
- Multiple calendars require separate `--calendar` flags

## Additional Commands

**List all calendars:**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli list
```

**View in calendar format (month view):**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli calm
```

**Quick view (next 5 events) with JSON:**
```bash
uvx --from "git+https://github.com/shanemcd/gcalcli@attachments-in-tsv-and-json" --with "google-api-core<2.28.0" gcalcli agenda --calendar smcdonal@redhat.com --json | jq '.[0:5]'
```

## Reference

- Official gcalcli documentation: https://github.com/insanum/gcalcli
- Custom fork with attachment support: https://github.com/shanemcd/gcalcli/tree/attachments-in-tsv-and-json
- Uses Google Calendar API v3
- Supports multiple output formats (JSON, TSV, text)

