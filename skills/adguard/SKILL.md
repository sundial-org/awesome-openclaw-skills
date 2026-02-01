---
name: adguard
description: Control AdGuard Home DNS filtering via HTTP API. Use when managing blocklists/allowlists, checking domain filtering status, toggling protection, or clearing DNS cache. Supports blocking/allowing domains, viewing statistics, and protecting/disabling DNS filtering.
---

# AdGuard Home Controller

Manage AdGuard Home DNS filtering from the command line via the REST API.

## Requirements

- AdGuard Home running with web interface
- Admin username and password
- `curl` installed (usually default on macOS/Linux)

## Quick Start

```bash
# Set password once
export ADGUARD_PASSWORD=your_admin_password

# Use commands
./adguard.sh status
./adguard.sh check example.com
./adguard.sh allow broken-site.com
./adguard.sh block malware.ru
```

## Configuration

Set environment variables for your AdGuard instance:

```bash
export ADGUARD_URL="http://192.168.1.100:3000"      # Your AdGuard IP and port
export ADGUARD_USERNAME="admin"                     # Usually 'admin' (default)
export ADGUARD_PASSWORD="your_admin_password"       # REQUIRED
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

### Config File Alternative

Create `~/.adguard/config.json` (optional):

```json
{
  "url": "http://192.168.1.100:3000",
  "username": "admin"
}
```

Then set `ADGUARD_PASSWORD` separately for security.

## Commands

### check `<domain>`

Check if a domain is currently blocked or allowed.

```bash
./adguard.sh check doubleclick.net
# ✗ doubleclick.net IS BLOCKED
#   Blocked by: Adblock Plus filter

./adguard.sh check example.com
# ✓ example.com is NOT blocked (allowed)
```

### allow `<domain>` | whitelist `<domain>`

Add a domain to the allowlist (whitelist). Creates an exception rule that overrides blocklists.

```bash
./adguard.sh allow broken-site.com
# ✓ Added rule: @@||broken-site.com^
#   Domain: broken-site.com
#   Action: allow
```

### block `<domain>` | blacklist `<domain>`

Add a domain to the blocklist. Creates a custom blocking rule.

```bash
./adguard.sh block spyware-domain.ru
# ✓ Added rule: ||spyware-domain.ru^
#   Domain: spyware-domain.ru
#   Action: block
```

### status | stats

Display DNS filtering statistics and protection state.

```bash
./adguard.sh status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AdGuard Home Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Protection: ✓ ENABLED
# 
# DNS Queries: 1,234
# Blocked by rules: 156
# Blocked by safe browsing: 23
# Safe search replacements: 5
# Block rate: 14%
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### toggle | protection

Enable or disable DNS protection. Useful for temporarily disabling filtering.

```bash
./adguard.sh toggle
# Disabling protection...
# ✓ Protection is now false
```

### cache-clear

Clear the DNS cache to apply rule changes immediately.

```bash
./adguard.sh cache-clear
# Clearing DNS cache...
# ✓ Cache cleared
```

## Finding Your AdGuard Home Device

If you don't know your AdGuard URL:

1. **Router admin panel** — Look for a device named "AdGuard Home" or check for port 3000
2. **Local network scan** — Use `nmap` or check "Connected Devices"
3. **If running on same machine** — Default is `http://localhost:3000`
4. **mDNS/Bonjour** — Try `http://adguard-home.local:3000` (depends on network)

## Filtering Rules Syntax

AdGuard uses a DNS filtering rule syntax:

| Rule | Effect |
|------|--------|
| `\|\|example.com^` | Block example.com and subdomains |
| `@@\|\|example.com^` | Allow example.com (exception/whitelist) |
| `example.com` | Block exact domain only |
| `\|\|ad.example.com^` | Block only ad.example.com |

See [API Reference](references/api.md) for complete syntax.

## Common Scenarios

### Allow a site that's blocked by accident

```bash
adguard.sh allow my-bank.com
```

### Block a known malware domain

```bash
adguard.sh block malicious-tracker.xyz
```

### Check if a domain is being filtered

```bash
adguard.sh check ads.google.com
```

### View today's statistics

```bash
adguard.sh status
```

### Temporarily disable filtering (e.g., for troubleshooting)

```bash
adguard.sh toggle
```

## Troubleshooting

**Error: Failed to authenticate**
→ Check `ADGUARD_PASSWORD` is correct and set
→ Verify `ADGUARD_URL` points to the right IP and port

**Error: API call failed (HTTP 401)**
→ Authentication failed, check credentials

**Rules don't take effect**
→ Run `adguard.sh cache-clear` to flush DNS cache
→ Wait 5+ minutes for clients to refresh their cache
→ Restart your device's network connection

**Can't connect to AdGuard**
→ Verify device is on the same network
→ Check firewall isn't blocking port 3000
→ Ping the device: `ping <ip>`

## Advanced: Batch Operations

Block multiple domains:

```bash
for domain in tracker1.com tracker2.com tracker3.com; do
    adguard.sh block "$domain"
done
```

Check multiple domains:

```bash
for domain in example.com test.org my-site.net; do
    echo "Checking $domain..."
    adguard.sh check "$domain"
done
```

## API Reference

See [references/api.md](references/api.md) for complete AdGuard Home API documentation.
