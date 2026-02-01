---
name: skill-exporter
description: Export Clawdbot skills as standalone, deployable microservices. Use when you want to dockerize a skill, deploy it to Railway or Fly.io, or create an independent API service. Generates Dockerfile, FastAPI wrapper, requirements.txt, deployment configs, and optional LLM client integration.
license: MIT
compatibility: Requires python3. Works with any AgentSkills-compatible agent.
metadata:
  author: MacStenk
  version: "1.0.0"
  clawdbot:
    emoji: "📦"
    requires:
      bins:
        - python3
---

# Skill Exporter

Transform Clawdbot skills into standalone, deployable microservices.

## Workflow

```
Clawdbot Skill (tested & working)
         ↓
    skill-exporter
         ↓
Standalone Microservice
         ↓
Railway / Fly.io / Docker
```

## Usage

### Export a skill

```bash
python3 {baseDir}/scripts/export.py \
  --skill ~/.clawdbot/skills/instagram \
  --target railway \
  --llm anthropic \
  --output ~/projects/instagram-service
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--skill` | Path to skill directory | required |
| `--target` | Deployment target: `railway`, `fly`, `docker` | `docker` |
| `--llm` | LLM provider: `anthropic`, `openai`, `none` | `none` |
| `--output` | Output directory | `./<skill-name>-service` |
| `--port` | API port | `8000` |

### Targets

**railway** — Generates `railway.json`, optimized Dockerfile, health checks
**fly** — Generates `fly.toml`, multi-region ready
**docker** — Generic Dockerfile, docker-compose.yml

### LLM Integration

When `--llm` is set, generates `llm_client.py` with:
- Caption/prompt generation
- Decision making helpers
- Rate limiting and error handling

## What Gets Generated

```
<skill>-service/
├── Dockerfile
├── docker-compose.yml
├── api.py              # FastAPI wrapper
├── llm_client.py       # If --llm specified
├── requirements.txt
├── .env.example
├── railway.json        # If --target railway
├── fly.toml            # If --target fly
└── scripts/            # Copied from original skill
    └── *.py
```

## Requirements

The source skill must have:
- `SKILL.md` with valid frontmatter
- At least one script in `scripts/`
- Scripts should be callable (functions, not just inline code)

## Post-Export

1. Copy `.env.example` to `.env` and fill in secrets
2. Test locally: `docker-compose up`
3. Deploy: `railway up` or `fly deploy`
