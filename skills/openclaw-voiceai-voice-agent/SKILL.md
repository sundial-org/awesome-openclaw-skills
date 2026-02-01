---
name: voice.ai-voice-agents
title: "Voice.ai Voice Agents"
description: >
  Create, manage, and deploy Voice.ai conversational AI agents.
  Use when the user wants to work with voice agents, list their agents, create new ones, or manage agent configurations.
---

# Voice.ai Agents

Build the best conversational AI voice agents with Voice.ai's Agent API.

## ✨ Features

- **Agent Management** - Create, update, and delete voice agents
- **One-Click Deploy** - Deploy agents for phone calls instantly
- **Knowledge Base** - RAG-powered agents with custom knowledge
- **MCP Integration** - Connect agents to external tools via MCP
- **Phone Numbers** - Manage inbound/outbound phone numbers
- **Analytics** - Track call history and agent performance

## ⚙️ Configuration

### Get Your API Key

1. Go to [Voice.ai Developer Dashboard](https://voice.ai/app/dashboard/developers)
2. Sign in or create an account
3. Generate a new API key
4. Copy and save it securely

### Set Up Authentication (3 Methods)

**Method 1: Environment Variable (Recommended)**
```bash
export VOICE_AI_API_KEY="your-api-key-here"
```

**Method 2: .env File**
```bash
# Create .env file in project root
echo 'VOICE_AI_API_KEY=your-api-key-here' >> .env
```

**Method 3: OpenClaw Config**
```json
{
  "skills": {
    "voice.ai-voice-agents": {
      "api_key": "your-api-key-here"
    }
  }
}
```

## 🔐 Before Any Operation

> **Important:** Always verify authentication before running any commands.

```bash
# 1. Check if API key is set
echo $VOICE_AI_API_KEY

# 2. Test connection (list agents)
node scripts/agent.js list

# 3. If errors, re-export your key
export VOICE_AI_API_KEY="your-api-key-here"
```

### Silent Initialization
The SDK automatically initializes when you run any command. No manual setup required after setting the API key.

## 🚀 Quick Start

```bash
export VOICE_AI_API_KEY="your-api-key"

# Create an agent
node scripts/agent.js create --name "Support Bot" --prompt "You are a helpful assistant"

# List all agents
node scripts/agent.js list

# Deploy an agent
node scripts/agent.js deploy --id <agent_id>
```

## 🤖 Agent Configuration

| Parameter              | Default | Description                          |
|------------------------|---------|--------------------------------------|
| llm_model              | gemini-2.5-flash-lite | LLM model for responses |
| llm_temperature        | 0.7     | Response creativity (0-2)            |
| max_call_duration      | 900     | Max call length in seconds           |
| allow_interruptions    | true    | Let users interrupt agent            |
| auto_noise_reduction   | true    | Filter background noise              |

## 🎙️ TTS Voice Settings

| Parameter   | Default | Description                    |
|-------------|---------|--------------------------------|
| voice_id    | -       | Voice ID for agent speech      |
| model       | auto    | TTS model (auto-selected)      |
| language    | en      | Language code                  |
| temperature | 1.0     | Voice expressiveness (0-2)     |
| top_p       | 0.8     | Sampling parameter (0-1)       |

## 🌍 Supported Languages

`auto`, `en`, `ca`, `sv`, `es`, `fr`, `de`, `it`, `pt`, `pl`, `ru`, `nl`

## 💻 CLI Usage

```bash
# Create a new agent
node scripts/agent.js create --name "My Agent" --prompt "System prompt here" --greeting "Hello!"

# List all agents
node scripts/agent.js list

# Get agent details
node scripts/agent.js get --id <agent_id>

# Update an agent
node scripts/agent.js update --id <agent_id> --prompt "New prompt"

# Deploy an agent
node scripts/agent.js deploy --id <agent_id>

# Pause an agent
node scripts/agent.js pause --id <agent_id>

# Delete an agent
node scripts/agent.js delete --id <agent_id>
```

## 🤖 OpenClaw Integration

### JSON Configuration

```json
{
  "name": "voice.ai-voice-agents",
  "enabled": true,
  "config": {
    "api_key": "${VOICE_AI_API_KEY}",
    "default_model": "gemini-2.5-flash-lite",
    "auto_deploy": false
  }
}
```

### Chat Triggers

OpenClaw automatically activates this skill when you mention:
- "voice agent", "voice bot", "phone agent"
- "create agent", "deploy agent", "list agents"
- "Voice.ai", "voice ai"

## 🗣️ User-Friendly Language

| When User Says... | Skill Does... |
|-------------------|---------------|
| "Create a support agent" | Creates agent with support-focused prompt |
| "Show my agents" | Lists all agents with status |
| "Deploy the agent" | Deploys agent for phone calls |
| "Update the greeting" | Updates agent greeting message |
| "Delete the test agent" | Deletes specified agent |
| "What agents do I have?" | Lists agents in friendly format |
| "Make an FAQ bot" | Creates agent with FAQ template |
| "Connect to my MCP server" | Configures MCP integration |

## 📁 Project Files

```
voice-ai-agents/
├── SKILL.md                    # This documentation
├── voice-ai-agents.yaml        # Skill configuration
├── voice-ai-agents-sdk.js      # JavaScript SDK
└── scripts/
    └── agent.js                # CLI tool
```

| File | Purpose |
|------|---------|
| `SKILL.md` | Documentation and OpenClaw skill definition |
| `voice-ai-agents.yaml` | API config, models, defaults |
| `voice-ai-agents-sdk.js` | Full SDK with all API methods |
| `scripts/agent.js` | Command-line interface |

## ❌ Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid or missing API key | Check `VOICE_AI_API_KEY` is set correctly |
| `403 Forbidden` | API key lacks permissions | Generate new key with proper scopes |
| `404 Not Found` | Agent ID doesn't exist | Run `list` to get valid agent IDs |
| `429 Too Many Requests` | Rate limit exceeded | Wait 60 seconds and retry |
| `500 Server Error` | Voice.ai API issue | Check [status page](https://status.voice.ai) |
| `ENOTFOUND` | Network error | Check internet connection |
| `Agent not deployed` | Agent exists but not active | Run `deploy --id <agent_id>` |

### Graceful Error Messages

The SDK provides user-friendly error messages:
```
❌ Authentication failed. Please check your API key.
   Get one at: https://voice.ai/app/dashboard/developers

❌ Agent "support-bot" not found. 
   Run 'node scripts/agent.js list' to see available agents.

❌ Rate limit reached. Please wait 60 seconds before retrying.
```

## 📝 Triggers

These phrases activate the Voice.ai Agents skill in OpenClaw:

| Category | Trigger Phrases |
|----------|-----------------|
| **Create** | "create voice agent", "make a phone bot", "new agent" |
| **List** | "show agents", "list my agents", "what agents exist" |
| **Deploy** | "deploy agent", "activate agent", "start the bot" |
| **Update** | "update agent", "change prompt", "edit greeting" |
| **Delete** | "delete agent", "remove bot", "destroy agent" |
| **Info** | "agent details", "show agent", "get agent info" |

## 🔗 MCP Server Integration

Connect your agent to external tools:

```javascript
const agent = await client.createAgent({
  name: "MCP Agent",
  config: {
    prompt: "You can use tools to help users",
    mcp_servers: [{
      name: "my-tools",
      url: "https://my-server.com/mcp",
      auth_type: "bearer_token",
      auth_token: "secret"
    }]
  }
});
```

## 📚 Knowledge Base (RAG)

Add custom knowledge to your agent:

```bash
# Create agent with knowledge base
node scripts/agent.js create --name "FAQ Bot" --kb-id 123
```

## 🔗 Links

- [Get API Key](https://voice.ai/app/dashboard/developers) ← Start here!
- [Voice Agents Guide](https://voice.ai/docs/guides/voice-agents/quickstart)
- [Agent API Reference](https://voice.ai/docs/api-reference/agent-management/create-agent)
- [Status Page](https://status.voice.ai)

## 📋 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-31 | Initial release with full agent management |

---

Made with ❤️ by [Nick Gill](https://github.com/gizmoGremlin)
