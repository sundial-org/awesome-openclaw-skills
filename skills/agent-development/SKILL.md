---
name: agent-development
description: |
  Design and build custom Claude Code agents with effective descriptions, tool access patterns,
  and self-documenting prompts. Covers Task tool delegation, model selection, memory limits,
  and declarative instruction design.

  Use when: creating custom agents, designing agent descriptions for auto-delegation,
  troubleshooting agent memory issues, or building agent pipelines.
license: MIT
---

# Agent Development for Claude Code

Build effective custom agents for Claude Code with proper delegation, tool access, and prompt design.

## Agent Description Pattern

The description field determines whether Claude will automatically delegate tasks.

### Strong Trigger Pattern

```yaml
---
name: agent-name
description: |
  [Role] specialist. MUST BE USED when [specific triggers].
  Use PROACTIVELY for [task category].
  Keywords: [trigger words]
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
---
```

### Weak vs Strong Descriptions

| Weak (won't auto-delegate) | Strong (auto-delegates) |
|---------------------------|-------------------------|
| "Analyzes screenshots for issues" | "Visual QA specialist. MUST BE USED when analyzing screenshots. Use PROACTIVELY for visual QA." |
| "Runs Playwright scripts" | "Playwright specialist. MUST BE USED when running Playwright scripts. Use PROACTIVELY for browser automation." |

**Key phrases**:
- "MUST BE USED when..."
- "Use PROACTIVELY for..."
- Include trigger keywords

### Delegation Mechanisms

1. **Explicit**: `Task tool subagent_type: "agent-name"` - always works
2. **Automatic**: Claude matches task to agent description - requires strong phrasing

**Session restart required** after creating/modifying agents.

## Tool Access Principle

**If an agent doesn't need Bash, don't give it Bash.**

| Agent needs to... | Give tools | Don't give |
|-------------------|------------|------------|
| Create files only | Read, Write, Edit, Glob, Grep | Bash |
| Run scripts/CLIs | Read, Write, Edit, Glob, Grep, Bash | — |
| Read/audit only | Read, Glob, Grep | Write, Edit, Bash |

**Why?** Models default to `cat > file << 'EOF'` heredocs instead of Write tool. Each bash command requires approval, causing dozens of prompts per agent run.

### Allowlist Pattern

Instead of restricting Bash, allowlist safe commands in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Write", "Edit", "WebFetch(domain:*)",
      "Bash(cd *)", "Bash(cp *)", "Bash(mkdir *)", "Bash(ls *)",
      "Bash(cat *)", "Bash(head *)", "Bash(tail *)", "Bash(grep *)",
      "Bash(diff *)", "Bash(mv *)", "Bash(touch *)", "Bash(file *)"
    ]
  }
}
```

## Model Selection (Quality First)

Don't downgrade quality to work around issues - fix root causes instead.

| Model | Use For |
|-------|---------|
| **Opus** | Creative work (page building, design, content) - quality matters |
| **Sonnet** | Most agents - content, code, research (default) |
| **Haiku** | Only script runners where quality doesn't matter |

## Memory Limits

### Root Cause Fix (REQUIRED)

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export NODE_OPTIONS="--max-old-space-size=16384"
```

Increases Node.js heap from 4GB to 16GB.

### Parallel Limits (Even With Fix)

| Agent Type | Max Parallel | Notes |
|------------|--------------|-------|
| Any agents | 2-3 | Context accumulates; batch then pause |
| Heavy creative (Opus) | 1-2 | Uses more memory |

### Recovery

1. `source ~/.bashrc` or restart terminal
2. `NODE_OPTIONS="--max-old-space-size=16384" claude`
3. Check what files exist, continue from there

## Sub-Agent vs Remote API

**Always prefer Task sub-agents over remote API calls.**

| Aspect | Remote API Call | Task Sub-Agent |
|--------|-----------------|----------------|
| Tool access | None | Full (Read, Grep, Write, Bash) |
| File reading | Must pass all content in prompt | Can read files iteratively |
| Cross-referencing | Single context window | Can reason across documents |
| Decision quality | Generic suggestions | Specific decisions with rationale |
| Output quality | ~100 lines typical | 600+ lines with specifics |

```typescript
// ❌ WRONG - Remote API call
const response = await fetch('https://api.anthropic.com/v1/messages', {...})

// ✅ CORRECT - Use Task tool
// Invoke Task with subagent_type: "general-purpose"
```

## Declarative Over Imperative

Describe **what** to accomplish, not **how** to use tools.

### Wrong (Imperative)

