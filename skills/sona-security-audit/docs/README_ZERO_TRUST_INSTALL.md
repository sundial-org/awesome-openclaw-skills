# Zero-trust-ish skill install (quarantine → hostile audit → promote)

**Goal:** never install skills directly into the live `skills/` directory.

Instead:
1) Install into **quarantine**
2) Run a **hostile pre-install audit** (fail-closed)
3) Only if clean, **promote** into the live skills dir

## Quarantine install

```bash
cd /home/virta/.openclaw/workspace/hybrid_orchestrator

# Audit only (no promotion)
./scripts/audit/quarantine_install.sh <slug>

# Audit + promote if clean
./scripts/audit/quarantine_install.sh <slug> --promote

# Choose strictness
./scripts/audit/quarantine_install.sh <slug> --level standard
./scripts/audit/quarantine_install.sh <slug> --level strict
./scripts/audit/quarantine_install.sh <slug> --level paranoid
```

## Policy defaults
- `standard` is the default level.
- **Network is deny-by-default**.
- Missing `openclaw-skill.json` manifest = **FAIL**.

## Where things go
- Quarantine: `~/.openclaw/quarantine/skills/<slug>`
- Reports: `~/.openclaw/quarantine/audits/<slug>/audit_<timestamp>.json`
- Live skills (promotion target): `/home/virta/.openclaw/workspace/skills/<slug>`

## Notes
- This is the enforcement layer. The audit itself is in `scripts/audit/run_audit_json.sh`.
- Sandbox behavioural simulation is planned next (Docker sealed run) and will also be fail-closed.
