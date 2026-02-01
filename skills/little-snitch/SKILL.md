---
name: little-snitch
description: Control Little Snitch firewall on macOS. View logs, manage profiles and rule groups, monitor network traffic. Use when the user wants to check firewall activity, enable/disable profiles or blocklists, or troubleshoot network connections.
---

# Little Snitch CLI

Control Little Snitch network monitor/firewall on macOS.

## Setup

Enable CLI access in **Little Snitch → Preferences → Security → Allow access via Terminal**

Once enabled, the `littlesnitch` command is available in Terminal.

⚠️ **Security Warning:** The littlesnitch command is very powerful and can potentially be misused by malware. When access is enabled, you must take precautions that untrusted processes cannot gain root privileges.

Reference: https://help.obdev.at/littlesnitch5/adv-commandline

## Commands

| Command | Root? | Description |
|---------|-------|-------------|
| `--version` | No | Show version |
| `restrictions` | No | Show license status |
| `log` | No | Read log messages |
| `profile` | Yes | Activate/deactivate profiles |
| `rulegroup` | Yes | Enable/disable rule groups & blocklists |
| `log-traffic` | Yes | Print traffic log data |
| `list-preferences` | Yes | List all preferences |
| `read-preference` | Yes | Read a preference value |
| `write-preference` | Yes | Write a preference value |
| `export-model` | Yes | Export data model (backup) |
| `restore-model` | Yes | Restore from backup |
| `capture-traffic` | Yes | Capture process traffic |

## Examples

### View Recent Logs (no root)
```bash
littlesnitch log --last 10m --json
```

### Stream Live Logs (no root)
```bash
littlesnitch log --stream
```

### Check License Status (no root)
```bash
littlesnitch restrictions
```

### Activate Profile (requires root)
```bash
sudo littlesnitch profile --activate "Silent Mode"
```

### Deactivate All Profiles (requires root)
```bash
sudo littlesnitch profile --deactivate-all
```

### Enable/Disable Rule Group (requires root)
```bash
sudo littlesnitch rulegroup --enable "My Rules"
sudo littlesnitch rulegroup --disable "Blocklist"
```

### View Traffic History (requires root)
```bash
sudo littlesnitch log-traffic --begin-date "2026-01-25 00:00:00"
```

### Stream Live Traffic (requires root)
```bash
sudo littlesnitch log-traffic --stream
```

### Backup Configuration (requires root)
```bash
sudo littlesnitch export-model > backup.json
```

## Log Options

| Option | Description |
|--------|-------------|
| `--last <time>[m\|h\|d]` | Show entries from last N minutes/hours/days |
| `--stream` | Live stream messages |
| `--json` | Output as JSON |
| `--predicate <string>` | Filter with predicate |

## Notes

- macOS only
- Many commands require `sudo` (root access)
- Profiles: predefined rule sets (e.g., "Silent Mode", "Alert Mode")
- Rule groups: custom rule collections and blocklists
