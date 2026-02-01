---
name: beszel
description: Monitor home lab servers via Beszel (PocketBase).
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["node"]}}}
---

# Beszel Monitoring

Check the status of your local servers.

## Usage
- `beszel status` - Get status of all systems
- `beszel containers` - List top containers by CPU usage

## Commands
```bash
# Get status
source ~/.zshrc && ~/clawd/skills/beszel/index.js status

# Get container stats
source ~/.zshrc && ~/clawd/skills/beszel/index.js containers
```
