# Charters (Cache)

Charters must be **clear and detailed**, capturing objective, scope, guardrails, dependencies, and verification plans.

# OC-YYYYMMDD-0001 — Kernel Governance OS (User)

### Objective
Define and enforce the governance OS for all OpenClaw projects.

### Scope (In)
- Project ID enforcement
- Charter-first workflow
- Conflict detection and logging
- Severity mapping and escalation
- Runtime integration with workspace templates

### Scope (Out)
- Project-specific delivery beyond governance scope
- Bypassing gates or severity handling

### Guardrails
- Safety and correctness are primary.
- Stop-work rules are mandatory.
- Overrides require written records.

### Dependencies
- `LOG_PROJECTS.md`
- `LOG_CONFLICTS.md`
- `LOG_DECISIONS.md`
- `LOG_ACTIVITY.md`
- OpenClaw workspace templates (external to the project management skill)

### Success Criteria
- All work is tied to a Project ID.
- All projects have charters.
- Conflicts are logged and routed.

### Verification Plan
- Audit logs for Project ID usage.
- Check Conflicts for proper routing.

### Non-Goals
- Business-specific delivery requirements.

### Change Control
- All changes recorded in **Decisions**.

---

### Charter Lite Template (Copy/Paste)

# <Project ID> — <Project Name>

#### Objective

#### Scope (In)

#### Scope (Out)

#### Success Criteria

#### Non-Goals

#### Change Control

### Charter Full (Optional Expansion)
- guardrails
- dependencies
- verification plan
