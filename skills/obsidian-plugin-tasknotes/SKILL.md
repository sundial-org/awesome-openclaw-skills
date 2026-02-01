---
name: tasknotes
description: Manage tasks in Obsidian via TaskNotes plugin API. Use when user wants to create tasks, list tasks, query by status or project, update task status, delete tasks, or check what they need to do.
---

# TaskNotes Skill

Manage Obsidian tasks via the TaskNotes plugin HTTP API.

## Requirements

1. **TaskNotes plugin** installed in Obsidian
2. **Enable HTTP API** in TaskNotes settings:
   - Open Obsidian Settings → TaskNotes
   - Enable "HTTP API" toggle
   - Set API port (default: 8080)
   - API token: leave empty for no auth, or set a token for security
3. **Environment variables** in `.env` file at vault root (if using auth):
   ```
   TASKNOTES_API_PORT=8080
   TASKNOTES_API_KEY=your_token_here
   ```
   If TaskNotes has no auth token set, you don't need a `.env` file.

## CLI Commands

```bash
# List all tasks
uv run scripts/tasks.py list

# List by status (use your configured status values)
uv run scripts/tasks.py list --status "in-progress"

# List by project
uv run scripts/tasks.py list --project "My Project"

# Create task
uv run scripts/tasks.py create "Task title" --project "My Project" --priority high

# Create task with scheduled time
uv run scripts/tasks.py create "Meeting prep" --scheduled "2025-01-15T14:00:00"

# Update task status
uv run scripts/tasks.py update "Tasks/task-file.md" --status done

# Add/update task description
uv run scripts/tasks.py update "Tasks/task-file.md" --details "Additional context here."

# Delete task
uv run scripts/tasks.py delete "Tasks/task-file.md"

# Get available options (statuses, priorities, projects)
uv run scripts/tasks.py options --table

# Human-readable output (add --table)
uv run scripts/tasks.py list --table
```

## Task Properties

**Status and Priority values:** Configured in your TaskNotes plugin settings. Run `options` command to see available values:
```bash
uv run scripts/tasks.py options --table
```

**Other fields:**
- `projects` - Array of project links, e.g. `["[[Project Name]]"]`
- `contexts` - Array like `["office", "energy-high"]`
- `due` - Due date (YYYY-MM-DD)
- `scheduled` - Scheduled date/time (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- `timeEstimate` - Minutes (number)
- `tags` - Array of tags
- `details` - Task description (writes to markdown body, not frontmatter)

## API Reference

Base URL: `http://localhost:8080/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /tasks | List tasks (supports filters) |
| POST | /tasks | Create task |
| GET | /tasks/{id} | Get single task |
| PUT | /tasks/{id} | Update task |
| DELETE | /tasks/{id} | Delete task |
| GET | /filter-options | Available statuses, priorities, projects |

### Query Parameters for GET /tasks

- `status` - Filter by status
- `project` - Filter by project name
- `priority` - Filter by priority
- `tag` - Filter by tag
- `overdue` - true/false
- `sort` - Sort field
- `limit` - Max results
- `offset` - Pagination offset

## When to Use

- "create a task for X" → create task
- "show my tasks" → list all tasks
- "show in-progress tasks" → list --status in-progress
- "mark X as done" → update task status to done
- "what should I work on" → list tasks by status

## Example Workflow

```bash
# Morning: Check what to work on
uv run scripts/tasks.py list --status in-progress --table
uv run scripts/tasks.py list --limit 5 --table

# Create task linked to project
uv run scripts/tasks.py create "Finish landing page" \
  --project "Website Redesign" \
  --priority high

# Complete a task
uv run scripts/tasks.py update "Tasks/finish-landing-page.md" --status done
```
