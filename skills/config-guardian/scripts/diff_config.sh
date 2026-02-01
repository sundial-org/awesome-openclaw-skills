#!/usr/bin/env bash
set -euo pipefail

BACKUP_PATH="${1:?Usage: diff_config.sh <backup_path> [config_path]}"
CONFIG_PATH="${2:-$HOME/.openclaw/openclaw.json}"

diff -u "$BACKUP_PATH" "$CONFIG_PATH" || true
