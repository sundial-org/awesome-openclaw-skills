---
name: todoist
description: Use the td (Todoist CLI) to read and manage Todoist todos/to-dos/tasks from the terminal. Trigger when the user asks about their todos/tasks/agenda/checklist (today/upcoming/overdue), wants to list inbox/tasks/projects/labels, add a task/todo with natural language, or update/complete/delete/move tasks (e.g., add a phone number to a task description, change due dates, priorities, labels).
---

# Todoist via `td` CLI

## Install / verify

Repo: https://github.com/Doist/todoist-cli

If `td` is not installed (e.g., `command not found: td`), install from the repo:

```bash
git clone https://github.com/Doist/todoist-cli
cd todoist-cli
npm install
npm run build
npm link
```

Then verify:

```bash
td --help
```

Use `td` for all Todoist operations. Prefer parseable output:

- Use `--json` (or `--ndjson`) for listing/reading tasks.
- Use `td task update ...` for edits (content, due, description, priority, labels, etc.).

## Quick agenda

- Today + overdue:
  - `td today --json`
- Next N days:
  - `td upcoming 7 --json`
- Inbox:
  - `td inbox --json`

When summarizing an agenda for the user:
- Separate **Overdue** vs **Due today** (and optionally **Upcoming**).
- Include priority (p1–p4) if present and any labels.

## Find the right task to edit

Preferred approaches:

1) If you already have the task id, use it directly:
- Reference format: `id:<taskId>` (e.g., `id:6WcqCcR4wF7XW5m6`)

2) If you only have a title/snippet, search/list then match:
- `td task list --json` (optionally filter via other list commands like `today`, `upcoming`, `inbox`)
- Then pick the correct item by `content` + due date + project.

To view a single task:
- `td task view <ref> --json`

## Common edits

Update description (notes):
- `td task update <ref> --description "..."`

Update title/content:
- `td task update <ref> --content "New task title"`

Change due date/time (natural language often works):
- `td task update <ref> --due "tomorrow 3pm"`

Priority:
- `td task update <ref> --priority p1` (or p2/p3/p4)

Labels (replaces existing labels):
- `td task update <ref> --labels "Chores,Calls"`

Complete / reopen:
- `td task complete <ref>`
- `td task uncomplete id:<taskId>`

Delete:
- `td task delete <ref> --yes` (only if the user explicitly wants deletion)

## Add tasks

Fast natural-language add:
- `td add "Call dentist tomorrow 10am p2 #Personal"`

Or explicit add (when you need structured fields):
- `td task add --content "..." --due "..." --priority p2 --labels "..."`

## Safety / UX

- Confirm before destructive actions (delete).
- If multiple tasks match the user’s description, ask a clarifying question (or show candidates) before updating.
- When the user asks to add info (e.g., a phone number), put it in the **description** unless they explicitly want it in the title.
