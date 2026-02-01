# Templates (Copy/Paste)

## Prompt Frame (Use for Intake or Clarifications)
- context:
- goal:
- constraints:
- assumptions_to_confirm:
- desired_output_format: (bullets, table, checklist, etc.)

## New Project Intake (Minimum Required)
- summary:
- proposed_outcome:
- uncertain_fields_to_clarify:

Optional (infer only when evidence is clear):
- constraints:
- required_deadlines:
- initial_risks:
- specialized_sub_agent:

## Project Creation Prompt (Split Questions)
- ask: “Should I make and log this into a project to store it in my memory?”
- ask: “Should I execute this now, or spin up a specialized agent for higher-quality work (this will use more tokens)?”

## HEARTBEAT Conflict Check Prompt
- ask: “How often should I check `LOG_CONFLICTS.md` for unresolved conflicts? (Default: daily; more frequent checks use more tokens.)”

## Charter Lite (Create in LOG_CHARTERS.md)
# <Project ID> — <Project Name>

## Objective

## Scope (In)

## Scope (Out)

## Success Criteria

## Non-Goals

## Change Control

## Charter Full (Optional Expansion)
- guardrails
- dependencies
- verification plan

## Scope Change Request
- project_id:
- change_summary:
- reason:
- impact_assessment:
- updated_scope:
- updated_success_criteria:
- approval_required:

## Conflict Record (Place in LOG_CONFLICTS.md INBOX)
- timestamp:
- project_id:
- severity:
- category:
- evidence:
- impact:
- required_action:
- resolution_criteria:
- status: open

## Override Record (for reject/critical exceptions)
- timestamp:
- project_id:
- rule_overridden:
- severity:
- rationale:
- approving_authority:
- safeguards:
- expiration_or_review_trigger:
- status: active

## Verification Checklist
- Success criteria met
- Evidence collected
- Scope remains in-bounds
- Guardrails honored
- Logs updated

## Memory Summary (Concise Reference)
- project_id (or non-project):
- summary:
- link_to_verbose_log_entry:
- next_step:
