# Graphiti Knowledge Graph Skill

Query and manage your knowledge graph using Graphiti's REST API with automatic service discovery.

## Installation

```bash
clawdhub install graphiti
```

Or manual:
```bash
git clone https://github.com/emasoudy/clawdbot-skills.git
cp -r clawdbot-skills/graphiti ~/.clawdbot/skills/
```

## Usage

Search knowledge graph:
```
User: "Search for information about our project"
Agent: [Queries Graphiti and returns relevant facts]
```

## Configuration

```bash
# Set custom Graphiti URL
clawdbot config set skills.graphiti.baseUrl "http://your-server:8001"

# Or use environment variable
export GRAPHITI_URL="http://your-server:8001"
```

Default: `http://localhost:8001`

## License

MIT - See LICENSE file
