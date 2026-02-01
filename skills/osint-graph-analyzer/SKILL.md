# OSINT Graph Analyzer 🕵️

Build knowledge graphs from OSINT data and discover hidden patterns using Neo4j graph algorithms.

## What It Does

Ingests OSINT data from multiple sources and creates a Neo4j knowledge graph for:
- **Entity linking** — Connect same person across platforms
- **Community detection** — Find clusters of related entities
- **Centrality analysis** — Identify key influencers in networks
- **Path analysis** — Trace connections between entities
- **Pattern recognition** — Detect anomalies and hidden relationships

## Use Cases

- **Investigation workflows** — Map relationships in complex cases
- **Threat intelligence** — Identify central nodes in attack networks
- **Social network analysis** — Discover communities and influence patterns
- **Counter-OSINT** — Understand your own exposure surface

## Requirements

- Neo4j 5.x (local or remote)
- Python 3.9+
- neo4j-driver package

## Usage

```bash
# Start Neo4j instance (local)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.23

# Ingest data
python3 scripts/osint-graph.py --ingest data/sources.csv

# Run community detection
python3 scripts/osint-graph.py --community-detection

# Find most central entities
python3 scripts/osint-graph.py --centrality --top 10

# Trace path between two entities
python3 scripts/osint-graph.py --path "Entity A" "Entity B"

# Export graph as visualization
python3 scripts/osint-graph.py --export graph.json
```

## Data Format

Supported formats:
- CSV (node + edge files)
- JSON (Cypher queries)
- Direct API ingestion (Telegram, Twitter, etc.)

CSV example:
```csv
nodes.csv:
id,name,type,properties
1,@target_account,person,"{country:US,verified:true}"
2,@associated_handle,person,"{country:RU}"

edges.csv:
source,target,relationship,timestamp
1,2,MENTIONED,2026-01-31
```

## Graph Algorithms

| Algorithm | What It Finds | Use Case |
|------------|----------------|-----------|
| **Louvain** | Community clusters | Find groups working together |
| **PageRank** | Influence centrality | Identify key influencers |
| **Betweenness** | Bridge nodes | Find connection points between communities |
| **Shortest Path** | Connection chains | Trace indirect relationships |
| **Weakly Connected** | Disconnected subgraphs | Find isolated clusters |

## Architecture

```
┌─────────────────┐
│  Ingestion      │  ← CSV/JSON/API sources
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Neo4j Graph    │  ← Nodes + Relationships
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Algorithms     │  ← GraphX / Neo4j Graph Algorithms
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Visualization  │  ← JSON export + D3.js / Cytoscape
└─────────────────┘
```

## Inspiration

- **CRIS** — Multi-agent criminal intelligence system with Neo4j
- **Context Graphs** — Semantic search + structural analysis
- **osint-analyser** — LLM-powered OSINT automation

## Local-Only Promise

- Data stays local (Neo4j instance)
- No external API calls for analysis
- Optional offline mode

## Version History

- **v0.1** — MVP: CSV ingest, basic algorithms, JSON export
- Roadmap: API integration, ML anomaly detection, real-time updates
