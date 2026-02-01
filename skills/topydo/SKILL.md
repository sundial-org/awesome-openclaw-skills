---
name: topydo
description: Manage todo.txt tasks using topydo CLI. Add, list, complete, prioritize, tag, and organize tasks with dependencies, due dates, recurrence, and projects. Use for any task management, todo lists, or when the user mentions tasks, todos, or todo.txt. Requires Python 3 and pip. Works on macOS, Linux, and Windows.
license: MIT
metadata:
  author: github.com/bastos
  version: "2.0"
---

# topydo - Todo.txt Task Manager

topydo is a powerful CLI for managing tasks in the todo.txt format. It supports dependencies, due dates, start dates, recurrence, priorities, projects, and contexts.

## Task Format Reference

```
(A) 2025-01-11 Task text +Project @Context due:2025-01-15 t:2025-01-10 rec:1w star:1
│   │          │         │        │        │             │            │      │
│   │          │         │        │        │             │            │      └─ Star marker
│   │          │         │        │        │             │            └─ Recurrence
│   │          │         │        │        │             └─ Start/threshold date
│   │          │         │        │        └─ Due date
│   │          │         │        └─ Context
│   │          │         └─ Project
│   │          └─ Task description
│   └─ Creation date
└─ Priority (A-Z)
```

## Installation

### Homebrew (macOS, preferred)
```bash
brew install topydo
```

### pip (all platforms)
```bash
pip3 install topydo
```

With optional features:
```bash
pip3 install 'topydo[columns,prompt,ical]'
```

### apt (Ubuntu/Debian)
```bash
sudo apt install python3-pip && pip3 install topydo
```

## Configuration

Config file locations (in order of precedence):
- `topydo.conf` or `.topydo` (current directory)
- `~/.topydo` or `~/.config/topydo/config`
- `/etc/topydo.conf`

Example `~/.topydo`:
```ini
[topydo]
filename = ~/todo.txt
archive_filename = ~/done.txt
colors = 1
identifiers = text

[add]
auto_creation_date = 1

[sort]
sort_string = desc:importance,due,desc:priority
ignore_weekends = 1
```

## Adding Tasks

Basic task:
```bash
topydo add "Buy groceries"
```

With priority (A is highest):
```bash
topydo add "(A) Urgent task"
```

With project and context:
```bash
topydo add "Write report +ProjectX @office"
```

With due date (absolute):
```bash
topydo add "Submit proposal due:2025-01-15"
```

With due date (relative):
```bash
topydo add "Call mom due:tomorrow"
```

With due date (weekday):
```bash
topydo add "Weekly review due:fri"
```

With start/threshold date:
```bash
topydo add "Future task t:2025-02-01"
```

With recurrence (weekly):
```bash
topydo add "Water plants due:sat rec:1w"
```

With strict recurrence (always on 1st of month):
```bash
topydo add "Pay rent due:2025-02-01 rec:+1m"
```

With dependency (must complete before task 1):
```bash
topydo add "Write tests before:1"
```

As subtask of task 1:
```bash
topydo add "Review code partof:1"
```

## Listing Tasks

List all relevant tasks:
```bash
topydo ls
```

Include hidden/blocked tasks:
```bash
topydo ls -x
```

Filter by project:
```bash
topydo ls +ProjectX
```

Filter by context:
```bash
topydo ls @office
```

Filter by priority:
```bash
topydo ls "(A)"
```

Filter by priority range:
```bash
topydo ls "(>C)"
```

Filter tasks due today:
```bash
topydo ls due:today
```

Filter overdue tasks:
```bash
topydo ls "due:<today"
```

Filter tasks due by Friday:
```bash
topydo ls "due:<=fri"
```

Combine multiple filters:
```bash
topydo ls +ProjectX @office due:today
```

Exclude context:
```bash
topydo ls -- -@waiting
```

Sort by priority:
```bash
topydo ls -s priority
```

Sort descending by due date, then priority:
```bash
topydo ls -s desc:due,priority
```

Group by project:
```bash
topydo ls -g project
```

Limit to 5 results:
```bash
topydo ls -n 5
```

Custom output format:
```bash
topydo ls -F "%I %p %s %{due:}d"
```

Output as JSON:
```bash
topydo ls -f json
```

## Completing Tasks

Complete task by ID:
```bash
topydo do 1
```

Complete multiple tasks:
```bash
topydo do 1 2 3
```

Complete all tasks due today:
```bash
topydo do -e due:today
```

Complete with custom date:
```bash
topydo do -d yesterday 1
```

## Priority Management

Set priority A:
```bash
topydo pri 1 A
```

Set priority for multiple tasks:
```bash
topydo pri 1 2 3 B
```

Remove priority:
```bash
topydo depri 1
```

## Tagging Tasks

Set due date:
```bash
topydo tag 1 due tomorrow
```

Star a task:
```bash
topydo tag 1 star 1
```

Remove a tag:
```bash
topydo tag 1 due
```

Set custom tag with relative date:
```bash
topydo tag -r 1 review 2w
```

## Modifying Tasks

Append text to task:
```bash
topydo append 1 "additional notes"
```

Append due date:
```bash
topydo append 1 due:friday
```

Edit task in text editor:
```bash
topydo edit 1
```

Edit all tasks in project:
```bash
topydo edit -e +ProjectX
```

## Deleting Tasks

Delete by ID:
```bash
topydo del 1
```

Delete multiple:
```bash
topydo del 1 2 3
```

Delete by expression:
```bash
topydo del -e completed:today
```

## Dependencies

Add dependency (task 2 depends on task 1):
```bash
topydo dep add 2 to 1
```

Task 2 is part of task 1:
```bash
topydo dep add 2 partof 1
```

List what depends on task 1:
```bash
topydo dep ls 1 to
```

List what task 1 depends on:
```bash
topydo dep ls to 1
```

Remove dependency:
```bash
topydo dep rm 2 to 1
```

Visualize dependencies (requires graphviz):
```bash
topydo dep dot 1 | dot -Tpng -o deps.png
```

## Postponing Tasks

Postpone by 1 week:
```bash
topydo postpone 1 1w
```

Postpone by 3 days:
```bash
topydo postpone 1 3d
```

Postpone including start date:
```bash
topydo postpone -s 1 1w
```

## Other Commands

Sort the todo.txt file:
```bash
topydo sort
```

Revert last command:
```bash
topydo revert
```

Show revert history:
```bash
topydo revert ls
```

List all projects:
```bash
topydo lsprj
```

List all contexts:
```bash
topydo lscon
```

Archive completed tasks:
```bash
topydo archive
```

## Relative Dates

- `today`, `tomorrow`, `yesterday`
- Weekdays: `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`
- Periods: `1d` (days), `2w` (weeks), `3m` (months), `1y` (years)
- Business days: `5b` (excludes weekends)

## Sort/Group Fields

- `priority`, `due`, `creation`, `completed`
- `importance`, `importance-avg`
- `project`, `context`, `text`, `length`

Prefix with `desc:` for descending. Example: `desc:importance,due`

## Tips

- Use a clean, human-readable format to present results to the user
- Enable stable text IDs: set `identifiers = text` in config
- Star important tasks: add `star:1` tag
- Hidden tags by default: `id`, `p`, `ical`
- Importance = priority + due date proximity + star status
