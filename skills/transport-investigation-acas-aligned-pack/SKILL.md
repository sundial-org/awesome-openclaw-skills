---
name: transport-investigation-acas-aligned-pack
description: Generates ACAS-aligned investigation invite wording, neutral question sets, and evidence logs. USE WHEN starting a driver incident investigation/interview.
---

# Investigation Pack (ACAS-aligned)

## PURPOSE
Create an ACAS-aligned investigation starter pack: invite wording, neutral question plan, and evidence log structure for transport incidents and potential misconduct.

## WHEN TO USE
- “Draft an investigation invite letter for this incident and evidence list.”
- “Create investigation questions for this driver interview, ACAS aligned.”
- “Summarise these incident notes into a clean manager brief.” (when it feeds an investigation)

DO NOT USE WHEN…
- Generic HR queries like “What is a fair disciplinary process?” with no case artefact needed.
- You’re drafting outcomes/sanctions without an investigation stage.

## INPUTS
- REQUIRED:
  - Incident summary (what/when/where), parties involved, and what’s alleged/being reviewed
  - Evidence available so far (CCTV, telematics, tacho extracts, witness notes, PCN, photos)
  - Proposed meeting date window and who will chair/note-take
- OPTIONAL:
  - Relevant internal policies (paste text), previous similar cases, union/companion info
- EXAMPLES:
  - “Allegation: falsified manual entry on [date]. Evidence: tacho report + supervisor note.”

## OUTPUTS
- `investigation-invite.md` (Word-ready)
- `question-plan.md`
- `evidence-log.md` (Excel-ready table)
- Success criteria:
  - Neutral tone, no assumptions of guilt
  - Includes right-to-be-accompanied wording
  - Clear evidence handling and logging

## WORKFLOW
1. Confirm this is an **investigation** (fact-finding), not a disciplinary hearing.
   - IF unclear → **STOP AND ASK THE USER** what stage they are at.
2. Draft invite using `assets/invite-letter-template.docx-ready.md`.
   - Include: purpose, date/time, attendees, right-to-be-accompanied, evidence access, and contact route.
3. Build a neutral question plan using `assets/neutral-question-plan-template.md`.
   - Start broad → then specifics → then mitigation/context → then closing.
4. Create an evidence log using `assets/evidence-log-template.md`.
   - Include chain-of-custody fields if needed.
5. Add ACAS alignment checks from `references/acas-alignment-checklist.md`.
6. If asked to edit existing documents → **ASK FIRST**.

## OUTPUT FORMAT
```text
# evidence-log.md
| Ref | Evidence item | Source | Date/time captured | Who captured | Storage location | Integrity notes | Relevance | Shared with employee (Y/N, date) |
|-----|---------------|--------|-------------------|-------------|------------------|-----------------|----------|----------------------------------|
```

## SAFETY & EDGE CASES
- Don’t provide legal advice; keep to process and neutrality.
- If the allegation is serious and outcomes could be dismissal, flag that HR/legal review may be required per internal governance (ask for your policy text).

## EXAMPLES
- Input: “Invite letter + questions for driver interview”
  - Output: invite + question plan + evidence log template populated with known items
