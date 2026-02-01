---
name: section-11
description: Evidence-based endurance cycling coaching protocol. Use when analyzing training data, reviewing sessions, planning workouts, answering training questions, or giving cycling coaching advice. Always fetch athlete JSON data before responding to any training question.
---

# Section 11 — AI Coaching Protocol

## First Use Setup

On first use, check if DOSSIER.md exists in the workspace:
1. If not found, fetch template from: https://raw.githubusercontent.com/CrankAddict/section-11/main/DOSSIER_TEMPLATE.md
2. Ask the athlete to fill in their data (zones, goals, schedule, etc.)
3. Save as DOSSIER.md in the workspace
4. Do not proceed with coaching until dossier is complete

## JSON Data Setup

Ask the athlete to set up their Intervals.icu data mirror:
1. Create a private GitHub repo for training data
2. Set up automated sync from Intervals.icu to `latest.json`
3. Provide the raw URL (e.g., `https://raw.githubusercontent.com/[user]/[repo]/main/latest.json`)
4. Save the URL in DOSSIER.md under "Data Source"

See: https://github.com/CrankAddict/section-11#2-set-up-your-data-mirror-optional-but-recommended

## Protocol

Fetch and follow: https://raw.githubusercontent.com/CrankAddict/section-11/main/SECTION_11.md

## Data Hierarchy
1. JSON data (always fetch first from athlete's data URL)
2. Protocol rules (SECTION_11.md)
3. Athlete dossier (DOSSIER.md)

## Required Actions
- Fetch latest.json before any training question
- No virtual math — use only fetched values
- Follow Section