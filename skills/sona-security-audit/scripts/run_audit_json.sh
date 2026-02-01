#!/usr/bin/env bash
set -euo pipefail

# Ensure user-local installs (pipx) are visible
export PATH="$HOME/.local/bin:$PATH"

# Run local security scanners and emit JSON to stdout.
# This is fail-closed: any hostile-audit violations fail the audit.
# Exit codes:
# 0 = pass
# 10 = fail (findings/policy violations)
# 3 = tools missing
# 2 = usage

TARGET=${1:-}
if [[ -z "$TARGET" ]]; then
  echo '{"ok":false,"error":"Usage: run_audit_json.sh <path>"}'
  exit 2
fi

missing=()
for t in jq trufflehog semgrep; do
  if ! command -v "$t" >/dev/null 2>&1; then
    missing+=("$t")
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  jq -n --argjson missing "$(printf '%s\n' "${missing[@]}" | jq -R . | jq -s .)" '{ok:false, error:"missing_tools", missing:$missing}'
  exit 3
fi

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

TRUFFLE_OUT="$TMPDIR/trufflehog.json"
SEMGREP_OUT="$TMPDIR/semgrep.json"
HOSTILE_OUT="$TMPDIR/hostile.json"

# Hostile repo audit (prompt injection, persistence, dependency policy, etc.)
# Configurable with OPENCLAW_AUDIT_LEVEL=standard|strict|paranoid
python3 ./scripts/hostile_audit.py "$TARGET" --level "${OPENCLAW_AUDIT_LEVEL:-standard}" >"$HOSTILE_OUT" || true

# Trufflehog JSON (silenced logs)
trufflehog filesystem "$TARGET" --no-update --json --log-level=-1 >"$TRUFFLE_OUT" 2>/dev/null || true

# Semgrep JSON (quiet)
semgrep scan --config auto --json --quiet "$TARGET" >"$SEMGREP_OUT" 2>/dev/null || true

# Count findings
TRUFFLE_COUNT=$(jq -s 'length' "$TRUFFLE_OUT" 2>/dev/null || echo 0)
SEMGREP_COUNT=$(jq '.results | length' "$SEMGREP_OUT" 2>/dev/null || echo 0)
HOSTILE_OK=$(jq -r '.ok // false' "$HOSTILE_OUT" 2>/dev/null || echo false)

OK=true
if [[ "$TRUFFLE_COUNT" -gt 0 || "$SEMGREP_COUNT" -gt 0 || "$HOSTILE_OK" != "true" ]]; then
  OK=false
fi

jq -n \
  --arg target "$TARGET" \
  --argjson ok "$OK" \
  --arg level "${OPENCLAW_AUDIT_LEVEL:-standard}" \
  --argjson truffleCount "$TRUFFLE_COUNT" \
  --argjson semgrepCount "$SEMGREP_COUNT" \
  --slurpfile hostile "$HOSTILE_OUT" \
  --slurpfile truffle "$TRUFFLE_OUT" \
  --slurpfile semgrep "$SEMGREP_OUT" \
  '{
    ok: $ok,
    target: $target,
    level: $level,
    tools: {
      hostile: { ok: ($hostile[0].ok // false) },
      trufflehog: { findings: $truffleCount },
      semgrep: { findings: $semgrepCount }
    },
    hostile: $hostile[0],
    trufflehog: $truffle,
    semgrep: $semgrep[0]
  }'

if [[ "$OK" == "true" ]]; then
  exit 0
else
  exit 10
fi
