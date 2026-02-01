# clawd-presence

A physical presence display for AI agents. Monogram + status updates on a dedicated screen.

![clawd-presence screenshot](assets/screenshot.png)

## The Problem

Chat has latency. You send a message, wait, wonder if it's stuck. A presence display gives you a faster feedback loop - the agent broadcasts what it's doing continuously. Glance at it like a clock. Know instantly if things are on track.

## Quick Start

```bash
# Install
git clone https://github.com/voidcooks/clawd-presence.git
cd clawd-presence

# Pick your letter and name
python3 scripts/configure.py --letter A --name "ATLAS"

# Start the display (run in a dedicated terminal)
python3 scripts/display.py
```

That's it. The display shows your letter, current state, and what the agent is working on.

## Updating Status

Your agent updates the display by calling:

```bash
python3 scripts/status.py work "Researching competitors"
python3 scripts/status.py think "Analyzing options"
python3 scripts/status.py idle "Ready"
python3 scripts/status.py alert "Need your attention"
```

Updates appear instantly. No more wondering what's happening.

## States

| State | Color | When to use |
|-------|-------|-------------|
| `work` | Green | Actively doing something |
| `think` | Yellow | Processing, deciding |
| `idle` | Cyan | Ready, waiting |
| `alert` | Red | Needs human attention |
| `sleep` | Blue | Low power mode |

## Auto-Idle

If no status update for 5 minutes, display returns to `idle`. Prevents stale states.

```bash
# Adjust timeout (default 300 seconds)
python3 scripts/configure.py --timeout 600
```

## Clawdbot Integration

Auto-detect your agent's name:
```bash
python3 scripts/configure.py --auto
```

Add to your agent's instructions:
```
Update presence when starting tasks:
python3 /path/to/clawd-presence/scripts/status.py <state> "<message>"
```

## All 26 Letters

Geometric monogram designs for A-Z included. Pick yours:

```bash
python3 scripts/configure.py --letter E --name "EMMA"
```

## Requirements

- Python 3.8+
- Terminal with 256-color support

## License

MIT
