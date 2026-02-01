---
name: autonomous-feature-planner
description: >
  Autonomously plans and specifies system features starting from the user’s most recent
  command, continuing without further user input until explicitly stopped.
  Use when the user explicitly invokes autonomous planning to extend a system from a
  prior command.
  Trigger keywords: use autonomous-feature-planner, start autonomous planning,
  autonomous expansion, continuous feature planning.
---

## Activation Criteria

Activate only when the user explicitly names this skill or clearly instructs continuous,
self-directed planning.

Activation requires:
- Exactly one immediately preceding user command
- That command must describe or imply a system, product, or process

Do not activate if:
- The previous command is conversational, evaluative, or meta
- The previous command is itself a stop instruction
- The user requests execution, deployment, or real-world action

## Foundation Handling

- The last user command before activation is the foundation.
- The foundation is immutable and may not be reinterpreted, summarized, or expanded.
- The foundation establishes the system domain and intent baseline.

If the foundation cannot define a system domain, fail immediately.

## Execution Model

This skill operates as a bounded-output autonomous planner.
Autonomy applies to sequencing, not to scope invention.

### Initialization

1. Capture the foundation command verbatim.
2. Derive one explicit system domain statement.
3. Declare all assumptions required to derive the domain.
4. Lock the domain and assumptions for the entire session.

If assumptions exceed minimal necessity, fail.

### Planning Loop

Each iteration must perform exactly the following steps:

1. Select exactly one next feature that:
   - Directly fits within the locked system domain
   - Is functionally distinct from all prior features
2. Define the feature scope using explicit inclusions and exclusions.
3. Produce a linear, ordered implementation plan with no branches.
4. Specify:
   - Required inputs
   - Produced outputs
   - Dependencies on prior features
5. State one verifiable success condition.
6. Terminate the iteration.

Only one feature is permitted per iteration.
No iteration may reference future, unplanned features.

## Output Rules

- Each iteration must be labeled sequentially.
- Output must be strictly structured and utilitarian.
- No summaries, retrospectives, vision statements, or meta-commentary.
- No repetition, restatement, or revision of earlier iterations.

## Ambiguity Handling

- All ambiguity must be resolved during initialization.
- Resolution must favor the narrowest viable interpretation.
- No new assumptions may be introduced after initialization.

If ambiguity cannot be resolved without speculation, fail immediately.

## Consistency Enforcement

- All output is append-only.
- Previously planned features are immutable.
- If a contradiction is detected, halt immediately with failure.

## Scope and Runaway Prevention

- Features must not generate sub-features.
- Meta-features about planning, autonomy, or the skill itself are forbidden.
- Each iteration must be finite and self-contained.
- The skill must not escalate into abstraction layers or strategy reformulation.

## Constraints & Non-Goals

- No execution, simulation, or external state changes.
- No file creation or modification.
- No user interaction during operation.
- No external tools, memory, or hidden state.
- No goal invention outside the locked domain.

## Failure Behavior

Immediately halt and output a single failure message if:
- The foundation cannot define a coherent system domain
- Minimal assumptions are insufficient
- Internal consistency cannot be preserved
- Planning would require execution or unverifiable facts

No additional output is permitted after failure.

## Stop Condition

Immediately stop all planning when the user issues any command containing:
- "stop autonomous-feature-planner"
- "stop planning"
- "disable autonomous-feature-planner"

After a stop command:
- Output exactly one character: "."
- Output no other text, whitespace, or newlines.
