---
name: chromadb-memory
description: Long-term memory via ChromaDB with local Ollama embeddings. Auto-recall injects relevant context every turn. No cloud APIs required — fully self-hosted.
version: 1.0.0
author: matts
homepage: https://github.com/openclaw/openclaw
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["curl"]
    category: "memory"
tags:
  - memory
  - chromadb
  - ollama
  - vector-search
  - local
  - self-hosted
  - auto-recall
---

# ChromaDB Memory

Long-term semantic memory backed by ChromaDB and local Ollama embeddings. Zero cloud dependencies.

## What It Does

- **Auto-recall**: Before every agent turn, queries ChromaDB with the user's message and injects relevant context automatically
- **`chromadb_search` tool**: Manual semantic search over your ChromaDB collection
- **100% local**: Ollama (nomic-embed-text) for embeddings, ChromaDB for vector storage

## Prerequisites

1. **ChromaDB** running (Docker recommended):
   ```bash
   docker run -d --name chromadb -p 8100:8000 chromadb/chroma:latest
   ```

2. **Ollama** with an embedding model:
   ```bash
   ollama pull nomic-embed-text
   ```

3. **Indexed documents** in ChromaDB. Use any ChromaDB-compatible indexer to populate your collection.

## Install

```bash
# 1. Copy the plugin extension
mkdir -p ~/.openclaw/extensions/chromadb-memory
cp {baseDir}/scripts/index.ts ~/.openclaw/extensions/chromadb-memory/
cp {baseDir}/scripts/openclaw.plugin.json ~/.openclaw/extensions/chromadb-memory/

# 2. Get your collection ID
curl -s http://localhost:8100/api/v2/tenants/default_tenant/databases/default_database/collections | python3 -c "import json,sys; [print(f'{c[\"id\"]}  {c[\"name\"]}') for c in json.load(sys.stdin)]"

# 3. Add to your OpenClaw config (~/.openclaw/openclaw.json):
```

```json
{
  "plugins": {
    "entries": {
      "chromadb-memory": {
        "enabled": true,
        "config": {
          "chromaUrl": "http://localhost:8100",
          "collectionId": "YOUR_COLLECTION_ID",
          "ollamaUrl": "http://localhost:11434",
          "embeddingModel": "nomic-embed-text",
          "autoRecall": true,
          "autoRecallResults": 3,
          "minScore": 0.5
        }
      }
    }
  }
}
```

```bash
# 4. Restart the gateway
openclaw gateway restart
```

## Config Options

| Option | Default | Description |
|--------|---------|-------------|
| `chromaUrl` | `http://localhost:8100` | ChromaDB server URL |
| `collectionId` | *required* | ChromaDB collection UUID |
| `ollamaUrl` | `http://localhost:11434` | Ollama API URL |
| `embeddingModel` | `nomic-embed-text` | Ollama embedding model |
| `autoRecall` | `true` | Auto-inject relevant memories each turn |
| `autoRecallResults` | `3` | Max auto-recall results per turn |
| `minScore` | `0.5` | Minimum similarity score (0-1) |

## How It Works

1. You send a message
2. Plugin embeds your message via Ollama (nomic-embed-text, 768 dimensions)
3. Queries ChromaDB for nearest neighbors
4. Results above `minScore` are injected into the agent's context as `<chromadb-memories>`
5. Agent responds with relevant long-term context available

## Token Cost

Auto-recall adds ~275 tokens per turn worst case (3 results × ~300 chars + wrapper). Against a 200K+ context window, this is negligible.

## Tuning

- **Too noisy?** Raise `minScore` to 0.6 or 0.7
- **Missing context?** Lower `minScore` to 0.4, increase `autoRecallResults` to 5
- **Want manual only?** Set `autoRecall: false`, use `chromadb_search` tool

## Architecture

```
User Message → Ollama (embed) → ChromaDB (query) → Context Injection
                                                  ↓
                                          Agent Response
```

No OpenAI. No cloud. Your memories stay on your hardware.
