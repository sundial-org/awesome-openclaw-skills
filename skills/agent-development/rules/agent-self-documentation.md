---
globs: [".claude/agents/*.md", "**/agents/*.md", "**/teams/**/*.md", "**/prompts/**/*.md"]
---

# Agent Self-Documentation Principle

When building or improving agent systems, all changes must be captured IN the agent prompts/templates themselves. Future agent instances won't have your conversation context.

## The Principle

> "Agents that won't have your context must be able to reproduce the behaviour independently."

Every improvement, fix, or pattern discovered during development must be encoded into the agent's prompt, not left as implicit knowledge.

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| One-off fix in current session | Update the agent prompt/template |
| "Remember to do X" in conversation | Add X to agent's process section |
| Fixing output manually | Add quality check to agent's checklist |
| Explaining pattern verbally | Document pattern in agent's instructions |

## What to Encode

| Discovery | Where to Capture |
|-----------|------------------|
| Bug fix pattern | Agent's "Corrections" or "Common Issues" section |
| Quality requirement | Agent's "Quality Checklist" section |
| File path convention | Agent's "Output" section |
| Tool usage pattern | Agent's "Process" section |
| Blocking prerequisite | Agent's "Blocking Check" section |

## Example: Learning Becomes Instruction

**During development** (conversation context):
> "The grid was showing 3+1 orphan layout with 4 items. Fixed by using `:has(:nth-child(4):last-child)` to detect item count."

**Encoded in agent prompt**:
```markdown
### Grid Layout Rules
- Use `.services-grid` class - it auto-adapts to item count
- 4 items → 2x2 grid (not 3+1)
- See `teams/creative/layout-presets.md` for patterns
```

## Test: Would a Fresh Agent Succeed?

Before completing any agent system improvement:

1. **Read the agent prompt as if you have no context**
2. **Ask**: Could a new session follow this and produce the same quality?
3. **If no**: Add missing instructions, patterns, or references

## Anti-Patterns

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

## Applies To

- Custom agents in `.claude/agents/`
- Team prompts in `teams/*/`
- Any reusable prompt or workflow
- MCP server tool definitions
