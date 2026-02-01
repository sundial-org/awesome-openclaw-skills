---
name: govee-lights
description: Control Govee smart lights via the Govee API. Supports turning lights on/off, adjusting brightness, setting colors, and scenes. Use for: (1) Controlling individual lights or groups by name, (2) Setting colors and brightness, (3) Managing device states
---

# Govee Lights Control

Control Govee smart lights using natural language commands.

## Quick Reference

| Command | Example |
|---------|---------|
| List devices | `python3 scripts/govee.py list` |
| Turn on | `python3 scripts/govee.py on "lamp"` |
| Turn off | `python3 scripts/govee.py off "lamp"` |
| Brightness | `python3 scripts/govee.py brightness "lamp" 75` |
| Color | `python3 scripts/govee.py color "lamp" 255 100 50` |

## Natural Language Patterns

- "Turn on [device name]"
- "Turn off [device name]"
- "Set [device name] to [brightness]%"
- "Set [device name] to [color name or RGB]"
- "Dim/Brighten [device name]"

## Setup

1. Get API key from [Govee Developer Portal](https://developer.govee.com/)
2. Set environment variable: `export GOVEE_API_KEY="your-key"`
3. Install dependencies: `pip3 install requests`

## Usage Examples

```bash
# List all devices
python3 scripts/govee.py list

# Control lights
python3 scripts/govee.py on "living room"
python3 scripts/govee.py off bedroom
python3 scripts/govee.py brightness "desk lamp" 50

# Set colors (RGB 0-255)
python3 scripts/govee.py color "strip" 255 0 0      # Red
python3 scripts/govee.py color "strip" 0 255 0      # Green
python3 scripts/govee.py color "strip" 255 165 0    # Orange
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.
