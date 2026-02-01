---
name: craft
description: Manage Craft notes, documents, and tasks via CLI. Use when the user asks to add notes, create documents, manage tasks, search their Craft documents, or work with daily notes. Craft is a note-taking app for macOS/iOS.
metadata: {"clawdbot":{"install":[{"id":"craft-cli","kind":"script","path":"scripts/craft","dest":"~/bin/craft","label":"Install Craft CLI"}]}}
---

# Craft CLI

Interact with Craft.do documents, blocks, and tasks.

## Setup

1. Install: Copy `scripts/craft` to `~/bin/craft` and make executable
2. Get API URL from Craft: Settings > Integrations > Craft Connect > Create Link
3. Set env var: `export CRAFT_API_URL='https://connect.craft.do/links/YOUR_LINK/api/v1'`

Add to shell profile for persistence.

## Commands

### Documents

```bash
craft folders                    # List all folders
craft docs [location]            # List documents (unsorted, trash, templates, daily_notes)
craft doc <id>                   # Get document content by ID
craft daily [date]               # Get daily note (today, yesterday, YYYY-MM-DD)
craft search <term>              # Search across documents
craft create-doc "Title" [folderId]  # Create new document
```

### Blocks

```bash
craft add-block <docId> "markdown"      # Add block to document
craft add-to-daily "markdown" [date]    # Add to daily note (default: today)
craft update-block <blockId> "markdown" # Update existing block
craft delete-block <blockId>...         # Delete block(s)
```

### Tasks

```bash
craft tasks [scope]              # List tasks (inbox, active, upcoming, logbook)
craft add-task "text" [scheduleDate]  # Add task to inbox
craft complete-task <id>         # Mark task as done
craft delete-task <id>           # Delete task
```

### Collections

```bash
craft collections                # List all collections
craft collection-items <id>      # Get items from collection
```

## Notes

- Markdown content passed as arguments; escape quotes if needed
- Dates: `today`, `yesterday`, or `YYYY-MM-DD`
- Task scopes: `inbox` (default), `active`, `upcoming`, `logbook`
- Document locations: `unsorted`, `trash`, `templates`, `daily_notes`
