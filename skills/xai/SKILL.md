---
name: xai
description: Chat with Grok models via xAI API. Supports Grok-3, Grok-3-mini, vision, and more.
homepage: https://docs.x.ai
triggers:
  - grok
  - xai
  - ask grok
metadata:
  clawdbot:
    emoji: "🤖"
---

# xAI / Grok

Chat with xAI's Grok models. Supports text and vision.

## Setup

Set your API key in the skill config:

```bash
# Via clawdbot config
clawdbot config set skills.entries.xai.apiKey "xai-YOUR-KEY"

# Or environment variable
export XAI_API_KEY="xai-YOUR-KEY"
```

Get your API key at: https://console.x.ai

## Commands

### Chat with Grok
```bash
node {baseDir}/scripts/chat.js "What is the meaning of life?"
```

### Use a specific model
```bash
node {baseDir}/scripts/chat.js --model grok-3-mini "Quick question: 2+2?"
```

### Vision (analyze images)
```bash
node {baseDir}/scripts/chat.js --image /path/to/image.jpg "What's in this image?"
```

### 🔍 Search X/Twitter (Real-time!)
```bash
node {baseDir}/scripts/search-x.js "Remotion video framework"
node {baseDir}/scripts/search-x.js --days 7 "Claude AI tips"
node {baseDir}/scripts/search-x.js --handles @remotion_dev "updates"
```

Uses xAI Responses API with x_search tool for real X posts with citations.

### List available models
```bash
node {baseDir}/scripts/models.js
```

## Available Models

- `grok-3` - Most capable, best for complex tasks
- `grok-3-mini` - Fast and efficient
- `grok-3-fast` - Optimized for speed
- `grok-2-vision-1212` - Vision model for image understanding

## Example Usage

**User:** "Ask Grok what it thinks about AI safety"
**Action:** Run chat.js with the prompt

**User:** "Use Grok to analyze this image" (with attached image)
**Action:** Run chat.js with --image flag

**User:** "What Grok models are available?"
**Action:** Run models.js

## API Reference

xAI API Docs: https://docs.x.ai/api

## Environment Variables

- `XAI_API_KEY` - Your xAI API key (required)
- `XAI_MODEL` - Default model (optional, defaults to grok-3)
