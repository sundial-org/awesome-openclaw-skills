#!/usr/bin/env python3
"""
Search for movies and TV shows in Jellyseerr.
"""
import json
import sys
from pathlib import Path
import requests

CONFIG_PATH = Path.home() / ".config" / "jellyseerr" / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: Configuration not found. Run scripts/setup.sh first.", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_PATH) as f:
        return json.load(f)

def search_content(config, query):
    """Search for movies and TV shows."""
    import urllib.parse
    # Jellyseerr requires %20 encoding for spaces, not +
    encoded_query = urllib.parse.quote(query, safe='')
    url = f"{config['server_url']}/api/v1/search?query={encoded_query}"
    headers = {'X-Api-Key': config['api_key']}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

def format_result(item):
    """Format search result for display."""
    media_type = item.get('mediaType')
    title = item.get('title') or item.get('name')
    year = item.get('releaseDate', '')[:4] if item.get('releaseDate') else item.get('firstAirDate', '')[:4] if item.get('firstAirDate') else ''
    overview = item.get('overview', 'No description available')
    
    # Status info
    status = item.get('mediaInfo', {}).get('status', 0) if item.get('mediaInfo') else 0
    status_text = {
        1: "PENDING",
        2: "PROCESSING", 
        3: "PARTIALLY_AVAILABLE",
        4: "AVAILABLE",
        5: "AVAILABLE"
    }.get(status, "NOT_REQUESTED")
    
    return {
        'id': item.get('id'),
        'type': media_type,
        'title': title,
        'year': year,
        'overview': overview[:100] + '...' if len(overview) > 100 else overview,
        'status': status_text,
        'tmdb_id': item.get('id')
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: search.py <query>", file=sys.stderr)
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    config = load_config()
    
    print(f"Searching for: {query}\n")
    
    results = search_content(config, query)
    items = results.get('results', [])
    
    if not items:
        print("No results found")
        sys.exit(0)
    
    for i, item in enumerate(items[:10], 1):
        result = format_result(item)
        media_icon = "🎬" if result['type'] == 'movie' else "📺"
        
        print(f"{i}. {media_icon} {result['title']} ({result['year']})")
        print(f"   Status: {result['status']}")
        print(f"   {result['overview']}")
        print(f"   TMDB ID: {result['tmdb_id']}")
        print()

if __name__ == '__main__':
    main()
