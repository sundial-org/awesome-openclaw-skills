#!/usr/bin/env bash
# safe-install.sh — Install a ClawdHub skill with automatic security audit
# Usage: safe-install.sh <slug> [clawdhub args...]
# Installs the skill, audits it, and removes it if critical issues are found.

set -uo pipefail

SLUG="${1:?Usage: safe-install.sh <slug> [clawdhub args...]}"
shift
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Detect workspace: CLAWDHUB_WORKDIR > git root > cwd
if [ -n "${CLAWDHUB_WORKDIR:-}" ]; then
  WORKDIR="$CLAWDHUB_WORKDIR"
elif git rev-parse --show-toplevel &>/dev/null; then
  WORKDIR="$(git rev-parse --show-toplevel)"
else
  WORKDIR="$(pwd)"
fi

SKILL_DIR="$WORKDIR/skills/$SLUG"

echo "📦 Installing $SLUG..."
OUTPUT=$(cd "$WORKDIR" && clawdhub install "$SLUG" "$@" 2>&1)
INSTALL_EXIT=$?

if [ $INSTALL_EXIT -ne 0 ]; then
  echo "$OUTPUT"
  echo "❌ Install failed."
  exit 1
fi

echo "$OUTPUT"

# Run audit
echo ""
echo "🔍 Running security audit..."
AUDIT_OUTPUT=$("$SCRIPT_DIR/skill-audit.sh" "$SKILL_DIR" 2>&1)
AUDIT_EXIT=$?

echo "$AUDIT_OUTPUT"

if [ $AUDIT_EXIT -eq 2 ]; then
  echo ""
  echo "⛔ CRITICAL issues found — removing $SLUG"
  rm -rf "$SKILL_DIR"
  echo "🗑️  Removed $SKILL_DIR"
  echo ""
  echo "If you've reviewed the skill and trust it, install manually:"
  echo "  clawdhub install $SLUG"
  exit 2
elif [ $AUDIT_EXIT -eq 1 ]; then
  echo ""
  echo "⚠️  Warnings found — $SLUG installed but review recommended"
  exit 0
else
  echo ""
  echo "✅ $SLUG installed and passed security audit"
  exit 0
fi