```markdown
### Check for placeholders
```bash
grep -r "PLACEHOLDER:" build/*.html
```
```

### Right (Declarative)

```markdown
### Check for placeholders
Search all HTML files in build/ for:
- PLACEHOLDER: comments
- TODO or TBD markers
- Template brackets like [Client Name]

Any match = incomplete content.
```

### What to Include

| Include | Skip |
|---------|------|
| Task goal and context | Explicit bash/tool commands |
| Input file paths | "Use X tool to..." |
| Output file paths and format | Step-by-step tool invocations |
| Success/failure criteria | Shell pipeline syntax |
| Blocking checks (prerequisites) | Micromanaged workflows |
| Quality checklists | |

## Self-Documentation Principle

> "Agents that won't have your context must be able to reproduce the behaviour independently."

Every improvement must be encoded into the agent's prompt, not left as implicit knowledge.

### What to Encode

| Discovery | Where to Capture |
|-----------|------------------|
| Bug fix pattern | Agent's "Corrections" or "Common Issues" section |
| Quality requirement | Agent's "Quality Checklist" section |
| File path convention | Agent's "Output" section |
| Tool usage pattern | Agent's "Process" section |
| Blocking prerequisite | Agent's "Blocking Check" section |

### Test: Would a Fresh Agent Succeed?

Before completing any agent improvement:
1. Read the agent prompt as if you have no context
2. Ask: Could a new session follow this and produce the same quality?
3. If no: Add missing instructions, patterns, or references

### Anti-Patterns

| Anti-Pattern | Why It Fails |
|--------------|--------------|
| "As we discussed earlier..." | No prior context exists |
| Relying on files read during dev | Agent may not read same files |
| Assuming knowledge from errors | Agent won't see your debugging |
| "Just like the home page" | Agent hasn't built home page |

## Agent Prompt Structure

Effective agent prompts include:

```markdown
## Your Role
[What the agent does]

## Blocking Check
[Prerequisites that must exist]

## Input
[What files to read]

## Process
[Step-by-step with encoded learnings]

## Output
[Exact file paths and formats]

## Quality Checklist
[Verification steps including learned gotchas]

## Common Issues
[Patterns discovered during development]
```

## Pipeline Agents

When inserting a new agent into a numbered pipeline (e.g., `HTML-01` → `HTML-05` → `HTML-11`):

| Must Update | What |
|-------------|------|
| New agent | "Workflow Position" diagram + "Next" field |
| **Predecessor agent** | Its "Next" field to point to new agent |

**Common bug**: New agent is "orphaned" because predecessor still points to old next agent.

**Verification**:
```bash
grep -n "Next:.*→\|Then.*runs next" .claude/agents/*.md
```

## The Sweet Spot

**Best use case**: Tasks that are **repetitive but require judgment**.

Example: Auditing 70 skills manually = tedious. But each audit needs intelligence (check docs, compare versions, decide what to fix). Perfect for parallel agents with clear instructions.

**Not good for**:
- Simple tasks (just do them)
- Highly creative tasks (need human direction)
- Tasks requiring cross-file coordination (agents work independently)

## Effective Prompt Template

```
For each [item]:
1. Read [source file]
2. Verify with [external check - npm view, API call, etc.]
3. Check [authoritative source]
4. Score/evaluate
5. FIX issues found ← Critical instruction
```

**Key elements**:
- **"FIX issues found"** - Without this, agents only report. With it, they take action.
- **Exact file paths** - Prevents ambiguity
- **Output format template** - Ensures consistent, parseable reports
- **Batch size ~5 items** - Enough work to be efficient, not so much that failures cascade

## Workflow Pattern

```
1. ME: Launch 2-3 parallel agents with identical prompt, different item lists
2. AGENTS: Work in parallel (read → verify → check → edit → report)
3. AGENTS: Return structured reports (score, status, fixes applied, files modified)
4. ME: Review changes (git status, spot-check diffs)
5. ME: Commit in batches with meaningful changelog
6. ME: Push and update progress tracking
```

**Why agents don't commit**: Allows human review, batching, and clean commit history.

## Signs a Task Fits This Pattern

**Good fit**:
- Same steps repeated for many items
- Each item requires judgment (not just transformation)
- Items are independent (no cross-item dependencies)
- Clear success criteria (score, pass/fail, etc.)
- Authoritative source exists to verify against

**Bad fit**:
- Items depend on each other's results
- Requires creative/subjective decisions
- Single complex task (use regular agent instead)
- Needs human input mid-process

## Quick Reference

### Agent Frontmatter Template

```yaml
---
name: my-agent
description: |
  [Role] specialist. MUST BE USED when [triggers].
  Use PROACTIVELY for [task category].
  Keywords: [trigger words]
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
---
```

### Fix Bash Approval Spam

1. Remove Bash from tools if not needed
2. Put critical instructions FIRST (right after frontmatter)
3. Use allowlists in `.claude/settings.json`

### Memory Crash Recovery

```bash
export NODE_OPTIONS="--max-old-space-size=16384"
source ~/.bashrc && claude
```
