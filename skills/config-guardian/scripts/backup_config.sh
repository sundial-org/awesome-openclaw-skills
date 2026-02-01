#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-$HOME/.openclaw/openclaw.json}"
BACKUP_DIR="${2:-$HOME/.openclaw/backups}"

mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_PATH="$BACKUP_DIR/openclaw-$STAMP.json"

cp "$CONFIG_PATH" "$BACKUP_PATH"
echo "$BACKUP_PATH"
