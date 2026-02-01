# Monitor Pattern

Watch for conditions and notify. Focuses on **clawdbot-specific integration** — cron vs heartbeat, state location, notification routing.

## Trigger: Cron vs Heartbeat

| Use Cron | Use Heartbeat |
|----------|---------------|
| Precise timing matters | Approximate frequency OK |
| Resource-intensive checks | Quick, lightweight checks |
| Dedicated scheduling | Piggyback on existing heartbeat |
| Needs to wake system | Only when session active |

### Cron Setup

For scheduled monitoring, use Clawdbot's cron system. Consult **clawddocs** `/automation/cron-jobs` for:
- Configuration format and options
- Schedule syntax (standard cron expressions)
- Prompt patterns for triggering skills

### Heartbeat Integration

Add to `<workspace>/HEARTBEAT.md`:

```markdown
## Monitor Check

If last monitor-name check was >1 hour ago:
1. Run `<skill>/scripts/check.py`
2. If alerts, notify user
3. Update heartbeat-state.json
```

## State Location

```
<skill>/state.json    # preferred — travels with skill
```

**Contents:**
```json
{
  "lastCheck": "2025-01-20T10:00:00Z",
  "lastValue": 42,
  "lastNotified": "2025-01-20T09:00:00Z"
}
```

## Notification via message

```
message action:send channel:telegram message:"🚨 [Monitor] Alert: [condition]"
```

**Format:**
```
🚨 **[Monitor Name]**
Condition: [what happened]
Current: [value]
Previous: [value]
```

## De-duplication

Avoid spam:

**Time-based:** Max once per hour for same condition
```python
if condition and (now - last_notified) > hours(1):
    notify()
```

**Threshold-crossing:** Only on crossing, not while above
```python
if current > threshold and previous <= threshold:
    notify("crossed above")
```

## Script Pattern

`<skill>/scripts/check.py`:

```python
#!/usr/bin/env python3
import json
from pathlib import Path

STATE = Path(__file__).parent.parent / "state.json"

def check():
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    current = fetch_current()  # implement this
    
    alerts = []
    if should_alert(current, state):
        alerts.append(format_alert(current, state))
    
    state["lastCheck"] = now_iso()
    state["lastValue"] = current
    STATE.write_text(json.dumps(state))
    
    print(json.dumps({"alerts": alerts}))
```

## Checklist

- [ ] Trigger chosen: cron (config) or heartbeat (HEARTBEAT.md)
- [ ] State in `<skill>/state.json`
- [ ] Notification uses `message` tool with channel
- [ ] De-duplication to prevent spam
- [ ] Manual check command documented
