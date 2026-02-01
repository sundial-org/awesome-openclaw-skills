---
name: dvsa-tc-audit-readiness-operator-licence-uk
description: Builds DVSA/Traffic Commissioner “show me” audit readiness checklists and evidence indexes. USE WHEN preparing for audits or operator licence scrutiny.
---

# DVSA & Traffic Commissioner Audit Readiness (UK)

## PURPOSE
Produce “show me” readiness materials: today’s checklist, an evidence index, and a gaps register aligned to operator-licence sensitivity and audit expectations.

## WHEN TO USE
- “Prep me for a DVSA visit and give me a checklist for today.”
- “Create a customer audit response pack for [CUSTOMER] and list gaps.”
- “Build an evidence index for operator licence compliance.”
- “What should we have ready to show an auditor today?”

DO NOT USE WHEN…
- The request is generic compliance chat with no artefact needed.
- Pure operations/customer service requests (routes/pricing/performance) not compliance-led.

## INPUTS
- REQUIRED:
  - Audit context (DVSA visit / TC inquiry readiness / customer audit) and date
  - Scope: which depot/operating centre/fleet, and period (e.g., last 28/90 days)
- OPTIONAL:
  - Your internal SOPs/policies (paste text) and retention rules
  - Prior audit findings/actions
- EXAMPLES:
  - “DVSA site visit today at Depot X; need show-me checklist and evidence index.”

## OUTPUTS
- `dvsa-visit-today-checklist.md`
- `audit-evidence-index.md` (Excel-ready table)
- `gaps-register.md`
- Success criteria:
  - Practical, checkable items
  - Clear “where to find it” references
  - Highlights operator licence sensitivities (without legal claims beyond your policy text)

## WORKFLOW
1. Confirm audit type and scope.
   - IF missing → **STOP AND ASK THE USER** for audit type, depot/fleet, and time period.
2. Generate today’s “show me” checklist using `assets/dvsa-visit-today-checklist-template.md`.
3. Build an evidence index (what, where stored, owner, retention, last updated) using `assets/audit-evidence-index-template.md`.
4. Identify likely gaps:
   - Mark unknowns as “Gap – confirm source/owner”.
   - Output `gaps-register.md` via `assets/gaps-register-template.md`.
5. Operator licence sensitivity:
   - Add a short section referencing `references/operator-licence-sensitivity-placeholders.md` and map to your internal policies.
6. If the user wants edits to existing files → **ASK FIRST**.

## OUTPUT FORMAT
```text
# dvsa-visit-today-checklist.md
Audit type:
Scope:
Date:

## Immediate readiness (today)
- …

## Documents to pull (and where)
- …

## People/process readiness (“show me”)
- …

## Known risks / sensitivities
- …
```

## SAFETY & EDGE CASES
- Don’t invent retention periods or legal duties; ask for internal policy text if needed.
- If asked for “is this legal?”, stop and request the precise records and desired output artefact.

## EXAMPLES
- Input: “DVSA visit today”
  - Output: checklist + evidence index + gaps register for rapid action
