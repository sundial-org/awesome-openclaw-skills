---
name: byterover-headless
description: "Query and curate knowledge-base using ByteRover CLI. Use `brv query` for knowledge retrieval, `brv curate` for adding context, and `brv push/pull` for syncing."
metadata: {"moltbot":{"emoji":"🧠","requires":{"bins":["brv"]},"install":[{"id":"npm","kind":"node","package":"@byterover/cli","bins":["brv"],"label":"Install ByteRover CLI (npm)"}]}}
---

# ByteRover Knowledge Management

Use the `brv` CLI to manage your own knowledgebase. ByteRover maintains a context tree that stores patterns, decisions, and implementation details about a project.

**IMPORTANT**: For headless/automated use, always add `--headless --format json` flags to get machine-parseable JSON output.

## Setup (Headless)

- ByteRover can be fully set up in headless mode. If user has not logged in or initialized `.brv/` in the current working directory (check via `projectInitialized` and and `authStatus` in `brv status --headless --format json
` response), ask them to provide:
1. **API key** - for authentication (obtain from https://app.byterover.dev/settings/keys)
2. **Team and space** - names or IDs for project initialization

### Login with API Key

Authenticate using an API key:

```bash
brv login --api-key <key>
```

Outputs text: `Logged in as <email>` on success.

### Initialize Project

Initialize ByteRover for a project (requires team and space for headless mode - can use either ID or name):

```bash
# Using names
brv init --headless --team my-team --space my-space --format json

# Using IDs
brv init --headless --team team-abc123 --space space-xyz789 --format json
```

Force re-initialization:
```bash
brv init --headless --team my-team --space my-space --force --format json
```

Example response:
```json
{
  "success": true,
  "command": "init",
  "data": {
    "status": "success",
    "teamName": "MyTeam",
    "spaceName": "MySpace",
    "configPath": "/path/to/project/.brv/config.json"
  }
}
```

**Note**: You can use either team/space names or IDs. Names are matched case-insensitively.

### Check Status

Check the current status of ByteRover and the project:

```bash
brv status --headless --format json
```

Example response:
```json
{
  "success": true,
  "command": "status",
  "data": {
    "cliVersion": "1.0.0",
    "authStatus": "logged_in",
    "userEmail": "user@example.com",
    "projectInitialized": true,
    "teamName": "MyTeam",
    "spaceName": "MySpace",
    "mcpStatus": "connected",
    "contextTreeStatus": "has_changes"
  }
}
```

## Query Knowledge

Ask questions to retrieve relevant knowledge:

```bash
brv query "How is authentication implemented?" --headless --format json
```

Example response:
```json
{
  "success": true,
  "command": "query",
  "data": {
    "status": "completed",
    "result": "Authentication uses JWT tokens...",
    "toolCalls": [{"tool": "search_knowledge", "status": "success", "summary": "5 matches"}]
  }
}
```

## Curate Context

Add new knowledge or context to the project's context tree:

```bash
brv curate "Auth uses JWT with 24h expiry. Tokens stored in httpOnly cookies via authMiddleware.ts" --headless --format json
```

Include specific files for comprehensive context (max 5 files):
```bash
brv curate "Authentication middleware validates JWT tokens" --files src/middleware/auth.ts --headless --format json
```

Example response:
```json
{
  "success": true,
  "command": "curate",
  "data": {
    "status": "queued",
    "taskId": "abc123",
    "message": "Context queued for processing"
  }
}
```

## Push Context Tree

Push local context tree changes to ByteRover cloud storage:

```bash
brv push --headless --format json -y
```

The `-y` flag skips confirmation prompt (required for headless mode).

Push to a specific branch:
```bash
brv push --branch feature-branch --headless --format json -y
```

Example response:
```json
{
  "success": true,
  "command": "push",
  "data": {
    "status": "success",
    "added": 3,
    "edited": 1,
    "deleted": 0,
    "branch": "main",
    "url": "https://app.byterover.com/team/space"
  }
}
```

Possible statuses:

- `success` - Push completed
- `no_changes` - No context changes to push
- `cancelled` - Push was cancelled
- `error` - Push failed

## Pull Context Tree

Pull context tree from ByteRover cloud storage:

```bash
brv pull --headless --format json
```

Pull from a specific branch:
```bash
brv pull --branch feature-branch --headless --format json
```

Example response:
```json
{
  "success": true,
  "command": "pull",
  "data": {
    "status": "success",
    "added": 5,
    "edited": 2,
    "deleted": 1,
    "branch": "main",
    "commitSha": "abc123def"
  }
}
```

Possible statuses:

- `success` - Pull completed
- `local_changes` - Local changes exist, push first
- `error` - Pull failed

## Error Handling

Always check the `success` field in JSON responses:

- `success: true` - Operation completed successfully
- `success: false` - Operation failed, check `data.error` or `data.message` for details

Common error scenarios:
- **Not authenticated**: Run `brv login --api-key <key>`
- **Project not initialized**: Run `brv init --headless --team <team> --space <space> --format json`
- **Local changes exist**: Push local changes before pulling

## Tips
1. For pull and push operations, you should ask for user permission first.
2. Always use `--headless --format json` for automation (except `brv login` which outputs text).
3. Check `brv status --headless --format json` first to verify auth and project state.
4. For curate operations, include relevant files with `--files` for better context.
5. Query responses may include tool call details showing what knowledge was searched.
6. For push operations, always use `-y` to skip confirmation in headless mode. For re-initialization, use `-f` to force re-initialization.
7. Pull will fail if there are unpushed local changes - push first.
