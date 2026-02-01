---
name: config-guardian
description: Validate and safeguard OpenClaw config updates (openclaw.json or openclaw config set/apply). Use this skill whenever changing gateway config, models, channels, agents, tools, sessions, or routing. Enforces backup, schema validation, and safe rollback before restarts.
---

# Config Guardian

## Overview
Use this workflow whenever editing `~/.openclaw/openclaw.json` or running `openclaw config set/apply`. It prevents invalid config, creates backups, validates against schema, and enables rollback.

## Workflow (use every time)

1. **Preflight**
   - Confirm the requested change and scope.
   - Check for sensitive keys (tokens, credentials).

2. **Backup**
   - Run `scripts/backup_config.sh` to create a timestamped snapshot.

3. **Validate (before change)**
   - Run `scripts/validate_config.sh`.
   - If validation fails, stop and report.

4. **Apply change**
   - Prefer `openclaw config set <path> <value>` for small changes.
   - For complex edits, edit the file directly and keep diffs minimal.

5. **Validate (after change)**
   - Run `scripts/validate_config.sh` again.
   - If it fails, restore from backup with `scripts/restore_config.sh`.

6. **Restart (only with explicit approval)**
   - If change requires restart, ask for approval first.
   - Use `openclaw gateway restart`.

## Guardrails
- **Never** restart or apply config without explicit user approval.
- **Never** remove keys or reorder blocks unless requested.
- **Always** keep a backup before edits.
- If unsure about schema: run `openclaw doctor --non-interactive` and stop on errors.

## Scripts
- `scripts/backup_config.sh` — create timestamped backup
- `scripts/validate_config.sh` — validate config via OpenClaw doctor
- `scripts/diff_config.sh` — diff current config vs backup
- `scripts/restore_config.sh` — restore backup

## Validation
- Use `openclaw doctor --non-interactive` for schema validation
- This checks against the actual schema that the gateway uses
- Warns about unknown keys, invalid types, and security issues
