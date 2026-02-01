# AdGuard Home Controller Skill

Manage AdGuard Home DNS filtering from the command line. Check domains, add to allowlists/blocklists, toggle protection, and view statistics—all via the AdGuard REST API.

## Installation

```bash
clawdhub install rowbotik/adguard
```

## Quick Start

```bash
# Set your AdGuard admin password
export ADGUARD_PASSWORD=your_admin_password

# Check if a domain is blocked
./scripts/adguard.sh check doubleclick.net

# Add to allowlist
./scripts/adguard.sh allow broken-site.com

# View statistics
./scripts/adguard.sh status
```

## Configuration

Create `~/.adguard/config.json` or set environment variables:

```bash
export ADGUARD_URL="http://192.168.1.100:3000"
export ADGUARD_USERNAME="admin"
export ADGUARD_PASSWORD="your_password"
```

## Commands

| Command | Effect |
|---------|--------|
| `check <domain>` | Check if domain is blocked |
| `allow <domain>` | Add to allowlist (whitelist) |
| `block <domain>` | Add to blocklist |
| `status` | View statistics and protection status |
| `toggle` | Enable/disable DNS protection |
| `cache-clear` | Clear DNS cache |

## Examples

```bash
# Check a tracker domain
./scripts/adguard.sh check ads.google.com
# ✗ ads.google.com IS BLOCKED
#   Blocked by: Adblock Plus filter

# Whitelist a broken site
./scripts/adguard.sh allow bank.example.com
# ✓ Added rule: @@||bank.example.com^

# View stats
./scripts/adguard.sh status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Protection: ✓ ENABLED
# DNS Queries: 1,234
# Blocked by rules: 156
# Block rate: 12%

# Disable filtering temporarily
./scripts/adguard.sh toggle
# Disabling protection...
# ✓ Protection is now false
```

## Features

- ✓ Check if domains are filtered
- ✓ Add/remove from allowlists and blocklists
- ✓ View DNS statistics
- ✓ Toggle protection on/off
- ✓ Clear DNS cache
- ✓ Proper error handling and validation
- ✓ Session-based authentication

## Requirements

- AdGuard Home running with web interface
- Admin credentials
- `curl` installed (default on macOS/Linux)

## Finding Your AdGuard Home

1. **Router admin panel** — Look for a device on port 3000
2. **Same machine** — `http://localhost:3000`
3. **Network scan** — Check connected devices for "AdGuard Home"
4. **mDNS** — Try `http://adguard-home.local:3000`

## Filtering Rules

Rules follow AdGuard's DNS filtering syntax:

- `||example.com^` — Block example.com and subdomains
- `@@||example.com^` — Allow example.com (exception)
- `||tracker.example.com^` — Block only tracker subdomain

See `references/api.md` for complete syntax and API docs.

## Troubleshooting

**Error: Failed to authenticate**
→ Check `ADGUARD_PASSWORD` and `ADGUARD_URL` are correct

**Rules don't take effect immediately**
→ Run `./scripts/adguard.sh cache-clear`
→ Wait 5+ minutes for clients to refresh

**Can't connect**
→ Verify AdGuard is running: `curl http://<ip>:3000`
→ Check firewall allows port 3000

## Documentation

- **SKILL.md** — Full command reference and examples
- **references/api.md** — Complete AdGuard REST API documentation
- **scripts/adguard.sh** — Main CLI tool

## License

MIT
