---
globs: ["**/*.ts", "**/*.tsx", ".claude/agents/*.md", "**/agents/*.md"]
---

# Agent Implementation Pattern

When building agent-like functionality in Claude Code projects, use Task sub-agents instead of remote API calls.

## Corrections

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Script calling Claude/OpenAI API remotely | Task tool with `subagent_type: "general-purpose"` |
| `fetch('https://api.anthropic.com/v1/messages')` in script | Task sub-agent with comprehensive prompt |
| Remote agent with single-shot context | Sub-agent that can read files iteratively |

## Why Sub-Agents Are Superior

| Aspect | Remote API Call | Task Sub-Agent |
|--------|-----------------|----------------|
| Tool access | None | Full (Read, Grep, Write, Bash) |
| File reading | Must pass all content in prompt | Can read files iteratively |
| Cross-referencing | Single context window | Can reason across documents |
| Decision quality | Generic suggestions | Specific decisions with rationale |
| Output quality | ~100 lines typical | 600+ lines with specifics |

## Pattern

```typescript
// ❌ WRONG - Remote API call
const response = await fetch('https://api.anthropic.com/v1/messages', {
  method: 'POST',
  headers: { 'x-api-key': ANTHROPIC_API_KEY },
  body: JSON.stringify({ model: 'claude-sonnet-4-20250514', messages: [...] })
});

// ✅ CORRECT - Use Task tool in Claude Code
// Invoke Task with subagent_type: "general-purpose"
// Sub-agent reads files, synthesizes, writes output
```

## When This Applies

- Creative Director agents (synthesizing discovery into briefs)
- Code review agents
- Documentation generators
- Any multi-file analysis task
- Content generation from multiple sources

## Real Example

**Task**: Generate Creative Brief from 6 discovery files + media catalog

**Remote API result**: Generic brief with placeholder suggestions
**Sub-agent result**: 610-line brief with specific hex codes, image IDs by filename, actual headlines, cross-referenced statistics with citations

The difference is dramatic because sub-agents can:
1. Read all 6 discovery files (3,600+ lines)
2. Read media catalog and reference specific images
3. Cross-reference facts between documents
4. Make informed decisions based on full context
