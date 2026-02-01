![](https://i.imgur.com/tP0xHSp.png)

# fal.ai API Skill

See [SKILL.md](./SKILL.md) for full documentation.

## Quick Start

```bash
# Set your API key
export FAL_KEY="your-api-key"

# Generate an image
python3 fal_api.py --prompt "A cute robot cat" --model flux-schnell

# List available models
python3 fal_api.py --list-models
```

## Configure Credentials

```bash
# Via environment
export FAL_KEY="your-api-key"

# Or via clawdbot config
clawdbot config set skill.fal_api.key YOUR_API_KEY
```

## Requirements

- Python 3.7+
- No external dependencies (uses stdlib)
