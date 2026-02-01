# Project Management Skills (Markdown-Only)

This repository defines **Project Management Skills**: a Markdown-only governance layer for OpenClaw. It enforces Project IDs, charter-first execution, conflict detection + logging, severity levels, and safety-over-speed decisions. It also instructs OpenClaw how to integrate with runtime workspace files (read/write order, memory sync, and logging). It does **not** ship those workspace files.

## What this skill emphasizes
- Clear scope, constraints, and success criteria before work begins.
- Structured, low-ambiguity prompts (explicit questions, confirm assumptions, and concise templates).
- Traceable decisions through logs and concise memory references.

## Repository map
- [SKILL.md](SKILL.md) — Skill entry point: triggers, onboarding, prompting principles, and stop-work rules.
- [INFO_GOVERNANCE.md](INFO_GOVERNANCE.md) — User project kernel: definitions, severity, workflow, routing.
- [INFO_RUNTIME.md](INFO_RUNTIME.md) — Runtime integration rules for workspace files and memory sync.
- [INFO_TEMPLATES.md](INFO_TEMPLATES.md) — Copy/paste templates for intake, charters, conflicts, and memory summaries.
- [INFO_RESEARCH.md](INFO_RESEARCH.md) — Research notes and prompt-quality references.
- [LOG_CACHES.md](LOG_CACHES.md) — Log index (load only what’s needed).
- [LOG_PROJECTS.md](LOG_PROJECTS.md) — Project registry and active focus.
- [LOG_CHARTERS.md](LOG_CHARTERS.md) — Charter records and charter templates.
- [LOG_CONFLICTS.md](LOG_CONFLICTS.md) — Conflicts, gates, and routing.
- [LOG_DECISIONS.md](LOG_DECISIONS.md) — Decision history.
- [LOG_ACTIVITY.md](LOG_ACTIVITY.md) — Activity log.
