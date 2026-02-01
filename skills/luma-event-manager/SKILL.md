---
name: luma
description: Luma Event Manager for Clawdbot — Discover events by topic or location, RSVP, view guest lists, and sync to Google Calendar. No API key required (web scraping), no Luma Plus subscription needed. Repo: github.com/mariovallereyes/luma-skill
homepage: https://github.com/mariovallereyes/luma-skill
metadata: {"clawdbot":{"emoji":"📅","requires":{"bins":["pass"]},"install":[{"id":"npm","kind":"shell","command":"cd skills/luma && npm install","label":"Install dependencies"}]}}
---

# Luma Event Manager

Manage Luma events as both **host** and **attendee** via web scraping (no API key required).

## Features

### Public (No Auth)
- Discover events near any location
- View event details
- Geographic filtering

### Authenticated (With Cookies)
- View your RSVP'd events
- View events you're hosting
- Access guest lists
- RSVP to events
- Sync events to Google Calendar (via `gog` CLI)

## Triggers

### Discover Events (Public)
- "luma search AI" — Find events by topic/theme
- "luma search startup near San Francisco" — Topic + location
- "luma events near San Francisco"
- "luma events near Belmont this weekend"
- "luma event ai-meetup-sf"

### Host Mode (Auth Required)
- "luma host events" — List your hosted events
- "luma host guests <slug>" — View guest list

### Attendee Mode (Auth Required)
- "luma my events" — Your RSVP'd events
- "luma rsvp <slug> <response>" — RSVP yes/no/maybe/waitlist

### Utility
- "luma configure" — Set up authentication
- "luma status" — Check connection
- "luma help" — Show help
- "luma add calendar <slug>" — Add event to Google Calendar

## Setup

### Basic (Public Events Only)
No setup required. Just use discover commands.

### Full Access (Your Events + Guest Lists)

1. Log into lu.ma in your browser
2. Open DevTools (F12) → Application → Cookies → lu.ma
3. Copy cookie values: `luma_session`, `luma_user_id`
4. Store in pass:
```bash
pass insert luma/cookies
# Enter: {"luma_session": "value", "luma_user_id": "value"}
```

### Calendar Sync (Optional)
Requires the `gog` CLI with an authorized Google account.

```bash
gog auth add you@example.com
```

Then:
```
"luma add calendar <slug>"
"luma add calendar <slug> --account you@example.com"
"luma add calendar <slug> --calendar_id primary"
```

## Examples

```
"Events near me this weekend"
"What's the AI meetup about?"
"luma event startup-pitch-night"
"Show my upcoming events"
```

## Notes
- Uses web scraping (no paid Luma Plus required)
- Exponential backoff with a 1 req/sec floor to respect lu.ma
- Fallback selectors + Next.js JSON parsing with warnings when selectors fail
- Cookie auth for private data
- Public events always accessible
