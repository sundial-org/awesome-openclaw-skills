---
name: simple-backup
description: Backup agent brain (workspace) and body (state) to local folder and optionally sync to cloud via rclone.
metadata: {"clawdbot":{"emoji":"💾","requires":{"bins":["rclone","gpg","tar"]}}}
---

# Simple Backup

A robust backup script that:
1.  **Stages:** Copies `~/clawd` (workspace), `~/.clawdbot` (state), and `skills/`.
2.  **Compresses:** Creates a `.tgz` archive.
3.  **Encrypts:** AES256 encryption using GPG (password required).
4.  **Prunes:** Rotates backups (Daily/Hourly retention).
5.  **Syncs:** Optionally pushes to a cloud provider via `rclone`.

## Setup

1.  **Dependencies:** Ensure `rclone` and `gpg` are installed (`brew install rclone gnupg`).
2.  **Password:** Set the encryption password:
    *   Env Var: `export BACKUP_PASSWORD="my-secret-password"`
    *   File: `~/.clawdbot/credentials/backup.key`
3.  **Cloud (Optional):** Configure an rclone remote:
    ```bash
    rclone config
    ```

## Usage

Run the backup:
```bash
simple-backup
```

## Configuration

You can override defaults with environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKUP_ROOT` | `~/clawd/BACKUPS` | Local storage location |
| `REMOTE_DEST` | (empty) | Rclone path (e.g. `gdrive:backups`) |
| `MAX_DAYS` | 7 | Days to keep daily backups |
| `HOURLY_RETENTION_HOURS` | 24 | Hours to keep hourly backups |
