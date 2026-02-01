---
name: lobster
description: >
  Lobster workflow runtime for deterministic pipelines with approval gates.
  Use when: (1) Running multi-step automations that need human approval before side effects,
  (2) Monitoring PRs/issues for changes, (3) Processing data through typed JSON pipelines,
  (4) Email triage or batch operations, (5) Any workflow that should halt and ask before acting.
  Lobster saves tokens by running deterministic pipelines instead of re-planning each step.
---

# Lobster

> **Contribute:** Source code & PRs welcome at [github.com/guwidoe/lobster-skill](https://github.com/guwidoe/lobster-skill)

Workflow runtime for AI agents — typed pipelines with approval gates.

## CLI Location

```bash
# Set alias (adjust path to your install location)
LOBSTER="node /home/molt/clawd/tools/lobster/bin/lobster.js"

# Or install globally: npm install -g @clawdbot/lobster
# Then use: lobster '<pipeline>'
```

## Quick Reference

```bash
# Run pipeline (human mode - pretty output)
$LOBSTER '<pipeline>'

# Run pipeline (tool mode - JSON envelope for integration)
$LOBSTER run --mode tool '<pipeline>'

# Run workflow file
$LOBSTER run path/to/workflow.lobster

# Resume after approval
$LOBSTER resume --token "<token>" --approve yes|no

# List commands/workflows
$LOBSTER commands.list
$LOBSTER workflows.list
```

## Core Commands

| Command | Purpose |
|---------|---------|
| `exec --json --shell "cmd"` | Run shell, parse stdout as JSON |
| `where 'field=value'` | Filter objects |
| `pick field1,field2` | Project fields |
| `head --n 5` | Take first N items |
| `sort --key field --desc` | Sort items |
| `groupBy --key field` | Group by key |
| `dedupe --key field` | Remove duplicates |
| `map --wrap key` | Transform items |
| `template --text "{{field}}"` | Render templates |
| `approve --prompt "ok?"` | **Halt for approval** |
| `diff.last --key "mykey"` | Compare to last run (stateful) |
| `state.get key` / `state.set key` | Read/write persistent state |
| `json` / `table` | Render output |

## Built-in Workflows

```bash
# Monitor PR for changes (stateful - remembers last state)
$LOBSTER "workflows.run --name github.pr.monitor --args-json '{\"repo\":\"owner/repo\",\"pr\":123}'"

# Monitor PR and emit message only on change
$LOBSTER "workflows.run --name github.pr.monitor.notify --args-json '{\"repo\":\"owner/repo\",\"pr\":123}'"
```

## Approval Flow (Tool Mode)

When a pipeline hits `approve`, it returns:

```json
{
  "status": "needs_approval",
  "requiresApproval": {
    "prompt": "Send 3 emails?",
    "items": [...],
    "resumeToken": "eyJ..."
  }
}
```

To continue:
```bash
$LOBSTER resume --token "eyJ..." --approve yes
```

## Example Pipelines

```bash
# List recent PRs, filter merged, show as table
$LOBSTER 'exec --json --shell "gh pr list --repo owner/repo --json number,title,state --limit 20" | where "state=MERGED" | table'

# Get data, require approval, then process
$LOBSTER run --mode tool 'exec --json --shell "echo [{\"id\":1},{\"id\":2}]" | approve --prompt "Process these?" | pick id | json'

# Diff against last run (only emit on change)
$LOBSTER 'exec --json --shell "gh pr view 123 --repo o/r --json state,title" | diff.last --key "pr:o/r#123" | json'
```

## Workflow Files (.lobster)

YAML/JSON files with steps, conditions, and approval gates:

```yaml
name: pr-review-reminder
steps:
  - id: fetch
    command: gh pr list --repo ${repo} --json number,title,reviewDecision
  - id: filter
    command: jq '[.[] | select(.reviewDecision == "")]'
    stdin: $fetch.stdout
  - id: notify
    command: echo "PRs needing review:" && cat
    stdin: $filter.stdout
    approval: required
```

Run: `$LOBSTER run workflow.lobster --args-json '{"repo":"owner/repo"}'`

## Clawdbot Integration

Lobster can call Clawdbot tools via `clawd.invoke`:

```bash
$LOBSTER 'clawd.invoke --tool message --action send --args-json "{\"target\":\"123\",\"message\":\"hello\"}"'
```

Requires `CLAWD_URL` and `CLAWD_TOKEN` environment variables.

## State Directory

Lobster stores state in `~/.lobster/state/` by default. Override with `LOBSTER_STATE_DIR`.
