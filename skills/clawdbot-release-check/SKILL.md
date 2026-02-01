---
name: clawdbot-release-check
description: Check for new clawdbot releases and notify once per new version.
homepage: https://github.com/clawdbot/clawdbot
metadata: {"clawdbot":{"emoji":"🔄","requires":{"bins":["curl","jq"]}}}
---

# Clawdbot Release Check

Checks for new clawdbot releases from GitHub and notifies you once per version. No nagging.

## Installation

```bash
clawdhub install clawdbot-release-check
```

## Quick Setup (with cron)

```bash
# Add daily update check at 9am, notify via Telegram
{baseDir}/scripts/setup.sh --telegram YOUR_TELEGRAM_ID

# Custom hour (e.g., 8am)
{baseDir}/scripts/setup.sh --hour 8 --telegram YOUR_TELEGRAM_ID

# Remove cron job
{baseDir}/scripts/setup.sh --uninstall
```

After setup, restart the gateway:
```bash
launchctl kickstart -k gui/$(id -u)/com.clawdis.gateway
```

## Manual Usage

```bash
# Check for updates (silent if up-to-date or already notified)
{baseDir}/scripts/check.sh

# Show version info
{baseDir}/scripts/check.sh --status

# Force notification (bypass "already notified" state)
{baseDir}/scripts/check.sh --force

# Show highlights from ALL missed releases
{baseDir}/scripts/check.sh --all-highlights

# Clear state (will notify again on next check)
{baseDir}/scripts/check.sh --reset

# Help
{baseDir}/scripts/check.sh --help
```

## How It Works

1. Fetches latest release from `github.com/clawdbot/clawdbot/releases`
2. Compares with your installed version (from `package.json`)
3. If behind, shows highlights from release notes
4. Saves state to prevent repeat notifications

## Example Output

```
🔄 **Clawdbot Update Available!**

Current: `2.0.0-beta5`
Latest:  `2026.1.5-3`

_(3 versions behind)_

**Highlights:**
- Models: add image-specific model config
- Agent tools: new `image` tool
- Config: default model shorthands

🔗 https://github.com/clawdbot/clawdbot/releases/tag/v2026.1.5-3

To update: `cd /path/to/clawdis && git pull && pnpm install && pnpm build`
```

## Files

**State** — `~/.clawdbot/clawdbot-release-check-state.json`:
```json
{
  "lastNotifiedVersion": "v2026.1.5-3",
  "lastCheckMs": 1704567890123
}
```

**Cache** — `~/.clawdbot/clawdbot-release-check-cache.json`:
- Release data cached for 24 hours (saves API calls)
- Highlights extracted once per release (saves tokens)
- Use `--clear-cache` to force refresh

## Configuration

Environment variables:
- `CLAWDBOT_DIR` — Path to clawdbot source (auto-detected from `~/dev/clawdis`, `~/clawdbot`, or npm global)
- `CACHE_MAX_AGE_HOURS` — Cache TTL in hours (default: 24)


