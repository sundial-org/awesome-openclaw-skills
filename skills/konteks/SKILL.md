---
name: konteks
description: Connect your Clawdbot/Moltbot to your Konteks account (konteks.app) for persistent memory, task management, and context sharing. Use when you need to store agent memories, create or read tasks/notes, check projects and folders, read daily plans, or sync context between conversations. Requires a Konteks API key from konteks.app/dashboard/settings.
---

# Konteks — Agent Context Layer

Connect to your human's Konteks account for persistent memory, tasks, notes, and projects.

## Setup

Your human needs to:
1. Sign up at https://konteks.app
2. Go to Settings → Generate API Key
3. Add to Clawdbot config:

```yaml
skills:
  konteks:
    apiKey: "sk_..."
    url: "https://konteks.app"  # optional, defaults to this
    agentId: "my-agent"         # optional, defaults to "default"
```

Read config values:
```bash
# These will be available as environment variables if configured in gateway config,
# or read from the skill config via the gateway API
```

## API Base

All endpoints: `{url}/api/agent/...`
Auth header: `Authorization: Bearer {apiKey}`

## Agent Memory (agent_contexts)

Store and retrieve persistent memories, decisions, preferences, and learnings.

**Write/update memory:**
```bash
curl -X POST "{url}/api/agent/context" \
  -H "Authorization: Bearer {apiKey}" \
  -H "Content-Type: application/json" \
  -d '{"category":"memory","key":"user_preference","value":"Prefers dark mode","agent_id":"{agentId}"}'
```

Categories: `memory`, `decision`, `preference`, `learning`, `project_note`

Upserts automatically — same agent_id + category + key updates the existing entry.

**Read memory:**
```bash
curl "{url}/api/agent/context?category=memory&limit=20" \
  -H "Authorization: Bearer {apiKey}"
```

Query params: `category`, `key`, `limit`

**Delete:**
```bash
curl -X DELETE "{url}/api/agent/context?id={contextId}" \
  -H "Authorization: Bearer {apiKey}"
```

## Tasks & Notes (items)

**List items:**
```bash
curl "{url}/api/agent/items?archived=false&completed=false&limit=50" \
  -H "Authorization: Bearer {apiKey}"
```

Query params: `smart_list` (inbox|anytime|someday), `folder_id`, `completed` (true|false), `archived` (true|false), `item_type` (task|note|hybrid), `limit`

**Create item:**
```bash
curl -X POST "{url}/api/agent/items" \
  -H "Authorization: Bearer {apiKey}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Review PR","item_type":"task","smart_list":"inbox","priority":"high","tags":["dev"]}'
```

Required: `title`, `item_type` (task|note|hybrid)
Optional: `body`, `folder_id`, `smart_list` (inbox|anytime|someday — defaults to inbox if no folder), `priority` (high|normal|someday), `due_date`, `scheduled_date`, `tags` (string array)

Items created by agent have `source: "ai"`.

**Update item:**
```bash
curl -X PATCH "{url}/api/agent/items/{id}" \
  -H "Authorization: Bearer {apiKey}" \
  -H "Content-Type: application/json" \
  -d '{"completed_at":"2026-01-29T12:00:00Z"}'
```

Updatable fields: `title`, `body`, `priority`, `due_date`, `scheduled_date`, `tags`, `completed_at`, `archived_at`, `canceled_at`, `folder_id`, `smart_list`

**Delete item:**
```bash
curl -X DELETE "{url}/api/agent/items/{id}" \
  -H "Authorization: Bearer {apiKey}"
```

## Projects & Areas (folders)

**List folders:**
```bash
curl "{url}/api/agent/folders?type=project" \
  -H "Authorization: Bearer {apiKey}"
```

Query params: `type` (project|area)

**Create folder:**
```bash
curl -X POST "{url}/api/agent/folders" \
  -H "Authorization: Bearer {apiKey}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Q1 Launch","folder_type":"project","icon":"🚀","goal":"Ship MVP by March"}'
```

Required: `name`, `folder_type` (project|area)
Optional: `icon`, `color`, `goal`

## Daily Plans

**Get today's plan:**
```bash
curl "{url}/api/agent/plans?date=2026-01-29" \
  -H "Authorization: Bearer {apiKey}"
```

Returns: `task_ids`, `summary`, `rationale`, `available_minutes`, `calendar_events`

## Usage Patterns

**On session start:** Read recent memories to restore context.
```
GET /api/agent/context?category=memory&limit=10
```

**After important decisions:** Write a memory entry.
```
POST /api/agent/context {"category":"decision","key":"chose_react","value":"Chose React over Vue for the dashboard because..."}
```

**When human asks to create a task:** Create it in Konteks so it shows in their app.
```
POST /api/agent/items {"title":"...","item_type":"task","smart_list":"inbox"}
```

**During heartbeats:** Check for overdue or due-today items.
```
GET /api/agent/items?completed=false&archived=false
```

**Learning something new:** Store it for future sessions.
```
POST /api/agent/context {"category":"learning","key":"ssh_config","value":"Home server is at 192.168.1.100, user admin"}
```
