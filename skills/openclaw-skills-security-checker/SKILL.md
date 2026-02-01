---
name: security-skill-scanner
version: 1.0.0
description: Security scanner for ClawdHub skills - detects suspicious patterns, manages whitelists, and monitors Moltbook for security threats.
homepage: https://github.com/digitaladaption/openclaw-skills-security-checker
metadata: {"clawdbot":{"emoji":"🔒","category":"security"},"author":"ClaudiatheLobster"}
---

# Security Skill Scanner

Scans ClawdHub skills for suspicious patterns, manages permission manifests, and monitors Moltbook for security threats.

## Features

- **Pattern Detection**: Scans SKILL.md files for credential theft, command injection, network exfil patterns
- **Whitelist Management**: Maintains list of known legitimate skills
- **Moltbook Monitoring**: Continuously monitors Moltbook for security discussions and scam alerts
- **Permission Manifests**: Generates and tracks skill permissions with Isnad chains
- **Daily Reports**: Automatic scanning with markdown/JSON reports

## Usage

### Scan All Skills
```bash
python3 /root/clawd/skills/security-skill-scanner/skill-scanner.py
```

### Scan Specific Skill
```bash
python3 /root/clawd/skills/security-skill-scanner/skill-scanner.py --skill nano-banana-pro
```

### Add to Whitelist
```bash
python3 /root/clawd/skills/security-skill-scanner/whitelist-manager.py add skill-name "reason for whitelist"
```

### Check Whitelist
```bash
python3 /root/clawd/skills/security-skill-scanner/whitelist-manager.py list
```

### Monitor Moltbook (One-shot)
```bash
bash /root/clawd/skills/security-skill-scanner/moltbook-monitor.sh
```

## Files

| File | Purpose |
|------|---------|
| `skill-scanner.py` | Main scanner with regex pattern detection |
| `whitelist-manager.py` | Manage false-positive whitelist |
| `moltbook-monitor.sh` | Moltbook security feed monitor |
| `permission-manager.py` | Generate skill permission manifests |
| `data/whitelist.json` | Whitelisted skills database |

## Patterns Detected

| Category | Patterns |
|----------|----------|
| Credential Theft | .env access, webhook.site, POST secrets |
| Command Injection | os.system, eval, shell=True, subprocess |
| Network Exfil | HTTP requests with Bearer tokens |
| Suspicious Downloads | wget, curl -O, remote scripts |

## Whitelisted Skills

These skills are known legitimate and excluded from warnings:
- nano-banana-pro (Google Gemini)
- notion (Notion API)
- trello (Trello API)
- gog (Google Workspace)
- local-places (Google Places)
- bluebubbles (iMessage)
- weather (Weather API)
- And 5 more...

## Cron Jobs (Optional)

Add to crontab for automated scanning:
```bash
# Daily skill scan at 4 AM
0 4 * * * python3 /root/clawd/skills/security-skill-scanner/skill-scanner.py >> /var/log/skill-scan.log 2>&1

# Moltbook monitor every 30 min
*/30 * * * * bash /root/clawd/skills/security-skill-scanner/moltbook-monitor.sh >> /var/log/moltbook-monitor.log 2>&1
```

## Pre-Install Hook (Block Suspicious Skills)

Install new skills with automatic security scanning that **BLOCKS** suspicious installations:

### Quick Install with Scan
```bash
# Interactive mode (asks before installing)
bash /root/clawd/skills/security-skill-scanner/install-skill.sh nano-banana-pro

# With force override (installs even if suspicious)
bash /root/clawd/skills/security-skill-scanner/install-skill.sh suspicious-skill --force

# Scan-only mode
python3 /root/clawd/skills/security-skill-scanner/install-hook.py skill-name --scan-only
```

### Integration with molthub

Add to your shell profile for automatic scanning on every install:

```bash
# Add to ~/.bashrc or ~/.zshrc
molthub() {
    if [ "$1" = "install" ] || [ "$1" = "add" ]; then
        python3 /root/clawd/skills/security-skill-scanner/install-hook.py "$2" --interactive
    else
        /home/linuxbrew/.linuxbrew/bin/molthub "$@"
    fi
}
```

Now every `molthub install <skill>` will be scanned first!

### What Happens

1. **Clean skill** → Installs normally ✅
2. **Whitelisted skill** → Installs normally ✅
3. **Suspicious skill** → **BLOCKED** with explanation 🚫
4. **Suspicious + --force** → Warns but installs ⚠️

### Example Output

```
🔒 Pre-Install Security Scan: nano-banana-pro
----------------------------------------------
Status: whitelisted
Action: allowed
✅ Scan passed - safe to install

🚀 Proceeding with installation...
✅ nano-banana-pro installed successfully
```

vs

```
🔒 Pre-Install Security Scan: weather-scam
----------------------------------------------
Status: suspicious
Action: blocked

🚨 THREATS DETECTED:
   🔴 [credential_theft] Access to .env file
      File: SKILL.md
   🔴 [network_exfil] HTTP requests with Bearer tokens
      File: scripts/steal_creds.py

❌ INSTALLATION BLOCKED

To override: python3 install-hook.py weather-scam --force
```

## Reports

- `/tmp/security-scanner/scan-report.md` - Human-readable scan results
- `/tmp/security-scanner/scan-results.json` - Structured JSON output
- `/tmp/security-scanner/moltbook-scan.log` - Moltbook monitoring log

## Integration

Import as a module:
```python
from skill_scanner import RegexScanner

scanner = RegexScanner()
results = scanner.scan_all_skills()
print(f"Found {results['threats_found']} threats")
```
