# Mijia Smart Home Control

A skill/plugin for AI coding agents to control Xiaomi Mijia smart home devices through natural language commands.

![Demo](demo.png)

Works with:
- [OpenClaw](https://openclaw.ai/) - Open source AI coding agent
- [Claude Code](https://github.com/anthropics/claude-code)
- [OpenCode](https://github.com/opencode-ai/opencode)
- [Droid](https://github.com/anthropics/droid)
- Other AI coding assistants that support custom skills/tools

## Features

- Control Xiaomi Mijia smart devices via natural language
- Support for desk lamps, smart plugs, and other Mijia devices
- Brightness and color temperature adjustment
- Multiple lighting modes (reading, computer, night, etc.)
- Easy to extend for additional device types

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- Xiaomi account with Mijia devices

## Installation

1. Clone this repository:

```bash
git clone https://github.com/user/mijia-skill.git
cd mijia-skill
```

2. Install dependencies:

```bash
uv sync
```

3. Configure your device ID:

```bash
export MIJIA_LAMP_DID="your_device_id"
```

4. First run will prompt for Xiaomi account login via QR code.

## Finding Your Device ID

Use the [mijia-api](https://github.com/Do1e/mijia-api) library to find your device IDs:

```python
from mijiaAPI import mijiaAPI

api = mijiaAPI()
api.login()  # Scan QR code to login
devices = api.get_device_list()
for device in devices:
    print(f"{device['name']}: {device['did']}")
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MIJIA_LAMP_DID` | Device ID for the desk lamp |

## Usage

### CLI Commands

```bash
# Check status
uv run python scripts/lamp_cli.py status

# Power control
uv run python scripts/lamp_cli.py on
uv run python scripts/lamp_cli.py off
uv run python scripts/lamp_cli.py toggle

# Brightness (1-100%)
uv run python scripts/lamp_cli.py brightness 50

# Color temperature (2700-6500K)
uv run python scripts/lamp_cli.py temp 4000

# Lighting modes
uv run python scripts/lamp_cli.py mode reading    # Reading mode
uv run python scripts/lamp_cli.py mode computer   # Computer mode
uv run python scripts/lamp_cli.py mode night      # Night reading
uv run python scripts/lamp_cli.py mode antiblue   # Anti-blue light
uv run python scripts/lamp_cli.py mode work       # Work mode
uv run python scripts/lamp_cli.py mode candle     # Candle effect
uv run python scripts/lamp_cli.py mode twinkle    # Twinkle alert
```

### Natural Language Examples

Once integrated with your AI coding agent, you can use natural language:

- "Turn on the light" / "Turn off the light"
- "Make it brighter" / "Make it dimmer"
- "Set brightness to 80%"
- "Switch to reading mode"
- "Warm light please" / "Cool white light"
- "What's the lamp status?"

## Integration

### Claude Code

Copy the skill to your Claude Code skills directory:

```bash
cp -r . ~/.clawdbot/skills/mijia
```

### Other AI Agents

Add the `SKILL.md` content to your agent's system prompt or tool configuration. The skill provides:
- Device control commands
- Natural language mapping table
- Usage instructions

## Extending

You can extend this skill to support more device types. See `scripts/lamp_cli.py` for an example implementation.

The [mijia-api](https://github.com/Do1e/mijia-api) library supports:
- Smart plugs
- Air purifiers
- Vacuum cleaners
- Rice cookers
- Door locks
- And more Mijia devices

## Credits

Built on top of [mijia-api](https://github.com/Do1e/mijia-api) by Do1e.

## License

MIT License
