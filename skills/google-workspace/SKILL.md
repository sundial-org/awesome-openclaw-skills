---
name: google-workspace
description: Gmail, Calendar, Drive, Docs, Sheets — NO Google Cloud Console required. Just OAuth sign-in. Zero setup complexity vs traditional Google API integrations.
metadata: {"clawdbot":{"emoji":"📬","requires":{"bins":["mcporter"]}}}
---

# Google Workspace Access (No Cloud Console!)

**Why this skill?** Traditional Google API access requires creating a project in Google Cloud Console, enabling APIs, creating OAuth credentials, and downloading client_secret.json. This skill skips ALL of that.

Uses `@presto-ai/google-workspace-mcp` — just sign in with your Google account and go.

## Key Advantage

| Traditional Approach | This Skill |
|---------------------|------------|
| Create Google Cloud Project | ❌ Not needed |
| Enable individual APIs | ❌ Not needed |
| Create OAuth credentials | ❌ Not needed |
| Download client_secret.json | ❌ Not needed |
| Configure redirect URIs | ❌ Not needed |
| **Just sign in with Google** | ✅ That's it |

## Setup (Already Done)

```bash
npm install -g @presto-ai/google-workspace-mcp
mcporter config add google-workspace --command "npx" --arg "-y" --arg "@presto-ai/google-workspace-mcp" --scope home
```

On first use, it opens a browser for Google OAuth. Credentials stored in `~/.config/google-workspace-mcp/`

## Quick Commands

### Gmail

```bash
# Search emails
mcporter call --server google-workspace --tool "gmail.search" query="is:unread" maxResults=10

# Get email content
mcporter call --server google-workspace --tool "gmail.get" messageId="<id>"

# Send email
mcporter call --server google-workspace --tool "gmail.send" to="email@example.com" subject="Hi" body="Hello"

# Create draft
mcporter call --server google-workspace --tool "gmail.createDraft" to="email@example.com" subject="Hi" body="Hello"
```

### Calendar

```bash
# List calendars
mcporter call --server google-workspace --tool "calendar.list"

# List events
mcporter call --server google-workspace --tool "calendar.listEvents" calendarId="your@email.com" timeMin="2026-01-27T00:00:00Z" timeMax="2026-01-27T23:59:59Z"

# Create event
mcporter call --server google-workspace --tool "calendar.createEvent" calendarId="your@email.com" summary="Meeting" start='{"dateTime":"2026-01-28T10:00:00Z"}' end='{"dateTime":"2026-01-28T11:00:00Z"}'

# Find free time
mcporter call --server google-workspace --tool "calendar.findFreeTime" attendees='["a@example.com","b@example.com"]' timeMin="2026-01-28T09:00:00Z" timeMax="2026-01-28T18:00:00Z" duration=30
```

### Drive

```bash
# Search files
mcporter call --server google-workspace --tool "drive.search" query="Budget Q3"

# Download file
mcporter call --server google-workspace --tool "drive.downloadFile" fileId="<id>" localPath="/tmp/file.pdf"
```

### Docs

```bash
# Find docs
mcporter call --server google-workspace --tool "docs.find" query="meeting notes"

# Read doc
mcporter call --server google-workspace --tool "docs.getText" documentId="<id>"

# Create doc
mcporter call --server google-workspace --tool "docs.create" title="New Doc" markdown="# Hello"
```

### Sheets

```bash
# Read spreadsheet
mcporter call --server google-workspace --tool "sheets.getText" spreadsheetId="<id>"

# Get range
mcporter call --server google-workspace --tool "sheets.getRange" spreadsheetId="<id>" range="Sheet1!A1:B10"
```

## Available Tools (49 total)

**Auth:** auth.clear, auth.refreshToken
**Docs:** docs.create, docs.find, docs.getText, docs.insertText, docs.appendText, docs.replaceText, docs.move, docs.extractIdFromUrl
**Drive:** drive.search, drive.downloadFile, drive.findFolder
**Sheets:** sheets.getText, sheets.getRange, sheets.find, sheets.getMetadata
**Slides:** slides.getText, slides.find, slides.getMetadata
**Calendar:** calendar.list, calendar.listEvents, calendar.getEvent, calendar.createEvent, calendar.updateEvent, calendar.deleteEvent, calendar.findFreeTime, calendar.respondToEvent
**Gmail:** gmail.search, gmail.get, gmail.send, gmail.createDraft, gmail.sendDraft, gmail.modify, gmail.listLabels, gmail.downloadAttachment
**Chat:** chat.listSpaces, chat.findSpaceByName, chat.sendMessage, chat.getMessages, chat.sendDm, chat.findDmByEmail, chat.listThreads, chat.setUpSpace
**People:** people.getUserProfile, people.getMe
**Time:** time.getCurrentDate, time.getCurrentTime, time.getTimeZone

## Troubleshooting

### Re-authenticate
```bash
mcporter call --server google-workspace --tool "auth.clear"
```
Then run any command to trigger re-auth.

### Token refresh
```bash
mcporter call --server google-workspace --tool "auth.refreshToken"
```

### Delete credentials
```bash
rm -rf ~/.config/google-workspace-mcp
```
