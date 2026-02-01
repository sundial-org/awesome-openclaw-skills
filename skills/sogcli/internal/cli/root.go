// Package cli defines the command-line interface for sog.
package cli

import (
	"fmt"
	"os"
)

// Root is the top-level CLI structure.
type Root struct {
	// Global flags (matching gog patterns)
	AIHelp  bool        `name:"ai-help" help:"Show detailed help for AI/LLM agents"`
	Account string      `help:"Account email to use" env:"SOG_ACCOUNT" short:"a"`
	JSON    bool        `help:"Output JSON to stdout (best for scripting)" xor:"format"`
	Plain   bool        `help:"Output stable, parseable text to stdout (TSV; no colors)" xor:"format"`
	Color   string      `help:"Color output: auto|always|never" default:"auto" enum:"auto,always,never"`
	Force   bool        `help:"Skip confirmations for destructive commands"`
	NoInput bool        `help:"Never prompt; fail instead (useful for CI)" name:"no-input"`
	Verbose bool        `help:"Enable verbose logging" short:"v"`
	Version VersionFlag `name:"version" help:"Print version and exit"`

	// Subcommands
	Auth     AuthCmd     `cmd:"" help:"Manage accounts"`
	Mail     MailCmd     `cmd:"" aliases:"m" help:"Read and send mail"`
	Cal      CalCmd      `cmd:"" aliases:"c" help:"Calendar operations (CalDAV)"`
	Contacts ContactsCmd `cmd:"" aliases:"con" help:"Contact operations (CardDAV)"`
	Tasks    TasksCmd    `cmd:"" aliases:"t" help:"Task operations (CalDAV VTODO)"`
	Drive    DriveCmd    `cmd:"" aliases:"files" help:"File operations (WebDAV)"`
	Invite   InviteCmd   `cmd:"" aliases:"inv" help:"Meeting invitations (iTIP/iMIP)"`
	Folders  FoldersCmd  `cmd:"" aliases:"f" help:"Manage folders"`
	Drafts   DraftsCmd   `cmd:"" aliases:"d" help:"Manage drafts"`
	Idle     IdleCmd     `cmd:"" help:"Watch for new mail (IMAP IDLE)"`
}

// VersionFlag handles --version.
type VersionFlag string

// BeforeApply prints version and exits.
func (v VersionFlag) BeforeApply() error {
	fmt.Println(v)
	os.Exit(0)
	return nil
}

// AIHelpText contains the detailed help for AI/LLM agents.
var AIHelpText = `# sog — Standards Ops Gadget

CLI for IMAP/SMTP/CalDAV/CardDAV/WebDAV.
Open-standards alternative to gog (Google) and mog (Microsoft).

## Quick Start

sog auth add you@fastmail.com --discover
sog auth test
sog mail list

## Global Flags

--account, -a    Account email to use ($SOG_ACCOUNT)
--json           JSON output (for scripting)
--plain          TSV output (parseable)
--force          Skip confirmations
--no-input       Never prompt (CI mode)
--verbose, -v    Debug logging
--ai-help        This help text

## Authentication

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

sog auth list                    List accounts
sog auth test [email]            Test connection
sog auth remove <email>          Remove account
sog auth password <email>        Set protocol-specific passwords
  --imap, --smtp, --caldav, --carddav, --webdav

## Mail (IMAP/SMTP)

sog mail list [folder]
  --max N          Maximum messages (default: 20)
  --unseen         Only unread messages

sog mail get <uid>
  --headers        Headers only
  --raw            Raw RFC822 format

sog mail search <query>
  IMAP SEARCH syntax: FROM, TO, SUBJECT, SINCE, BEFORE, etc.
  Example: sog mail search "FROM john SINCE 1-Jan-2026"

sog mail send --to <email> --subject <text> [flags]
  --to             Recipient(s)
  --cc             CC recipient(s)
  --bcc            BCC recipient(s)
  --subject        Subject line
  --body           Message body
  --body-file      Read body from file (- for stdin)

sog mail reply <uid> --body <text>
sog mail forward <uid> --to <email>
sog mail move <uid> <folder>
sog mail copy <uid> <folder>
sog mail flag <uid> <flag>       Flags: seen, flagged, answered, deleted
sog mail unflag <uid> <flag>
sog mail delete <uid>

## Folders

sog folders list
sog folders create <name>
sog folders delete <name>
sog folders rename <old> <new>

## Drafts

sog drafts list
sog drafts create [flags]        Same flags as mail send
sog drafts send <uid>
sog drafts delete <uid>

## Calendar (CalDAV)

sog cal list [calendar]
  --from           Start date (default: today)
  --to             End date (default: +30d)
  --max            Maximum events

sog cal get <uid>
sog cal search <query>           Search in title/description/location
sog cal today [calendar]
sog cal week [calendar]

sog cal create <title> --start <datetime> [flags]
  --start          Start time (YYYY-MM-DDTHH:MM or YYYY-MM-DD for all-day)
  --end            End time
  --duration       Duration (1h, 30m)
  --location       Location
  --description    Description

sog cal update <uid> [flags]     Same flags as create
sog cal delete <uid>
sog cal calendars                List calendars

## Contacts (CardDAV)

sog contacts list [address-book]
  --max            Maximum contacts

sog contacts get <uid>
sog contacts search <query>      Search name/email/phone

sog contacts create <name> [flags]
  -e, --email      Email address(es)
  -p, --phone      Phone number(s)
  --org            Organization
  --title          Job title
  --note           Note

sog contacts update <uid> [flags]  Same flags as create
sog contacts delete <uid>
sog contacts books               List address books

## Tasks (CalDAV VTODO)

sog tasks list [list]
  --all            Include completed tasks

sog tasks add <title> [flags]
  --due            Due date (YYYY-MM-DD)
  -p, --priority   Priority (1-9, 1=highest)
  -d, --description Description

sog tasks get <uid>
sog tasks update <uid> [flags]   Same flags as add
sog tasks done <uid>             Mark complete
sog tasks undo <uid>             Mark incomplete
sog tasks delete <uid>
sog tasks clear                  Delete all completed tasks
sog tasks due <date>             Tasks due by date
sog tasks overdue                Overdue tasks
sog tasks lists                  List task lists

## Files (WebDAV)

sog drive ls [path]
  -l               Long format with details
  --all            Show hidden files

sog drive get <path>             Get file metadata
sog drive download <remote> [local]
sog drive upload <local> [remote]
sog drive mkdir <path>
sog drive delete <path>
sog drive move <src> <dst>
sog drive copy <src> <dst>
sog drive cat <path>             Output file to stdout

## Meeting Invites (iTIP/iMIP)

sog invite send <summary> <attendees>... --start <datetime> [flags]
  --start          Start time
  --duration       Duration (default: 1h)
  --location       Location
  --description    Description

sog invite reply <file> --status <accept|decline|tentative>
  --comment        Optional comment

sog invite cancel <uid> <attendees>...
sog invite parse <file>          Parse .ics file
sog invite preview <summary> <attendees>... --start <datetime>

## IMAP IDLE

sog idle [folder]                Watch for new mail (push notifications)
  --timeout        Timeout in seconds

## Output Formats

Default: Human-readable colored output
--json:  One JSON object per line (JSONL)
--plain: Tab-separated values (TSV)

## Environment Variables

SOG_ACCOUNT      Default account email

## Examples

# List recent emails
sog mail list --max 10

# Send an email
sog mail send --to user@example.com --subject "Hello" --body "Hi there"

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
`
