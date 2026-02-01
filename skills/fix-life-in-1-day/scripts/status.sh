#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/handler.sh" status "${1:-$HOME/clawd}"
