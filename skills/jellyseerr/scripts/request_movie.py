#!/usr/bin/env python3
"""
Request a movie through Jellyseerr.
"""
import json
import sys
from pathlib import Path
import requests
from track_requests import add_request

CONFIG_PATH = Path.home() / ".config" / "jellyseerr" / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: Configuration not found. Run scripts/setup.sh first.", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_PATH) as f:
        return json.load(f)

def search_movie(config, query):
    """Search for a movie."""
    import urllib.parse
    # Jellyseerr requires %20 encoding for spaces, not +
    encoded_query = urllib.parse.quote(query, safe='')
    url = f"{config['server_url']}/api/v1/search?query={encoded_query}"
    headers = {'X-Api-Key': config['api_key']}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    results = response.json().get('results', [])
    
    # Filter for movies only
    movies = [r for r in results if r.get('mediaType') == 'movie']
    return movies

def request_movie(config, tmdb_id):
    """Submit a movie request."""
    url = f"{config['server_url']}/api/v1/request"
    headers = {
        'X-Api-Key': config['api_key'],
        'Content-Type': 'application/json'
    }
    
    data = {
        'mediaId': tmdb_id,
        'mediaType': 'movie'
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Request a movie')
    parser.add_argument('title', nargs='+', help='Movie title')
    parser.add_argument('--auto', action='store_true', help='Auto-select first result')
    args = parser.parse_args()
    
    title = ' '.join(args.title)
    config = load_config()
    
    print(f"Searching for movie: {title}")
    movies = search_movie(config, title)
    
    if not movies:
        print("No movies found")
        sys.exit(1)
    
    # Show results
    print(f"\nFound {len(movies)} movie(s):\n")
    for i, movie in enumerate(movies[:5], 1):
        year = movie.get('releaseDate', '')[:4] if movie.get('releaseDate') else ''
        status = movie.get('mediaInfo', {}).get('status', 0) if movie.get('mediaInfo') else 0
        
        status_text = {
            1: "PENDING",
            2: "PROCESSING",
            3: "PARTIALLY_AVAILABLE",
            4: "AVAILABLE",
            5: "AVAILABLE"
        }.get(status, "NOT_REQUESTED")
        
        print(f"{i}. {movie['title']} ({year})")
        print(f"   Status: {status_text}")
        if status >= 4:
            print(f"   ⚠️  Already available!")
        print()
    
    # Select movie
    if args.auto:
        selection = 1
    else:
        try:
            selection = int(input("Select movie number (or 0 to cancel): "))
            if selection == 0:
                print("Cancelled")
                sys.exit(0)
        except (ValueError, EOFError):
            print("Cancelled")
            sys.exit(0)
    
    if selection < 1 or selection > len(movies):
        print("Invalid selection")
        sys.exit(1)
    
    selected = movies[selection - 1]
    
    # Check if already available
    status = selected.get('mediaInfo', {}).get('status', 0) if selected.get('mediaInfo') else 0
    if status >= 4:
        print(f"\n⚠️  {selected['title']} is already available!")
        sys.exit(0)
    
    # Submit request
    print(f"\nRequesting: {selected['title']} ({selected.get('releaseDate', '')[:4]})")
    
    try:
        result = request_movie(config, selected['id'])
        print(f"✓ Request submitted successfully!")
        print(f"  Request ID: {result.get('id')}")
        if config.get('auto_approve'):
            print(f"  Status: Auto-approved for download")
        
        # Add to tracking for availability notifications
        add_request(selected['id'], 'movie', selected['title'])
        print(f"  📬 You'll be notified when it's available!")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            print(f"⚠️  This movie has already been requested")
        else:
            raise

if __name__ == '__main__':
    main()
