---
name: notectl
description: Manage Apple Notes via AppleScript CLI
---

# notectl - Apple Notes CLI

Manage Apple Notes from the command line using AppleScript.

## Commands

| Command | Description |
|---------|-------------|
| `notectl folders` | List all folders with note counts |
| `notectl list [folder]` | List notes in a folder (default: Notes) |
| `notectl show <title>` | Show note content by title |
| `notectl add <title>` | Create a new note |
| `notectl search <query>` | Search notes by title or content |
| `notectl append <title>` | Append text to an existing note |

## Examples

```bash
# List all folders
notectl folders

# List notes in default folder
notectl list

# List notes in specific folder
notectl list "rainbat-projects"
notectl list Papi

# Show a note
notectl show "Meeting Notes"

# Create a note
notectl add "New Idea"
notectl add "Project Plan" --folder research --body "Initial thoughts..."

# Search all notes
notectl search "clawdbot"
notectl search "API"

# Append to a note (daily log style)
notectl append "Daily Log" --text "- Completed feature X"
```

## Options for `add`

| Option | Description | Default |
|--------|-------------|---------|
| `-f, --folder <name>` | Folder to create note in | Notes |
| `-b, --body <text>` | Note body content | empty |

## Options for `append`

| Option | Description |
|--------|-------------|
| `-t, --text <text>` | Text to append to the note |

## Available Folders

Folders on this system:
- Notes (default)
- research
- rainbat-projects
- Papi
- renova-roll
- Journal
- CheatSheets
- pet-projects
