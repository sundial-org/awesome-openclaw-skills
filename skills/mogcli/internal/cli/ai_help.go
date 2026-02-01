package cli

// AIHelpText contains detailed help for AI/LLM agents.
var AIHelpText = `# mog — Microsoft Ops Gadget

CLI for Microsoft 365 — Mail, Calendar, Drive, Contacts, Tasks, OneNote.

## Quick Start

mog auth login --client-id YOUR_AZURE_CLIENT_ID
mog auth status
mog mail search "*" --max 10

## Global Flags

--json           JSON output (for scripting)
--plain          Plain text output (TSV)
--verbose, -v    Show full IDs
--force          Skip confirmations
--no-input       Never prompt (CI mode)
--ai-help        This help text

## Authentication

mog auth login --client-id <id>    # Device code flow
mog auth status                     # Check auth status
mog auth logout                     # Clear tokens

Required Azure AD permissions (delegated):
- User.Read, offline_access
- Mail.ReadWrite, Mail.Send
- Calendars.ReadWrite
- Files.ReadWrite.All
- Contacts.ReadWrite
- Tasks.ReadWrite
- Notes.ReadWrite

## Mail

mog mail search <query>              # Search messages (* for all)
  --max N                            # Maximum results (default: 25)
  --folder <id>                      # Search in specific folder

mog mail get <id>                    # Get message by ID

mog mail send [flags]
  --to <email>                       # Recipient(s) (required)
  --cc <email>                       # CC recipient(s)
  --bcc <email>                      # BCC recipient(s)
  --subject <text>                   # Subject (required)
  --body <text>                      # Body text
  --body-file <path>                 # Read body from file (- for stdin)
  --body-html <html>                 # HTML body

mog mail folders                     # List mail folders

mog mail drafts list
mog mail drafts create [flags]       # Same flags as send
mog mail drafts send <draftId>
mog mail drafts delete <draftId>

mog mail attachment list <messageId>
mog mail attachment download <messageId> <attachmentId> --out <path>

## Calendar

mog calendar list                    # List events
  --from <date>                      # Start date (default: today)
  --to <date>                        # End date (default: +30d)
  --max N                            # Maximum events
  --calendar <id>                    # Specific calendar

mog calendar get <eventId>

mog calendar create [flags]
  --summary <text>                   # Event title (required)
  --from <datetime>                  # Start time (required, ISO format)
  --to <datetime>                    # End time (required)
  --location <text>                  # Location
  --body <text>                      # Description
  --attendees <email>                # Attendee emails
  --all-day                          # All-day event
  --calendar <id>                    # Specific calendar

mog calendar update <eventId> [flags]
mog calendar delete <eventId>
mog calendar calendars               # List calendars

mog calendar respond <eventId> <response>
  # response: accept, decline, tentative
  --comment <text>                   # Optional comment

mog calendar freebusy <emails>... --start <datetime> --end <datetime>

Aliases: mog cal → mog calendar

## Drive (OneDrive)

mog drive ls [path]                  # List files
mog drive search <query>             # Search files
mog drive get <id>                   # Get file metadata

mog drive download <id> --out <path>
mog drive upload <path>
  --folder <id>                      # Destination folder
  --name <name>                      # Rename on upload

mog drive mkdir <name>
  --parent <id>                      # Parent folder

mog drive move <id> <destinationId>
mog drive rename <id> <newName>
mog drive copy <id> --name <name>
mog drive rm <id>                    # Delete file

## Contacts

mog contacts list
mog contacts search <query>
mog contacts get <id>

mog contacts create [flags]
  --name <text>                      # Display name (required)
  --email <email>                    # Email address
  --phone <number>                   # Phone number
  --company <text>                   # Company name
  --title <text>                     # Job title

mog contacts update <id> [flags]     # Same flags as create
mog contacts delete <id>
mog contacts directory <query>       # Search org directory

## Tasks (Microsoft To-Do)

mog tasks lists                      # List task lists
mog tasks list [listId]              # List tasks
  --all                              # Include completed

mog tasks add <title>
  --list <id>                        # Task list ID
  --due <date>                       # Due date (YYYY-MM-DD or 'tomorrow')
  --notes <text>                     # Task notes
  --important                        # Mark as important

mog tasks update <taskId> [flags]
  --list <id>                        # Task list ID (required)

mog tasks done <taskId> --list <id>
mog tasks undo <taskId> --list <id>
mog tasks delete <taskId> --list <id>
mog tasks clear [listId]             # Clear completed tasks

Aliases: mog todo → mog tasks

## OneNote

mog onenote notebooks                # List notebooks
mog onenote sections <notebookId>    # List sections
mog onenote pages <sectionId>        # List pages
mog onenote get <pageId>             # Get page content
  --html                             # Output raw HTML
mog onenote search <query>           # Search (limited)

## Excel

mog excel list                       # List workbooks (via drive search)
mog excel metadata <id>              # List worksheets
mog excel get <id> [sheet] [range]   # Read data
mog excel update <id> <sheet> <range> <values>...
mog excel append <id> <table> <values>...
mog excel create <name>
mog excel export <id> --out <path>
mog excel copy <id> <name>

Note: Excel operations limited in Go version. Use drive commands.

## Word

mog word list                        # Via drive search
mog word export <id> --out <path>
mog word copy <id> <name>

Note: Use drive commands for most operations.

## PowerPoint

mog ppt list                         # Via drive search
mog ppt export <id> --out <path>
mog ppt copy <id> <name>

Note: Use drive commands for most operations.

## Slug System

Microsoft Graph uses very long IDs. mog generates 8-character slugs:
- All commands output slugs by default
- All commands accept slugs or full IDs
- Use --verbose to see full IDs
- Slugs cached in ~/.config/mog/slugs.json

## Output Formats

Default: Human-readable colored output
--json:  JSON output for scripting
--plain: Tab-separated values

## Environment Variables

MOG_CLIENT_ID    Azure AD client ID

## Configuration

~/.config/mog/settings.json   Client ID
~/.config/mog/tokens.json     OAuth tokens (sensitive)
~/.config/mog/slugs.json      ID slug cache

## Examples

# Send email
mog mail send --to user@example.com --subject "Hello" --body "Hi!"

# Today's calendar
mog cal list --from today --to tomorrow

# Create meeting
mog cal create --summary "Team Sync" \
  --from "2025-01-15T14:00:00" --to "2025-01-15T15:00:00" \
  --attendees "alice@example.com"

# Add task
mog tasks add "Review PR" --due tomorrow --important

# Upload file
mog drive upload ./report.pdf

# Search contacts
mog contacts search "john"
`
