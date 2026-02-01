---
name: verify-task
description: "MUST use after completing any multi-step task or project. Verifies completion against the original plan, checks quality criteria, and documents outcomes."
---

# Verify Task

## Overview

Confirm successful completion and document outcomes against the original plan.

## When to Verify

- All tasks from plan are marked complete
- User asks "is it done?" or "did it work?"
- Before declaring a project finished
- After each checkpoint in long-running tasks

## Verification Process

### Step 1: Load Original Plan

Read the plan that was created by write-plan skill.

### Step 2: Verify Each Checkpoint

Go through each checkpoint and confirm:
- [ ] All tasks marked complete
- [ ] Verification criteria met
- [ ] Quality standards achieved

### Step 3: Final Quality Checks

**General quality criteria:**
- [ ] Output matches original goal
- [ ] No obvious errors or issues
- [ ] Documentation updated (if applicable)
- [ ] User can use/access the result

### Step 4: User Confirmation

```
"Verification complete. Final checks:

✓ All tasks from plan completed (X/Y)
✓ Quality criteria met
✓ [Specific checks]

[Preview/demonstrate result]

Does this meet your expectations? Any adjustments needed?"
```

### Step 5: Document Completion

Save completion report to: `memory/plans/YYYY-MM-DD-<project>-complete.md`

Template:
```markdown
# [Project] - Completion Report

**Date Completed:** YYYY-MM-DD
**Original Goal:** [from plan]
**Final Result:** [brief description]

## Completion Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Checkpoints | X | X |
| Tasks | Y | Y |
| Time | Z min | W min |

## Verification Checklist

- [x] All tasks complete
- [x] Quality criteria met
- [x] User approved

## What Was Delivered

[Description of final output]

## Blockers Encountered

1. [Blocker] → [Resolution]

## Lessons Learned

- [What worked well]
- [What to do differently next time]
```

## Handling Issues

### If verification fails:

**Minor issues:** Quick fixes, proceed
**Major issues:** Return to doing-tasks or re-plan

## Principles

- **Objectivity** - Verify against the plan, not assumptions
- **Thoroughness** - Check all criteria
- **Honesty** - Report issues, don't hide problems
- **User-centric** - Final approval comes from user satisfaction
