---
name: bitwarden
description: Access and manage Bitwarden/Vaultwarden passwords securely using the rbw CLI.
metadata: {"clawdbot":{"emoji":"🔒","os":["linux","macos"],"requires":{"bins":["rbw"]}}}
---

# Bitwarden Skill

Interact with Bitwarden or Vaultwarden vaults using the `rbw` CLI.

## Usage & Configuration

### 1. Setup (First Run)
```bash
rbw config set email <your_email>
rbw config set baseurl <vault_url> # Optional, defaults to bitwarden.com
rbw login
```
*Note: Login requires the Master Password and potentially 2FA (email/TOTP).*

### 2. Unlock
```bash
rbw unlock
```
*Note: `rbw` caches the session key in the agent. If interactive input is required (pinentry), see if you can setup `pinentry-curses` (CLI-based pinentry) as the pinentry provider.*

### 3. Management
- **List items:** `rbw list`
- **Get item:** `rbw get "Name"`
- **Get JSON:** `rbw get --full "Name"`
- **Search:** `rbw search "query"`
- **Add:** `rbw add ...`
- **Sync:** `rbw sync` (Refresh vault)
*Note: Always sync before getting details to ensure accuracy.*
## Tools

The agent uses `exec` to run `rbw` commands.
- For unlocking, use `tmux` if `rbw` prompts for a password via pinentry-curses.
- For adding items, `rbw add` may require `EDITOR` configuration or `tmux`.
