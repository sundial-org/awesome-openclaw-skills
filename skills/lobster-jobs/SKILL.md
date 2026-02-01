---
name: lobster-jobs
description: Transform OpenClaw cron jobs into Lobster workflows. Analyze, inspect, and validate job migrations. Use when converting automations to deterministic, approval-gated workflows with resume capabilities.
metadata:
  openclaw:
    emoji: 🦞
    requires:
      bins: ["openclaw", "python3"]
---

# lobster-jobs

Transform OpenClaw cron jobs into Lobster workflows with approval gates and resumable execution.

## Purpose

OpenClaw cron jobs are either:
- **systemEvent**: Simple shell commands (fully deterministic)
- **agentTurn**: Natural language instructions spawning AI agents (flexible but token-heavy)

Lobster workflows offer:
- **Deterministic execution**: No LLM re-planning each step
- **Approval gates**: Hard stops requiring explicit user approval
- **Stateful execution**: Remembers cursors/checkpoints
- **Resumability**: Pauses and resumes exactly where left off

This skill helps analyze existing cron jobs and transform them into Lobster workflows.

## Commands

### Tier 1 (Available Now)

#### `lobster-jobs list`
List all cron jobs with their Lobster readiness score.

Output categories:
- ✅ **Fully Migratable**: Simple shell commands (systemEvent)
- 🟡 **Partial Migration**: Mixed deterministic + LLM steps (agentTurn)
- ❌ **Not Migratable**: Heavy LLM reasoning required

#### `lobster-jobs inspect <job-id>`
Inspect a specific cron job with detailed migration assessment.

Shows:
- Job metadata (schedule, target, payload type)
- Lobster migration status and reason
- Payload preview
- Migration recommendation

#### `lobster-jobs validate <workflow-file>`
Validate a Lobster workflow YAML file against schema.

Checks:
- Required fields (name, steps)
- Step structure (id, command)
- Approval gate syntax
- Condition syntax

### Tier 2 (Available Now)

#### `lobster-jobs convert <job-id>`
Transform a cron job into a Lobster workflow.

```bash
lobster-jobs convert 17fe68ca
lobster-jobs convert 17fe68ca --output-dir ~/workflows
lobster-jobs convert 17fe68ca --force  # Overwrite existing
```

Generates:
- `.lobster` workflow file in `~/.lobster/workflows/`
- Extracts commands from systemEvent or agentTurn payloads
- Auto-validates generated workflow

Options:
- `--output-dir, -o`: Custom output directory
- `--force, -f`: Overwrite existing workflow
- `--keep-on-error`: Keep file even if validation fails

#### `lobster-jobs new <name>`
Create a new Lobster workflow from scratch using templates.

```bash
lobster-jobs new my-workflow
lobster-jobs new my-workflow --template with-approval
lobster-jobs new my-workflow --template stateful
```

Templates:
- `simple-shell`: Basic command execution
- `with-approval`: Approval gate workflow
- `stateful`: Workflow with cursor/state tracking

## Installation

```bash
# Add to PATH
export PATH="$PATH:/home/art/niemand/skills/lobster-jobs/bin"

# Or create symlink
ln -s /home/art/niemand/skills/lobster-jobs/bin/lobster-jobs ~/.local/bin/
```

## Quick Start

```bash
# See all your cron jobs and their migration status
lobster-jobs list

# Inspect a specific job
lobster-jobs inspect 17fe68ca

# Convert a job to Lobster workflow
lobster-jobs convert 17fe68ca

# Create a new workflow from template
lobster-jobs new my-workflow --template with-approval

# Validate a workflow file
lobster-jobs validate ~/.lobster/workflows/my-workflow.lobster
```

## Workflow File Format

```yaml
name: my-workflow
description: Optional description

steps:
  - id: fetch_data
    command: some-cli fetch --json
    
  - id: process
    command: some-cli process
    stdin: $fetch_data.stdout
    
  - id: approve_send
    command: approve --prompt "Send notification?"
    approval: required
    
  - id: send
    command: message.send --channel telegram --text "Done!"
    condition: $approve_send.approved
```

## Migration Strategy

### Wrapper Approach (Recommended)
Keep cron as scheduler, change payload to call Lobster:

```json
{
  "payload": {
    "kind": "systemEvent",
    "text": "lobster run ~/.lobster/workflows/my-workflow.lobster"
  }
}
```

Benefits:
- Rollback is trivial (revert payload)
- Incremental migration
- Cron scheduling already works

## Handling LLM Judgment

For jobs needing both deterministic steps and LLM reasoning:

```yaml
steps:
  - id: gather
    command: gh issue list --json title,body
    
  - id: triage
    command: clawd.invoke
    prompt: "Classify these issues by urgency"
    
  - id: notify
    command: telegram-send
```

The workflow is deterministic; the LLM is a black-box step.

## Edge Cases

| Issue | Handling |
|-------|----------|
| **Idempotency** | Workflows track step completion; restart-safe |
| **Approval timeouts** | Configurable timeout with default action |
| **Secret handling** | Environment variables or 1Password refs |
| **Partial failures** | `convert` validates before writing |

## References

- Lobster: https://github.com/openclaw/lobster
- Lobster VISION: https://github.com/openclaw/lobster/blob/main/VISION.md
