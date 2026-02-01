# Runtime Integration (OpenClaw Workspace)

This document instructs OpenClaw how to interact with its **runtime workspace templates and memory files**. It does **not** include those files.

**This project management skill references runtime workspace templates; it does not contain them.**
**Codex authors this skill; OpenClaw executes it at runtime.**

## A) Boot Read Order (OpenClaw Action List)
On boot, open these workspace files and read in this order (note: `MEMORY.md` is a single Markdown file in the workspace):
1. `~/.openclaw/workspace/SOUL.md`
2. `~/.openclaw/workspace/USER.md`
3. `~/.openclaw/workspace/memory/YYYY-MM-DD.md` (today + yesterday)
4. If in **MAIN SESSION**, also read `~/.openclaw/workspace/MEMORY.md` (single Markdown file)

Then load skill cache files in the project management skill:
- `LOG_CACHES.md` (index only)
- Load only the specific log file needed: `LOG_PROJECTS.md`, `LOG_CHARTERS.md`, `LOG_CONFLICTS.md`, `LOG_DECISIONS.md`, `LOG_ACTIVITY.md`

## B) Boot Write Actions (Workspace-Only)
- If `BOOT.md` is missing or stale in `~/.openclaw/workspace/`, write a **minimal BOOT.md** that performs the boot read order above and restores **Active Project Focus**.
- BOOT rule: **If BOOT sends a message, use the message tool then reply NO_REPLY.**
- IMPORTANT: **Do not create BOOT.md inside the project management skill; only write it in the OpenClaw workspace path.**

## C) “Learn / Remember” Write Targets (Examples Required)
Use the workspace templates for continuity and keep reminders concise and unambiguous:
- If you discover a recurring process improvement, write it into `~/.openclaw/workspace/AGENTS.md` as a new operational rule (because it governs future sessions).
- If you learn a user-specific environment detail (messenger channel name, preferred escalation target), write it into `~/.openclaw/workspace/TOOLS.md` (local notes).
- If a conflict needs escalation, record it in `LOG_CONFLICTS.md` **and** write a reminder into `~/.openclaw/workspace/MEMORY.md` (single Markdown file) to ask the User Project to resolve it during the next main-session check-in.
- If you want a timed reminder, add a HEARTBEAT task into `~/.openclaw/workspace/HEARTBEAT.md` (keep empty/comments to disable; add tasks to enable periodic checks).
- If a project is created or updated, write a **concise reference** into `~/.openclaw/workspace/MEMORY.md` (single Markdown file) that points to the **verbose, detailed log entry** in the project management skill (e.g., `LOG_ACTIVITY.md` or `LOG_DECISIONS.md`).

Example reminder tasks (write as plain Markdown task lines, not code):
- In 30m: re-check LOG_CONFLICTS.md **Conflicts** INBOX for block+ items
- Daily: roll yesterday’s memory/YYYY-MM-DD.md into MEMORY.md (main session only)
- Every 2h: confirm Active Project Focus matches current work

## D) Stop-Work Integration
- If Project ID is missing, **ask the user** whether to create a project with a specialized sub-agent. If declined, proceed as non-project work and write a concise MEMORY note into `~/.openclaw/workspace/MEMORY.md` that links to the verbose log entry.
- If severity is **block/reject/critical**: update `LOG_CONFLICTS.md` **Conflicts** INBOX + write `~/.openclaw/workspace/MEMORY.md` reminder: “Ask user to resolve conflict <anchor>” + (optionally) add HEARTBEAT reminder to recheck in X.
- Regardless of outcome, **sync logs and memory** (even for small tasks or early stops).

## E) HEARTBEAT Conflict Checks (Default Daily)
On setup and first call of this skill, ask the user how often to run conflict checks via HEARTBEAT, and state that more frequent checks consume more tokens. Default to **daily** if they do not choose. Write a HEARTBEAT task that reads `LOG_CONFLICTS.md` and informs the user about any unresolved conflicts.

## F) SOUL Enforcement (Always Use Skill + Memory Sync)
During setup, request user permission to **FORCE** updates to `~/.openclaw/workspace/MEMORY.md`, `~/.openclaw/workspace/AGENTS.md`, and `~/.openclaw/workspace/SOUL.md`. If granted, write the following rules in a single onboarding transaction:
- MEMORY: “Maintain long-term continuity for project management: review project-management-skills guidance on each main session, and record concise references to project logs after governed work. If MEMORY.md is missing, create it and add this rule at the top.”
- AGENTS: “At the start of each session, load project-management-skills for any user request involving planning, coordination, memory, or conflicts. If a conflict is detected, log it and surface it to the user during the same response.”
- SOUL: “When working on projects, be analytical, descriptive, and proactive in gathering all relevant data before acting. Take initiative to request missing inputs or evidence needed for governance.”
If permission is denied, do not enforce the always-call rule and stop project governance for that session.
If the skill cannot be called (missing, unavailable, or fails to load), **remove only the SOUL excerpt you added** so OpenClaw does not reference a missing skill. This acts as the uninstall pathway for the always-call rule, without deleting other SOUL content.

## G) Unprompted Work Logging (User-Only Project Classification)
To ensure project classification only occurs for user-prompted work:
- For any **unprompted** action (heartbeat/autonomous tasks), log each action into a temporary file: `~/.openclaw/workspace/TEMP_UNPROMPTED_LOG.md` with timestamp, action summary, and any artifacts.
- Do **not** open or update projects for these actions until a user prompt arrives.
- On the next user prompt, read the temporary log and inform the user what was done. Ask whether each item should be classified under an existing project, a new project, or no project at all.
- After classification, move the relevant entries into the appropriate project log(s) and clear the temporary file.

## H) Explicit Project Management Skill/Non-Skill Boundary
- **This project management skill references runtime workspace templates; it does not contain them.**
- **Codex authors this skill; OpenClaw executes it at runtime.**
