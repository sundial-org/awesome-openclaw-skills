# OSINT Graph Analyzer 🕵️

Build knowledge graphs from OSINT data and discover hidden patterns.

## Quick Start

```bash
# Start Neo4j (Docker)
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.23

# Ingest example data
python3 scripts/osint-graph.py --ingest data/nodes.csv data/edges.csv

# Run community detection
python3 scripts/osint-graph.py --community

# Find top influencers
python3 scripts/osint-graph.py --centrality pagerank --top 5

# Export for visualization
python3 scripts/osint-graph.py --export graph.json
```

## Features

✅ **Ingestion** — CSV, JSON, direct API  
✅ **Algorithms** — Community detection, centrality, path analysis  
✅ **Visualization** — JSON export for D3.js/Cytoscape  
✅ **Local-only** — No external API calls  

## Use Cases

- Investigation workflows
- Threat intelligence
- Social network analysis
- Counter-OSINT exposure analysis

## Inspired By

- CRIS multi-agent system (6 specialized agents)
- Context Graphs with Neo4j
- osint-analyser (LLM-powered OSINT)

## Installation

```bash
# Clone repo
git clone https://github.com/orosha-ai/osint-graph-analyzer

# Install dependencies
pip install neo4j

# Run
python3 scripts/osint-graph.py --help
```

## License

MIT
