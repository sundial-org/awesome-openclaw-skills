#!/usr/bin/env bash
set -euo pipefail

BACKUP_PATH="${1:?Usage: restore_config.sh <backup_path> [config_path]}"
CONFIG_PATH="${2:-$HOME/.openclaw/openclaw.json}"

cp "$BACKUP_PATH" "$CONFIG_PATH"
echo "Restored $CONFIG_PATH from $BACKUP_PATH"
