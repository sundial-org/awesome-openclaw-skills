---
name: timer
description: Set timers and alarms. When a background timer completes, you receive a System notification - respond with the reminder message (NOT HEARTBEAT_OK) to notify the user.
metadata: {"clawdbot":{"emoji":"⏱️","requires":{"bins":["node"]}}}
---

# Timer

Set timers that run in the background. When they complete, you will receive a system notification and MUST respond with the reminder to notify the user.

## Quick Start

```bash
# Set a 5-minute timer
bash background:true command:"node {baseDir}/timer.js 5m"

# Set a timer with a label
bash background:true command:"node {baseDir}/timer.js 10m 'Check the oven'"

# Set a timer in seconds
bash background:true command:"node {baseDir}/timer.js 30s"

# Set a timer in hours
bash background:true command:"node {baseDir}/timer.js 1h"
```

## Time Formats

| Format | Description | Example |
|--------|-------------|---------|
| `Ns` | N seconds | `30s`, `90s` |
| `Nm` | N minutes | `5m`, `15m` |
| `Nh` | N hours | `1h`, `2h` |
| `N` | N minutes (default) | `5` = 5 minutes |
| `MM:SS` | Minutes and seconds | `5:30` |
| `HH:MM:SS` | Hours, minutes, seconds | `1:30:00` |

## ⚠️ CRITICAL: Timer Completion Notification

When a timer completes, you receive a `System:` message like:
```
System: [2026-01-24 21:27:13] Exec completed (swift-me, code 0) :: ⏰ Timer complete! Check the pasta!
```

### ❌ WRONG - Do NOT respond like this:
```
HEARTBEAT_OK

🎉 Your timer is complete! Check the pasta!
```
This response will be **filtered and NOT delivered** to the user!

### ✅ CORRECT - Respond like this:
```
⏰ Timer Alert! Your timer is complete: Check the pasta!
```
Start directly with the notification message. Do NOT include HEARTBEAT_OK.

**Why?** Responses starting with `HEARTBEAT_OK` followed by less than 300 characters are automatically suppressed and never reach the user. Your timer notification will be lost!

## Examples

### Cooking Timer
```bash
bash background:true command:"node {baseDir}/timer.js 12m 'Pasta is ready!'"
```
When complete, respond: "⏰ Your 12-minute timer is up! Pasta is ready!"

### Quick Reminder
```bash
bash background:true command:"node {baseDir}/timer.js 2m 'Take a break'"
```

### Pomodoro Session
```bash
# Work session
bash background:true command:"node {baseDir}/timer.js 25m 'Pomodoro done - time for a break!'"
# After user is notified...
# Break
bash background:true command:"node {baseDir}/timer.js 5m 'Break over - back to work!'"
```

### Multiple Timers
```bash
bash background:true command:"node {baseDir}/timer.js 5m 'Tea is ready'"
bash background:true command:"node {baseDir}/timer.js 10m 'Eggs are done'"
bash background:true command:"node {baseDir}/timer.js 30m 'Meeting starts soon'"
```

## Managing Timers

```bash
# List all running timers
process action:list

# Check specific timer status
process action:poll sessionId:XXX

# View timer output
process action:log sessionId:XXX

# Cancel a timer
process action:kill sessionId:XXX
```

## Notes

- Timers run as background processes with unique sessionIds
- Completed timers exit with code 0
- Cancelled timers (via kill) exit with code 130
- Sound notification plays on macOS when timer completes (if `afplay` available)
- Progress is logged every second (short timers) or every 10 seconds (long timers)
