# Research Notes: AI Engineering & Prompt Quality (Access-Limited)

## Access Status
External web access may be blocked by a 403 proxy response, so live documentation might be unavailable. When access is limited, rely on standard, widely cited prompting guidance (e.g., promptingguide.ai, learnprompting.org) and established AI engineering practices.

## Evidence-Based Prompting Practices (General)
These are widely accepted practices for high-quality prompting and governance workflows:

1. **Make the task explicit**
   - State the goal, scope, and success criteria in plain language.

2. **Provide context and constraints**
   - Include relevant background, dependencies, and boundaries to reduce ambiguity.

3. **Ask targeted questions**
   - Use short, single-purpose questions to resolve uncertainty.

4. **Specify output format**
   - Request bullets, tables, checklists, or templates to keep responses structured.

5. **Confirm assumptions**
   - Surface inferred details and ask for confirmation before writing them into logs.

6. **Verify before finalizing**
   - Use checklists and validation steps to ensure outputs match success criteria.

## Evidence-Based (General) AI Engineering Practices
1. **Define explicit objectives & safety boundaries**
   - Clearly define success criteria, constraints, and stop-work rules up front.
2. **Evaluation-first development**
   - Build test cases and checklists before expanding capabilities.
   - Use regression checks for prompt changes.
3. **Structured memory & logging**
   - Keep verbose logs for traceability while storing concise memory summaries.
   - Establish a single source of truth for state.
4. **Agent orchestration and tool discipline**
   - Enforce gate-based workflows (intake → ID → charter → conflicts → plan → execute → verify).
   - Require explicit validation before execution of high-risk steps.
5. **Risk-based routing**
   - Define severity levels and escalation rules in advance.
   - Route critical or blocking conflicts to a human decision point.

## Clawdbot Documentation (Pending)
Once documentation is accessible, verify:
- Boot order and runtime memory semantics
- Any existing “project” or “task” lifecycle semantics
- Built-in logging and conflict routing behavior
- Supported sub-agent or delegation mechanisms

## Skill-Specific Recommendations (Based on Current Project Management Skill)
- Keep the **Charter Lite** as the default intake and only expand to full charter when risk increases.
- Use separated log files (`LOG_PROJECTS.md`, `LOG_CHARTERS.md`, `LOG_CONFLICTS.md`, `LOG_DECISIONS.md`, `LOG_ACTIVITY.md`) as the verbose source of truth and reference them from memory.
- Use the minimal intake template to reduce user friction while still preserving governance gates.
