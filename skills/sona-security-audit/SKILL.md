---
name: security-audit
description: "Fail-closed security auditing for OpenClaw/ClawHub skills & repos: trufflehog secrets scanning, semgrep SAST, prompt-injection/persistence signals, and supply-chain hygiene checks before enabling or installing."
metadata: {"openclaw":{"emoji":"🛡️","requires":{"bins":["jq","trufflehog","semgrep","python3"]},"install":[{"id":"apt-jq","kind":"apt","package":"jq","bins":["jq"],"label":"Install jq (apt)"},{"id":"apt-ghog","kind":"apt","package":"python3","bins":["python3"],"label":"Install Python 3 (apt)"},{"id":"apt-trufflehog","kind":"apt","package":"trufflehog","bins":["trufflehog"],"label":"Install trufflehog (apt)"},{"id":"pipx-semgrep","kind":"shell","label":"Install semgrep (pipx)","command":"python3 -m pip install --user pipx && python3 -m pipx ensurepath && pipx install semgrep"},{"id":"brew-jq","kind":"brew","formula":"jq","bins":["jq"],"label":"Install jq (brew)"},{"id":"brew-trufflehog","kind":"brew","formula":"trufflehog","bins":["trufflehog"],"label":"Install trufflehog (brew)"},{"id":"brew-semgrep","kind":"brew","formula":"semgrep","bins":["semgrep"],"label":"Install semgrep (brew)"}]}}
---

# security-audit

A hostile-by-design, **fail-closed** audit workflow for codebases and OpenClaw/ClawHub skills.

It does **not** try to answer “does this skill work?”.
It tries to answer: **“can this skill betray the system?”**

## What it checks (high level)

This skill’s scripts combine multiple layers:

- **Secrets / credential leakage:** trufflehog
- **Static analysis:** semgrep (auto rules)
- **Hostile repo audit (custom):** prompt-injection signals, persistence mechanisms, suspicious artifacts, dependency hygiene

If any layer fails, the overall audit is **FAIL**.

## Run an audit (JSON)

From this skill folder (use `bash` so it works even if executable bits were not preserved by a zip download):

```bash
bash scripts/run_audit_json.sh <path>
```

Example:

```bash
bash scripts/run_audit_json.sh . > /tmp/audit.json
jq '.ok, .tools' /tmp/audit.json
```

### Security levels (user configurable)

Set the strictness level (default: `standard`):

```bash
OPENCLAW_AUDIT_LEVEL=standard bash scripts/run_audit_json.sh <path>
OPENCLAW_AUDIT_LEVEL=strict   bash scripts/run_audit_json.sh <path>
OPENCLAW_AUDIT_LEVEL=paranoid bash scripts/run_audit_json.sh <path>
```

- `standard`: pragmatic strict defaults (lockfiles required; install hooks/persistence/prompt-injection signals fail)
- `strict`: more patterns become hard FAIL (e.g. minified/obfuscation artifacts)
- `paranoid`: no "best-effort" hashing failures; more fail-closed behavior

## Manifest requirement (for zero-trust install workflows)

For strict/quarantine workflows, require a machine-readable intent/permissions manifest at repo root:

- `openclaw-skill.json`

If a repo/skill does not provide this manifest, the hostile audit should treat it as **FAIL**.

See: `docs/OPENCLAW_SKILL_MANIFEST_SCHEMA.md`.

## Optional: execution sandbox (Docker)

Docker is **optional** here. This skill can be used for static auditing without Docker.

If you want to execute any generated/untrusted code, run it in a separate sandbox workflow (recommended).

## Files

- `scripts/run_audit_json.sh` — main JSON audit runner
- `scripts/hostile_audit.py` — prompt-injection/persistence/dependency hygiene scanner
- `scripts/security_audit.sh` — convenience wrapper (always returns JSON, never non-zero)
- `openclaw-skill.json` — machine-readable intent/permissions manifest
