---
name: timesheet
description: Track time, manage projects and tasks using timesheet.io CLI
user-invocable: true
homepage: https://timesheet.io
metadata: {"requires": {"bins": ["timesheet"]}}
---

# Timesheet CLI Skill

Control timesheet.io time tracking from the command line. Use `--json` flag for all commands to get structured output.

## Authentication

Check auth status before using other commands:
```bash
timesheet auth status --json
```

If not authenticated, guide the user to run:
```bash
timesheet auth login
```

Or for automation, set an API key:
```bash
export TIMESHEET_API_KEY=ts_your.apikey
```

## Timer Operations

### Start a Timer
```bash
# List projects first to get project ID
timesheet projects list --json

# Start timer for a project
timesheet timer start <project-id>
```

### Check Timer Status
```bash
timesheet timer status --json
```

Returns: status (running/paused/stopped), project name, duration, start time.

### Control Timer
```bash
timesheet timer pause
timesheet timer resume
timesheet timer stop  # Creates a task from the timer
```

### Update Running Timer
```bash
timesheet timer update --description "Working on feature X"
timesheet timer update --billable
```

## Project Management

### List Projects
```bash
timesheet projects list --json
```

### Create Project
```bash
timesheet projects create "Project Name" --json
timesheet projects create "Client Project" --billable --json
```

### Show/Update/Delete
```bash
timesheet projects show <id> --json
timesheet projects update <id> --title "New Name"
timesheet projects delete <id>
```

## Task Management

### List Tasks
```bash
timesheet tasks list --json           # Recent tasks
timesheet tasks list --today --json   # Today's tasks
timesheet tasks list --this-week --json
```

### Create Task Manually
```bash
timesheet tasks create -p <project-id> -s "2024-01-15 09:00" -e "2024-01-15 17:00" --json
timesheet tasks create -p <project-id> -s "09:00" -e "17:00" -d "Task description" --json
```

### Update Task
```bash
timesheet tasks update <id> --description "Updated description"
timesheet tasks update <id> --billable
timesheet tasks update <id> --start "10:00" --end "12:00"
```

### Delete Task
```bash
timesheet tasks delete <id>
```

## Teams & Tags

### Teams
```bash
timesheet teams list --json
```

### Tags
```bash
timesheet tags list --json
timesheet tags create "Urgent" --color 1
timesheet tags delete <id>
```

## Reports

### Time Summary
```bash
timesheet reports summary --today --json
timesheet reports summary --this-week --json
timesheet reports summary --this-month --json
timesheet reports summary --from 2024-01-01 --to 2024-01-31 --json
```

### Export Data
```bash
timesheet reports export -f xlsx -s 2024-01-01 -e 2024-01-31
timesheet reports export -f csv --this-month
```

## Profile & Config

```bash
timesheet profile show --json
timesheet profile settings --json

timesheet config show
timesheet config set defaultProjectId <id>
```

## Common Workflows

### Log Time for Current Work
1. Check if timer is running: `timesheet timer status --json`
2. If not, start timer: `timesheet timer start <project-id>`
3. When done, stop timer: `timesheet timer stop`

### Quick Time Entry
```bash
# Create a completed task directly
timesheet tasks create -p <project-id> -s "09:00" -e "12:00" -d "Morning standup and dev work" --json
```

### Find Project by Name
```bash
timesheet projects list --json | jq '.[] | select(.title | contains("ProjectName"))'
```

## Error Handling

Exit codes:
- 0: Success
- 1: General error
- 2: Usage error (invalid arguments)
- 3: Authentication error - run `timesheet auth login`
- 4: API error
- 5: Rate limit exceeded - wait and retry
- 6: Network error

## Tips

- Always use `--json` for parsing output programmatically
- Use `--quiet` or `-q` to suppress non-essential output
- Set `defaultProjectId` in config to skip project selection for timer
- Pipe-friendly output is automatic when not in a terminal
