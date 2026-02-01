---
name: mog
description: Microsoft Ops Gadget — CLI for Microsoft 365 (Mail, Calendar, Drive, Contacts, Tasks, Word, PowerPoint, Excel, OneNote).
---

# mog — Microsoft Ops Gadget

CLI for Microsoft 365: Mail, Calendar, OneDrive, Contacts, Tasks, Word, PowerPoint, Excel, OneNote.

The Microsoft counterpart to `gog` (Google Ops Gadget). Same patterns, different cloud.

## Quick Reference

For comprehensive usage, run:
```bash
mog --ai-help
```

This outputs the full dashdash-compliant documentation including:
- Setup/Prerequisites
- All commands and options
- Date/time formats
- Examples (positive and negative)
- Troubleshooting
- Slug system explanation
- gog compatibility notes

## Modules

| Module | Commands |
|--------|----------|
| **mail** | search, get, send, folders, drafts, attachment |
| **calendar** | list, create, get, update, delete, calendars, respond, freebusy, acl |
| **drive** | ls, search, download, upload, mkdir, move, rename, copy, rm |
| **contacts** | list, search, get, create, update, delete, directory |
| **tasks** | lists, list, add, done, undo, delete, clear |
| **word** | list, export, copy |
| **ppt** | list, export, copy |
| **excel** | list, get, update, append, create, metadata, tables, add-sheet, clear, copy, export |
| **onenote** | notebooks, sections, pages, get, create-notebook, create-section, create-page, delete, search |

## Quick Start

```bash
# Mail
mog mail search "from:someone" --max 10
mog mail send --to a@b.com --subject "Hi" --body "Hello"
mog mail send --to a@b.com --subject "Report" --body-file report.md
mog mail send --to a@b.com --subject "Newsletter" --body-html "<h1>Hello</h1>"
cat draft.txt | mog mail send --to a@b.com --subject "Hi" --body-file -

# Calendar
mog calendar list
mog calendar create --summary "Meeting" --from 2025-01-15T10:00:00 --to 2025-01-15T11:00:00
mog calendar freebusy alice@example.com bob@example.com

# Drive
mog drive ls
mog drive upload ./file.pdf
mog drive download <slug> --out ./file.pdf

# Tasks
mog tasks list
mog tasks add "Buy milk" --due tomorrow
mog tasks clear

# Contacts
mog contacts list
mog contacts directory "john"

# Excel
mog excel list
mog excel get <id> Sheet1 A1:D10
mog excel update <id> Sheet1 A1:B2 val1 val2 val3 val4
mog excel append <id> TableName col1 col2 col3

# OneNote
mog onenote notebooks
mog onenote search "meeting notes"
```

## Slugs

mog generates 8-character slugs for Microsoft's long GUIDs:
- `a3f2c891` instead of `AQMkADAwATMzAGZmAS04MDViLTRiNzgt...`
- All commands accept slugs or full IDs
- Use `--verbose` to see full IDs

## Aliases

- `mog cal` → `mog calendar`
- `mog todo` → `mog tasks`

## Credential Storage

OAuth tokens stored in config directory (0600 permissions):

| Platform | Location |
|----------|----------|
| **macOS** | `~/.config/mog/` |
| **Linux** | `~/.config/mog/` |
| **Windows** | `%USERPROFILE%\.config\mog\` |

Files:
- `tokens.json` - OAuth tokens (encrypted at rest by OS)
- `settings.json` - Client ID
- `slugs.json` - Slug cache

## See Also

- `mog --ai-help` - Full documentation
- `mog <command> --help` - Command-specific help
