# Craft.do Integration Skill

Complete REST API integration for Craft.do - the beautiful note-taking and document app.

## Overview

This skill provides full programmatic access to Craft.do for:
- **Task automation:** Create, update, manage tasks across inbox/daily notes/logbook
- **Document workflows:** Programmatically create, read, organize documents
- **Folder management:** Build nested folder hierarchies via API
- **Obsidian migration:** One-time full vault migration with content preservation
- **Content manipulation:** Add/edit markdown content via blocks API

Craft.do features:
- Native markdown support
- Task management (inbox, daily notes, logbook)
- Collections (database tables)
- Hierarchical folders and documents
- Full REST API access

## Setup

1. Get your API key from Craft.do settings
2. Store credentials securely:

```bash
export CRAFT_API_KEY="pdk_xxx"
export CRAFT_ENDPOINT="https://connect.craft.do/links/YOUR_LINK/api/v1"
```

## API Capabilities

### ✅ What Works

#### List Folders
```bash
curl -H "Authorization: Bearer $CRAFT_API_KEY" \
  "$CRAFT_ENDPOINT/folders"
```

Returns all locations: unsorted, daily_notes, trash, templates, and custom folders.

#### List Documents
```bash
curl -H "Authorization: Bearer $CRAFT_API_KEY" \
  "$CRAFT_ENDPOINT/documents?folderId=FOLDER_ID"
```

#### Create Folder (with optional parent for nesting)
```bash
# Root-level folder
curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "folders": [{
      "name": "Projects"
    }]
  }' \
  "$CRAFT_ENDPOINT/folders"

# Nested folder (requires parent folder ID)
curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "folders": [{
      "name": "Q1 2024",
      "parentFolderId": "PARENT_FOLDER_ID"
    }]
  }' \
  "$CRAFT_ENDPOINT/folders"
```

#### Create Document
```bash
curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [{
      "title": "Document Title"
    }],
    "destination": {
      "folderId": "FOLDER_ID"
    }
  }' \
  "$CRAFT_ENDPOINT/documents"
```

**Note:** Documents are created without content initially. Use the `/blocks` endpoint to add content.

#### Add Content to Document
```bash
curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "blocks": [{
      "type": "text",
      "markdown": "# Document content\n\nFull markdown support!"
    }],
    "position": {
      "pageId": "DOCUMENT_ID",
      "position": "end"
    }
  }' \
  "$CRAFT_ENDPOINT/blocks"
```

#### Read Document Content
```bash
curl -H "Authorization: Bearer $CRAFT_API_KEY" \
  "$CRAFT_ENDPOINT/blocks?id=DOCUMENT_ID"
```

Returns full markdown content with all blocks.

#### Create Task
```bash
curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [{
      "markdown": "Task description",
      "location": {"type": "inbox"},
      "status": "active"
    }]
  }' \
  "$CRAFT_ENDPOINT/tasks"
```

#### Update Task (Mark Complete)
```bash
curl -X PUT \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tasksToUpdate": [{
      "id": "TASK_ID",
      "markdown": "- [x] Completed task"
    }]
  }' \
  "$CRAFT_ENDPOINT/tasks"
```

#### List Tasks
```bash
# Active tasks
curl -H "Authorization: Bearer $CRAFT_API_KEY" \
  "$CRAFT_ENDPOINT/tasks?scope=active"

# All completed (logbook)
curl -H "Authorization: Bearer $CRAFT_API_KEY" \
  "$CRAFT_ENDPOINT/tasks?scope=logbook"

# Upcoming
curl -H "Authorization: Bearer $CRAFT_API_KEY" \
  "$CRAFT_ENDPOINT/tasks?scope=upcoming"

# Inbox only
curl -H "Authorization: Bearer $CRAFT_API_KEY" \
  "$CRAFT_ENDPOINT/tasks?scope=inbox"
```

#### Move Documents
```bash
curl -X PUT \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "documentIds": ["DOC_ID"],
    "destination": {"location": "unsorted"}
  }' \
  "$CRAFT_ENDPOINT/documents/move"
```

Note: Can only move to `unsorted`, `templates`, or custom folder IDs. Cannot move directly to `trash`.

### ❌ Limitations

- **No Collections API** - Collections (databases) not accessible via API
- **No task deletion** - Can only create/update tasks, not delete
- **No document deletion** - Cannot delete documents directly (only move)
- **No search endpoint** - Search requires specific query format (needs more testing)
- **Limited filtering** - Collections filtering/grouping only in UI, not via API

## Common Use Cases

### Sync Tasks from External System
```bash
# Create task in Craft from Mission Control
TASK_TITLE="Deploy new feature"
curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"tasks\": [{
      \"markdown\": \"$TASK_TITLE\",
      \"location\": {\"type\": \"inbox\"},
      \"status\": \"active\"
    }]
  }" \
  "$CRAFT_ENDPOINT/tasks"
```

