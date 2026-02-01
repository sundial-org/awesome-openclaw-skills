# ClickUp API Reference

## Critical Best Practices

### ALWAYS Include Subtasks

**Rule:** ALWAYS add `subtasks=true` to task queries

```bash
# ✅ CORRECT
curl "https://api.clickup.com/api/v2/team/{team_id}/task?subtasks=true" \
  -H "Authorization: {api_key}"

# ❌ WRONG - Missing subtasks parameter
curl "https://api.clickup.com/api/v2/team/{team_id}/task" \
  -H "Authorization: {api_key}"
```

**Why:** Without `subtasks=true`, you only get parent tasks, missing potentially 70%+ of actual work items.

### Handle Pagination

**Rule:** ClickUp API returns max 100 tasks per page - loop until `last_page: true`

```bash
page=0
while true; do
    result=$(curl -s "https://api.clickup.com/api/v2/team/{team_id}/task?subtasks=true&page=$page" \
        -H "Authorization: {api_key}")
    
    # Process tasks...
    echo "$result" | jq '.tasks[]'
    
    # Check if last page
    is_last=$(echo "$result" | jq -r '.last_page')
    if [ "$is_last" = "true" ]; then
        break
    fi
    
    ((page++))
done
```

**Why:** Large workspaces can have 300+ tasks. One page only shows first 100.

### Parent vs Subtask Detection

```bash
# Get parent tasks only
jq '.tasks[] | select(.parent == null)'

# Get subtasks only
jq '.tasks[] | select(.parent != null)'

# Count breakdown
jq '{
    total: (.tasks | length),
    parents: ([.tasks[] | select(.parent == null)] | length),
    subtasks: ([.tasks[] | select(.parent != null)] | length)
}'
```

## Common Query Patterns

### Get All Open Tasks

```bash
curl "https://api.clickup.com/api/v2/team/{team_id}/task?include_closed=false&subtasks=true" \
  -H "Authorization: {api_key}"
```

### Get Task Count by Assignee

```bash
curl -s "https://api.clickup.com/api/v2/team/{team_id}/task?include_closed=false&subtasks=true" \
  -H "Authorization: {api_key}" | \
jq -r '.tasks[] | 
    if .assignees and (.assignees | length) > 0 
    then .assignees[0].username 
    else "Unassigned" 
    end' | sort | uniq -c | sort -rn
```

### Get Specific Task Details

```bash
curl "https://api.clickup.com/api/v2/task/{task_id}" \
  -H "Authorization: {api_key}"
```

### List Spaces

```bash
curl "https://api.clickup.com/api/v2/team/{team_id}/space" \
  -H "Authorization: {api_key}" | jq '.spaces'
```

### List Lists in a Space

```bash
curl "https://api.clickup.com/api/v2/space/{space_id}/list" \
  -H "Authorization: {api_key}" | jq '.lists'
```

### Create a Task

```bash
curl "https://api.clickup.com/api/v2/list/{list_id}/task" \
  -X POST \
  -H "Authorization: {api_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Task Name",
    "description": "Task description",
    "assignees": [user_id],
    "status": "to do",
    "priority": 3
  }'
```

### Update a Task

```bash
curl "https://api.clickup.com/api/v2/task/{task_id}" \
  -X PUT \
  -H "Authorization: {api_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "status": "in progress"
  }'
```

## API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/team/{team_id}/task` | GET | Get all tasks (with pagination) |
| `/task/{task_id}` | GET | Get specific task |
| `/task/{task_id}` | PUT | Update task |
| `/task/{task_id}` | DELETE | Delete task |
| `/list/{list_id}/task` | POST | Create task |
| `/team/{team_id}/space` | GET | List spaces |
| `/space/{space_id}/list` | GET | List lists |
| `/list/{list_id}` | GET | Get list details |

## Response Structure

### Task Object

```json
{
  "id": "task_id",
  "name": "Task name",
  "description": "Task description",
  "status": {
    "status": "to do",
    "color": "#d3d3d3"
  },
  "assignees": [
    {
      "id": 123,
      "username": "user@example.com",
      "email": "user@example.com"
    }
  ],
  "parent": "parent_task_id",  // null if parent task
  "priority": {
    "priority": "urgent",
    "color": "#f50000"
  },
  "due_date": "1609459200000",  // Unix timestamp in ms
  "list": {
    "id": "list_id",
    "name": "List Name"
  },
  "url": "https://app.clickup.com/t/task_id"
}
```

## Common Gotchas

1. **Pagination:** Don't forget to loop through all pages
2. **Subtasks:** Always include `subtasks=true` for accurate counts
3. **Timestamps:** ClickUp uses Unix timestamps in milliseconds (not seconds)
4. **Parent field:** `null` means it's a parent task, not empty string
5. **Rate limits:** 100 requests per minute per API token

## Helper Script

Use `scripts/clickup-query.sh` for common operations:

```bash
# Set environment variables first
export CLICKUP_API_KEY="pk_..."
export CLICKUP_TEAM_ID="90161392624"

# Get all tasks
./scripts/clickup-query.sh tasks

# Count tasks
./scripts/clickup-query.sh task-count

# Get assignee breakdown
./scripts/clickup-query.sh assignees

# Get specific task
./scripts/clickup-query.sh task 901612795398
```
