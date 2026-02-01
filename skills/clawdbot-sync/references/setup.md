# Setup Guide

## Prerequisites

1. Both machines on same network (Tailscale recommended)
2. SSH access between machines
3. rsync installed on both

## SSH Key Setup

### On Source Machine (Server)

```bash
# Generate key if needed
ssh-keygen -t ed25519 -C "clawdbot-sync"

# Copy to target
ssh-copy-id user@target-host

# Test connection
ssh user@target-host "echo ok"
```

### Tailscale Setup

Both machines should be on the same Tailscale network:

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Login
tailscale up

# Check status
tailscale status
```

## Adding Peers

```bash
# Syntax
/sync add <name> <host> <user> <remote-path>

# Examples
/sync add mac-mini 100.95.193.55 clawdbot /Users/clawdbot/clawd
/sync add server 100.89.48.26 clawdbot /home/clawdbot/clawd
```

## Testing

```bash
# Check connection
/sync status

# Preview changes
/sync diff mac-mini

# Sync
/sync now mac-mini
```

## Troubleshooting

### Connection Refused
- Check SSH is running: `systemctl status ssh`
- Check firewall: `sudo ufw allow ssh`

### Permission Denied
- Ensure SSH keys are set up
- Check authorized_keys permissions: `chmod 600 ~/.ssh/authorized_keys`

### Tailscale Not Connected
- Check status: `tailscale status`
- Re-authenticate: `tailscale up --reset`
