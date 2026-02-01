# Local RAG Search - Agent Skill

An Agent Skill that teaches Claude how to effectively use the [mcp-local-rag](https://github.com/nkapila6/mcp-local-rag) MCP server for intelligent web searches with semantic similarity ranking.

## What This Skill Does

This skill enables agents to:
- **Choose the right search tool** based on the task (DuckDuckGo, Google, or multi-engine deep research)
- **Formulate effective queries** using natural language
- **Tune parameters** for different use cases (quick answers vs comprehensive research)
- **Perform deep research** across multiple search engines and topics
- **Respect privacy** by defaulting to DuckDuckGo

## Prerequisites

This skill requires the [mcp-local-rag MCP server](https://github.com/nkapila6/mcp-local-rag) to be installed and configured in your MCP client.

### Install mcp-local-rag

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "mcp-local-rag": {
      "command": "uvx",
      "args": [
        "--python=3.10",
        "--from",
        "git+https://github.com/nkapila6/mcp-local-rag",
        "mcp-local-rag"
      ]
    }
  }
}
```

Or use Docker:

```json
{
  "mcpServers": {
    "mcp-local-rag": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--init",
        "-e", "DOCKER_CONTAINER=true",
        "ghcr.io/nkapila6/mcp-local-rag:v1.0.2"
      ]
    }
  }
}
```

## Installation

### Claude Desktop

1. Navigate to **Settings** → **Skills**
2. Click **Add Skill** → **Add from folder**
3. Select this skill folder (`local-rag-search/`)

## Usage

Once both the MCP server and skill are loaded, simply ask Claude to search for information:

- "Search the web for the latest Python 3.13 features"
- "Do deep research on sustainable energy solutions"
- "Find technical documentation about Docker optimization"

Claude will automatically apply the skill's best practices to use the appropriate tools effectively.

## Features

- ✅ **Smart tool selection** - Automatically chooses DuckDuckGo, Google, or deep research based on query
- ✅ **Privacy-first** - Defaults to DuckDuckGo for general searches
- ✅ **Multi-engine research** - Supports 9+ search backends for comprehensive coverage
- ✅ **Semantic ranking** - Uses RAG-like similarity scoring for most relevant results
- ✅ **No external APIs** - All processing runs locally with embedded models

## Supported Search Backends

- DuckDuckGo (privacy-focused)
- Google (comprehensive)
- Bing, Brave, Yahoo, Yandex
- Wikipedia (factual/encyclopedia)
- Mojeek, Grokipedia

## License

MIT - Same as the parent mcp-local-rag project
