# security-audit (OpenClaw skill)

This repository is a text-based OpenClaw/ClawHub skill bundle.

- Entry point: `SKILL.md`
- Purpose: hostile, fail-closed auditing of repos/skills before enabling

## Quick start

```bash
./scripts/run_audit_json.sh <path> > /tmp/audit.json
jq '.ok, .tools' /tmp/audit.json
```

## Security levels

```bash
OPENCLAW_AUDIT_LEVEL=standard ./scripts/run_audit_json.sh <path>
OPENCLAW_AUDIT_LEVEL=strict   ./scripts/run_audit_json.sh <path>
OPENCLAW_AUDIT_LEVEL=paranoid ./scripts/run_audit_json.sh <path>
```

## License

MIT (see `LICENSE`).
