# LM Studio Subagents Skill

An OpenClaw skill that equips agents to search for and offload tasks to local models running in LM Studio. This skill enables agents to discover available models, select appropriate ones based on task requirements, and use them for cost-effective local processing.

## Features

- **REST-only (no CLI)** - Uses LM Studio v1 REST API only; no `lms` on PATH required
- **Model discovery** - Lists and selects from models via GET /api/v1/models
- **Task offloading** - Routes appropriate tasks to local models to save paid API tokens
- **Stateful multi-turn** - Optional response_id / previous_response_id for conversation context
- **JIT loading** - No explicit load required; first chat request loads the model (stats.model_load_time_seconds)
- **No configuration required** - Works with models in LM Studio without OpenClaw config setup
- **Local processing** - All processing happens locally for privacy
- **Model selection** - Supports LLMs, VLMs, and embedding models based on task needs

## Installation

### Via ClawdHub (Recommended)

```bash
npm i -g clawdhub
clawdhub install lmstudio-subagents
```

### Manual Installation

1. Clone this repository or download the skill folder
2. Place the `lmstudio-subagents` folder in your OpenClaw skills directory:
   - Workspace: `<workspace>/skills/lmstudio-subagents/`
   - Global: `~/.openclaw/skills/lmstudio-subagents/`

## Prerequisites

- LM Studio 0.4+ with server running (default: http://127.0.0.1:1234)
- No CLI required
- Models downloaded in LM Studio

## Usage

The skill is automatically triggered when the agent needs to:
- Offload simple tasks to free local models (summarization, extraction, classification, rewriting, first-pass code review, brainstorming)
- Use specialized model capabilities (vision models for images, smaller models for quick tasks, larger models for complex reasoning)
- Save paid API tokens by using local models when quality is sufficient
- Process tasks locally for privacy

Example: "Use lmstudio-subagents to summarize this document"

## How It Works

1. Lists available models via GET /api/v1/models
2. Optionally checks loaded_instances or POST /api/v1/models/load for specific options
3. Selects model by key and capabilities (vision, embedding, context)
4. Calls POST /api/v1/chat (JIT loads model if needed)
5. Parses output and optional response_id for stateful follow-up
6. Optionally POST /api/v1/models/unload with instance_id

## Performance

Tested with LM Studio 0.4.x. JIT first-request load time in response stats.model_load_time_seconds. API call latency varies with generation length.

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please open an issue or pull request.

## Links

- [GitHub Repository](https://github.com/t-sinclair2500/clawdbot_skills) - Source code and issues
- [ClawdHub](https://clawdhub.com) - Browse and install skills
- [OpenClaw Documentation](https://docs.openclaw.ai) - Learn more about OpenClaw
- [LM Studio](https://lmstudio.ai) - Download LM Studio
