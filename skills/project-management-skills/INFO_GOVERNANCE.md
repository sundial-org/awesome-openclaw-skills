# Governance OS (User, Definitions, Severity, Workflow, Routing)

## User Project (Kernel)

### Objective
Provide the governing OS for all OpenClaw project work: enforce Project IDs, charter-first execution, conflict detection and logging, severity handling, and safety-over-speed decisions.

### Scope
**In scope**
- Project governance, gating, and compliance.
- Standardization of charters, conflicts, severity, and logging.
- Runtime integration with OpenClaw workspace templates and memory practices.

**Out of scope**
- Delivering project-specific content outside of defined charters.
- Bypassing conflict detection or severity handling.
- Modifying runtime workspace templates inside the project management skill.

### Guardrails
- User Project rules override all local project preferences.
- Stop-work rules are mandatory.
- Safety and correctness supersede speed.

### Success Criteria
- Every work item has a valid Project ID (or is explicitly logged as non-project work).
- Every active project has a charter.
- Conflicts are detected, logged, and routed.
- Decisions and actions are logged with traceability.

### Change Control & Override Policy
- Changes to this User Project require a written record in `LOG_DECISIONS.md`.
- Any override of rules (reject/critical exceptions) must be documented as an **Override Record** in `LOG_CONFLICTS.md` and referenced in `LOG_DECISIONS.md`.
- Overrides are temporary and must include resolution criteria and an expiration or review trigger.

---

## Definitions
- **Project ID**: The unique identifier for a unit of work, formatted as `OC-YYYYMMDD-####`.
- **Charter**: The authoritative statement of objective, scope, guardrails, dependencies, success criteria, and verification plan for a project.
- **Scope Creep**: Work that expands beyond the charter without an approved change request.
- **Conflict**: Any mismatch between requested work and charter, policy, guardrails, or required evidence.
- **Severity**: The escalation level of a conflict: info, warn, block, reject, critical.
- **Override**: A documented exception to a stop-work rule, authorized and recorded.
- **Evidence**: Verifiable references supporting a decision or outcome.
- **Verification**: The process confirming deliverables meet the charter’s success criteria.
- **Stop-Work**: A mandatory halt in execution due to missing Project ID, missing charter, or blocking conflicts.

---

## Severity Levels

### info
**Action**: Record for awareness; proceed.
**Example**: Minor clarification needed but not blocking work.

### warn
**Action**: Proceed with caution; document risk.
**Example**: Low-risk dependency uncertainty.

### block
**Action**: Stop work until resolved; log conflict; route if required.
**Example**: Out-of-scope change vs charter.

### reject
**Action**: Do not proceed; log conflict; require new Project ID or charter.
**Example**: Missing Project ID.

### critical
**Action**: Immediate stop; log conflict; route; require override record if proceeding.
**Example**: Guardrail violation or secret risk.

### Required Mappings
- **Missing Project ID => prompt for project creation; log as non-project if declined**
- **Missing/unfinished charter => block**
- **Out-of-scope vs charter => block** (reject if repeated without change request)
- **Guardrail violation / secret risk => critical**

---

## Governed Workflow (Canonical)

This workflow applies to **every request**. It is a gate-based system; if any gate returns **block**, **reject**, or **critical**, you must **stop** and write a conflict record.

### Flow
1. **Intake**
   - Capture the request, desired outcome, and constraints.
   - Infer missing fields only when evidence is clear.
   - **Confirm assumptions** you are not confident in before committing them.
   - Use clear, short questions and specify the expected response format.
2. **ID Gate**
   - Ask the user whether this should become a project (**ask even for small tasks**):
     - “Should I make and log this into a project to store it in my memory?”
     - “Should I execute this now, or spin up a specialized agent for higher-quality work (this will use more tokens)?”
   - If yes: confirm any uncertain fields, auto-create a Project ID, and start a **Charter Lite** in `LOG_CHARTERS.md`.
   - If no: proceed as **non-project work** and log the categorization.
3. **Charter Gate**
   - Confirm a **Charter Lite** exists in `LOG_CHARTERS.md`.
   - If missing: block and log conflict.
4. **Conflict Gate**
   - Run the Conflict Detection Checklist from `LOG_CONFLICTS.md`.
   - If conflict detected: log and route as required.
5. **Plan**
   - Draft steps that respect scope, guardrails, and dependencies.
6. **Execute**
   - Perform the work within charter scope.
7. **Verify**
   - Validate against success criteria and verification plan.
8. **Log**
   - Record actions and outcomes in `LOG_ACTIVITY.md`.
   - Record decisions in `LOG_DECISIONS.md`.
   - **Always log and sync memory, even for small tasks or early stops.**
9. **Memory Sync**
   - Write concise references into `MEMORY.md` that point to the verbose logs.
10. **Update Indexes**
    - Update `LOG_PROJECTS.md`, `LOG_CHARTERS.md`, `LOG_CONFLICTS.md` as needed.

### Gate Failure Rule
If any gate returns **block**, **reject**, or **critical**, **stop**. Create a conflict record in `LOG_CONFLICTS.md` and follow the routing rule below. Always sync a memory reference to the conflict.

---

## Conflict Routing (Manual Messenger Payload)

**Rule:** If severity >= **block**, always route using the payload below.

### Payload Template (Copy/Paste)
- project_id:
- severity:
- summary:
- evidence:
- link_to_conflict_anchor:
- next_step:
