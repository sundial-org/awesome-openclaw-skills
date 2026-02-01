---
name: clickup
description: "Enterprise-grade ClickUp project management integration with advanced reporting, multi-workspace support, and client/project tracking. Core capabilities: (1) Multi-workspace task management with automatic workspace switching, (2) Advanced analytics & reporting (task counts, assignee breakdowns, status/priority analysis, daily standup reports) with automatic subtask inclusion and pagination, (3) Client folder organization with project tracking (📋 Client Overview, 📁 Completed Work, active project lists), (4) Full CRUD operations for spaces, folders, lists, tasks, and custom fields, (5) Time tracking & timer management with billing support, (6) Document creation and page management (API v3), (7) Task dependencies, linking, and relationship mapping, (8) Sales pipeline tracking with prospect/project status, (9) Retainer & recurring billing management. Built for agencies managing multiple clients across complex workspace hierarchies."
---

# ClickUp Skill

**Enterprise-grade ClickUp integration for agency workflows.** Manage multiple clients, projects, and workspaces with advanced reporting, automatic subtask handling, and sophisticated folder organization.

## Key Benefits

| Feature | Why It Matters |
|---------|----------------|
| **🔍 Always includes subtasks** | Never miss 70%+ of actual work — subtasks included automatically |
| **📊 Advanced reporting** | Task counts, workload distribution, status breakdowns, standup reports |
| **🏢 Multi-workspace** | Seamlessly switch between Client Work, Product Development, Personal Projects, and more |
| **👥 Client organization** | Structured folders: 📋 Client Overview, 📁 Completed Work, active projects |
| **📈 Sales pipeline** | Track proposals, negotiations, and project lifecycles |
| **⏱️ Time tracking** | Built-in timers and manual entries with billing support |
| **📄 Document management** | Create docs and pages via API v3 |
| **🔗 Task relationships** | Dependencies, blocking/waiting, and arbitrary task linking |

## Quick Start

### Setup
Set your ClickUp API token:
```bash
export CLICKUP_API_TOKEN="pk_your_token_here"
```

Get your token from: ClickUp Settings → Apps → Generate API Token

### Basic Operations

**List all workspaces:**
```bash
python skills/clickup/scripts/clickup_client.py get_teams
```

**Create a task:**
```bash
python skills/clickup/scripts/clickup_client.py create_task list_id="123" name="New Task" status="to do"
```

**Update a task:**
```bash
python skills/clickup/scripts/clickup_client.py update_task task_id="abc" status="in progress"
```

## Workspace Hierarchy

```
Team (Workspace)
├── Spaces
│   ├── Folders
│   │   └── Lists → Tasks
│   └── Lists (Folderless) → Tasks
└── Documents
```

All operations require explicit workspace identification via IDs.

## Multi-Workspace Support

This skill supports operations across multiple ClickUp workspaces:

1. Use `get_teams` to list available workspaces
2. Reference workspace by `team_id` in operations
3. Each workspace maintains independent spaces, folders, lists
4. Custom task IDs require both `custom_task_ids=true` and `team_id`

## Common Workflows

### Workflow: Create Task in Specific Workspace

1. Get workspace ID: `get_teams`
2. Get target space: `get_spaces team_id="xxx"`
3. Get or create list: `get_folders space_id="yyy"` → `get_lists folder_id="zzz"`
4. Create task: `create_task list_id="aaa" name="Task" ...`

### Workflow: Configure Space Statuses

1. Get space: `get_space space_id="xxx"`
2. Update space with statuses: `update_space space_id="xxx" statuses=[...]`

See [API Reference](references/api_reference.md) for status configuration format.

### Workflow: Track Time on Task

**Option A - Manual Entry:**
```bash
python skills/clickup_client.py create_time_entry \
  team_id="xxx" \
  task_id="yyy" \
  duration=3600000 \
  description="Worked on feature"
```

**Option B - Timer:**
```bash
# Start timer
python skills/clickup/scripts/clickup_client.py start_timer team_id="xxx" task_id="yyy"

# Stop timer (stops current running timer for user)
python skills/clickup/scripts/clickup_client.py stop_timer team_id="xxx"
```

### Workflow: Create Document Structure

1. Create doc: `create_doc workspace_id="xxx" name="Project Docs"`
2. Add pages: Use ClickUp UI (pages API is in beta)

Note: Documents use ClickUp API v3 (workspace_id instead of team_id).

### Workflow: Reporting & Analytics

**Get task counts (with parent/subtask breakdown):**
```bash
python skills/clickup/scripts/clickup_client.py task_counts team_id="xxx"
# Returns: {"total": 50, "parents": 20, "subtasks": 30, "unassigned": 5}
```

**Get workload by assignee:**
```bash
python skills/clickup/scripts/clickup_client.py assignee_breakdown team_id="xxx"
# Returns: {"John Doe": 15, "Jane Smith": 12, "Unassigned": 8}
```

