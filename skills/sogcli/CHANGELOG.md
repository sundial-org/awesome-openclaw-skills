# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-01-24

### Changed
- Complete README rewrite to match mog style
- Comprehensive command reference with aliases
- gog/mog compatibility table
- Better organized documentation

### Added
- SKILL.md for Clawdbot integration

## [0.2.0] - 2026-01-24

### Changed

#### CLI Alignment with gog/mog
- `sog drive get` now returns file metadata (was download)
- `sog drive download` for downloading files (was get)
- `sog drive upload` is now primary (put is alias)
- `sog drive ls` is now primary (list is alias)
- `sog drive delete` is now primary (rm, del are aliases)
- `sog drive move` is now primary (mv, rename are aliases)
- `sog drive copy` is now primary (cp is alias)
- `sog tasks undo` is now primary (uncomplete, undone are aliases)
- `sog tasks add` has `create` alias
- `sog tasks done` has `complete` alias
- `sog tasks delete` has `rm`, `del` aliases
- `sog cal list` has `events` alias
- `sog cal get` has `event` alias

#### AI Help
- Changed from subcommand (`sog ai-help`) to flag (`sog --ai-help`)
- `--ai-help` now appears right after `--help` in usage
- Comprehensive documentation for all commands

### Added
- `sog cal search` — Search events by query
- `sog cal update` — Update an event
- `sog contacts update` — Update a contact
- `sog tasks update` — Update a task
- `sog tasks clear` — Clear completed tasks

## [0.1.0] - 2026-01-24

### Added

#### Mail (IMAP/SMTP)
- `sog mail list` — List messages in a folder
- `sog mail get` — Get message by UID
- `sog mail search` — Search messages
- `sog mail send` — Send a message
- `sog mail reply` — Reply to a message
- `sog mail forward` — Forward a message
- `sog mail move` — Move message to folder
- `sog mail copy` — Copy message to folder
- `sog mail flag` — Set message flag
- `sog mail unflag` — Remove message flag
- `sog mail delete` — Delete a message
- `sog folders list/create/delete/rename` — Folder management
- `sog drafts list/create/send/delete` — Draft management
- `sog idle` — Watch for new mail (IMAP IDLE)

#### Calendar (CalDAV)
- `sog cal list` — List events
- `sog cal get` — Get event details
- `sog cal today` — Today's events
- `sog cal week` — This week's events
- `sog cal create` — Create an event
- `sog cal delete` — Delete an event
- `sog cal calendars` — List calendars

#### Contacts (CardDAV)
- `sog contacts list` — List contacts
- `sog contacts get` — Get contact details
- `sog contacts search` — Search contacts
- `sog contacts create` — Create a contact
- `sog contacts delete` — Delete a contact
- `sog contacts books` — List address books

#### Tasks (CalDAV VTODO)
- `sog tasks list` — List tasks
- `sog tasks add` — Add a task
- `sog tasks get` — Get task details
- `sog tasks done` — Mark task complete
- `sog tasks delete` — Delete a task
- `sog tasks due` — Tasks due by date
- `sog tasks overdue` — Overdue tasks
- `sog tasks lists` — List task lists

#### Files (WebDAV)
- `sog drive ls` — List files and folders
- `sog drive get` — Get file metadata
- `sog drive download` — Download a file
- `sog drive upload` — Upload a file
- `sog drive mkdir` — Create a directory
- `sog drive delete` — Delete file or directory
- `sog drive move` — Move/rename file
- `sog drive copy` — Copy file
- `sog drive cat` — Output file contents

#### Meeting Invites (iTIP/iMIP)
- `sog invite send` — Send meeting invitation
- `sog invite reply` — Reply to invitation (accept/decline/tentative)
- `sog invite cancel` — Cancel a meeting
- `sog invite parse` — Parse .ics file
- `sog invite preview` — Preview invite without sending

#### Authentication
- `sog auth add` — Add account with auto-discovery
- `sog auth list` — List configured accounts
- `sog auth test` — Test account connection
- `sog auth remove` — Remove an account
- `sog auth password` — Set protocol-specific passwords
- Secure keychain storage for passwords
- Support for separate passwords per protocol (IMAP, SMTP, CalDAV, CardDAV, WebDAV)

#### Output Formats
- `--json` — JSON output for scripting
- `--plain` — TSV output for parsing
- Colored terminal output (auto-detected)

### Tested Providers
- Fastmail (full support)
- Works with any standards-compliant provider

[0.3.0]: https://github.com/visionik/sogcli/releases/tag/v0.3.0
[0.2.0]: https://github.com/visionik/sogcli/releases/tag/v0.2.0
[0.1.0]: https://github.com/visionik/sogcli/releases/tag/v0.1.0
