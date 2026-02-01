---
name: apple-mail
description: Apple Mail.app integration for macOS. Read inbox, search emails, send emails, reply, and manage messages with fast direct access (no enumeration).
metadata: {"clawdbot":{"emoji":"📧","os":["darwin"],"requires":{"bins":["sqlite3"]}}}
---

# Apple Mail

Interact with Mail.app via AppleScript and SQLite. Run scripts from: `cd {baseDir}`

## Commands

| Command | Usage |
|---------|-------|
| **Refresh** | `scripts/mail-refresh.sh [account] [wait_seconds]` |
| List recent | `scripts/mail-list.sh [mailbox] [account] [limit]` |
| Search | `scripts/mail-search.sh "query" [mailbox] [limit]` |
| Fast search | `scripts/mail-fast-search.sh "query" [limit]` |
| Read email | `scripts/mail-read.sh <message-id> [message-id...]` |
| Delete | `scripts/mail-delete.sh <message-id> [message-id...]` |
| Mark read | `scripts/mail-mark-read.sh <message-id> [message-id...]` |
| Mark unread | `scripts/mail-mark-unread.sh <message-id> [message-id...]` |
| Send | `scripts/mail-send.sh "to@email.com" "Subject" "Body" [from-account] [attachment]` ¹ |
| Reply | `scripts/mail-reply.sh <message-id> "body" [reply-all]` |
| List accounts | `scripts/mail-accounts.sh` |
| List mailboxes | `scripts/mail-mailboxes.sh [account]` |

## Refreshing Mail

Force Mail.app to check for new messages:

```bash
scripts/mail-refresh.sh                    # All accounts, wait up to 10s
scripts/mail-refresh.sh Google             # Specific account only
scripts/mail-refresh.sh "" 5               # All accounts, max 5 seconds
scripts/mail-refresh.sh Google 0           # Google account, no wait
```

**Smart sync detection:**
- Script monitors database message count
- Returns early when sync completes (no changes for 2s)
- Reports new message count: `Sync complete in 2s (+3 messages)`

**Notes:**
- Mail.app must be running (script will error if not)
- `mail-list.sh` does NOT auto-refresh — call `mail-refresh.sh` first if you need fresh data

## Output Format

List/search returns: `ID | ReadStatus | Date | Sender | Subject`
- `●` = unread, blank = read

## Gmail Mailboxes

⚠️ Gmail special folders need `[Gmail]/` prefix:

| Shows as | Use |
|----------|-----|
| `Spam` | `[Gmail]/Spam` |
| `Sent Mail` | `[Gmail]/Sent Mail` |
| `All Mail` | `[Gmail]/All Mail` |
| `Trash` | `[Gmail]/Trash` |

Custom labels work without prefix.

## Fast Search (SQLite)

✨ **Now safe even if Mail.app is running** — copies database to temp file first.

```bash
scripts/mail-fast-search.sh "query" [limit]  # ~50ms vs minutes
```

Previously required Mail.app to be quit. Now works anytime by copying the database to a temp file before querying.

## Performance Notes

**Speed by operation:**
| Operation | Speed | Notes |
|-----------|-------|-------|
| `mail-fast-search.sh` | ~50ms | SQLite query, fastest |
| `mail-accounts.sh` | <1s | Simple AppleScript |
| `mail-list.sh` | 1-3s | AppleScript, direct mailbox access |
| `mail-send.sh` | 1-2s | Creates and sends message |
| `mail-read.sh` | ~2s | Position-optimized lookup |
| `mail-delete.sh` | ~0.5s | Position-optimized lookup |
| `mail-mark-*.sh` | ~1.5s | Position-optimized lookup |

**Optimization technique:**
SQLite provides account UUID and approximate message position. AppleScript jumps directly to that position instead of iterating from the start.

**Batch operations supported:**
- `mail-read.sh 123 456 789` - Read multiple (separator between each)
- `mail-delete.sh 123 456 789` - Delete multiple
- `mail-mark-read.sh 123 456` - Mark multiple as read
- `mail-mark-unread.sh 123 456` - Mark multiple as unread

**⚠️ No auto-refresh:** Scripts read cached data. Call `mail-refresh.sh` first if you need latest emails.

## Managing Emails

**Delete emails:**
```bash
scripts/mail-delete.sh 12345                    # Delete one
scripts/mail-delete.sh 12345 12346 12347        # Delete multiple
```

**Mark as read/unread:**
```bash
scripts/mail-mark-read.sh 12345 12346           # Mark as read
scripts/mail-mark-unread.sh 12345               # Mark as unread
```

**Bulk operations example:**
```bash
# Find spam emails
scripts/mail-fast-search.sh "spam" 50 > spam.txt

# Extract IDs and delete them
grep "^[0-9]" spam.txt | cut -d'|' -f1 | xargs scripts/mail-delete.sh
```

## Reading Email Bodies

```bash
scripts/mail-read.sh 12345              # Single email
scripts/mail-read.sh 12345 12346 12347  # Multiple emails (separated output)
```

Uses position-optimized lookup (~2s per message). Multiple emails are separated by `========` with a summary at the end.

## Errors

| Error | Cause |
|-------|-------|
| `Mail.app is not running` | Open Mail.app before running scripts |
| `Account not found` | Invalid account — check mail-accounts.sh |
| `Message not found` | Invalid/deleted ID — get fresh from mail-list.sh |
| `Can't get mailbox` | Invalid name — check mail-mailboxes.sh |
| `Mail database not found` | SQLite DB missing — check ~/Library/Mail/V{9,10,11}/MailData/ |

## Technical Details

**Database:** `~/Library/Mail/V{9,10,11}/MailData/Envelope Index`

**Message lookup method (optimized):**
1. Query SQLite for account UUID, mailbox path, and approximate position
2. AppleScript accesses the specific account directly (no iteration)
3. Search starts at the approximate position (±5 messages buffer)
4. Falls back to full mailbox search only if position hint fails

**Safety:**
- Fast search copies database to temp file before querying
- Safe to use even if Mail.app is running
- Delete/read/mark operations query live database but access is minimal

## Notes

- Message IDs are internal, get fresh ones from list/search
- Confirm recipient before sending
- AppleScript search is slow but comprehensive; SQLite is fast for metadata
- Delete/mark operations support bulk actions (pass multiple IDs)
- Always refresh before listing if you need the absolute latest emails

¹ **Known limitation:** Mail.app adds a leading blank line to sent emails. This is an AppleScript/Mail.app behavior that cannot be bypassed.