**Get tasks by status:**
```bash
python skills/clickup/scripts/clickup_client.py status_breakdown team_id="xxx"
# Returns: {"to do": 20, "in progress": 10, "complete": 15}
```

**Get tasks by priority:**
```bash
python skills/clickup/scripts/clickup_client.py priority_breakdown team_id="xxx"
# Returns: {"urgent": 2, "high": 5, "normal": 15, "low": 8, "none": 20}
```

**Daily standup report (grouped by status):**
```bash
# All team members
python skills/clickup/scripts/clickup_client.py standup_report team_id="xxx"

# Specific person (use user ID)
python skills/clickup/scripts/clickup_client.py standup_report team_id="xxx" assignee_id="12345"
```

**Get all tasks with pagination (auto-handled):**
```bash
python skills/clickup/scripts/clickup_client.py get_all_tasks team_id="xxx"
# Always includes subtasks automatically (critical!)
```

**Filter reports by space or assignee:**
```bash
# Specific space
python skills/clickup/scripts/clickup_client.py task_counts team_id="xxx" space_ids='["SPACE_ID_HERE"]'

# Specific assignee
python skills/clickup/scripts/clickup_client.py get_all_tasks team_id="xxx" assignees='["12345"]'

# Include closed tasks
python skills/clickup/scripts/clickup_client.py task_counts team_id="xxx" include_closed="true"
```

**Critical Rules for Reporting:**
1. **Always include subtasks** — Our methods do this automatically via `subtasks=true`
2. **Pagination handled** — `get_all_tasks` loops until all pages retrieved
3. **Parent vs Subtask** — Parents have `parent: null`, subtasks have `parent: "task_id"`
4. **Rate limit** — 100 requests/min; our pagination respects this

### Workflow: Link Doc to Task

**Option A - Add as attachment:**
```bash
python skills/clickup/scripts/clickup_client.py link_doc_to_task \
  task_id="xxx" \
  doc_id="yyy"
```

**Option B - Mention in description:**
```bash
python skills/clickup/scripts/clickup_client.py mention_doc_in_task \
  task_id="xxx" \
  doc_id="yyy"
```

Both create clickable links to the document from the task.

### Workflow: Task Dependencies

**Set up blocking relationship:**
```bash
# Task B is blocked by/waiting on Task A
python skills/clickup/scripts/clickup_client.py add_dependency \
  task_id="TASK_B_ID" \
  depends_on="TASK_A_ID"

# Check dependencies
python skills/clickup/scripts/clickup_client.py get_dependencies \
  task_id="TASK_B_ID"

# Remove dependency
python skills/clickup/scripts/clickup_client.py remove_dependency \
  task_id="TASK_B_ID" \
  depends_on="TASK_A_ID"
```

**Set up reverse dependency (task is blocking another):**
```bash
# Task A is blocking Task B
python skills/clickup/scripts/clickup_client.py add_dependency \
  task_id="TASK_A_ID" \
  waiting_on="TASK_B_ID"
```

### Workflow: Link Related Tasks (Non-Dependency)

For related tasks that aren't blocking each other:

```bash
# Link Task A to Task B (arbitrary relationship)
python skills/clickup/scripts/clickup_client.py link_tasks \
  task_id="TASK_A_ID" \
  links_to="TASK_B_ID"

# Remove link
python skills/clickup/scripts/clickup_client.py unlink_tasks \
  task_id="TASK_A_ID" \
  links_to="TASK_B_ID"
```

