---
name: cpc-mpqc-competence-tracker-compliance-uk
description: Plans CPC/MPQC competence tracking with reminders, evidence lists, and compliance reporting. USE WHEN maintaining training/certification readiness.
---

# CPC/MPQC Training & Competence Tracking (UK)

## PURPOSE
Maintain audit-ready training and competence evidence: a matrix, reminders plan, and a compliance report view.

## WHEN TO USE
- “Training and competence tracking: CPC/MPQC planning, reminders, certification evidence, compliance reporting.”
- “Write a toolbox talk on driver hours and breaks for next week.” (when tied to competence evidence)
- “Create a compliance training report for this month/quarter.”

DO NOT USE WHEN…
- Generic learning content not tied to compliance evidence.
- Requests for PowerPoints/company values decks.

## INPUTS
- REQUIRED:
  - Driver list (name/ID), roles, depots
  - Required training types (CPC modules, MPQC, internal toolbox talks)
- OPTIONAL:
  - Expiry dates, certificates, providers, past completion records
  - Internal policy on frequency/mandatory modules (paste text)
- EXAMPLES:
  - “Need a monthly report and reminders for expiring MPQC.”

## OUTPUTS
- `training-matrix.md` (Excel-ready)
- `reminders-plan.md`
- `compliance-training-report.md`
- Success criteria:
  - Evidence-ready fields (who/what/when/proof)
  - Clear upcoming expiries and owners

## WORKFLOW
1. Confirm required training set and the reporting period.
   - IF missing → **STOP AND ASK THE USER**.
2. Create/refresh training matrix using `assets/training-matrix-template.md`.
3. Build reminders schedule using `assets/reminder-plan-template.md`.
4. Draft compliance report using `assets/compliance-report-template.md`.
5. Evidence standard:
   - Reference `references/competence-evidence-standard.md` and map to your internal storage locations.
6. If asked to update existing trackers → **ASK FIRST**.

## OUTPUT FORMAT
```text
# training-matrix.md
| Driver | Role | CPC due | CPC last completed | MPQC expiry | Last toolbox talk | Evidence link/location | Status (RAG) | Notes |
|--------|------|---------|-------------------|-------------|-------------------|------------------------|--------------|------|
```

## SAFETY & EDGE CASES
- Don’t invent certificate numbers or dates; mark unknowns clearly.
- If training requirements vary by customer/site, create a “customer/site delta” section and ask for specifics.

## EXAMPLES
- Input: “Plan reminders for MPQC expiries”
  - Output: matrix + reminders plan + monthly report draft
