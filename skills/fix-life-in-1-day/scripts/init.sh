#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/handler.sh" start "${1:-en}" "${2:-$HOME/clawd}"
