---
name: slack-personal
description: Read, send, search, and manage Slack messages via the slk CLI. Use when the user asks to check Slack, read channels, send Slack messages, search Slack, check unreads, manage drafts, view saved items, or interact with Slack workspace. Also use for heartbeat Slack checks. Triggers on "check slack", "any slack messages", "send on slack", "slack unreads", "search slack", "slack threads", "draft on slack".
homepage: https://www.npmjs.com/package/slkcli
metadata: {"moltbot":{"emoji":"💬","requires":{"bins":["slk"]},"install":[{"id":"npm","kind":"node","package":"slkcli","bins":["slk"],"label":"Install slk (npm)"}],"os":["darwin"]}}
---

# slk — Slack CLI

Session-based Slack CLI for macOS. Auto-authenticates from the Slack desktop app — no tokens, no OAuth, no app installs. Acts as your user (`xoxc-` session tokens).

## Commands

```bash
# Auth
slk auth                              # Test authentication, show user/team

# Read
slk channels                          # List channels (alias: ch)
slk read <channel> [count]            # Read recent messages, default 20 (alias: r)
slk thread <channel> <ts> [count]     # Read thread replies, default 50 (alias: t)
slk search <query> [count]            # Search messages across workspace
slk users                             # List workspace users (alias: u)

# Activity
slk activity                          # All channels with unread/mention counts (alias: a)
slk unread                            # Only unreads, excludes muted (alias: ur)
slk starred                           # VIP users + starred items (alias: star)
slk saved [count] [--all]             # Saved for later items (alias: sv)
slk pins <channel>                    # Pinned items in a channel (alias: pin)

# Write
slk send <channel> <message>          # Send a message (alias: s)
slk react <channel> <ts> <emoji>      # React to a message

# Drafts (synced to Slack editor UI)
slk draft <channel> <message>         # Draft a channel message
slk draft thread <ch> <ts> <message>  # Draft a thread reply
slk draft user <user_id> <message>    # Draft a DM
slk drafts                            # List active drafts
slk draft drop <draft_id>             # Delete a draft
```

Channel accepts name (`general`, `ai-coding`) or ID (`C08A8AQ2AFP`).

## Auth

Automatic — extracts session token from Slack desktop app's LevelDB + decrypts cookie from macOS Keychain.

**First run:** macOS will show a Keychain dialog asking to allow access to "Slack Safe Storage":
- **Allow** — one-time access, prompted again next time
- **Always Allow** — permanent, no future prompts (convenient but any process running as your user can extract credentials silently)
- **Deny** — blocks access, slk cannot authenticate

**Token cache:** `~/.local/slk/token-cache.json` — auto-validated, auto-refreshed on `invalid_auth`.

If auth fails (token rotated, Slack logged out):
```bash
rm ~/.local/slk/token-cache.json
slk auth
```

Slack desktop app must be installed and logged in. Does not need to be running if token is cached.

## Reading Threads

Threads require a Slack timestamp. Use `--ts` to get it, then read the thread:

```bash
slk read general 10 --ts
# Output: [1/30/2026, 11:41 AM ts:1769753479.788949] User [3 replies]: ...

slk thread general 1769753479.788949
```

## Agent Workflow Examples

- **Heartbeat/cron unread check** — `slk unread` → `slk read <channel>` for channels that need attention
- **Save & pick up** — Human saves threads in Slack ("Save for later"). Agent runs `slk saved` during heartbeat, reads full threads with `slk thread`, summarizes or extracts action items
- **Daily channel digest** — `slk read <channel> 100` across key channels → compile decisions, open questions, action items → `slk send daily-digest "📋 ..."`
- **Thread monitoring** — Watch specific threads for new replies (incidents, PR reviews, decisions)
- **Draft for human review** — `slk draft <channel> "..."` posts to Slack's editor UI for human to review before sending
- **Search-driven context** — `slk search "deployment process"` or `slk pins <channel>` to pull context before answering questions

## Limitations

- **macOS only** — uses Keychain + Electron storage paths
- **Session-based** — acts as your user, not a bot. Be mindful of what you send
- **Draft drop** may fail with `draft_has_conflict` if Slack has that conversation open
- **Session token** expires on logout — keep Slack app running or rely on cached token

## Missing Features & Issues

Create PR or Report Issue at: https://github.com/therohitdas/slkcli
