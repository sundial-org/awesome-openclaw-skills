---
name: mijia
description: Control Xiaomi Mijia smart home devices. Use this skill when the user wants to control desk lamps, smart plugs, or other Mijia devices. Supports turning lights on/off, adjusting brightness, setting color temperature, switching modes, and more.
invocable: true
---

# Mijia Smart Home Control

Control Xiaomi Mijia smart devices via the mijiaAPI.

## Setup

Before using this skill, you need to:

1. Install dependencies:
```bash
cd /path/to/mijia-skill
uv sync
```

2. Set your device ID as an environment variable:
```bash
export MIJIA_LAMP_DID="your_device_id"
```

3. First run will prompt for Xiaomi account login via QR code.

## Finding Device IDs

To find your device IDs, use the mijia-api library:

```python
from mijiaAPI import mijiaAPI
api = mijiaAPI()
api.login()
devices = api.get_device_list()
for d in devices:
    print(f"{d['name']}: {d['did']}")
```

## How to Use

Skill path: `~/.clawdbot/skills/mijia`

### Lamp Control Commands

```bash
# Navigate to skill directory
cd ~/.claude/skills/mijia

# Check status
uv run python scripts/lamp_cli.py status

# Turn on/off
uv run python scripts/lamp_cli.py on
uv run python scripts/lamp_cli.py off
uv run python scripts/lamp_cli.py toggle

# Adjust brightness (1-100%)
uv run python scripts/lamp_cli.py brightness 50

# Adjust color temperature (2700-6500K)
uv run python scripts/lamp_cli.py temp 4000

# Set mode
uv run python scripts/lamp_cli.py mode reading    # Reading mode
uv run python scripts/lamp_cli.py mode computer   # Computer mode
uv run python scripts/lamp_cli.py mode night      # Night reading
uv run python scripts/lamp_cli.py mode antiblue   # Anti-blue light
uv run python scripts/lamp_cli.py mode work       # Work mode
uv run python scripts/lamp_cli.py mode candle     # Candle effect
uv run python scripts/lamp_cli.py mode twinkle    # Twinkle alert
```

## Natural Language Understanding

When the user says the following, execute the corresponding command:

| User Says | Command |
|-----------|---------|
| Turn on the light / open lamp | `scripts/lamp_cli.py on` |
| Turn off the light / close lamp | `scripts/lamp_cli.py off` |
| Toggle the light | `scripts/lamp_cli.py toggle` |
| Brighter / more bright | Check status first, then increase by 20-30% |
| Dimmer / less bright | Check status first, then decrease by 20-30% |
| Full brightness / maximum | `scripts/lamp_cli.py brightness 100` |
| Minimum brightness | `scripts/lamp_cli.py brightness 1` |
| Warm light | `scripts/lamp_cli.py temp 2700` |
| Cool light / white light | `scripts/lamp_cli.py temp 6500` |
| Reading mode | `scripts/lamp_cli.py mode reading` |
| Computer mode | `scripts/lamp_cli.py mode computer` |
| Night mode | `scripts/lamp_cli.py mode night` |
| Lamp status / what's the light status | `scripts/lamp_cli.py status` |

## Before Executing

1. Navigate to skill directory: `cd ~/.clawdbot/skills/mijia`
2. Ensure `MIJIA_LAMP_DID` environment variable is set
3. Run with uv: `uv run python scripts/lamp_cli.py <command>`
4. Report the result to the user after execution
