---
name: hybrid-memory
description: Hybrid memory strategy combining OpenClaw's built-in vector memory with Graphiti temporal knowledge graph. Use when you need to recall past context, answer temporal questions ("when did X happen?"), or search memory files. Provides decision framework for when to use memory_search vs Graphiti.
---

# Hybrid Memory System

Two memory systems, each with different strengths. Use both.

## When to Use Which

| Question Type | Tool | Example |
|--------------|------|---------|
| Document content | `memory_search` | "What's in GOALS.md?" |
| Curated notes | `memory_search` | "What are our project guidelines?" |
| Temporal facts | Graphiti | "When did we set up Slack?" |
| Conversations | Graphiti | "What did the user say last Tuesday?" |
| Entity tracking | Graphiti | "What projects involve Alice?" |

## Quick Reference

### memory_search (Built-in)

Semantic search over markdown files (`MEMORY.md`, `memory/**/*.md`).

```
memory_search query="your question"
```

Then use `memory_get` to read specific lines if needed.

### Graphiti (Temporal)

Search for facts with time awareness:

```bash
graphiti-search.sh "your question" GROUP_ID 10
```

Log important facts:

```bash
graphiti-log.sh GROUP_ID user "Name" "Fact to remember"
```

Common group IDs:
- `main-agent` — Primary agent
- `user-personal` — User's personal context

## Recall Pattern

When answering questions about past context:

1. **Temporal questions** → Check Graphiti first
2. **Document questions** → Use `memory_search`
3. **Uncertain** → Try both, combine results
4. **Low confidence** → Say you checked but aren't sure

## AGENTS.md Template

Add to your AGENTS.md:

```markdown
### Memory Recall (Hybrid)

**Temporal questions** ("when?", "what changed?", "last Tuesday"):
```bash
graphiti-search.sh "query" main-agent 10
```

**Document questions** ("what's in X?", "find notes about Y"):
```
memory_search query="your query"
```

When answering past context: check Graphiti for temporal, memory_search for docs.
```

## Setup

Full setup guide: https://github.com/clawdbrunner/openclaw-graphiti-memory

**Part 1: OpenClaw Memory** — Configure embedding provider (Gemini recommended)
**Part 2: Graphiti** — Deploy Docker stack, install sync daemons
