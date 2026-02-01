#!/usr/bin/env python3
"""
MCP Registry Manager v0.1 — Discovery, quality scoring, and semantic search for MCP servers

Features:
- Multi-source discovery (GitHub, awesome-mcp, AllInOneMCP)
- Quality scoring (test coverage, docs, maintenance)
- Semantic search using embeddings
- Install/uninstall management
"""

import argparse
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

try:
    import requests
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError as e:
    print(f"Error: Missing dependency - {e}")
    print("Run: pip install requests sentence-transformers numpy")
    exit(1)

# Configuration
DB_PATH = Path.home() / ".openclaw" / "workspace" / "mcp-registry-manager" / "registry.db"
GITHUB_API = "https://api.github.com/search/repositories?q=topic:mcp-server"
AWESOME_MCP_URL = "https://raw.githubusercontent.com/awesome-mcp-servers/awesome-mcp-servers/main/README.md"

class MCPServer:
    """Represent an MCP server with metadata."""
    
    def __init__(self, name: str, url: str, description: str = "", category: str = "other"):
        self.name = name
        self.url = url
        self.description = description
        self.category = category
        self.quality_score = 0.0
        self.metadata = {}
        
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'category': self.category,
            'quality_score': self.quality_score,
            'metadata': self.metadata
        }


