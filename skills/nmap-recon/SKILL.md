# Nmap Recon

Network reconnaissance and port scanning using Nmap. Use when asked to scan a target, find open ports, detect services, check for vulnerabilities, or perform network reconnaissance.

## Triggers

- "scan [target]", "port scan", "nmap", "what ports are open", "recon [target]", "service detection", "vulnerability scan"

## Requirements

- `nmap` must be installed (standard on Kali, available via package managers)
- Root/sudo for SYN scans and OS detection

## Usage

### Quick Scan (Top 1000 ports)
```bash
nmap -sC -sV -oA scan_$(date +%Y%m%d_%H%M%S) TARGET
```

### Full Port Scan
```bash
nmap -p- -sC -sV -oA fullscan_$(date +%Y%m%d_%H%M%S) TARGET
```

### Fast Scan (Quick check)
```bash
nmap -F -T4 TARGET
```

### Stealth SYN Scan (requires root)
```bash
sudo nmap -sS -sV -O -oA stealth_$(date +%Y%m%d_%H%M%S) TARGET
```

### UDP Scan (Top 100 ports)
```bash
sudo nmap -sU --top-ports 100 -oA udp_$(date +%Y%m%d_%H%M%S) TARGET
```

### Vulnerability Scan
```bash
nmap --script vuln -oA vulnscan_$(date +%Y%m%d_%H%M%S) TARGET
```

### Aggressive Scan (OS, version, scripts, traceroute)
```bash
nmap -A -T4 -oA aggressive_$(date +%Y%m%d_%H%M%S) TARGET
```

## Output Parsing

Nmap outputs in multiple formats with `-oA`:
- `.nmap` - Human readable
- `.xml` - Machine parseable
- `.gnmap` - Greppable format

### Parse open ports from greppable output:
```bash
grep "open" scan.gnmap | awk -F'[/]' '{print $1}' | tr ',' '\n' | sort -u
```

### Extract service versions:
```bash
grep -E "^[0-9]+/" scan.nmap | awk '{print $1, $3, $4}'
```

### Quick summary from XML:
```bash
xmllint --xpath "//port[@state='open']" scan.xml 2>/dev/null
```

## Common Scan Profiles

| Profile | Command | Use Case |
|---------|---------|----------|
| Quick | `nmap -F -T4` | Fast initial recon |
| Standard | `nmap -sC -sV` | Service detection + default scripts |
| Full | `nmap -p- -sC -sV` | All 65535 ports |
| Stealth | `sudo nmap -sS -T2` | Evasive scanning |
| Vuln | `nmap --script vuln` | Vulnerability detection |
| Aggressive | `nmap -A -T4` | Full enumeration |

## Script Categories

```bash
# List available scripts
ls /usr/share/nmap/scripts/

# Run specific category
nmap --script=default,safe TARGET
nmap --script=vuln TARGET
nmap --script=exploit TARGET
nmap --script=auth TARGET

# Run specific script
nmap --script=http-title TARGET
nmap --script=smb-vuln* TARGET
```

## Target Specification

```bash
# Single host
nmap 192.168.1.1

# CIDR range
nmap 192.168.1.0/24

# Range
nmap 192.168.1.1-254

# From file
nmap -iL targets.txt

# Exclude hosts
nmap 192.168.1.0/24 --exclude 192.168.1.1
```

## Timing Templates

- `-T0` Paranoid (IDS evasion)
- `-T1` Sneaky (IDS evasion)
- `-T2` Polite (slow)
- `-T3` Normal (default)
- `-T4` Aggressive (fast)
- `-T5` Insane (very fast, may miss ports)

## Authorization Required

⚠️ **Only scan targets you own or have explicit written authorization to test.**

Never scan:
- Public infrastructure without permission
- Networks you don't control
- Production systems without approval

## Example Workflow

```bash
# 1. Quick scan to find live hosts
nmap -sn 192.168.1.0/24 -oA live_hosts

# 2. Fast port scan on discovered hosts
nmap -F -T4 -iL live_hosts.gnmap -oA quick_ports

# 3. Deep scan interesting hosts
nmap -p- -sC -sV -oA deep_scan TARGET

# 4. Vulnerability scan
nmap --script vuln -oA vuln_scan TARGET
```
