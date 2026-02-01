# Changelog

## 0.1.1
- Documentation: run scripts via `bash scripts/...` so installs still work if zip downloads do not preserve executable bits.

## 0.1.0
- Initial public release.
- Fail-closed JSON audit runner combining:
  - trufflehog (secrets)
  - semgrep (static analysis)
  - hostile repo audit (prompt injection signals, persistence checks, suspicious artifacts, dependency hygiene)
- Configurable strictness via `OPENCLAW_AUDIT_LEVEL=standard|strict|paranoid`.
- Includes a draft `openclaw-skill.json` manifest + schema notes.
