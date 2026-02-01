---
name: lightrag
description: Search and manage knowledge bases using LightRAG API. Supports multiple servers, context-aware writing, and direct information retrieval. Use when the user wants to query a LightRAG-powered knowledge base or use it as context for tasks.
---

# LightRAG Skill

This skill allows you to interact with one or more LightRAG API servers. You can perform queries in various modes (local, global, hybrid, mix, naive) and use the retrieved context for further processing.

## Configuration

The skill uses a configuration file at `~/.lightrag_config.json` to store server details.
Format:
```json
{
  "servers": {
    "alias1": {
      "url": "http://server1:9621",
      "api_key": "optional_key"
    },
    "alias2": {
      "url": "http://server2:9621",
      "api_key": "optional_key"
    }
  },
  "default_server": "alias1"
}
```

## Workflows

### 1. Direct Search
To find information, use `scripts/query_lightrag.py`.
Modes: `local`, `global`, `hybrid`, `mix`, `naive`.

### 2. Using Context for Writing
To use a knowledge base as context (e.g., for a test or article):
1. Run `query_lightrag.py` with the `--only-context` flag.
2. Pass the resulting context to your writing task/model.

## Reference
See [API_DOCS.md](references/API_DOCS.md) for endpoint details.
