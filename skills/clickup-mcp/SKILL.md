---
name: clickup-mcp
description: Manage ClickUp tasks, docs, time tracking, comments, chat, and search via official MCP. OAuth authentication required.
homepage: https://clickup.com
metadata: {"clawdbot":{"emoji":"✅","requires":{"bins":["mcporter"],"env":["CLICKUP_TOKEN"]}}}
---

# ClickUp MCP (Official)

Access ClickUp via the official MCP server. Full workspace search, task management, time tracking, comments, chat, and docs.

## Setup

### Option 1: Direct OAuth (Supported Clients Only)

ClickUp MCP only allows OAuth from **allowlisted clients**:
- Claude Desktop, Claude Code, Cursor, VS Code, Windsurf, ChatGPT

```bash
# Claude Code
claude mcp add clickup --transport http https://mcp.clickup.com/mcp
# Then /mcp in session to authorize
```

### Option 2: Claude Code → mcporter (Recommended)

Use Claude Code to OAuth, then extract token for mcporter:

**Step 1: Authorize via Claude Code**
```bash
claude mcp add clickup --transport http https://mcp.clickup.com/mcp
claude
# In Claude Code, run: /mcp
# Complete OAuth in browser
```

**Step 2: Extract token**
```bash
jq -r '.mcpOAuth | to_entries | .[] | select(.key | startswith("clickup")) | .value.accessToken' ~/.claude/.credentials.json
```

**Step 3: Add to environment**
```bash
# Add to ~/.clawdbot/.env
CLICKUP_TOKEN=eyJhbGciOiJkaXIi...
```

**Step 4: Configure mcporter**

Add to `config/mcporter.json`:
```json
{
  "mcpServers": {
    "clickup": {
      "baseUrl": "https://mcp.clickup.com/mcp",
      "description": "Official ClickUp MCP",
      "headers": {
        "Authorization": "Bearer ${CLICKUP_TOKEN}"
      }
    }
  }
}
```

**Step 5: Test**
```bash
mcporter list clickup
mcporter call 'clickup.clickup_search(keywords: "test", count: 3)'
```

### Token Refresh

Tokens are long-lived (~10 years). If expired:
1. Re-run `/mcp` in Claude Code
2. Re-extract token from `~/.claude/.credentials.json`
3. Update `CLICKUP_TOKEN` in `.env`

## Available Tools (32)

### Search

| Tool | Description |
|------|-------------|
| `clickup_search` | Universal search across tasks, docs, dashboards, chat, files |

### Tasks

| Tool | Description |
|------|-------------|
| `clickup_create_task` | Create task with name, description, status, assignees, due date, priority |
| `clickup_get_task` | Get task details (with optional subtasks) |
| `clickup_update_task` | Update any task field |
| `clickup_attach_task_file` | Attach file to task (URL or base64) |
| `clickup_add_tag_to_task` | Add tag to task |
| `clickup_remove_tag_from_task` | Remove tag from task |

### Comments

| Tool | Description |
|------|-------------|
| `clickup_get_task_comments` | Get all comments on task |
| `clickup_create_task_comment` | Add comment (supports @mentions) |

### Time Tracking

| Tool | Description |
|------|-------------|
| `clickup_start_time_tracking` | Start timer on task |
| `clickup_stop_time_tracking` | Stop active timer |
| `clickup_add_time_entry` | Log time manually |
| `clickup_get_task_time_entries` | Get time entries for task |
| `clickup_get_current_time_entry` | Check active timer |

### Workspace & Hierarchy

| Tool | Description |
|------|-------------|
| `clickup_get_workspace_hierarchy` | Get full structure (Spaces, Folders, Lists) |
| `clickup_create_list` | Create list in Space |
| `clickup_create_list_in_folder` | Create list in Folder |
| `clickup_get_list` | Get list details |
| `clickup_update_list` | Update list settings |
| `clickup_create_folder` | Create folder in Space |
| `clickup_get_folder` | Get folder details |
| `clickup_update_folder` | Update folder settings |

### Members

| Tool | Description |
|------|-------------|
| `clickup_get_workspace_members` | List all workspace members |
| `clickup_find_member_by_name` | Find member by name/email |
| `clickup_resolve_assignees` | Get user IDs from names |

### Chat

| Tool | Description |
|------|-------------|
| `clickup_get_chat_channels` | List all Chat channels |
| `clickup_send_chat_message` | Send message to channel |

### Docs

| Tool | Description |
|------|-------------|
| `clickup_create_document` | Create new Doc |
| `clickup_list_document_pages` | Get Doc structure |
| `clickup_get_document_pages` | Get page content |
| `clickup_create_document_page` | Add page to Doc |
| `clickup_update_document_page` | Edit page content |

## Usage Examples

### Search Workspace

```bash
mcporter call 'clickup.clickup_search(
  keywords: "Q4 marketing",
  count: 10
)'
```

### Create Task

```bash
mcporter call 'clickup.clickup_create_task(
  name: "Review PR #42",
  list_id: "901506994423",
  description: "Check the new feature",
  status: "to do"
)'
```

### Update Task

```bash
mcporter call 'clickup.clickup_update_task(
  task_id: "abc123",
  status: "in progress"
)'
```

### Add Comment

```bash
mcporter call 'clickup.clickup_create_task_comment(
  task_id: "abc123",
  comment_text: "@Mark can you review this?"
)'
```

### Time Tracking

```bash
# Start timer
mcporter call 'clickup.clickup_start_time_tracking(
  task_id: "abc123",
  description: "Working on feature"
)'

# Stop timer
mcporter call 'clickup.clickup_stop_time_tracking()'

# Log time manually (duration in ms, e.g., 2h = 7200000)
mcporter call 'clickup.clickup_add_time_entry(
  task_id: "abc123",
  start: "2026-01-06 10:00",
  duration: "2h",
  description: "Code review"
)'
```

### Get Workspace Structure

```bash
mcporter call 'clickup.clickup_get_workspace_hierarchy(limit: 10)'
```

### Chat

```bash
# List channels
mcporter call 'clickup.clickup_get_chat_channels()'

# Send message
mcporter call 'clickup.clickup_send_chat_message(
  channel_id: "channel-123",
  content: "Team standup in 5 minutes!"
)'
```

## Limitations

- **No delete operations** — Safety measure; use ClickUp UI
- **No custom fields** — Not exposed in official MCP
- **No views management** — Not available
- **OAuth required** — Must use allowlisted client (Claude Code workaround available)
- **Rate limits** — Same as ClickUp API (~100 req/min)

## Resources

- [ClickUp MCP Documentation](https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server)
- [Supported Tools](https://developer.clickup.com/docs/mcp-tools)
- [ClickUp API Reference](https://clickup.com/api)
- [Feedback / Allowlist Request](https://feedback.clickup.com)
