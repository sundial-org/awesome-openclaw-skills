---
name: plan-executor
description: Executes frozen, validated plans produced by an autonomous planner with zero interpretation, zero interaction, and strict termination guarantees. Use only when a plan is explicitly finalized, immutable, and execution-safe. Trigger keywords: execute plan, run execution, enact finalized plan.
compatibility:
  - requires planner output with explicit FINALIZED, EXECUTION-READY, and IMMUTABLE markers
allowed-tools:
  - system-io
metadata:
  version: 1.0.0
  owner: user
---

## Activation Criteria

Activate this skill if and only if all conditions below are satisfied simultaneously:

- A single plan is present.
- The plan is explicitly marked FINALIZED, EXECUTION-READY, and IMMUTABLE.
- The plan contains a finite, ordered list of steps with contiguous numeric indices starting at 1.
- Each step includes:
  - a single concrete action
  - a clearly defined target
  - explicit inputs
  - an explicit success condition
  - an explicit failure condition
- No step references planning, validation, ideation, optimization, or user feedback.
- No step depends on external judgment, preference, or discretion.

Do not activate this skill under any other circumstances.

## Execution Steps

1. Enter execution mode. From this point, no reinterpretation, planning, validation, or clarification is permitted.
2. Lock the plan state. Treat all plan content as read-only.
3. Perform preflight verification:
   - Verify step indices are contiguous and unique.
   - Verify all required fields are present for every step.
   - Verify the total number of steps is finite.
   - Verify no step references undeclared resources or targets.
4. If preflight verification fails, halt immediately.
5. Execute steps strictly in ascending numerical order.
6. For each step:
   - Execute the action exactly as written.
   - Apply inputs exactly as specified.
   - Monitor only the declared success and failure conditions.
   - Do not retry unless explicitly stated in the step.
7. If a step reports success, proceed to the next step.
8. If a step reports failure, halt immediately.
9. Continue until all steps are completed successfully or execution is halted.
10. Exit execution mode.

## Ambiguity Handling

- Any ambiguity, omission, contradiction, implicit assumption, or multiple interpretations is a fatal error.
- Ambiguity includes but is not limited to:
  - vague verbs
  - unspecified targets
  - conditional language without explicit branches
  - references to “best,” “optimal,” “reasonable,” or similar terms
- On detection, halt execution immediately without recovery attempts.

## Constraints & Non-Goals

- This skill must not plan, replan, revise, optimize, or extend the plan.
- This skill must not infer intent, preferences, or context.
- This skill must not ask questions or request confirmation.
- This skill must not continue after any failure or violation.
- This skill must not perform actions outside the explicit scope of the plan.
- This skill must not execute indefinitely.
- This skill must not output intermediate commentary, logs, or explanations.

## Guardrails

- Execution scope is strictly limited to declared actions and targets.
- No side effects outside declared targets are permitted.
- Irreversible actions are prohibited unless explicitly declared and justified in the plan.
- Cascading effects not explicitly described invalidate the plan.
- Any detected deviation between declared behavior and actual behavior causes immediate halt.
- The skill must remain passive unless executing a valid step.

## Termination Rules

- Normal termination occurs only after the final step completes successfully.
- Failure termination occurs immediately on any error, ambiguity, or rule violation.
- User-issued stop command causes immediate termination.

## Failure Behavior

- On failure termination, output a single execution-failure notice stating execution halted due to invalid or unsafe conditions.
- On user-issued stop command, output exactly one dot (`.`).
- On successful completion, output nothing.
