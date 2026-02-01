---
name: appdeploy
description: Deploy web apps with backend APIs, database, and file storage. Use when the user asks to deploy or publish a website or web app and wants a public URL. Requires installing the AppDeploy MCP server first.
compatibility: Requires AppDeploy MCP server connection
allowed-tools:
  - mcp__appdeploy
metadata:
  author: appdeploy
  version: "1.0"
---

# AppDeploy

Deploy web apps to a public URL with optional backend, database, and storage.

## Install the MCP First

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "appdeploy": {
      "url": "http://api-v2.appdeploy.ai/mcp"
    }
  }
}
```

Once connected, you'll have access to all deployment tools.

## What You Get

- **Web Apps** → Deploy to a public URL instantly
- **Backend APIs** → Custom HTTP endpoints
- **Database** → Database tables, full CRUD APIs (`db.add`, `db.get`, `db.list`, `db.update`, `db.delete`)
- **File Storage** → Upload/download files (`storage.write`, `storage.read`, `storage.url`)
- **WebSockets** → Real-time updates (`ws.send`)
- **Versioning** → Rollback to previous deployments, read code, logs, etc.

## Workflow

**Always follow this order:**

```
1. get_deploy_instructions  → Returns ALL rules and constraints, follow them exactly
```

> **Important**: The MCP tools are self-documenting. `get_deploy_instructions` returns everything you need to know about deployment rules. Follow its guidance.

## Available Tools

| Tool | Purpose |
|------|---------|
| `get_deploy_instructions` | Get deployment rules (MUST call first) |
| `get_app_template` | Get starter template + SDK types |
| `deploy_app` | Create or update an app |
| `get_app_status` | Check deployment status |
| `delete_app` | Delete an app (only on user request) |
| `get_apps` | List user's apps |
| `get_app_versions` | List versions for rollback |
| `apply_app_version` | Rollback to a previous version |
| `src_glob` | List files in deployed app |
| `src_grep` | Search code in deployed app |
| `src_read` | Read file from deployed app |

## App Types

Choose based on requirements:

- **frontend-only** → Static sites, no server-side code
- **frontend+backend** → Full-stack with APIs, database, storage

## Quick Example

```
User: "Build me a todo app with persistence"

1. Call get_deploy_instructions
2. Call get_app_template({ app_type: "frontend+backend", frontend_template: "react-vite" })
3. Generate files following the returned instructions
4. Call deploy_app with app_type: "frontend+backend"
5. Poll get_app_status until status is "ready"
6. Return the public URL to the user
```

## Key Points

- Call `get_deploy_instructions` before writing any code
- The MCP returns comprehensive rules - follow them exactly
- Use `frontend+backend` when you need database, storage, or custom APIs
- Poll `get_app_status` until you get a terminal state (ready/failed/deleted)
