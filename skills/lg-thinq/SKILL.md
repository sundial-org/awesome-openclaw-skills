---
name: lg-thinq
description: "Control LG smart appliances via ThinQ API. Use when user asks about their fridge, washer, dryer, AC, or other LG appliances. Supports checking status, changing temperature, toggling modes (express, eco), and monitoring door status."
metadata: {"version":"1.0.0","clawdbot":{"emoji":"🧊","os":["darwin","linux"]}}
---

# LG ThinQ Skill

Control LG smart home appliances via the ThinQ Connect API.

## Setup

1. Get a Personal Access Token from https://connect-pat.lgthinq.com
2. Store token: `echo "YOUR_TOKEN" > ~/.config/lg-thinq/token`
3. Store country code: `echo "MX" > ~/.config/lg-thinq/country`

## Quick Commands

All scripts are in the skill's `scripts/` directory. Activate venv first:
```bash
cd ~/clawd && source .venv/bin/activate
```

### List Devices
```bash
python3 skills/lg-thinq/scripts/thinq.py devices
```

### Get Device Status
```bash
python3 skills/lg-thinq/scripts/thinq.py status <device_id>
python3 skills/lg-thinq/scripts/thinq.py status fridge  # alias
```

### Control Refrigerator
```bash
# Set fridge temperature (0-6°C)
python3 skills/lg-thinq/scripts/thinq.py fridge-temp 3

# Set freezer temperature (-24 to -14°C typical)
python3 skills/lg-thinq/scripts/thinq.py freezer-temp -15

# Toggle express fridge
python3 skills/lg-thinq/scripts/thinq.py express-fridge on|off

# Toggle express freeze
python3 skills/lg-thinq/scripts/thinq.py express-freeze on|off

# Toggle eco mode
python3 skills/lg-thinq/scripts/thinq.py eco on|off
```

### Washer/Dryer Status
```bash
python3 skills/lg-thinq/scripts/thinq.py status washer
python3 skills/lg-thinq/scripts/thinq.py status dryer
```

## Supported Devices

| Device | Status | Control |
|--------|--------|---------|
| Refrigerator | ✅ temp, door, modes | ✅ temp, express, eco |
| WashTower Washer | ✅ state, time | ⚠️ limited |
| WashTower Dryer | ✅ state, time | ⚠️ limited |
| Air Conditioner | ✅ temp, mode | ✅ temp, mode, fan |

## Temperature Ranges

- **Fridge**: 0°C to 6°C
- **Freezer**: -24°C to -14°C (varies by model)

## Error Handling

- `NOT_CONNECTED_DEVICE`: Device offline, check WiFi or open ThinQ app
- `INVALID_COMMAND_ERROR`: Wrong command format or value out of range
- `NOT_PROVIDED_FEATURE`: Feature not supported by this model

## Natural Language Examples

User says → Action:
- "check my fridge" → `status fridge`
- "set fridge to 5 degrees" → `fridge-temp 5`
- "turn on express freeze" → `express-freeze on`
- "is the fridge door open?" → `status fridge` (check doorStatus)
- "how's the washer doing?" → `status washer`
