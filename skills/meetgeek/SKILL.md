---
name: meetgeek
description: Query MeetGeek meeting intelligence from CLI - list meetings, get AI summaries, transcripts, action items, and search across all your calls with natural language.
---

# MeetGeek Skill

Retrieve meeting intelligence from MeetGeek - summaries, transcripts, action items, and search across calls.

**npm:** https://www.npmjs.com/package/meetgeek-cli  
**GitHub:** https://github.com/nexty5870/meetgeek-cli

## Installation

```bash
npm install -g meetgeek-cli
```

## Setup

```bash
meetgeek auth   # Interactive API key setup
```

Get your API key from: MeetGeek → Integrations → Public API Integration

## Commands

### List recent meetings
```bash
meetgeek list
meetgeek list --limit 20
```

### Get meeting details
```bash
meetgeek show <meeting-id>
```

### Get AI summary (with action items)
```bash
meetgeek summary <meeting-id>
```

### Get full transcript
```bash
meetgeek transcript <meeting-id>
meetgeek transcript <meeting-id> -o /tmp/call.txt  # save to file
```

### Get highlights
```bash
meetgeek highlights <meeting-id>
```

### Search meetings
```bash
# Search in a specific meeting
meetgeek ask "topic" -m <meeting-id>

# Search across all recent meetings
meetgeek ask "what did we discuss about the budget"
```

### Auth management
```bash
meetgeek auth --show   # check API key status
meetgeek auth          # interactive setup
meetgeek auth --clear  # remove saved key
```

## Usage Patterns

### Find a specific call
```bash
# List meetings to find the one you want
meetgeek list --limit 10

# Then use the meeting ID (first 8 chars shown, use full ID)
meetgeek summary 81a6ab96-19e7-44f5-bd2b-594a91d2e44b
```

### Get action items from a call
```bash
meetgeek summary <meeting-id>
# Look for the "✅ Action Items" section
```

### Find what was discussed about a topic
```bash
# Search across all meetings
meetgeek ask "pricing discussion"

# Or in a specific meeting
meetgeek ask "timeline" -m <meeting-id>
```

### Export transcript for reference
```bash
meetgeek transcript <meeting-id> -o ~/call-transcript.txt
```

## Notes

- Meeting IDs are UUIDs - the list shows first 8 chars
- Transcripts include speaker names and timestamps
- Summaries are AI-generated with key points + action items
- Search is keyword-based across transcript text

## Config

API key stored in: `~/.config/meetgeek/config.json`
