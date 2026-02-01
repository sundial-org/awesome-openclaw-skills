#!/usr/bin/env python3
"""
Parallel.ai Search API
Usage: python3 search.py <query> [--max-results N] [--mode one-shot|agentic]
"""

import os
import sys
import json
import argparse

from parallel import Parallel

API_KEY = os.environ.get("PARALLEL_API_KEY", "y2s_m4er5i6-5qCikOLUtmnkvOYRU24eDphq_jg1")

def search(objective: str, max_results: int = 10, mode: str = "one-shot"):
    """Search using Parallel SDK."""
    client = Parallel(api_key=API_KEY)
    return client.beta.search(
        mode=mode,
        max_results=max_results,
        objective=objective
    )

def format_results(response) -> str:
    """Format search results for display."""
    output = []
    output.append(f"🔍 Search ID: {response.search_id}\n")
    
    for i, result in enumerate(response.results, 1):
        title = result.title or "No title"
        url = result.url
        excerpts = result.excerpts or []
        date = f" ({result.publish_date})" if result.publish_date else ""
        
        output.append(f"**{i}. [{title}]({url})**{date}")
        
        if excerpts:
            # Clean and truncate excerpt
            excerpt = excerpts[0].replace("\n", " ").strip()[:400]
            output.append(f"   {excerpt}...")
        output.append("")
    
    if response.usage:
        usage = ", ".join(f"{u.name}: {u.count}" for u in response.usage)
        output.append(f"📊 Usage: {usage}")
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="Parallel.ai Search")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--max-results", "-n", type=int, default=10)
    parser.add_argument("--mode", "-m", default="one-shot", choices=["one-shot", "agentic"])
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    query = " ".join(args.query)
    response = search(query, max_results=args.max_results, mode=args.mode)
    
    if args.json:
        # Convert to dict for JSON output
        print(json.dumps({
            "search_id": response.search_id,
            "results": [
                {
                    "url": r.url,
                    "title": r.title,
                    "publish_date": r.publish_date,
                    "excerpts": r.excerpts
                }
                for r in response.results
            ]
        }, indent=2))
    else:
        print(format_results(response))

if __name__ == "__main__":
    main()
