---
name: graphiti
description: Knowledge graph operations via Graphiti API. Search facts, add episodes, and extract entities/relationships.
homepage: https://github.com/getzep/graphiti
metadata: {"clawdbot":{"emoji":"🕸️","requires":{"services":["neo4j","qdrant","graphiti"]},"install":[{"id":"docker","kind":"docker-compose","label":"Install Graphiti stack (Docker)"}]}}
---

# Graphiti Knowledge Graph

Query and manage your knowledge graph using Graphiti's REST API with dynamic service discovery.

## Prerequisites

- Neo4j database (graph storage)
- Qdrant (vector search)
- Graphiti service running (default: http://localhost:8001)

## Tools

### graphiti_search
Search the knowledge graph for relevant facts.

**Usage:**
```bash
bash command:"
GRAPHITI_URL=\$({baseDir}/references/env-check.sh)
curl -s -X POST \"\$GRAPHITI_URL/facts/search\" \
  -H 'Content-Type: application/json' \
  -d '{\"query\": \"YOUR_QUERY\", \"max_facts\": 10}' | jq .
"
```

### graphiti_add
Add a new episode/memory to the knowledge graph.

**Usage:**
```bash
bash command:"
GRAPHITI_URL=\$({baseDir}/references/env-check.sh)
curl -s -X POST \"\$GRAPHITI_URL/messages\" \
  -H 'Content-Type: application/json' \
  -d '{\"name\": \"EPISODE_NAME\", \"content\": \"EPISODE_CONTENT\"}' | jq .
"
```

## Dynamic Configuration

The skill uses environment discovery to find Graphiti automatically:

1. **Clawdbot config**: `clawdbot config get skills.graphiti.baseUrl`
2. **Environment variable**: `$GRAPHITI_URL`
3. **Default fallback**: `http://localhost:8001`

To change the Graphiti URL:
```bash
export GRAPHITI_URL="http://10.0.0.10:8001"
# OR
clawdbot config set skills.graphiti.baseUrl "http://10.0.0.10:8001"
```

## Examples

Search for information:
```bash
bash command:"
GRAPHITI_URL=\$({baseDir}/references/env-check.sh)
curl -s -X POST \"\$GRAPHITI_URL/facts/search\" \
  -H 'Content-Type: application/json' \
  -d '{\"query\": \"Tell me about Essam Masoudy\", \"max_facts\": 5}'
"
```

Add a memory:
```bash
bash command:"
GRAPHITI_URL=\$({baseDir}/references/env-check.sh)
curl -s -X POST \"\$GRAPHITI_URL/messages\" \
  -H 'Content-Type: application/json' \
  -d '{\"name\": \"Project Update\", \"content\": \"Completed Phase 1 of Clawdbot integration\"}'
"
```
