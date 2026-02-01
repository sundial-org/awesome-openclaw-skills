---
name: write-plan
description: "MUST use after brainstorming and before executing. Creates detailed implementation plans with checkpoints, verification criteria, and execution options."
---

# Write Plan

## Overview

Transform validated designs into detailed, actionable implementation plans with checkpoints.

Every plan includes:
- Bite-sized tasks (2-5 minutes each)
- Checkpoints with verification criteria
- Estimated time for each section
- Execution options at the end

## Plan Structure

```markdown
# [Project Name] - Implementation Plan

**Goal:** One sentence describing success
**Approach:** Brief summary of the chosen approach
**Estimated Total Time:** X minutes

## Checkpoint 1: [Milestone Name]
- [ ] Task 1: [Description] (~X min)
  - **Action:** [Specific action]
  - **Verify:** [How to confirm done]
- [ ] Task 2: [Description] (~X min)
  ...

## Checkpoint 2: [Milestone Name]
...

## Verification Criteria
- [ ] All checkpoints complete
- [ ] Quality standards met
- [ ] User approval obtained
```

## Task Granularity

- **Small:** 2-5 minutes of work
- **Specific:** Clear what "done" means
- **Verifiable:** Can confirm completion
- **Independent:** Doesn't block on other tasks in same checkpoint

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `memory/plans/<filename>.md`. Two execution options:**

**1. Single-Agent (this session)** - I execute tasks sequentially, review at each checkpoint

**2. Dispatch Multiple Agents (parallel)** - Spawn subagents for independent tasks

**Which approach?"**

**If Single-Agent chosen:**
- Stay in this session
- Execute tasks sequentially
- Report progress at each checkpoint

**If Dispatch Multiple Agents chosen:**
- Use dispatch-multiple-agents skill
- Spawn subagents for parallel work
- Integrate results

## Integration with Other Skills

- After **brainstorming** → Use write-plan
- Before **doing-tasks** → Plan must exist
- With **dispatch-multiple-agents** → For parallel execution
