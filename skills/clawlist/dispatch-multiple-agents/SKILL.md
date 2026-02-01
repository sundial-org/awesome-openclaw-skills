---
name: dispatch-multiple-agents
description: "Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies. Dispatch subagents to work concurrently."
---

# Dispatch Multiple Agents

When you have multiple independent tasks, don't do them sequentially. Dispatch agents to work in parallel.

## When to Use

**Use when:**
- 3+ independent tasks need attention
- Tasks don't share state or resources
- No dependencies between tasks
- Speed matters

**Don't use when:**
- Tasks are related (fixing one might fix others)
- Tasks share files/resources (would conflict)
- You need full system context for all tasks
- Tasks must happen in specific order

## The Pattern

### 1. Identify Independent Domains

Group work by what's needed:
- Task A: Research competitor A
- Task B: Research competitor B  
- Task C: Research competitor C

Each is independent.

### 2. Create Focused Tasks

Each subagent gets:
- **Specific scope:** One clear task
- **All context needed:** Don't make them hunt
- **Clear output:** What should they return?
- **Constraints:** What NOT to touch

### 3. Dispatch in Parallel

Using sessions_spawn for concurrent execution.

### 4. Review and Integrate

When agents return:
- Read each result
- Verify no conflicts
- Integrate findings
- Report summary

## Integration with Other Skills

Use dispatch-multiple-agents WITHIN the workflow:

```
brainstorming → write-plan → dispatch-multiple-agents → verify-task
                                   ↓
                            doing-tasks (per subagent)
```

## Example

**Problem:** Research 5 competitors

**Dispatch:**
- Agent 1 → Competitor A
- Agent 2 → Competitor B
- Agent 3 → Competitor C
- Agent 4 → Competitor D
- Agent 5 → Competitor E

**Result:** Full analysis in minutes, not hours.
