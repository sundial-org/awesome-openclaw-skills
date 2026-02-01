#!/usr/bin/env python3
"""
Memory Linking Script (A-Mem / Zettelkasten Layer)
Creates a knowledge graph with embeddings and bidirectional links between facts.
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict, Counter
import math

# Configuration - Auto-detect workspace
def get_workspace_dir() -> Path:
    """Auto-detect workspace directory from environment or standard locations."""
    # 1. Check CLAWDBOT_WORKSPACE env var
    if env_workspace := os.getenv("CLAWDBOT_WORKSPACE"):
        return Path(env_workspace)
    
    # 2. Check current working directory
    cwd = Path.cwd()
    if (cwd / "SOUL.md").exists() or (cwd / "AGENTS.md").exists():
        return cwd
    
    # 3. Fall back to ~/.clawdbot/workspace
    default_workspace = Path.home() / ".clawdbot" / "workspace"
    if not default_workspace.exists():
        default_workspace.mkdir(parents=True, exist_ok=True)
    
    return default_workspace

WORKSPACE_DIR = get_workspace_dir()
MEMORY_DIR = WORKSPACE_DIR / "memory"
EXTRACTED_FILE = MEMORY_DIR / "extracted.jsonl"
KNOWLEDGE_GRAPH_FILE = MEMORY_DIR / "knowledge-graph.json"
KNOWLEDGE_SUMMARY_FILE = MEMORY_DIR / "knowledge-summary.md"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def find_api_key() -> Optional[str]:
    """Find OpenAI API key for embeddings."""
    if OPENAI_API_KEY:
        return OPENAI_API_KEY
    
    key_path = Path.home() / ".config" / "openai" / "api_key"
    if key_path.exists():
        return key_path.read_text().strip()
    
    return None


def get_embedding(text: str, api_key: str) -> Optional[List[float]]:
    """Get embedding vector from OpenAI."""
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "text-embedding-3-small",
        "input": text
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["data"][0]["embedding"]
    except Exception as e:
        print(f"Embedding error: {e}")
        return None


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    return dot_product / (mag1 * mag2)


def extract_keywords(content: str, subject: str) -> List[str]:
    """Extract keywords from content (simple approach)."""
    # Combine content and subject
    text = f"{subject} {content}".lower()
    
    # Remove common words
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "should", "could", "can", "may", "might", "must", "this",
        "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"
    }
    
    # Simple tokenization
    words = text.replace(".", " ").replace(",", " ").replace("!", " ").replace("?", " ").split()
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]
    
    # Get unique keywords, limit to top 10 by frequency
    word_counts = Counter(keywords)
    return [word for word, _ in word_counts.most_common(10)]


def auto_detect_domain_tags(content: str, subject: str) -> List[str]:
    """Auto-detect domain tags from content without hardcoded lists."""
    tags = []
    content_lower = content.lower()
    subject_lower = subject.lower()
    combined = f"{content_lower} {subject_lower}"
    
    # Common technical domains (auto-detected)
    domain_keywords = {
        "blockchain": ["blockchain", "web3", "crypto", "smart contract", "wallet", "nft"],
        "ai": ["ai", "llm", "machine learning", "neural", "model", "gpt", "claude"],
        "development": ["code", "programming", "development", "git", "github", "api"],
        "mobile": ["mobile", "android", "ios", "flutter", "react native", "app"],
        "web": ["web", "website", "frontend", "backend", "server", "http"],
        "database": ["database", "sql", "postgres", "mongodb", "query"],
        "cloud": ["cloud", "aws", "gcp", "azure", "deploy", "kubernetes"],
    }
    
    for domain, keywords in domain_keywords.items():
        if any(keyword in combined for keyword in keywords):
            tags.append(domain)
    
    return tags


def generate_tags(fact: Dict) -> List[str]:
    """Generate tags based on fact type, subject, and content."""
    tags = [fact["type"]]
    
    subject = fact.get("subject", "").lower()
    if subject:
        tags.append(subject)
    
    # Auto-detect domain tags from content
    content = fact.get("content", "")
    domain_tags = auto_detect_domain_tags(content, subject)
    tags.extend(domain_tags)
    
    return list(set(tags))  # Remove duplicates


def check_contradiction(fact1: Dict, fact2: Dict) -> bool:
    """Check if two facts might contradict each other (simple heuristic)."""
    # Same subject but different content
    if fact1.get("subject") != fact2.get("subject"):
        return False
    
    content1 = fact1.get("content", "").lower()
    content2 = fact2.get("content", "").lower()
    
    # Check for negation patterns
    negation_pairs = [
        ("will", "won't"),
        ("is", "isn't"),
        ("do", "don't"),
        ("yes", "no"),
        ("enable", "disable"),
        ("active", "inactive"),
    ]
    
    for pos, neg in negation_pairs:
        if (pos in content1 and neg in content2) or (neg in content1 and pos in content2):
            return True
    
    return False


def load_facts() -> List[Dict]:
    """Load facts from extracted.jsonl."""
    if not EXTRACTED_FILE.exists():
        print(f"ERROR: {EXTRACTED_FILE} not found. Run memory-extract.py first.")
        return []
    
    facts = []
    with open(EXTRACTED_FILE) as f:
        for i, line in enumerate(f):
            try:
                fact = json.loads(line)
                fact["id"] = i  # Assign unique ID
                facts.append(fact)
            except:
                pass
    
    return facts


def build_knowledge_graph(facts: List[Dict], api_key: Optional[str]) -> Dict:
    """Build knowledge graph with embeddings and links."""
    print("Building knowledge graph...")
    
    graph = {
        "nodes": [],
        "links": [],
        "metadata": {
            "created": datetime.now().isoformat(),
            "total_facts": len(facts),
            "has_embeddings": api_key is not None
        }
    }
    
    # Process each fact
    for fact in facts:
        # Generate keywords and tags
        keywords = extract_keywords(fact.get("content", ""), fact.get("subject", ""))
        tags = generate_tags(fact)
        
        # Get embedding if API key available
        embedding = None
        if api_key:
            embed_text = f"{fact.get('subject', '')} {fact.get('content', '')}"
            embedding = get_embedding(embed_text, api_key)
        
        # Create enhanced node
        node = {
            "id": fact["id"],
            "type": fact.get("type"),
            "content": fact.get("content"),
            "subject": fact.get("subject"),
            "date": fact.get("date"),
            "source": fact.get("source"),
            "confidence": fact.get("confidence", 0.8),
            "keywords": keywords,
            "tags": tags,
            "embedding": embedding,
            "valid_from": fact.get("date"),
            "valid_to": None,  # Updated if contradicted
            "links": []  # Will be filled in next step
        }
        
        graph["nodes"].append(node)
    
    # Find related facts and create links
    print("Finding related facts...")
    
    for i, node1 in enumerate(graph["nodes"]):
        if i % 10 == 0:
            print(f"  Processing {i}/{len(graph['nodes'])}...")
        
        for j, node2 in enumerate(graph["nodes"]):
            if i >= j:  # Skip self and already processed pairs
                continue
            
            # Calculate similarity
            similarity = 0.0
            
            # Embedding-based similarity
            if node1["embedding"] and node2["embedding"]:
                similarity = cosine_similarity(node1["embedding"], node2["embedding"])
            else:
                # Fallback: keyword overlap
                keywords1 = set(node1["keywords"])
                keywords2 = set(node2["keywords"])
                if keywords1 and keywords2:
                    overlap = len(keywords1 & keywords2)
                    total = len(keywords1 | keywords2)
                    similarity = overlap / total if total > 0 else 0.0
            
            # Create link if similarity above threshold
            if similarity > 0.3:
                link = {
                    "source": node1["id"],
                    "target": node2["id"],
                    "strength": similarity,
                    "type": "related"
                }
                
                # Check for contradiction
                fact1 = facts[i]
                fact2 = facts[j]
                if check_contradiction(fact1, fact2):
                    link["type"] = "contradicts"
                    
                    # Mark older fact as superseded
                    date1 = node1["date"]
                    date2 = node2["date"]
                    if date1 < date2:
                        node1["valid_to"] = date2
                    else:
                        node2["valid_to"] = date1
                
                graph["links"].append(link)
                node1["links"].append(node2["id"])
                node2["links"].append(node1["id"])
    
    return graph


def generate_summary(graph: Dict) -> str:
    """Generate human-readable summary of the knowledge graph."""
    summary = ["# Knowledge Graph Summary\n"]
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    summary.append(f"Total Facts: {graph['metadata']['total_facts']}\n")
    summary.append(f"Total Links: {len(graph['links'])}\n\n")
    
    # Group facts by subject
    by_subject = defaultdict(list)
    for node in graph["nodes"]:
        subject = node.get("subject", "Unknown")
        by_subject[subject].append(node)
    
    # Sort subjects by number of facts
    sorted_subjects = sorted(by_subject.items(), key=lambda x: len(x[1]), reverse=True)
    
    summary.append("## Facts by Subject\n\n")
    for subject, nodes in sorted_subjects[:20]:  # Top 20 subjects
        summary.append(f"### {subject} ({len(nodes)} facts)\n\n")
        for node in nodes[:5]:  # Top 5 facts per subject
            valid_status = ""
            if node.get("valid_to"):
                valid_status = f" [SUPERSEDED on {node['valid_to']}]"
            
            summary.append(f"- **[{node['type']}]** {node['content'][:100]}...{valid_status}\n")
            summary.append(f"  - Date: {node['date']} | Confidence: {node['confidence']:.2f}\n")
            summary.append(f"  - Tags: {', '.join(node['tags'][:5])}\n")
            
            if node.get("links"):
                summary.append(f"  - Related to: {len(node['links'])} other facts\n")
            summary.append("\n")
    
    # Recent decisions
    summary.append("## Recent Decisions\n\n")
    decisions = [n for n in graph["nodes"] if n["type"] == "decision"]
    decisions.sort(key=lambda x: x["date"], reverse=True)
    for decision in decisions[:10]:
        summary.append(f"- **{decision['date']}**: {decision['content']}\n")
    
    summary.append("\n## Recent Learnings\n\n")
    learnings = [n for n in graph["nodes"] if n["type"] == "learning"]
    learnings.sort(key=lambda x: x["date"], reverse=True)
    for learning in learnings[:10]:
        summary.append(f"- **{learning['date']}**: {learning['content']}\n")
    
    return "".join(summary)


def main():
    """Main linking pipeline."""
    print("Memory Linking (A-Mem)")
    print(f"Workspace: {WORKSPACE_DIR}")
    print("=" * 50)
    
    # Load facts
    facts = load_facts()
    if not facts:
        return
    
    print(f"Loaded {len(facts)} facts")
    
    # Check for API key
    api_key = find_api_key()
    if api_key:
        print("✓ OpenAI API key found (embeddings enabled)")
    else:
        print("✗ No OpenAI API key (using keyword-based similarity)")
    
    # Build knowledge graph
    graph = build_knowledge_graph(facts, api_key)
    
    # Save knowledge graph
    MEMORY_DIR.mkdir(exist_ok=True)
    with open(KNOWLEDGE_GRAPH_FILE, "w") as f:
        json.dump(graph, f, indent=2)
    
    print(f"\n✓ Knowledge graph saved to: {KNOWLEDGE_GRAPH_FILE}")
    
    # Generate summary
    summary = generate_summary(graph)
    with open(KNOWLEDGE_SUMMARY_FILE, "w") as f:
        f.write(summary)
    
    print(f"✓ Summary saved to: {KNOWLEDGE_SUMMARY_FILE}")
    
    # Stats
    contradictions = sum(1 for link in graph["links"] if link["type"] == "contradicts")
    avg_links = sum(len(node["links"]) for node in graph["nodes"]) / len(graph["nodes"]) if graph["nodes"] else 0
    
    print(f"\nStats:")
    print(f"  - Total facts: {len(facts)}")
    print(f"  - Total links: {len(graph['links'])}")
    print(f"  - Contradictions found: {contradictions}")
    print(f"  - Avg links per fact: {avg_links:.1f}")


if __name__ == "__main__":
    main()
