---
name: dex
description: Task tracking for async/multi-step work. Use dex to create, track, and complete tasks that span multiple sessions or require coordination (e.g., coding agent dispatches, PR reviews, background jobs). Tasks stored as JSON files in .dex/tasks/.
---

# Dex Task Tracking

Track async work: coding agent dispatches, multi-step projects, anything needing follow-up.

## Commands
```bash
dex create -d "Description" --context "Background, goal, done-when"
dex list                    # Pending tasks
dex list --all              # Include completed
dex show <id>               # View task
dex show <id> --full        # Full context
dex complete <id> --result "What was done, decisions, follow-ups"
dex edit <id> --context "Updated context"
dex delete <id>
```

## Task Structure
- **Description**: One-line summary
- **Context**: Background, requirements, done criteria
- **Result**: What was built, decisions, follow-ups

## Example
```bash
# Before dispatching agent
dex create -d "Add caching to API" --context "Workspace: feat1 (100.x.x.x)
Branch: feat/cache
Done when: PR merged, CI green"

# After work complete
dex complete abc123 --result "Merged PR #50. Redis caching with 5min TTL."
```

## Storage
`.dex/tasks/{id}.json` — one file per task, git-friendly.
