#!/bin/bash
# ClickUp API Query Helper
# Handles pagination, subtasks, and common query patterns

set -euo pipefail

# Check for required environment variables
if [ -z "${CLICKUP_API_KEY:-}" ]; then
    echo "Error: CLICKUP_API_KEY not set" >&2
    exit 1
fi

if [ -z "${CLICKUP_TEAM_ID:-}" ]; then
    echo "Error: CLICKUP_TEAM_ID not set" >&2
    exit 1
fi

# Usage function
usage() {
    cat << EOF
Usage: $0 <command> [options]

Commands:
  tasks              Get all open tasks (with pagination)
  task-count         Count open tasks (parent vs subtasks)
  assignees          List task count by assignee
  task <task-id>     Get specific task details
  spaces             List all spaces
  lists              List all lists in a space
  
Options:
  --include-closed   Include closed tasks
  --space <id>       Filter by space ID
  --list <id>        Filter by list ID
  
Examples:
  $0 tasks
  $0 task-count
  $0 assignees
  $0 task 901612795398
  $0 tasks --space 90165825353

Environment variables required:
  CLICKUP_API_KEY    Your ClickUp API token
  CLICKUP_TEAM_ID    Your team/workspace ID
EOF
    exit 1
}

# API call helper
clickup_api() {
    local endpoint="$1"
    curl -s "https://api.clickup.com/api/v2${endpoint}" \
        -H "Authorization: ${CLICKUP_API_KEY}"
}

# Get all tasks with pagination
get_all_tasks() {
    local include_closed="${1:-false}"
    local all_tasks="[]"
    local page=0
    local last_page="false"
    
    while [ "$last_page" = "false" ]; do
        local result=$(clickup_api "/team/${CLICKUP_TEAM_ID}/task?include_closed=${include_closed}&subtasks=true&page=${page}")
        
        # Merge tasks
        all_tasks=$(echo "$all_tasks $result" | jq -s '.[0] + .[1].tasks')
        
        # Check if last page
        last_page=$(echo "$result" | jq -r '.last_page')
        
        if [ "$last_page" = "true" ]; then
            break
        fi
        
        ((page++))
    done
    
    echo "{\"tasks\": $all_tasks, \"total\": $(echo "$all_tasks" | jq 'length')}"
}

# Count tasks by type
task_count() {
    local tasks=$(get_all_tasks false)
    
    echo "$tasks" | jq '{
        total: .total,
        parent_tasks: ([.tasks[] | select(.parent == null)] | length),
        subtasks: ([.tasks[] | select(.parent != null)] | length)
    }'
}

# Get assignee breakdown
assignee_breakdown() {
    local tasks=$(get_all_tasks false)
    
    echo "$tasks" | jq -r '.tasks[] | 
        if .assignees and (.assignees | length) > 0 
        then .assignees[0].username 
        else "Unassigned" 
        end' | sort | uniq -c | sort -rn | \
        awk '{printf "{\"assignee\": \"%s\", \"count\": %d}\n", substr($0, index($0,$2)), $1}'
}

# Get specific task
get_task() {
    local task_id="$1"
    clickup_api "/task/${task_id}"
}

# List spaces
list_spaces() {
    clickup_api "/team/${CLICKUP_TEAM_ID}/space" | jq '.spaces'
}

# List lists in a space
list_lists() {
    local space_id="$1"
    clickup_api "/space/${space_id}/list" | jq '.lists'
}

# Main command routing
case "${1:-}" in
    tasks)
        shift
        include_closed="false"
        if [ "${1:-}" = "--include-closed" ]; then
            include_closed="true"
        fi
        get_all_tasks "$include_closed"
        ;;
    task-count)
        task_count
        ;;
    assignees)
        assignee_breakdown
        ;;
    task)
        if [ -z "${2:-}" ]; then
            echo "Error: task ID required" >&2
            usage
        fi
        get_task "$2"
        ;;
    spaces)
        list_spaces
        ;;
    lists)
        if [ -z "${2:-}" ]; then
            echo "Error: space ID required" >&2
            usage
        fi
        list_lists "$2"
        ;;
    *)
        usage
        ;;
esac
