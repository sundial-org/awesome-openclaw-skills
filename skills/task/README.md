# /task skill (tasker docstore)

Profiles:
- Natural language (this folder): NL + `/task` with `disable-model-invocation: false`
- Slash-only: copy `skills/task-slash/` into your skills folder as `task/` (low-bloat)

This skill uses:
- `command-dispatch: tool` for deterministic behavior

It expects:
- plugin tool `tasker_cmd` allowlisted (recommended)
- `tasker` CLI available via plugin `binary` config, `TASKER_BIN`, or PATH

See `docs/CLAWDBOT_INTEGRATION.md` at repo root for end-to-end setup.
