---
name: doing-tasks
description: "Use when executing any task. Work through plans systematically, tracking progress, handling blockers, and coordinating with other skills. The central execution skill."
---

# Doing Tasks - Execution Core

## The Rule

**If a task exists, you MUST use the appropriate skill before acting.**

```
User message received
    ↓
Might any skill apply? → YES (even 1% chance) → Invoke skill
    ↓                                    ↓
    NO ← definitely not                  Announce: "Using [skill]"
    ↓                                    ↓
Respond                              Follow skill exactly
```

## Skill Priority

When multiple skills could apply:

1. **Process skills first** (brainstorming, debugging) - determine HOW
2. **Planning skills second** (write-plan) - create roadmap
3. **Execution skills third** (doing-tasks, dispatch-multiple-agents) - do the work
4. **Verification skills last** (verify-task) - confirm completion

## The Workflow

### Standard Project Flow:

```
brainstorming → write-plan → doing-tasks → verify-task
     ↑                              ↓
     └────── refinement ←───────────┘
```

### With Parallel Execution:

```
brainstorming → write-plan → dispatch-multiple-agents → verify-task
                                   ↓
                            doing-tasks (per subagent)
```

## Red Flags - STOP and Check Skills

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying. |
| "Let me explore first" | Skills tell you HOW to explore. |
| "I can check files quickly" | Check for skills first. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |

## Execution Discipline

### Do:
- Check for skills BEFORE any action
- Follow the plan exactly
- Mark tasks complete as you finish
- Report blockers immediately
- Ask for clarification when unclear

### Don't:
- Skip skills because "it's simple"
- Add unplanned scope without approval
- Work silently for long periods
- Guess when unclear
- Let blockers sit unreported

## Integration with Clawlist

For long-running or infinite tasks:

```
doing-tasks → update ongoing-tasks.md → schedule next run
```

The doing-tasks skill executes, then updates the task tracking file for heartbeat monitoring.

## Sub-Skills Reference

- **brainstorming** - Before any creative work
- **write-plan** - After design, before execution
- **dispatch-multiple-agents** - For parallel independent tasks
- **verify-task** - After completion

## Example

**User:** "Build me a todo app"

**Correct flow:**
1. "Using brainstorming skill to clarify requirements"
2. Brainstorm: Ask questions, explore approaches
3. "Using write-plan skill to create implementation plan"
4. Write-plan: Create checkpoints and tasks
5. "Using doing-tasks skill to execute"
6. Execute: Work through plan
7. "Using verify-task skill to confirm completion"
8. Verify: Check against plan, get user approval

**Incorrect:**
- Jumping straight to coding without brainstorming
- Starting work without a plan
- Skipping verification
