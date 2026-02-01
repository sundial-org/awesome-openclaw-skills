---
name: apple-mail-search
description: Fast Apple Mail search via SQLite on macOS. Search emails by subject, sender, date, attachments - results in ~50ms vs 8+ minutes with AppleScript. Use when asked to find, search, or list emails.
homepage: https://github.com/steipete/clawdbot
metadata: {"clawdbot":{"emoji":"📬","os":["darwin"],"requires":{"bins":["sqlite3"]}}}
---

# Apple Mail Search

Search Apple Mail.app emails instantly via SQLite. ~50ms vs 8+ minutes with AppleScript.

## Installation

```bash
# Copy mail-search to your PATH
cp mail-search /usr/local/bin/
chmod +x /usr/local/bin/mail-search
```

## Usage

```bash
mail-search subject "invoice"           # Search subjects
mail-search sender "@amazon.com"        # Search by sender email
mail-search from-name "John"            # Search by sender name
mail-search to "recipient@example.com"  # Search sent mail
mail-search unread                      # List unread emails
mail-search attachments                 # List emails with attachments
mail-search attachment-type pdf         # Find PDFs
mail-search recent 7                    # Last 7 days
mail-search date-range 2025-01-01 2025-01-31
mail-search open 12345                  # Open email by ID
mail-search stats                       # Database statistics
```

## Options

```
-n, --limit N    Max results (default: 20)
-j, --json       Output as JSON
-c, --csv        Output as CSV
-q, --quiet      No headers
--db PATH        Override database path
```

## Examples

```bash
# Find bank statements from last month
mail-search subject "statement" -n 50

# Get unread emails as JSON for processing
mail-search unread --json | jq '.[] | .subject'

# Find all PDFs from a specific sender
mail-search sender "@bankofamerica.com" -n 100 | grep -i statement

# Export recent emails to CSV
mail-search recent 30 --csv > recent_emails.csv
```

## Why This Exists

| Method | Time for 130k emails |
|--------|---------------------|
| AppleScript iteration | 8+ minutes |
| Spotlight/mdfind | **Broken since Big Sur** |
| SQLite (this tool) | ~50ms |

Apple removed the emlx Spotlight importer in macOS Big Sur. This tool queries the `Envelope Index` SQLite database directly.

## Technical Details

**Database:** `~/Library/Mail/V{9,10,11}/MailData/Envelope Index`

**Key tables:**
- `messages` - Email metadata (dates, flags, FKs)
- `subjects` - Subject lines
- `addresses` - Email addresses and display names
- `recipients` - TO/CC mappings
- `attachments` - Attachment filenames

**Limitations:**
- Read-only (cannot compose/send)
- Metadata only (bodies in .emlx files)
- Mail.app only (not Outlook, etc.)

## Advanced: Raw SQL

For custom queries, use sqlite3 directly:

```bash
sqlite3 -header -column ~/Library/Mail/V10/MailData/Envelope\ Index "
SELECT m.ROWID, s.subject, a.address
FROM messages m
JOIN subjects s ON m.subject = s.ROWID
LEFT JOIN addresses a ON m.sender = a.ROWID
WHERE s.subject LIKE '%your query%'
ORDER BY m.date_sent DESC
LIMIT 20;
"
```

## License

MIT
