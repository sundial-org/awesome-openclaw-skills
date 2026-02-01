---
name: ms-outlook-teams-assistant
description: "Track and nag about Microsoft Outlook email and (optionally) Microsoft Teams messages on a Windows machine, without relying on web versions. Use when the user asks to: (1) monitor inbox/mentions and remind them on Telegram/Teams until dismissed, (2) draft short, personable, low-jargon email replies from an existing Outlook thread, (3) surface action items from the last N days (default 7). Works via Outlook Desktop automation (COM) and optionally Microsoft Graph for Teams if configured."
---

# MS Outlook + Teams Assistant (Desktop-first)

## What this skill does

- **Inbox nagging (Outlook Desktop)**: find messages from the last 7 days that likely need a reply, then send reminders until dismissed.
- **Email reply drafting**: produce concise drafts that match the user’s tone rules (conversational, spartan, polite; simple English; short; reduce redundancy; avoid em dashes).
- **Teams tracking (optional)**: if Microsoft Graph is configured and permitted by tenant policy, track recent Teams chat messages that likely need a reply and nag similarly.

## Safety defaults

- Do **not** auto-send emails or Teams messages.
- Create **drafts** in Outlook, or paste drafts into Telegram for approval.
- For reminders: send to **Telegram** by default; only send to Teams if explicitly enabled.

## Setup (one time)

### A) Outlook Desktop automation (recommended)

1. Ensure Outlook Desktop is installed and signed in.
2. Install the Python dependency (ask before doing this on the machine):
   - `pip install pywin32`
3. Create a config file:
   - Copy `references/config.example.json` → `references/config.json` and fill it.
   - IMPORTANT: Do not commit `references/config.json` if it contains personal IDs.

### B) Teams via Graph (optional)

Only if you can create an Entra ID app registration and grant permissions.

- Copy `references/config.example.json` → `references/config.json` and fill `teams.tenantId`, `teams.clientId`, and `teams.scopes`.
- Then run `scripts/teams_scan.py` once to complete Device Code sign-in.

See `references/teams-graph-setup.md`.

## Core workflows

### 1) Scan and remind (Outlook)

Use `scripts/scan_outlook.py`.

### 1b) Scan Teams (Graph)

Use `scripts/teams_scan.py`.

Parameters:
- `--days 7` (default)

First run will print a **device code** sign-in message (follow it once).

Parameters:
- `--days 7` (default)
- `--mode report|telegram` (default: report)
- `--max-items 200`

Heuristics (editable in config):
- Within last N days
- Not from obvious broadcast sources
- Prefer threads where user is **To:** (not only CC) OR subject/body contains direct asks
- Prefer messages not replied by user (best-effort)

Output:
- A list of actionable items with: subject, sender, received time, why it was flagged.

Then:
- If `--mode telegram`, send a single concise reminder message with bullet items.

### 2) Dismiss / snooze an item

This skill uses a local state file to avoid nag loops.

- Dismiss: add the message’s `internetMessageId` (or subject+timestamp fallback) to the dismissed list.
- Snooze: store a `snoozeUntil` timestamp.

Use `scripts/state.py` helpers (or edit JSON directly if needed).

### 3) Draft an email reply (Outlook)

Use `scripts/draft_reply.py`.

### 4) Generate reminders (no send)

Use `scripts/scan_all.py` to update cached scan results, then `scripts/remind.py` to generate a Telegram-ready reminder message (it does not send).
It applies:
- 1:1 Teams → remind when `needsReply=true`
- Group Teams → remind when `mentionedMe=true` AND `needsReply=true`
- Outlook → remind for flagged items

The agent should send the output to Telegram if non-empty.

Inputs:
- Either a message `EntryID` (preferred) or search by subject + recent window.

Behavior:
- Extract the thread (best-effort) + key metadata.
- Generate 2 drafts:
  - **Short** (2–5 sentences)
  - **Normal** (5–10 sentences)
- Apply tone rules from `references/writing-style.md`.

Outputs:
- Print drafts to stdout.
- Optionally create an Outlook **draft reply** (no sending) if `--create-draft` is set.

## When you need more context from the user

Ask only what you cannot infer:
- Which email to reply to (subject / sender / when)
- The user’s intent (agree/decline/ask for info/confirm timeline)
- Any constraints (deadlines, attachments, names)

Keep questions minimal (max 3 at a time).
