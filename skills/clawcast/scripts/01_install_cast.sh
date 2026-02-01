#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DIR}/00_lib.sh"
state_init
enable_strict_path
bold "1) Installing cast (Foundry)"
line
if has_cmd cast; then
  ok "cast is already installed: $(cast --version 2>/dev/null || echo cast)"
  exit 0
fi
if ! has_cmd curl; then
  err "curl is required but not found. Install curl and re-run."
  exit 1
fi
warn "cast not found. Installing Foundry..."
curl -L https://foundry.paradigm.xyz | bash
enable_strict_path
if ! has_cmd foundryup; then
  for p in "${HOME}/.bashrc" "${HOME}/.zshrc" "${HOME}/.profile"; do
    [[ -f "$p" ]] && source "$p" >/dev/null 2>&1 || true
  done
fi
if ! has_cmd foundryup; then
  err "foundryup not found after install. Make sure ${FOUNDRY_BIN_DIR} is in PATH, then re-run."
  exit 1
fi
foundryup
enable_strict_path
if ! has_cmd cast; then
  err "cast still not found after Foundry install."
  exit 1
fi
ok "Installed cast: $(cast --version 2>/dev/null || echo cast)"
