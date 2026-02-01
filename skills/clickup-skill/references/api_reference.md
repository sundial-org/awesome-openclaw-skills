# ClickUp API Reference

## Authentication

All requests require an API token passed in the `Authorization` header:
```
Authorization: pk_xxxxxxxxxxxxxxxxxxxx
```

Set via environment variable: `CLICKUP_API_TOKEN`

## Rate Limits
- 100 requests per minute per token
- 500 requests per minute per OAuth app

## Workspace Hierarchy

```
Team (Workspace)
└── Space
    ├── Folder
    │   └── List
    │       └── Task
    └── List (Folderless)
        └── Task
```

## Common Operations

### Workspaces (Teams)
- `GET /team` - List all workspaces
- `GET /team/{team_id}` - Get workspace details

### Spaces
- `GET /team/{team_id}/space` - List spaces
- `POST /team/{team_id}/space` - Create space
- `PUT /space/{space_id}` - Update space
- `DELETE /space/{space_id}` - Delete space

**Space Configuration Options:**
```json
{
  "name": "Space Name",
  "multiple_assignees": true,
  "features": {
    "due_dates": {"enabled": true, "remap_due_dates": true, "remap_closed_due_date": false},
    "time_tracking": {"enabled": true},
    "tags": {"enabled": true},
    "time_estimates": {"enabled": true},
    "checklists": {"enabled": true},
    "custom_fields": {"enabled": true},
    "remap_dependencies": {"enabled": true},
    "dependency_warning": {"enabled": true},
    "portfolios": {"enabled": true}
  }
}
```

### Folders
- `GET /space/{space_id}/folder` - List folders
- `POST /space/{space_id}/folder` - Create folder
- `PUT /folder/{folder_id}` - Update folder
- `DELETE /folder/{folder_id}` - Delete folder

### Lists
- `GET /folder/{folder_id}/list` - List lists in folder
- `GET /space/{space_id}/list` - List folderless lists
- `POST /folder/{folder_id}/list` - Create list in folder
- `POST /space/{space_id}/list` - Create folderless list
- `PUT /list/{list_id}` - Update list
- `DELETE /list/{list_id}` - Delete list

**List Configuration Options:**
```json
{
  "name": "List Name",
  "content": "Description",
  "status": {"status": "red", "hide_label": true},
  "priority": 1,
  "assignee": 123,
  "due_date": 1567780450202,
  "due_date_time": false,
  "start_date": 1567780450202,
  "start_date_time": false,
  "folder_id": "456"
}
```

### Tasks
- `GET /list/{list_id}/task` - List tasks
- `GET /task/{task_id}` - Get task details
- `POST /list/{list_id}/task` - Create task
- `PUT /task/{task_id}` - Update task
- `DELETE /task/{task_id}` - Delete task

**Task Creation Options:**
```json
{
  "name": "Task Name",
  "description": "Task description",
  "assignees": [123, 456],
  "tags": ["tag1", "tag2"],
  "status": "to do",
  "priority": 1,
  "due_date": 1567780450202,
  "due_date_time": false,
  "time_estimate": 8640000,
  "start_date": 1567780450202,
  "start_date_time": false,
  "notify_all": true,
  "parent": null,
  "links_to": null,
  "custom_fields": [
    {"id": "abc", "value": "value"}
  ]
}
```

**Task Update Options:**
Same as create, plus:
```json
{
  "archived": false
}
```

### Time Tracking
- `GET /team/{team_id}/time_entries` - List time entries
- `GET /team/{team_id}/time_entries/{time_entry_id}` - Get time entry
- `POST /team/{team_id}/time_entries` - Create time entry
- `PUT /team/{team_id}/time_entries/{time_entry_id}` - Update time entry
- `DELETE /team/{team_id}/time_entries/{time_entry_id}` - Delete time entry
- `POST /task/{task_id}/time/start_timer` - Start timer
- `POST /task/{task_id}/time/stop_timer` - Stop timer

**Time Entry Creation:**
```json
{
  "tid": "task_id",
  "description": "Worked on feature",
  "duration": 3600000,
  "start": 1567780450202,
  "billable": true,
  "assignee": 123
}
```

### Documents
- `GET /team/{team_id}/doc` - List documents
- `GET /doc/{doc_id}` - Get document
- `POST /team/{team_id}/doc` - Create document
- `PUT /doc/{doc_id}` - Update document
- `DELETE /doc/{doc_id}` - Delete document
- `GET /doc/{doc_id}/page` - List pages
- `POST /doc/{doc_id}/page` - Create page
- `PUT /doc/{doc_id}/page/{page_id}` - Update page

**Document Creation:**
```json
{
  "name": "Document Name",
  "parent": {"id": "parent_id", "type": 6},
  "template_id": "template_id",
  "visibility": "private"
}
```

**Document Page Creation:**
```json
{
  "name": "Page Title",
  "content": "Page content in ClickUp format",
  "parent_page_id": "parent_page_id"
}
```

## Custom Fields

### Get Custom Fields
- `GET /list/{list_id}/field` - List custom fields in list

### Set Custom Field Value
- `POST /task/{task_id}/field/{field_id}` - Set field value

**Custom Field Types:**
- `url`: String
- `drop_down`: Integer (option index)
- `labels`: Array of strings
- `text`: String
- `number`: Number
- `date`: Timestamp
- `emoji`: String
- `checkbox`: Boolean
- `currency`: Number
- `location`: Object with `lat`, `lng`, `formatted_address`
- `users`: Array of user IDs
- `attachment`: File object

## Statuses

### Space Statuses
- `GET /space/{space_id}/status` - Get space statuses

Status types:
- `open` - Active statuses
- `closed` - Done/complete statuses
- `custom` - Custom workflow statuses

## Tags

- `GET /space/{space_id}/tag` - List tags
- `POST /space/{space_id}/tag` - Create tag
- `PUT /space/{space_id}/tag/{tag_name}` - Update tag
- `DELETE /space/{space_id}/tag/{tag_name}` - Delete tag

## Multi-Workspace Considerations

When working across workspaces:

1. **Workspace IDs are unique** - All operations require explicit team_id
2. **Custom task IDs** - If using custom task IDs, include `custom_task_ids=true` and `team_id` in requests
3. **Permissions** - API token must have access to target workspace
4. **Rate limits** - Shared across all workspaces for the token

### Script Usage for Multi-Workspace

```bash
# List all workspaces
python scripts/clickup_client.py get_teams

# Get spaces in specific workspace
python scripts/clickup_client.py get_spaces team_id="123"

# Create task in workspace A
python scripts/clickup_client.py create_task list_id="abc" name="Task Name"

# Create task in workspace B (same script, different IDs)
python scripts/clickup_client.py create_task list_id="xyz" name="Another Task"
```
