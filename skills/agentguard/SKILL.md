# AgentGuard - Security Monitoring Skill

**Version:** 1.0.0  
**Author:** Manas AI  
**Category:** Security & Monitoring

## Overview

AgentGuard is a comprehensive security monitoring skill that watches over agent operations, detecting suspicious behavior, logging communications, and providing actionable security reports.

---

## Capabilities

### 1. File Access Monitoring
Track all file read/write operations with pattern analysis.

**Trigger:** Continuous background monitoring  
**Command:** `agentguard monitor files [--watch-dir <path>]`

**What it detects:**
- Unusual file access patterns (bulk reads, sensitive directories)
- Access to credential files (.env, .secrets, keys)
- Unexpected write operations to system directories
- File exfiltration attempts (large reads followed by network calls)

### 2. API Call Detection
Monitor outbound API calls for suspicious activity.

**Command:** `agentguard monitor api`

**What it detects:**
- Calls to unknown/untrusted endpoints
- Unusual API call frequency (rate anomalies)
- Sensitive data in request payloads
- Authentication token exposure
- Calls to known malicious domains

### 3. Communication Logging
Log all external communications for audit trails.

**Command:** `agentguard log comms [--output <path>]`

**Logs include:**
- HTTP/HTTPS requests (sanitized)
- WebSocket connections
- Email sends
- Message platform outputs (Telegram, Discord, etc.)
- Timestamp, destination, payload hash

### 4. Anomaly Detection
ML-lite pattern analysis for behavioral anomalies.

**Command:** `agentguard detect anomalies [--sensitivity <low|medium|high>]`

**Detection methods:**
- Baseline deviation (learns normal patterns)
- Time-of-day anomalies
- Sequence analysis (unusual operation chains)
- Volume spikes
- New destination detection

### 5. Security Reports
Generate comprehensive daily security reports.

**Command:** `agentguard report [--period <daily|weekly|monthly>]`

**Report includes:**
- Activity summary
- Alert breakdown by severity
- Top accessed resources
- Communication destinations
- Anomaly timeline
- Recommendations

---

## Configuration

### Config File: `config/agentguard.yaml`

```yaml
monitoring:
  enabled: true
  file_watch_dirs:
    - ~/clawd
    - ~/.clawdbot
  exclude_patterns:
    - "*.log"
    - "node_modules/**"
    - ".git/**"

alerts:
  sensitivity: medium  # low, medium, high
  channels:
    - telegram
  alert_on:
    - credential_access
    - bulk_file_read
    - unknown_api_endpoint
    - data_exfiltration
  cooldown_minutes: 15

api_monitoring:
  trusted_domains:
    - api.anthropic.com
    - api.openai.com
    - api.telegram.org
    - api.elevenlabs.io
  block_on_suspicious: false  # true = prevent call, false = alert only

logging:
  retention_days: 30
  log_dir: ~/.agentguard/logs
  hash_sensitive_data: true

reporting:
  auto_daily_report: true
  report_time: "09:00"
  report_channel: telegram
```

---

## Usage Examples

### Start Full Monitoring
```
agentguard start
```
Enables all monitoring features with default config.

### Check Current Security Status
```
agentguard status
```
Returns current threat level, active monitors, recent alerts.

### Investigate Specific Activity
```
agentguard investigate --timerange "last 2 hours" --type file_access
```

### Generate Immediate Report
```
agentguard report --now
```

### Review Alert History
```
agentguard alerts --last 24h --severity high
```

### Whitelist a Domain
```
agentguard trust add api.newservice.com --reason "Required for X integration"
```

---

## Alert Severity Levels

| Level | Color | Meaning | Example |
|-------|-------|---------|---------|
| INFO | 🔵 | Normal logged activity | File read in workspace |
| LOW | 🟢 | Minor deviation | Slightly elevated API calls |
| MEDIUM | 🟡 | Notable anomaly | Access to .env file |
| HIGH | 🟠 | Potential threat | Bulk credential access |
| CRITICAL | 🔴 | Immediate action needed | Data exfiltration pattern |

---

## Integration Points

### With Clawdbot
- Receives file/API operation hooks
- Sends alerts via configured channels
- Integrates with heartbeat for periodic checks

### With Other Skills
- Shares threat data with other security skills
- Can block operations (if configured)
- Provides audit logs for compliance skills

---

## Data Storage

```
~/.agentguard/
├── logs/
│   ├── file_access/
│   ├── api_calls/
│   └── communications/
├── baselines/
│   └── behavior_model.json
├── alerts/
│   └── YYYY-MM-DD.json
└── reports/
    └── YYYY-MM-DD_report.md
```

---

## Privacy & Security

- **No external data transmission** - All processing is local
- **Sensitive data hashing** - Credentials are never logged in plain text
- **Configurable retention** - Auto-delete old logs
- **Encrypted storage** - Optional AES encryption for logs

---

## Troubleshooting

### High false positive rate
→ Increase baseline learning period or reduce sensitivity

### Missing file events
→ Check `file_watch_dirs` config covers target directories

### Reports not generating
→ Verify `report_time` format and timezone settings

---

## Execution Scripts

| Script | Purpose |
|--------|---------|
| `execution/monitor.py` | Core monitoring daemon |
| `execution/detector.py` | Anomaly detection engine |
| `execution/logger.py` | Structured logging handler |
| `execution/alerter.py` | Alert dispatch system |
| `execution/reporter.py` | Report generation |

---

## Author Notes

AgentGuard is designed with defense-in-depth principles. It assumes agents can be compromised or manipulated, and provides visibility into their operations.

For maximum security, run AgentGuard in a separate process with limited write access to prevent a compromised agent from disabling monitoring.
