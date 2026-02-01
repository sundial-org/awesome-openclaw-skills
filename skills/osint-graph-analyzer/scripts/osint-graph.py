#!/usr/bin/env python3
"""
OSINT Graph Analyzer v0.1 — Build knowledge graphs from OSINT data

Features:
- Neo4j graph storage
- CSV/JSON ingestion
- Graph algorithms (community detection, centrality, paths)
- JSON export for visualization
"""

import argparse
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional

try:
    from neo4j import GraphDatabase
except ImportError:
    print("Error: neo4j-driver not installed. Run: pip install neo4j")
    exit(1)

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

class OSINTGraph:
    """Neo4j-based OSINT knowledge graph."""
    
    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
        
    def clear_graph(self):
        """Clear all nodes and relationships."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Graph cleared")
            
    def ingest_csv(self, nodes_file: str, edges_file: str):
        """Ingest nodes and edges from CSV files."""
        print(f"📥 Ingesting from {nodes_file} and {edges_file}...")
        
        with self.driver.session() as session:
            # Ingest nodes
            with open(nodes_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    node_id = row['id']
                    node_type = row.get('type', 'Entity')
                    props = json.loads(row.get('properties', '{}')) if 'properties' in row else {}
                    
                    query = f"""
                    MERGE (n:{node_type} {{id: $id}})
                    SET n += $props
                    """
                    session.run(query, id=node_id, props=props)
            
            print(f"✓ {sum(1 for _ in open(nodes_file)) - 1} nodes ingested")
            
            # Ingest edges
            with open(edges_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    source = row['source']
                    target = row['target']
                    rel_type = row.get('relationship', 'CONNECTED_TO')
                    timestamp = row.get('timestamp')
                    
                    query = f"""
                    MATCH (a {{id: $source}}), (b {{id: $target}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r.timestamp = datetime($timestamp)
                    """
                    session.run(query, source=source, target=target, timestamp=timestamp)
            
            print(f"✓ {sum(1 for _ in open(edges_file)) - 1} edges ingested")
            
    def community_detection(self, algorithm: str = "louvain"):
        """Run community detection algorithm."""
        print(f"🔍 Running community detection ({algorithm})...")
        
        with self.driver.session() as session:
            if algorithm == "louvain":
                result = session.run("""
                CALL gds.louvain.stream('myGraph')
                YIELD nodeId, communityId
                MATCH (n)
                WHERE id(n) = nodeId
                SET n.community = communityId
                RETURN count(DISTINCT communityId) as communities
                """)
                communities = result.single()['communities']
                print(f"✓ Found {communities} communities")
                
    def centrality(self, metric: str = "pagerank", top_n: int = 10):
        """Calculate and return top N nodes by centrality."""
        print(f"📊 Calculating {metric} (top {top_n})...")
        
        with self.driver.session() as session:
            if metric == "pagerank":
                result = session.run("""
                CALL gds.pageRank.stream('myGraph')
                YIELD nodeId, score
                MATCH (n)
                WHERE id(n) = nodeId
                RETURN n.name as name, n.type as type, score
                ORDER BY score DESC
                LIMIT $top_n
                """, top_n=top_n)
            elif metric == "betweenness":
                result = session.run("""
                CALL gds.betweenness.stream('myGraph')
                YIELD nodeId, score
                MATCH (n)
                WHERE id(n) = nodeId
                RETURN n.name as name, n.type as type, score
                ORDER BY score DESC
                LIMIT $top_n
                """, top_n=top_n)
            else:
                print(f"Error: Unknown metric '{metric}'")
                return []
            
            top_nodes = []
            for record in result:
                top_nodes.append({
                    'name': record['name'],
                    'type': record['type'],
                    'score': round(record['score'], 4)
                })
            
            return top_nodes
            
    def shortest_path(self, source_name: str, target_name: str):
        """Find shortest path between two entities."""
        print(f"🔗 Finding path: {source_name} → {target_name}...")
        
        with self.driver.session() as session:
            result = session.run("""
            MATCH path = shortestPath(
                (a {name: $source})-[*]-(b {name: $target})
            )
            RETURN [node in nodes(path) | node.name] as path,
                   length(path) as hops
            """, source=source_name, target=target_name)
            
            record = result.single()
            if record:
                path = record['path']
                hops = record['hops']
                print(f"✓ Found path ({hops} hops): {' → '.join(path)}")
                return path, hops
            else:
                print("✗ No path found")
                return None, None
                
    def export_graph(self, output_file: str = "graph.json"):
        """Export graph to JSON for visualization."""
        print(f"📤 Exporting graph to {output_file}...")
        
        with self.driver.session() as session:
            nodes_result = session.run("""
            MATCH (n)
            RETURN n.id as id, n.name as name, n.type as type,
                   labels(n) as labels, properties(n) as props
            """)
            
            edges_result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN a.name as source, b.name as target, type(r) as relationship,
                   properties(r) as props
            """)
            
            nodes = []
            for record in nodes_result:
                node = {
                    'id': record['id'],
                    'name': record['name'],
                    'type': record['type'],
                    'labels': record['labels'],
                    'props': dict(record['props'])
                }
                nodes.append(node)
                
            edges = []
            for record in edges_result:
                edge = {
                    'source': record['source'],
                    'target': record['target'],
                    'relationship': record['relationship'],
                    'props': dict(record['props'])
                }
                edges.append(edge)
            
            graph = {'nodes': nodes, 'edges': edges}
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(graph, f, indent=2)
            
            print(f"✓ Exported {len(nodes)} nodes, {len(edges)} edges")
            
    def create_graph_projection(self):
        """Create Neo4j Graph Data Science projection."""
        with self.driver.session() as session:
            session.run("""
            CALL gds.graph.project(
                'myGraph',
                '*',
                '*'
            )
            """)
            print("✓ Graph projection created for algorithms")


def main():
    parser = argparse.ArgumentParser(description="OSINT Graph Analyzer v0.1")
    parser.add_argument("--clear", action="store_true", help="Clear graph")
    parser.add_argument("--ingest", nargs=2, metavar=('NODES', 'EDGES'), help="Ingest CSV files")
    parser.add_argument("--community", action="store_true", help="Run community detection")
    parser.add_argument("--centrality", type=str, help="Calculate centrality (pagerank/betweenness)")
    parser.add_argument("--top", type=int, default=10, help="Top N results for centrality")
    parser.add_argument("--path", nargs=2, metavar=('FROM', 'TO'), help="Find shortest path")
    parser.add_argument("--export", type=str, help="Export graph to JSON")
    parser.add_argument("--uri", type=str, default=NEO4J_URI, help="Neo4j URI")
    parser.add_argument("--user", type=str, default=NEO4J_USER, help="Neo4j user")
    parser.add_argument("--password", type=str, default=NEO4J_PASSWORD, help="Neo4j password")
    
    args = parser.parse_args()
    
    graph = OSINTGraph(uri=args.uri, user=args.user, password=args.password)
    
    try:
        if args.clear:
            graph.clear_graph()
        
        if args.ingest:
            graph.ingest_csv(args.ingest[0], args.ingest[1])
            graph.create_graph_projection()
        
        if args.community:
            graph.community_detection()
        
        if args.centrality:
            top = graph.centrality(args.centrality, args.top)
            print("\n📊 Top Entities:")
            for i, node in enumerate(top, 1):
                print(f"  {i}. {node['name']} ({node['type']}) - {node['score']}")
        
        if args.path:
            graph.shortest_path(args.path[0], args.path[1])
        
        if args.export:
            graph.export_graph(args.export)
            
    finally:
        graph.close()


if __name__ == "__main__":
    main()