Note: `link_tasks` creates a "linked task" relationship (appears in task's "Linked Tasks" section), while `add_dependency` creates blocking/waiting relationships.

### Workflow: Bulk Task Operations

For bulk operations, loop through tasks:
```bash
# Get tasks
TASKS=$(python skills/clickup/scripts/clickup_client.py get_tasks list_id="xxx")

# Process each (parse JSON and loop)
```

## Script Reference

### scripts/clickup_client.py

Main CLI interface for ClickUp operations.

**Usage:**
```bash
python scripts/clickup_client.py <command> [key=value ...]
```

**Commands:**

#### Workspace Operations
- `get_teams` - List all accessible workspaces

#### Space Operations
- `get_spaces team_id="xxx"` - List spaces
- `create_space team_id="xxx" name="Name" [options...]` - Create space
- `update_space space_id="xxx" [options...]` - Update space

#### Folder Operations
- `get_folders space_id="xxx"` - List folders
- `create_folder space_id="xxx" name="Name"` - Create folder

#### List Operations
- `get_lists folder_id="xxx"` - Lists in folder
- `get_space_lists space_id="xxx"` - Folderless lists
- `create_list folder_id="xxx" name="Name" [options...]` - Create in folder
- `create_space_list space_id="xxx" name="Name" [options...]` - Create folderless

#### Task Operations
- `get_task task_id="xxx"` - Get task details (includes dependencies, linked tasks)
- `get_tasks list_id="xxx" [filters...]` - List tasks
- `create_task list_id="xxx" name="Name" [options...]` - Create task
- `update_task task_id="xxx" [options...]` - Update task

#### Time Tracking
- `get_time_entries team_id="xxx" [filters...]` - List entries
- `create_time_entry team_id="xxx" task_id="yyy" duration=3600000 [...]` - Create entry
- `start_timer team_id="xxx" task_id="yyy"` - Start timer
- `stop_timer team_id="xxx"` - Stop timer

#### Documents (API v3)
- `get_docs workspace_id="xxx"` - List documents
- `create_doc workspace_id="xxx" name="Name" [options...]` - Create document
- `get_doc doc_id="xxx"` - Get document details

**Note on Pages:** Doc pages API is in beta. Pages may need to be created via ClickUp UI.

#### Doc-Task Linking
- `link_doc_to_task task_id="xxx" doc_id="yyy"` - Attach doc URL to task
- `mention_doc_in_task task_id="xxx" doc_id="yyy"` - Add doc link to task description

#### Task Dependencies (Blocking/Waiting On)
- `add_dependency task_id="xxx" depends_on="yyy"` - Task is blocked by/waiting on another task
- `add_dependency task_id="xxx" waiting_on="yyy"` - Another task is blocked by/waiting on this task
- `remove_dependency task_id="xxx" depends_on="yyy"` - Remove dependency
- `get_dependencies task_id="xxx"` - List all dependencies for a task

#### Task Linking (Arbitrary Relationships)
- `link_tasks task_id="xxx" links_to="yyy"` - Create arbitrary link between tasks
- `unlink_tasks task_id="xxx" links_to="yyy"` - Remove task link

#### Reporting & Analytics
- `get_all_tasks team_id="xxx" [include_closed="true"] [space_ids='["id1"]'] [assignees='["uid1"]']` - All tasks with auto-pagination (always includes subtasks)
- `task_counts team_id="xxx" [filters...]` - Count breakdown: total, parents, subtasks, unassigned
- `assignee_breakdown team_id="xxx" [filters...]` - Workload distribution by assignee
- `status_breakdown team_id="xxx" [filters...]` - Tasks grouped by status
- `priority_breakdown team_id="xxx" [filters...]` - Tasks grouped by priority
- `standup_report team_id="xxx" [assignee_id="yyy"]` - Daily standup report grouped by status

#### Documents
- `get_docs team_id="xxx"` - List documents
- `create_doc team_id="xxx" name="Name" [options...]` - Create document

## Advanced Configuration

### Custom Fields

To work with custom fields:

1. Get field definitions: `GET /list/{list_id}/field` (see API Reference)
2. Set values when creating/updating tasks:
   ```bash
   python skills/clickup/scripts/clickup_client.py update_task \
     task_id="xxx" \
     'custom_fields=[{"id":"field_id","value":"value"}]'
   ```

### Status Configuration

When creating/updating spaces or lists:

```bash
python skills/clickup/scripts/clickup_client.py update_space \
  space_id="xxx" \
  'statuses=[{"status":"To Do","type":"open"},{"status":"Done","type":"closed"}]'
```

### Priority Levels

- `1` - Urgent
- `2` - High
- `3` - Normal
- `4` - Low

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid API token | Check CLICKUP_API_TOKEN |
| `404 Not Found` | Invalid ID | Verify workspace/space/folder/list/task IDs |
| `429 Too Many Requests` | Rate limit | Wait and retry (100 req/min limit) |
| `400 Bad Request` | Invalid parameters | Check JSON format in arguments |

## Python Client Usage

For complex operations, import the client directly:

```python
from skills.clickup.scripts.clickup_client import ClickUpClient

client = ClickUpClient()

# Get all workspaces
teams = client.get_teams()

# Create task with full control
task = client.create_task(
    list_id="123",
    name="Complex Task",
    description="Detailed description",
    assignees=[123, 456],
    tags=["urgent", "client"],
    priority=2,
    due_date=1704067200000,
    time_estimate=14400000
)
```

## References

- **API Details**: See [references/api_reference.md](references/api_reference.md) for complete endpoint documentation, request/response formats, and field types.
- **ClickUp API Docs**: https://clickup.com/api

## Best Practices

1. **Store IDs**: Workspace/space/folder/list IDs rarely change. Store them in `TOOLS.md` for quick reference.
2. **Custom Task IDs**: If using custom IDs, always include `custom_task_ids=true` and `team_id` in task operations.
3. **Rate Limiting**: Space out bulk operations to avoid 429 errors.
4. **Time Tracking**: Use milliseconds for all duration/timestamp values.
5. **Multi-Workspace**: Always double-check `team_id` when working across workspaces to avoid modifying wrong workspace.
