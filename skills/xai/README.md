# xAI / Grok Skill for Clawdbot

Chat with xAI's Grok models from Clawdbot. Supports text chat, vision, and all Grok models including Grok-4.

## Installation

```bash
clawdhub install xai
# or
cd ~/clawd/skills && git clone https://github.com/mvanhorn/clawdbot-skill-xai xai
```

## Setup

Get your API key from [console.x.ai](https://console.x.ai), then:

```bash
clawdbot config set skills.entries.xai.apiKey "xai-YOUR-KEY"
```

Or set environment variable:
```bash
export XAI_API_KEY="xai-YOUR-KEY"
```

## Usage

### Chat with Grok
```bash
node scripts/chat.js "What is the meaning of life?"
```

### Use specific model
```bash
node scripts/chat.js --model grok-4-0709 "Complex question here"
node scripts/chat.js --model grok-3-mini "Quick question"
```

### Vision (analyze images)
```bash
node scripts/chat.js --image photo.jpg "What's in this image?"
```

### System prompts
```bash
node scripts/chat.js --system "You are a pirate" "Tell me about ships"
```

### List available models
```bash
node scripts/models.js
```

## Available Models

- `grok-3` - Capable general model
- `grok-3-mini` - Fast and efficient
- `grok-4-0709` - Latest Grok 4
- `grok-4-fast-reasoning` - Fast with reasoning
- `grok-2-vision-1212` - Image understanding
- `grok-2-image-1212` - Image generation

## Clawdbot Integration

Once installed, you can just say:
- "Ask Grok about [topic]"
- "Use Grok to analyze this image"
- "Have Grok 4 explain [concept]"

## License

MIT
