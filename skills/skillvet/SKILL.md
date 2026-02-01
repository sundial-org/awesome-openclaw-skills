---
name: skillvet
description: Security scanner for ClawHub/community skills — detects malware, credential theft, exfiltration, prompt injection, and obfuscation before you install. Use when installing skills from ClawHub or any public marketplace, reviewing third-party agent skills for safety, or vetting untrusted code before giving it to your AI agent. Triggers: install skill, audit skill, check skill, vet skill, skill security, safe install, is this skill safe.
---

# Skillvet

Security scanner for agent skills. 15 critical checks, 5 warning checks. No dependencies — just bash and grep.

## Usage

**Safe install** (installs, audits, auto-removes if critical):

```bash
bash skills/skillvet/scripts/safe-install.sh <skill-slug>
```

**Audit an existing skill:**

```bash
bash skills/skillvet/scripts/skill-audit.sh skills/some-skill
```

**Audit all installed skills:**

```bash
for d in skills/*/; do bash skills/skillvet/scripts/skill-audit.sh "$d"; done
```

Exit codes: `0` clean, `1` warnings only, `2` critical findings.

## Critical Checks (auto-blocked)

| Check | Example |
|-------|---------|
| Known exfiltration endpoints | webhook.site, ngrok.io, requestbin |
| Bulk env variable harvesting | `printenv \|`, `${!*@}` |
| Foreign credential access | ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN in scripts |
| Code obfuscation | eval(), base64 decode, hex escapes |
| Path traversal / sensitive files | `../../`, `~/.ssh`, `~/.clawdbot` |
| Data exfiltration via curl/wget | `curl --data`, `wget --post` with variables |
| Reverse/bind shells | `/dev/tcp/`, `nc -e`, `socat` |
| .env file theft | dotenv loading in scripts (not docs) |
| Prompt injection in markdown | "ignore previous instructions" in SKILL.md |
| LLM tool exploitation | Instructions to send/email secrets |
| Agent config tampering | Write/modify AGENTS.md, SOUL.md, clawdbot.json |
| Unicode obfuscation | Zero-width chars, RTL override |
| Suspicious setup commands | curl piped to bash |
| Social engineering | Download external binaries |
| Shipped .env files | .env files (not .example) in the skill |

## Warning Checks (flagged for review)

Subprocess execution, network requests, minified/bundled files, file write operations, unknown external tool requirements.

## Limitations

Static analysis only. English-centric prompt injection patterns. Minified JS is flagged but not deobfuscated. A clean scan raises the bar but doesn't guarantee safety.

The scanner flags itself when audited — its own patterns contain the strings it detects. This is expected.
