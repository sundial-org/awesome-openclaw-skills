#!/bin/bash
set -e

# ==========================================
# Simple Backup Script
# ==========================================
# Backs up Clawdbot brain, body, and skills to local folder + rclone remote.
# ==========================================

# Ensure PATH includes homebrew
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# --- Configuration (Defaults can be overridden by Env Vars) ---
# Where backups are stored locally
BACKUP_ROOT="${BACKUP_ROOT:-$HOME/clawd/BACKUPS}"

# Where backups are sent (Rclone remote:path)
# Example: "gdrive:backups"
REMOTE_DEST="${REMOTE_DEST:-}"

# Retention settings
MAX_DAYS="${MAX_DAYS:-7}"
HOURLY_RETENTION_HOURS="${HOURLY_RETENTION_HOURS:-24}"

# Source directories to backup
BRAIN_DIR="${BRAIN_DIR:-$HOME/clawd}"
BODY_DIR="${BODY_DIR:-$HOME/.clawdbot}"
SKILLS_DIR="${SKILLS_DIR:-$HOME/clawdbot/skills}"

# --- Dependency Check ---
for cmd in tar gpg rclone; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is not installed."
        exit 1
    fi
done

# --- Credential Check ---
# 1. Try Env Var
# 2. Try Standard Credential File
if [ -z "$BACKUP_PASSWORD" ]; then
    KEY_FILE="$HOME/.clawdbot/credentials/backup.key"
    if [ -f "$KEY_FILE" ]; then
        BACKUP_PASSWORD=$(cat "$KEY_FILE" | tr -d '\n')
    else
        echo "Error: Encryption password missing."
        echo "Set BACKUP_PASSWORD env var OR place password in $KEY_FILE"
        exit 1
    fi
fi

# --- Setup ---
TIMESTAMP=$(date +%Y%m%d-%H%M)
TODAY=$(date +%Y%m%d)
CURRENT_HOUR=$(date +%H)
STAGING_DIR=$(mktemp -d)

mkdir -p "$BACKUP_ROOT"

# Label logic: DAILY once per day after 3AM, otherwise HOURLY.
LABEL="HOURLY"
if [ "$CURRENT_HOUR" -ge 3 ]; then
    # If a daily backup for today doesn't exist yet, make this the daily one
    if ls "$BACKUP_ROOT"/backup-"$TODAY"-*-DAILY.tgz.gpg >/dev/null 2>&1; then
        LABEL="HOURLY"
    else
        LABEL="DAILY"
    fi
fi

ARCHIVE_NAME="backup-${TIMESTAMP}-${LABEL}.tgz"
ENCRYPTED_NAME="${ARCHIVE_NAME}.gpg"

echo "📦 Starting backup: ${TIMESTAMP} (${LABEL})"
echo "   Root: $BACKUP_ROOT"

# --- 1. Stage Files ---
echo "   Staging files..."
mkdir -p "$STAGING_DIR/clawd"
mkdir -p "$STAGING_DIR/.clawdbot"
mkdir -p "$STAGING_DIR/skills"

# Copy Brain (Workspace)
if [ -d "$BRAIN_DIR" ]; then
    rsync -a --exclude 'BACKUPS' --exclude '.git' --exclude 'node_modules' --exclude 'canvas' "$BRAIN_DIR/" "$STAGING_DIR/clawd/"
else
    echo "   Warning: Brain dir not found at $BRAIN_DIR"
fi

# Copy Body (State)
if [ -d "$BODY_DIR" ]; then
    rsync -a --exclude 'logs' --exclude 'media' --exclude 'browser' "$BODY_DIR/" "$STAGING_DIR/.clawdbot/"
else
    echo "   Warning: Body dir not found at $BODY_DIR"
fi

# Copy Skills
if [ -d "$SKILLS_DIR" ]; then
    rsync -a --exclude 'node_modules' "$SKILLS_DIR/" "$STAGING_DIR/skills/"
else
    echo "   Warning: Skills dir not found at $SKILLS_DIR"
fi

# --- 2. Compress ---
echo "   Compressing..."
tar -czf "$STAGING_DIR/$ARCHIVE_NAME" -C "$STAGING_DIR" .

# --- 3. Encrypt ---
echo "   Encrypting..."
gpg --batch --yes --passphrase "$BACKUP_PASSWORD" --symmetric --cipher-algo AES256 -o "$STAGING_DIR/$ENCRYPTED_NAME" "$STAGING_DIR/$ARCHIVE_NAME"

# --- 4. Move to Local Storage ---
mv "$STAGING_DIR/$ENCRYPTED_NAME" "$BACKUP_ROOT/"
echo "   Saved to $BACKUP_ROOT/$ENCRYPTED_NAME"

# --- 5. Cleanup Staging ---
rm -rf "$STAGING_DIR"

# --- 6. Prune Local Backups ---
echo "   Pruning old local backups (keeping $MAX_DAYS daily days, $HOURLY_RETENTION_HOURS hourly hours)..."
find "$BACKUP_ROOT" -type f -name "*-DAILY.tgz.gpg" -mtime +"$MAX_DAYS" -print0 | xargs -0 -I {} rm -- {} 2>/dev/null || true
find "$BACKUP_ROOT" -type f -name "*-HOURLY.tgz.gpg" -mmin +$((HOURLY_RETENTION_HOURS * 60)) -print0 | xargs -0 -I {} rm -- {} 2>/dev/null || true

# --- 7. Cloud Sync (Optional) ---
if [ -n "$REMOTE_DEST" ]; then
    echo "   Syncing to Cloud ($REMOTE_DEST)..."
    # Extract remote name (everything before :)
    REMOTE_NAME="${REMOTE_DEST%%:*}"
    
    if rclone listremotes | grep -q "$REMOTE_NAME"; then
        rclone sync "$BACKUP_ROOT" "$REMOTE_DEST" --include "*.gpg" --progress
        echo "✅ Backup complete and synced."
    else
        echo "⚠️  Remote '$REMOTE_NAME' not configured in rclone. Cloud sync skipped."
        echo "   Run 'rclone config' to setup."
    fi
else
    echo "ℹ️  REMOTE_DEST not set. Cloud sync skipped."
fi
