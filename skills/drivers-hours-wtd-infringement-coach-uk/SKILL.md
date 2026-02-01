---
name: drivers-hours-wtd-infringement-coach-uk
description: Creates a 1-page driver-facing tacho/WTD infringement note plus corrective actions and review date. USE WHEN you need to explain infringements and schedule follow-up.
---

# Drivers’ Hours & WTD Infringement Coach (UK)

## PURPOSE
Turn tacho/WTD infringement evidence into a friendly, professional 1-page driver note plus corrective actions and a review date, applying the company RAG escalation rule.

## WHEN TO USE
- “Explain this tacho infringement to the driver and draft the message.”
- “Check this shift pattern for EU Drivers’ Hours and WTD risk.”
- “Do a weekly tacho and WTD compliance review for these drivers.” (driver-facing outputs needed)
- “Draft a coaching note for repeated breaks/rest issues.”
- “Summarise these infringements into actions and review dates.”

DO NOT USE WHEN…
- Generic questions like “What are the drivers’ hours rules?” with no driver context or artefact needed.
- Generic HR/disciplinary process requests not tied to a specific compliance case.
- Fuel-saving/defensive driving tips unrelated to compliance deliverables.

## INPUTS
- REQUIRED:
  - Driver identifier (name/ID) and role (e.g., HGV/PCV), and period covered (start/end dates)
  - Infringement list (from .ddd/CSV/PDF summary) including dates/times and type
  - Working time context (duty/shift length, POA if recorded, breaks) if WTD-relevant
- OPTIONAL:
  - Prior RAG history (count of ambers/reds in last X weeks/months per your policy)
  - Any driver explanation already given
  - Relevant internal SOP excerpt (paste text) for local rules
- EXAMPLES:
  - “Driver A, week 2026-01-05 to 2026-01-11: 2x insufficient break, 1x daily rest short by 45 mins…”

## OUTPUTS
- `driver-infringement-note.md` (max ~1 page): explanation + expectations + support
- `corrective-action-plan.md`: actions, owner, due dates, review date
- Success criteria:
  - Tone: friendly & professional (UK spelling)
  - No assumptions: facts are attributed to provided records
  - Includes a clear review date and next steps

## WORKFLOW
1. **Validate inputs**
   - Confirm: driver ID, date range, infringement types, and source (PDF/CSV notes).
   - IF any are missing → **STOP AND ASK THE USER** for the missing items.
2. **Summarise facts only**
   - List infringements in plain English (what happened + when), without blame.
   - IF records conflict (e.g., two sources disagree) → **STOP AND ASK THE USER** which source is authoritative.
3. **Classify severity for RAG**
   - Apply the company rule in `references/rag-escalation-rule.md`.
   - IF RAG status depends on missing prior history → **STOP AND ASK THE USER** for counts/previous outcomes.
4. **Draft the driver-facing note (max 1 page)**
   - Use `assets/driver-note-template.md`.
   - Include: what the rule expects, what the record shows, why it matters, and what to do next time.
5. **Propose corrective actions**
   - Use `assets/corrective-action-plan-template.md`.
   - Actions must be specific, practical, and measurable (e.g., break planning, reminder prompts, route/shift adjustments).
6. **Schedule review**
   - Choose a review date proportional to risk:
     - Green/Amber: typically next weekly review window
     - Red: sooner review + manager check-in (and potential investigation trigger per your policy)
7. **Output pack**
   - Produce the two .md artefacts with consistent filenames.
   - IF the user asks to edit existing files → **ASK FIRST** before making edits.

## OUTPUT FORMAT
```text
# driver-infringement-note.md
Driver:
Period covered:
Source records:

## What we saw in the record (facts)
- [date/time] — [plain English infringement]
- …

## What the rules require (plain English)
- …

## What to do next time (practical steps)
- …
- …

## Support we can offer
- …

## Status and next review
RAG status:
Next review date:
Manager/Compliance follow-up:
```

## DEPENDENCIES
- None required beyond the provided extracts/summaries.
- If the user provides files (.ddd/CSV/PDF), rely on the user’s summary unless your environment includes a trusted parser.

## SAFETY & EDGE CASES
- Never accuse or assume intent; stick to evidence.
- If there is any possibility of an employment action (discipline), recommend using the investigation skill pack and keep this note factual/coaching-focused.
- Don’t invent legal thresholds; only explain what’s in the provided evidence + internal policy text.

## EXAMPLES
- Input: “Explain insufficient break x2 and rest shortage x1 for Driver A”
  - Output: `driver-infringement-note.md` + `corrective-action-plan.md` with review date next week
- Input: “Repeated break issues; prior 3 ambers”
  - Output: Note + actions; status indicates escalation path per RAG rule; recommends investigation workflow if needed
