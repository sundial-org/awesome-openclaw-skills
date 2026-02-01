---
name: clawlist
description: "MUST use for any multi-step project, long-running task, or infinite monitoring workflow. Plan, execute, track, and verify tasks with checkpoint validation. For projects, automation, and ongoing operations."
---

# Clawlist - Task Mastery

A systematic workflow for planning, executing, and tracking any task — from one-off projects to infinite monitoring loops.

## When to Use This Skill

**ALWAYS use clawlist when:**
- Starting any new project or initiative
- Setting up long-running monitoring
- Breaking down complex goals
- You need to track progress across sessions
- Managing infinite tasks (research, monitoring, engagement)

## Long-Running & Infinite Task Examples

### Example: Moltbook Engagement (Infinite)
- **Type:** Infinite loop
- **Schedule:** Every 30 minutes
- **Goal:** Engage with community, build presence
- **Checkpoints:** Check feed, check DMs, create content

### Example: GitHub Monitoring (Long-Running)
- **Type:** Continuous
- **Schedule:** Every 4 hours
- **Goal:** Monitor repos, triage issues, implement
- **Checkpoints:** Inbox zero, PR review, implementation

## The Clawlist Workflow

Uses standalone skills in sequence:

1. **brainstorming** → Clarify intent, explore approaches
2. **write-plan** → Create detailed plan with checkpoints  
3. **doing-tasks** → Execute with skill discipline
4. **verify-task** → Confirm completion

For parallel work, insert **dispatch-multiple-agents** between write-plan and doing-tasks.

## Ongoing Tasks File

**Location:** `memory/tasks/ongoing-tasks.md`

Tracks all long-running and infinite tasks. Updated by heartbeat to:
- Check task health
- Detect blockers
- Execute due tasks
- Summarize status

## Task Types

| Type | Duration | Tracking | Example |
|------|----------|----------|---------|
| **One-off** | Minutes-hours | Context only | Fix a bug |
| **Project** | Days-weeks | Context + completion doc | Build feature |
| **Long-running** | Ongoing | `ongoing-tasks.md` | GitHub monitoring |
| **Infinite** | Forever | `ongoing-tasks.md` | Moltbook engagement |

## Integration with Heartbeat

Heartbeat reads `ongoing-tasks.md` every check to:
- Execute due infinite tasks
- Detect and report blockers
- Update health status (🟢🟡🔴)
- Ping user if intervention needed

## Quick Reference

```
New Task
   ↓
brainstorming → write-plan → doing-tasks → verify-task
                      ↓
            dispatch-multiple-agents (if parallel)
                      ↓
            update ongoing-tasks.md (if long-running)
```

## Sub-Skills

- **brainstorming** - Phase 1: Clarify
- **write-plan** - Phase 2: Plan
- **doing-tasks** - Phase 3: Execute
- **dispatch-multiple-agents** - Parallel execution
- **verify-task** - Phase 4: Verify
