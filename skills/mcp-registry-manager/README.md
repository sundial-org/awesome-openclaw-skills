# MCP Registry Manager 🌐

Centralized discovery and quality scoring for the MCP (Model Context Protocol) ecosystem.

## Quick Start

```bash
# Install dependencies
pip install requests sentence-transformers numpy pandas

# Discover MCP servers
python3 scripts/mcp-registry.py --discover

# Semantic search
python3 scripts/mcp-registry.py --search "file system operations"

# Install a server
python3 scripts/mcp-registry.py --install @modelcontext/official-filesystem

# List installed servers
python3 scripts/mcp-registry.py --list --installed
```

## Features

✅ **Multi-source discovery** — GitHub, awesome-mcp-servers, AllInOneMCP  
✅ **Quality scoring** — Test coverage, documentation, maintenance  
✅ **Semantic search** — Find by what it does, not just names  
✅ **Install management** — Install/uninstall with tracking  
✅ **Categorization** — Files, databases, APIs, dev tools, etc.  

## Problem

MCP is exploding (100+ servers) but:
- Discovery is fragmented
- No quality signals
- No semantic search
- No unified management

## Quality Score

| Factor | Weight |
|--------|--------|
| Test coverage | 40% |
| Documentation | 30% |
| Maintenance | 20% |
| Community | 10% |

## Categories

- Files (filesystem, S3)
- Databases (PostgreSQL, MongoDB, Redis)
- APIs (HTTP, GraphQL, REST)
- Dev Tools (Git, Docker, CI)
- Media (image, video, audio)
- Utilities (time, crypto, encryption)

## Installation

```bash
git clone https://github.com/orosha-ai/mcp-registry-manager
pip install requests sentence-transformers numpy pandas
```

## License

MIT
