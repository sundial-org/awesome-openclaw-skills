---
name: tailscale
version: 1.0.0
description: Manage Tailscale tailnet via CLI and API. Use when the user asks to "check tailscale status", "list tailscale devices", "ping a device", "send file via tailscale", "tailscale funnel", "create auth key", "check who's online", or mentions Tailscale network management.
---

# Tailscale Skill

Hybrid skill using CLI for local operations and API for tailnet-wide management.

## Setup

API config (optional, for tailnet-wide operations): `~/.clawdbot/credentials/tailscale/config.json`

```json
{
  "apiKey": "tskey-api-k...",
  "tailnet": "-"
}
```

Get your API key from: Tailscale Admin Console → Settings → Keys → Generate API Key

The `tailnet` can be `-` (auto-detect), your org name, or email domain.

---

## Local Operations (CLI)

These work on the current machine only.

### Status & Diagnostics

```bash
# Current status (peers, connection state)
tailscale status
tailscale status --json | jq '.Peer | to_entries[] | {name: .value.HostName, ip: .value.TailscaleIPs[0], online: .value.Online}'

# Network diagnostics (NAT type, DERP, UDP)
tailscale netcheck
tailscale netcheck --format=json

# Get this machine's Tailscale IP
tailscale ip -4

# Identify a Tailscale IP
tailscale whois 100.x.x.x
```

### Connectivity

```bash
# Ping a peer (shows direct vs relay)
tailscale ping <hostname-or-ip>

# Connect/disconnect
tailscale up
tailscale down

# Use an exit node
tailscale up --exit-node=<node-name>
tailscale exit-node list
tailscale exit-node suggest
```

### File Transfer (Taildrop)

```bash
# Send files to a device
tailscale file cp myfile.txt <device-name>:

# Receive files (moves from inbox to directory)
tailscale file get ~/Downloads
tailscale file get --wait ~/Downloads  # blocks until file arrives
```

### Expose Services

```bash
# Share locally within tailnet (private)
tailscale serve 3000
tailscale serve https://localhost:8080

# Share publicly to internet
tailscale funnel 8080

# Check what's being served
tailscale serve status
tailscale funnel status
```

### SSH

```bash
# SSH via Tailscale (uses MagicDNS)
tailscale ssh user@hostname

# Enable SSH server on this machine
tailscale up --ssh
```

---

## Tailnet-Wide Operations (API)

These manage your entire tailnet. Requires API key.

### List All Devices

```bash
./scripts/ts-api.sh devices

# With details
./scripts/ts-api.sh devices --verbose
```

### Device Details

```bash
./scripts/ts-api.sh device <device-id-or-name>
```

### Check Online Status

```bash
# Quick online check for all devices
./scripts/ts-api.sh online
```

### Authorize/Delete Device

```bash
./scripts/ts-api.sh authorize <device-id>
./scripts/ts-api.sh delete <device-id>
```

### Device Tags & Routes

```bash
./scripts/ts-api.sh tags <device-id> tag:server,tag:prod
./scripts/ts-api.sh routes <device-id>
```

### Auth Keys

```bash
# Create a reusable auth key
./scripts/ts-api.sh create-key --reusable --tags tag:server

# Create ephemeral key (device auto-removes when offline)
./scripts/ts-api.sh create-key --ephemeral

# List keys
./scripts/ts-api.sh keys
```

### DNS Management

```bash
./scripts/ts-api.sh dns                 # Show DNS config
./scripts/ts-api.sh dns-nameservers     # List nameservers
./scripts/ts-api.sh magic-dns on|off    # Toggle MagicDNS
```

### ACLs

```bash
./scripts/ts-api.sh acl                 # Get current ACL
./scripts/ts-api.sh acl-validate <file> # Validate ACL file
```

---

## Common Use Cases

**"Who's online right now?"**
```bash
./scripts/ts-api.sh online
```

**"Send this file to my phone"**
```bash
tailscale file cp document.pdf my-phone:
```

**"Expose my dev server publicly"**
```bash
tailscale funnel 3000
```

**"Create a key for a new server"**
```bash
./scripts/ts-api.sh create-key --reusable --tags tag:server --expiry 7d
```

**"Is the connection direct or relayed?"**
```bash
tailscale ping my-server
```
