#!/usr/bin/env python3
"""
Request a TV show through Jellyseerr.
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

def search_tv(config, query):
    """Search for a TV show."""
    import urllib.parse
    # Jellyseerr requires %20 encoding for spaces, not +
    encoded_query = urllib.parse.quote(query, safe='')
    url = f"{config['server_url']}/api/v1/search?query={encoded_query}"
    headers = {'X-Api-Key': config['api_key']}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    results = response.json().get('results', [])
    
    # Filter for TV shows only
    shows = [r for r in results if r.get('mediaType') == 'tv']
    return shows

def request_tv(config, tmdb_id, seasons=None):
    """Submit a TV show request."""
    url = f"{config['server_url']}/api/v1/request"
    headers = {
        'X-Api-Key': config['api_key'],
        'Content-Type': 'application/json'
    }
    
    data = {
        'mediaId': tmdb_id,
        'mediaType': 'tv',
        'seasons': seasons or 'all'
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Request a TV show')
    parser.add_argument('title', nargs='+', help='TV show title')
    parser.add_argument('--season', type=int, help='Specific season number')
    parser.add_argument('--auto', action='store_true', help='Auto-select first result')
    args = parser.parse_args()
    
    title = ' '.join(args.title)
    config = load_config()
    
    print(f"Searching for TV show: {title}")
    shows = search_tv(config, title)
    
    if not shows:
        print("No TV shows found")
        sys.exit(1)
    
    # Show results
    print(f"\nFound {len(shows)} TV show(s):\n")
    for i, show in enumerate(shows[:5], 1):
        name = show.get('name')
        year = show.get('firstAirDate', '')[:4] if show.get('firstAirDate') else ''
        status = show.get('mediaInfo', {}).get('status', 0) if show.get('mediaInfo') else 0
        
        status_text = {
            1: "PENDING",
            2: "PROCESSING",
            3: "PARTIALLY_AVAILABLE",
            4: "AVAILABLE",
            5: "AVAILABLE"
        }.get(status, "NOT_REQUESTED")
        
        print(f"{i}. {name} ({year})")
        print(f"   Status: {status_text}")
        print()
    
    # Select show
    if args.auto:
        selection = 1
    else:
        try:
            selection = int(input("Select show number (or 0 to cancel): "))
            if selection == 0:
                print("Cancelled")
                sys.exit(0)
        except (ValueError, EOFError):
            print("Cancelled")
            sys.exit(0)
    
    if selection < 1 or selection > len(shows):
        print("Invalid selection")
        sys.exit(1)
    
    selected = shows[selection - 1]
    
    # Determine seasons to request
    seasons_to_request = None
    if args.season:
        seasons_to_request = [args.season]
        print(f"\nRequesting: {selected['name']} - Season {args.season}")
    else:
        print(f"\nRequesting: {selected['name']} (All seasons)")
    
    # Submit request
    try:
        result = request_tv(config, selected['id'], seasons_to_request)
        print(f"✓ Request submitted successfully!")
        print(f"  Request ID: {result.get('id')}")
        if config.get('auto_approve'):
            print(f"  Status: Auto-approved for download")
        
        # Add to tracking for availability notifications
        season_text = f" Season {args.season}" if args.season else ""
        add_request(selected['id'], 'tv', f"{selected['name']}{season_text}")
        print(f"  📬 You'll be notified when it's available!")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            print(f"⚠️  This show (or season) has already been requested")
        else:
            raise

if __name__ == '__main__':
    main()
