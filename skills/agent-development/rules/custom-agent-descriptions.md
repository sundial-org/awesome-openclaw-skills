---
globs: ["**/agents/*.md", "**/.claude/agents/*"]
---

# Custom Agent Description Pattern

When creating custom agents in `.claude/agents/`, the description field determines whether Claude will automatically delegate tasks to the agent.

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `description: "Analyzes screenshots for issues"` | `description: "Visual QA specialist. MUST BE USED when analyzing screenshots. Use PROACTIVELY for any visual QA task."` |
| `description: "Runs Playwright scripts"` | `description: "Playwright specialist. MUST BE USED when running Playwright scripts. Use PROACTIVELY for browser automation."` |
| Weak/passive descriptions | Strong trigger phrases with "MUST BE USED" and "Use PROACTIVELY" |

## Pattern

```yaml
---
name: agent-name
description: "[Role] specialist. MUST BE USED when [specific triggers]. Use PROACTIVELY for [task category]."
tools: [tool list]
model: sonnet
---
```

## Why This Matters

Claude Code has two delegation mechanisms:
1. **Explicit**: `Task tool subagent_type: "agent-name"` - always works
2. **Automatic**: Claude matches task descriptions to agent descriptions - requires strong phrasing

Without "MUST BE USED" and "Use PROACTIVELY", automatic delegation may not trigger even when the task matches.

## Session Restart Required

After creating or modifying agents, restart the Claude Code session. Agents are loaded at session start and won't appear in available subagent_types until restart.

## Pipeline Agents: Update Predecessor

When inserting a new agent into a numbered pipeline (e.g., `HTML-01` → `HTML-05` → `HTML-11`):

| Must Update | What |
|-------------|------|
| New agent | "Workflow Position" diagram + "Next" field |
| **Predecessor agent** | Its "Next" field to point to new agent |

**Common bug**: New agent has correct position, but predecessor still points to the old next agent. The new agent is "orphaned" and gets skipped.

**Verification**:
```bash
grep -n "Next:.*→\|Then.*runs next" .claude/agents/*.md
```

Every pipeline agent should point to exactly one successor.
