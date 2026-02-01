---
name: sog
description: Standards Ops Gadget — CLI for IMAP/SMTP/CalDAV/CardDAV/WebDAV. Open-standards alternative to gog (Google) and mog (Microsoft).
homepage: https://github.com/visionik/sogcli
metadata: {"clawdbot":{"emoji":"📬","requires":{"bins":["sog"]},"install":[{"id":"go","kind":"go","package":"github.com/visionik/sogcli/cmd/sog@latest","bins":["sog"],"label":"Install sog (go install)"}]}}
---

# sog — Standards Ops Gadget

CLI for IMAP/SMTP/CalDAV/CardDAV/WebDAV.
Open-standards alternative to gog (Google) and mog (Microsoft).

## Quick Start

```bash
sog auth add you@fastmail.com --discover
sog auth test
sog mail list
```

## Global Flags

```
--account, -a    Account email to use ($SOG_ACCOUNT)
--json           JSON output (for scripting)
--plain          TSV output (parseable)
--force          Skip confirmations
--no-input       Never prompt (CI mode)
--verbose, -v    Debug logging
--ai-help        Detailed help text
```

## Authentication

```bash
sog auth add <email> [flags]
  --discover       Auto-discover servers from DNS
  --imap-host      IMAP server hostname
  --imap-port      IMAP port (default: 993)
  --smtp-host      SMTP server hostname
  --smtp-port      SMTP port (default: 587)
  --caldav-url     CalDAV server URL
  --carddav-url    CardDAV server URL
  --webdav-url     WebDAV server URL
  --password       Password (stored in keychain)

sog auth list                    # List accounts
sog auth test [email]            # Test connection
sog auth remove <email>          # Remove account
sog auth password <email>        # Set protocol-specific passwords
  --imap, --smtp, --caldav, --carddav, --webdav
```

## Mail (IMAP/SMTP)

```bash
sog mail list [folder]
  --max N          Maximum messages (default: 20)
  --unseen         Only unread messages

sog mail get <uid>
  --headers        Headers only
  --raw            Raw RFC822 format

sog mail search <query>
  # IMAP SEARCH syntax: FROM, TO, SUBJECT, SINCE, BEFORE, etc.
  # Example: sog mail search "FROM john SINCE 1-Jan-2026"

sog mail send --to <email> --subject <text> [flags]
  --to             Recipient(s)
  --cc             CC recipient(s)
  --bcc            BCC recipient(s)
  --subject        Subject line
  --body           Message body
  --body-file      Read body from file (- for stdin)
  --body-html      HTML body content

sog mail reply <uid> --body <text>
sog mail forward <uid> --to <email>
sog mail move <uid> <folder>
sog mail copy <uid> <folder>
sog mail flag <uid> <flag>       # Flags: seen, flagged, answered, deleted
sog mail unflag <uid> <flag>
sog mail delete <uid>
```

## Folders

```bash
sog folders list
sog folders create <name>
sog folders delete <name>
sog folders rename <old> <new>
```

## Drafts

```bash
sog drafts list
sog drafts create [flags]        # Same flags as mail send
sog drafts send <uid>
sog drafts delete <uid>
```

## Calendar (CalDAV)

```bash
sog cal list [calendar]
  --from           Start date (default: today)
  --to             End date (default: +30d)
  --max            Maximum events

sog cal get <uid>
sog cal search <query>           # Search in title/description/location
sog cal today [calendar]
sog cal week [calendar]

sog cal create <title> --start <datetime> [flags]
  --start          Start time (YYYY-MM-DDTHH:MM or YYYY-MM-DD for all-day)
  --end            End time
  --duration       Duration (1h, 30m)
  --location       Location
  --description    Description

sog cal update <uid> [flags]     # Same flags as create
sog cal delete <uid>
sog cal calendars                # List calendars
```

## Contacts (CardDAV)

```bash
sog contacts list [address-book]
  --max            Maximum contacts

sog contacts get <uid>
sog contacts search <query>      # Search name/email/phone

sog contacts create <name> [flags]
  -e, --email      Email address(es)
  -p, --phone      Phone number(s)
  --org            Organization
  --title          Job title
  --note           Note

sog contacts update <uid> [flags]  # Same flags as create
sog contacts delete <uid>
sog contacts books               # List address books
```

## Tasks (CalDAV VTODO)

```bash
sog tasks list [list]
  --all            Include completed tasks

sog tasks add <title> [flags]
  --due            Due date (YYYY-MM-DD)
  -p, --priority   Priority (1-9, 1=highest)
  -d, --description Description

sog tasks get <uid>
sog tasks update <uid> [flags]   # Same flags as add
sog tasks done <uid>             # Mark complete
sog tasks undo <uid>             # Mark incomplete
sog tasks delete <uid>
sog tasks clear                  # Delete all completed tasks
sog tasks due <date>             # Tasks due by date
sog tasks overdue                # Overdue tasks
sog tasks lists                  # List task lists
```

## Files (WebDAV)

```bash
sog drive ls [path]
  -l               Long format with details
  --all            Show hidden files

sog drive get <path>             # Get file metadata
sog drive download <remote> [local]
sog drive upload <local> [remote]
sog drive mkdir <path>
sog drive delete <path>
sog drive move <src> <dst>
sog drive copy <src> <dst>
sog drive cat <path>             # Output file to stdout
```

## Meeting Invites (iTIP/iMIP)

```bash
sog invite send <summary> <attendees>... --start <datetime> [flags]
  --start          Start time
  --duration       Duration (default: 1h)
  --location       Location
  --description    Description

sog invite reply <file> --status <accept|decline|tentative>
  --comment        Optional comment

sog invite cancel <uid> <attendees>...
sog invite parse <file>          # Parse .ics file
sog invite preview <summary> <attendees>... --start <datetime>
```

## IMAP IDLE

```bash
sog idle [folder]                # Watch for new mail (push notifications)
  --timeout        Timeout in seconds
```

## Output Formats

- Default: Human-readable colored output
- `--json`: One JSON object per line (JSONL)
- `--plain`: Tab-separated values (TSV)

## Examples

```bash
# List recent emails
sog mail list --max 10

# Send an email
sog mail send --to user@example.com --subject "Hello" --body "Hi there"
sog mail send --to user@example.com --subject "Report" --body-file report.md
cat draft.txt | sog mail send --to user@example.com --subject "Hi" --body-file -

# Today's calendar
sog cal today

# Create a meeting with invite
sog invite send "Team Sync" alice@example.com bob@example.com \
  --start "2026-01-25T14:00" --duration 30m --location "Zoom"

# Add a task
sog tasks add "Review PR" --due 2026-01-26 -p 1

# Upload a file
sog drive upload report.pdf /documents/

# Search contacts
sog contacts search "John"
```

## Tested Providers

- **Fastmail** ✅ (full support)

Other standards-compliant providers should work but have not been tested yet.

## Credential Storage

Passwords are stored securely in the native system credential store:

| Platform | Backend |
|----------|---------|
| **macOS** | Keychain |
| **Windows** | Windows Credential Manager |
| **Linux/BSD** | D-Bus Secret Service (GNOME Keyring, KWallet) |

Supports separate passwords per protocol (IMAP, SMTP, CalDAV, CardDAV, WebDAV).

## Notes

- Set `SOG_ACCOUNT=you@example.com` to avoid repeating `--account`
- Part of the Ops Gadget family: gog (Google), mog (Microsoft), sog (Standards)