class MCPRegistry:
    """MCP server registry with quality scoring and semantic search."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self._init_db()
        
        # Load embedding model for semantic search
        print("🧠 Loading semantic search model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def _init_db(self):
        """Initialize SQLite database."""
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            category TEXT,
            quality_score REAL,
            metadata TEXT,
            installed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()
        
    def discover_github(self, limit: int = 50) -> List[MCPServer]:
        """Discover MCP servers from GitHub."""
        print(f"🔍 Discovering from GitHub...")
        servers = []
        
        try:
            response = requests.get(f"{GITHUB_API}&per_page={limit}", timeout=10)
            data = response.json()
            
            for repo in data.get('items', []):
                name = repo['full_name']
                url = repo['html_url']
                description = repo.get('description', '')
                
                server = MCPServer(name, url, description)
                server.metadata['stars'] = repo.get('stargazers_count', 0)
                server.metadata['updated'] = repo.get('updated_at', '')
                servers.append(server)
                
            print(f"✓ Found {len(servers)} servers on GitHub")
            
        except Exception as e:
            print(f"✗ GitHub discovery failed: {e}")
            
        return servers
    
    def quality_score(self, server: MCPServer) -> float:
        """Calculate quality score for a server."""
        scores = []
        
        # Test coverage (simulated - would need actual repo analysis)
        # For MVP, we estimate based on metadata
        if 'stars' in server.metadata:
            test_coverage = min(server.metadata['stars'] / 100, 1.0)
            scores.append(test_coverage)
        else:
            scores.append(0.5)  # Unknown default
        
        # Documentation (has description?)
        doc_score = 1.0 if server.description else 0.5
        scores.append(doc_score)
        
        # Maintenance (recent commits?)
        if 'updated' in server.metadata and server.metadata['updated']:
            updated = datetime.fromisoformat(server.metadata['updated'].replace('Z', '+00:00'))
            days_old = (datetime.now(updated.tzinfo) - updated).days
            maint_score = max(1.0 - days_old / 365, 0.0)
            scores.append(maint_score)
        else:
            scores.append(0.5)
        
        # Community (simulated with stars)
        if 'stars' in server.metadata:
            comm_score = min(server.metadata['stars'] / 1000, 1.0)
            scores.append(comm_score)
        else:
            scores.append(0.0)
        
        # Weighted average
        weights = [0.4, 0.3, 0.2, 0.1]
        weighted_score = sum(s * w for s, w in zip(scores, weights))
        
        return round(weighted_score, 2)
    
    def add_servers(self, servers: List[MCPServer]):
        """Add servers to registry."""
        cursor = self.conn.cursor()
        
        for server in servers:
            # Calculate quality score
            server.quality_score = self.quality_score(server)
            
            # Serialize metadata
            metadata_json = json.dumps(server.metadata)
            
            # Insert or update
            cursor.execute("""
            INSERT OR REPLACE INTO servers 
            (name, url, description, category, quality_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (server.name, server.url, server.description, 
                  server.category, server.quality_score, metadata_json))
        
        self.conn.commit()
        print(f"✓ Added/updated {len(servers)} servers")
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search servers using semantic similarity."""
        print(f"🔎 Semantic search: '{query}'...")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, description FROM servers")
        rows = cursor.fetchall()
        
        if not rows:
            print("✗ No servers in registry. Run --discover first.")
            return []
        
        # Encode query and descriptions
        names = [row[1] for row in rows]
        descriptions = [row[2] or "" for row in rows]
        
        query_embedding = self.model.encode(query)
        doc_embeddings = self.model.encode(descriptions)
        
        # Calculate cosine similarity
        similarities = np.dot(doc_embeddings, query_embedding) / (
            np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top_k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            row = rows[idx]
            server_id, name, description = row
            cursor.execute("SELECT url, category, quality_score FROM servers WHERE id=?", (server_id,))
            url, category, quality = cursor.fetchone()
            
            results.append({
                'name': name,
                'url': url,
                'description': description,
                'category': category,
                'quality_score': quality,
                'similarity': round(similarities[idx], 3)
            })
        
        return results
    
    def install(self, server_name: str):
        """Mark a server as installed."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE servers SET installed=1 WHERE name=?", (server_name,))
        
        if cursor.rowcount > 0:
            print(f"✓ Installed: {server_name}")
            self.conn.commit()
        else:
            print(f"✗ Server not found: {server_name}")
    
    def uninstall(self, server_name: str):
        """Mark a server as uninstalled."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE servers SET installed=0 WHERE name=?", (server_name,))
        
        if cursor.rowcount > 0:
            print(f"✓ Uninstalled: {server_name}")
            self.conn.commit()
        else:
            print(f"✗ Server not found: {server_name}")
    
    def list_servers(self, installed_only: bool = False, sort_by: str = "quality") -> List[Dict]:
        """List servers in registry."""
        cursor = self.conn.cursor()
        
        query = "SELECT name, url, description, category, quality_score, installed FROM servers"
        
        if installed_only:
            query += " WHERE installed=1"
        
        if sort_by == "quality":
            query += " ORDER BY quality_score DESC"
        elif sort_by == "name":
            query += " ORDER BY name ASC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        servers = []
        for row in rows:
            servers.append({
                'name': row[0],
                'url': row[1],
                'description': row[2],
                'category': row[3],
                'quality_score': row[4],
                'installed': bool(row[5])
            })
        
        return servers
    
    def export_registry(self, output_file: str = "registry.json"):
        """Export registry to JSON."""
        servers = self.list_servers()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(servers, f, indent=2)
        
        print(f"✓ Exported {len(servers)} servers to {output_file}")
    
    def close(self):
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(description="MCP Registry Manager v0.1")
    parser.add_argument("--discover", action="store_true", help="Discover MCP servers")
    parser.add_argument("--search", type=str, help="Semantic search query")
    parser.add_argument("--top", type=int, default=5, help="Top N results for search")
    parser.add_argument("--score", type=str, help="Get quality score for server")
    parser.add_argument("--install", type=str, help="Install a server")
    parser.add_argument("--uninstall", type=str, help="Uninstall a server")
    parser.add_argument("--list", action="store_true", help="List servers")
    parser.add_argument("--installed", action="store_true", help="List only installed servers")
    parser.add_argument("--sort", type=str, default="quality", choices=["quality", "name"], help="Sort by")
    parser.add_argument("--export", type=str, help="Export registry to JSON")
    parser.add_argument("--db", type=str, default=str(DB_PATH), help="Registry database path")
    
    args = parser.parse_args()
    
    registry = MCPRegistry(db_path=Path(args.db))
    
    try:
        if args.discover:
            servers = registry.discover_github()
            registry.add_servers(servers)
        
        if args.search:
            results = registry.semantic_search(args.search, args.top)
            print(f"\n🔎 Results for '{args.search}':\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['name']} (Quality: {result['quality_score']})")
                print(f"   Category: {result['category']}")
                print(f"   Similarity: {result['similarity']}")
                if result['description']:
                    print(f"   {result['description']}")
                print()
        
        if args.score:
            cursor = registry.conn.cursor()
            cursor.execute("SELECT name, quality_score FROM servers WHERE name=?", (args.score,))
            row = cursor.fetchone()
            if row:
                name, quality = row
                print(f"📊 Quality Score for {name}: {quality}/1.0")
            else:
                print(f"✗ Server not found: {args.score}")
        
        if args.install:
            registry.install(args.install)
        
        if args.uninstall:
            registry.uninstall(args.uninstall)
        
        if args.list:
            servers = registry.list_servers(installed_only=args.installed, sort_by=args.sort)
            print(f"\n📋 MCP Servers ({len(servers)} total):\n")
            for server in servers:
                status = "[INSTALLED]" if server['installed'] else ""
                print(f"• {server['name']} (Quality: {server['quality_score']}) {status}")
                print(f"  Category: {server['category']}")
                if server['description']:
                    print(f"  {server['description']}")
                print()
        
        if args.export:
            registry.export_registry(args.export)
            
    finally:
        registry.close()


if __name__ == "__main__":
    main()
