---
name: clawd-presence
description: Physical presence display for AI agents. Shows a customizable monogram (A-Z), status state, and current activity on a dedicated terminal/screen. Provides faster feedback than chat - glance at the display to see what the agent is doing. Use when setting up always-on agent visibility.
---

# Clawd Presence

Terminal-based presence display for AI agents.

## Why

Chat has latency. A presence display inverts this - the agent broadcasts state continuously, you glance at it like a clock.

## Setup

```bash
# Configure (auto-detect from clawdbot or manual)
python3 scripts/configure.py --auto
# or
python3 scripts/configure.py --letter A --name "AGENT"

# Run display in dedicated terminal
python3 scripts/display.py
```

## Update Status

Call from your agent whenever starting a task:

```bash
python3 scripts/status.py work "Building feature"
python3 scripts/status.py think "Analyzing data"
python3 scripts/status.py idle "Ready"
python3 scripts/status.py alert "Need attention"
python3 scripts/status.py sleep
```

## States

| State | Color | Use |
|-------|-------|-----|
| `idle` | Cyan | Waiting |
| `work` | Green | Executing |
| `think` | Yellow | Processing |
| `alert` | Red | Needs human |
| `sleep` | Blue | Low power |

## Auto-Idle

Returns to idle after 5 minutes of no updates. Prevents stale states.

```bash
python3 scripts/configure.py --timeout 300  # seconds, 0 to disable
```

## Files

- `scripts/display.py` - Main display
- `scripts/status.py` - Update status
- `scripts/configure.py` - Settings
- `assets/monograms/` - Letter designs A-Z
