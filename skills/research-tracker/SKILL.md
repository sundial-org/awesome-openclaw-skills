---
name: research-tracker
description: Manage autonomous AI research agents with SQLite-based state tracking. Use when spawning long-running research sub-agents, tracking multi-step investigations, coordinating agent handoffs, or monitoring background work. Triggers on: research projects, sub-agent coordination, autonomous investigation, progress tracking, agent oversight.
---

# Research Tracker

CLI tool for managing autonomous research agents with append-only state, instruction queues, and oversight.

## Prerequisites

```bash
brew tap 1645labs/tap
brew install julians-research-tracker
```

Or: `go install github.com/1645labs/julians-research-tracker/cmd/research@latest`

## Quick Start

### Start a research project
```bash
research init market-q1 --name "Q1 Market Analysis" --objective "Analyze competitor pricing and positioning"
```

### As the research agent — log progress
```bash
export RESEARCH_SESSION_ID="$SESSION_KEY"  # Track which agent is writing

research log market-q1 STEP_BEGIN --step 1 --payload '{"task":"gather sources"}'
# ... do work ...
research log market-q1 STEP_COMPLETE --step 1
research heartbeat market-q1
```

### Check status (from main session or heartbeat)
```bash
research status market-q1 --json
research context market-q1 --last 5  # Truncated context for prompts
```

### Send instructions to running agent
```bash
research instruct market-q1 "Focus on enterprise segment" --priority URGENT
research stop-signal market-q1  # Request graceful stop
```

### Agent checks for instructions
```bash
research pending market-q1 --json
research ack market-q1 --all  # Acknowledge after processing
research check-stop market-q1  # Exit 0 = stop, Exit 1 = continue
```

## Commands Reference

| Command | Purpose |
|---------|---------|
| `init <id> -o "..."` | Create project with objective |
| `list [--status active\|done\|all]` | List projects (includes `needs_attention` flag) |
| `show <id>` | Project details + recent events |
| `stop <id>` | Stop project, send STOP instruction |
| `archive <id>` | Archive completed project |
| `log <id> <event> [--step N]` | Log event (STEP_BEGIN, CHECKPOINT, BLOCKED, etc.) |
| `heartbeat <id>` | Update alive timestamp |
| `block <id> --reason "..."` | Mark blocked, needs input |
| `complete <id>` | Mark done |
| `status <id> [--json]` | Current state summary |
| `context <id> [--last N]` | Truncated context for agent prompts |
| `instruct <id> "text"` | Send instruction |
| `pending <id>` | List unacked instructions |
| `ack <id> [--all]` | Acknowledge instructions |
| `check-stop <id>` | Exit code: 0=stop, 1=continue |
| `audit <id> --verdict pass\|drift` | Log audit result |

## Event Types

`STARTED`, `STEP_BEGIN`, `STEP_COMPLETE`, `CHECKPOINT`, `BLOCKED`, `UNBLOCKED`, `AUDIT_PASS`, `AUDIT_DRIFT`, `HEARTBEAT`, `DONE`, `STOPPED`, `TIMEOUT`

## Integration Pattern

### Spawning a research agent

```
1. research init <project> --objective "..."
2. sessions_spawn with task including:
   - Project ID and objective
   - Instructions to use research CLI for state
   - Check stop signal before each step
   - Log progress with heartbeat
3. Heartbeat monitors: research list --json | check needs_attention
4. Send instructions via: research instruct <project> "..."
```

### Agent loop (in spawned agent)

```bash
while research check-stop $PROJECT; [ $? -eq 1 ]; do
  research pending $PROJECT --json  # Check instructions
  research log $PROJECT STEP_BEGIN --step $STEP
  # ... do work ...
  research log $PROJECT STEP_COMPLETE --step $STEP
  research heartbeat $PROJECT
  STEP=$((STEP + 1))
done
research complete $PROJECT
```

## Attention Detection

`research list --json` includes `needs_attention: true` when:
- Last event is BLOCKED
- Has unacked URGENT or STOP instructions
- Heartbeat stale (>5 min since last HEARTBEAT event)
- Last audit was AUDIT_DRIFT

## Database

SQLite at `~/.config/research-tracker/research.db` (WAL mode, append-only events).

Run `research db migrate` after install. Schema auto-migrates on first use.
