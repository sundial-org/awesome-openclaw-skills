# Agent Development Skill

Design and build custom Claude Code agents with effective descriptions, tool access patterns, and self-documenting prompts.

## Auto-Trigger Keywords

This skill should be automatically loaded when discussions involve:

- "create agent", "custom agent", "build agent"
- "agent description", "agent frontmatter"
- "Task tool", "subagent_type"
- "agent pipeline", "agent workflow"
- "agent memory", "memory limits", "heap size"
- "agent delegation", "auto-delegation"
- "agent not triggering", "agent not running"
- ".claude/agents/", "agents/*.md"
- "model selection", "Opus vs Sonnet vs Haiku"
- "declarative instructions", "agent prompts"
- "self-documenting", "agent documentation"
- "parallel agents", "batch agents"
- "sub-agent patterns", "agent design"

## What This Skill Covers

1. **Agent Description Patterns** - Strong trigger phrases for auto-delegation
2. **Tool Access** - When to give Bash, allowlist patterns
3. **Model Selection** - Opus/Sonnet/Haiku decision matrix
4. **Memory Management** - NODE_OPTIONS fix, parallel limits
5. **Sub-Agent vs API** - Why Task sub-agents are superior
6. **Declarative Design** - What vs how in agent instructions
7. **Self-Documentation** - Encoding learnings into prompts
8. **Pipeline Agents** - Linking agents in workflows
9. **Parallel Execution** - Batch patterns, workflow design

## Quick Start

### Create a New Agent

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

# My Agent

## Your Role
[What this agent does]

## Process
[Steps to follow]

## Output
[Expected deliverables]
```

### Fix Memory Issues

```bash
# Add to ~/.bashrc
export NODE_OPTIONS="--max-old-space-size=16384"
source ~/.bashrc
```

### Fix Bash Approval Spam

Remove Bash from tools list, or use allowlists in `.claude/settings.json`.

## Related Skills

- `cloudflare-dev` - Development workflow (uses agents)
- `project-planning` - Project setup (creates agents)

## Version History

- **v1.0.0** (2025-01-18): Initial release with consolidated agent patterns
