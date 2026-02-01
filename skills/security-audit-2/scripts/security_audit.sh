#!/usr/bin/env bash
set -u

# Convenience wrapper for our audit gate.
# Default target: current directory.
# Always emits JSON to stdout (even when findings exist).
# Optionally writes JSON to --out.
#
# Note: run_audit_json.sh uses exit code 10 for findings. We intentionally
# swallow non-zero exit codes here so callers always get a JSON payload.

# Default: audit the current OpenClaw workspace root.
TARGET="/home/virta/.openclaw/workspace"
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    *) TARGET="$1"; shift; break;;
  esac
done

cd /home/virta/.openclaw/workspace/hybrid_orchestrator

REPORT=""
set +e
REPORT=$(./scripts/audit/run_audit_json.sh "$TARGET")
RC=$?
set -e

if [[ -n "$OUT" ]]; then
  mkdir -p "$(dirname "$OUT")"
  printf '%s\n' "$REPORT" > "$OUT"
fi

printf '%s\n' "$REPORT"

# Preserve signal via exit code for shell users, but do not break OpenClaw exec calls:
# OpenClaw treats non-zero as tool failure. So we always exit 0.
# (Callers should read `.ok` in the JSON.)
exit 0