### Create Daily Note
```bash
TODAY=$(date +%Y-%m-%d)
curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"documents\": [{
      \"title\": \"Daily Note - $TODAY\",
      \"content\": [{\"textContent\": \"# $TODAY\\n\\n## Tasks\\n\\n## Notes\\n\"}],
      \"location\": \"daily_notes\"
    }]
  }" \
  "$CRAFT_ENDPOINT/documents"
```

### Archive Completed Work
```bash
# Get all completed tasks
curl -H "Authorization: Bearer $CRAFT_API_KEY" \
  "$CRAFT_ENDPOINT/tasks?scope=logbook" | jq '.items[] | {id, markdown, completedAt}'
```

## Integration Patterns

### Mission Control → Craft Sync

**Problem:** Mission Control has automation but ugly UI. Craft has beautiful UI but no automation.

**Solution:** Use Mission Control as the source of truth, sync completed work to Craft for viewing.

```bash
#!/bin/bash
# sync-to-craft.sh - Sync completed tasks to Craft

# Read completed tasks from Mission Control
COMPLETED_TASKS=$(cat mission-control/tasks.json | jq -r '.[] | select(.status=="done") | .title')

# Push each to Craft
echo "$COMPLETED_TASKS" | while read -r task; do
  curl -X POST \
    -H "Authorization: Bearer $CRAFT_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"tasks\": [{
        \"markdown\": \"- [x] $task\",
        \"location\": {\"type\": \"inbox\"}
      }]
    }" \
    "$CRAFT_ENDPOINT/tasks"
done
```

## Markdown Support

Craft fully supports markdown:
- Headers: `# H1`, `## H2`, etc.
- Lists: `- item`, `1. item`
- Tasks: `- [ ] todo`, `- [x] done`
- Links: `[text](url)`
- Code: `` `inline` `` or ` ```block``` `
- Emphasis: `*italic*`, `**bold**`

All content is stored and returned as markdown, making it perfect for programmatic manipulation.

## Best Practices

1. **Store API key securely** - Never commit to code
2. **Test in unsorted folder first** - Easy to find/clean up
3. **Use markdown format** - Native to both systems
4. **One-way sync only** - Craft → read-only, Mission Control → write
5. **Batch operations** - API supports arrays for efficiency
6. **Handle errors gracefully** - API returns detailed validation errors

## Error Handling

Common errors:
- `VALIDATION_ERROR` - Check required fields (markdown, location)
- `403` - Invalid/expired API key
- `404` - Document/task ID not found

Example validation error:
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": [{
    "path": ["tasks", 0, "markdown"],
    "message": "Invalid input: expected string"
  }]
}
```

## Future Possibilities

When Craft adds to their API:
- [ ] Collections CRUD via API
- [ ] Task deletion
- [ ] Document deletion
- [ ] Advanced search
- [ ] Webhooks for real-time sync
- [ ] Batch operations for large datasets

## Resources

- [Craft API Docs](https://craft.do/api) (get your personal API endpoint from Craft settings)
- [Craft Blog - Collections](https://www.craft.do/blog/introducing-collections)
- [Craft YouTube](https://www.youtube.com/channel/UC8OIJ9uNRQZiG78K2BSn67A)

## Testing Checklist

- [x] List folders
- [x] List documents
- [x] Create document
- [x] Add content to document (via /blocks endpoint)
- [x] Read document content
- [x] Create task
- [x] Update task (mark complete)
- [x] List tasks (all scopes)
- [x] Move documents between locations
- [x] Full Obsidian → Craft migration with content
- [ ] Search (needs format refinement)
- [x] Collections - NOT accessible via API
- [x] Delete tasks - NOT supported
- [x] Delete documents - NOT supported (only move)

## Example: Complete Workflow

```bash
# 1. Create a project folder
PROJECT_ID=$(curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Q1 2024 Projects"}' \
  "$CRAFT_ENDPOINT/folders" | jq -r '.id')

# 2. Create a project document
DOC_ID=$(curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"documents\": [{
      \"title\": \"Project Alpha\",
      \"content\": [{\"textContent\": \"## Overview\\n\\nProject details here.\"}],
      \"location\": \"$PROJECT_ID\"
    }]
  }" \
  "$CRAFT_ENDPOINT/documents" | jq -r '.items[0].id')

# 3. Create tasks for the project
curl -X POST \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {"markdown": "Design wireframes", "location": {"type": "inbox"}},
      {"markdown": "Build prototype", "location": {"type": "inbox"}},
      {"markdown": "User testing", "location": {"type": "inbox"}}
    ]
  }' \
  "$CRAFT_ENDPOINT/tasks"

# 4. Mark first task complete
TASK_ID=$(curl -H "Authorization: Bearer $CRAFT_API_KEY" \
  "$CRAFT_ENDPOINT/tasks?scope=active" | jq -r '.items[0].id')

curl -X PUT \
  -H "Authorization: Bearer $CRAFT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"tasksToUpdate\": [{
      \"id\": \"$TASK_ID\",
      \"markdown\": \"- [x] Design wireframes\"
    }]
  }" \
  "$CRAFT_ENDPOINT/tasks"
```

---

**Status:** Tested and working (2026-01-31)
**Tested with:** Craft API v1
**Author:** Eliza
