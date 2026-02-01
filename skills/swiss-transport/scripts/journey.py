#!/usr/bin/env python3
"""
Swiss Public Transport Journey Planner
Usage: python3 journey.py <from> <to> [--limit N] [--time HH:MM] [--date YYYY-MM-DD]
"""
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

def format_time(iso_time):
    """Extract HH:MM from ISO datetime"""
    try:
        return iso_time[11:16]
    except:
        return iso_time

def format_duration(duration):
    """Format duration from 00d00:12:00 to readable format"""
    try:
        parts = duration.split(':')
        days_hours = parts[0].split('d')
        days = int(days_hours[0]) if len(days_hours) > 1 else 0
        hours = int(days_hours[-1])
        mins = int(parts[1])
        
        if days > 0:
            return f"{days}d {hours}h {mins}m"
        elif hours > 0:
            return f"{hours}h {mins}m"
        else:
            return f"{mins}m"
    except:
        return duration

def get_connections(from_station, to_station, limit=3, time=None, date=None):
    """Query connections from transport.opendata.ch API"""
    params = {
        'from': from_station,
        'to': to_station,
        'limit': limit
    }
    
    if time:
        params['time'] = time
    if date:
        params['date'] = date
    
    url = f"https://transport.opendata.ch/v1/connections?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            return data
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def print_connections(data):
    """Print connections in a readable format"""
    connections = data.get('connections', [])
    
    if not connections:
        print("No connections found.")
        return
    
    from_station = data['from']['name']
    to_station = data['to']['name']
    
    print(f"\n🚂 {from_station} → {to_station}\n")
    print("=" * 80)
    
    for i, conn in enumerate(connections, 1):
        dep_time = format_time(conn['from']['departure'])
        arr_time = format_time(conn['to']['arrival'])
        duration = format_duration(conn['duration'])
        transfers = conn['transfers']
        platform = conn['from'].get('platform', 'N/A')
        
        print(f"\n{i}. Departure: {dep_time} (Platform {platform})")
        print(f"   Arrival:   {arr_time}")
        print(f"   Duration:  {duration}")
        print(f"   Changes:   {transfers}")
        
        # Print sections
        if 'sections' in conn:
            print(f"\n   Route:")
            for j, section in enumerate(conn['sections'], 1):
                if section.get('journey'):
                    journey = section['journey']
                    from_name = section['departure']['station']['name']
                    to_name = section['arrival']['station']['name']
                    category = journey.get('category', 'N/A')
                    number = journey.get('number', '')
                    
                    print(f"   {j}. {category} {number}: {from_name} → {to_name}")
                elif section.get('walk'):
                    walk_duration = section['walk'].get('duration')
                    if walk_duration:
                        print(f"   {j}. 🚶 Walk ({walk_duration} min)")
        
        print()

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 journey.py <from> <to> [--limit N] [--time HH:MM] [--date YYYY-MM-DD]")
        print("\nExample:")
        print("  python3 journey.py 'Zürich HB' 'Bern'")
        print("  python3 journey.py 'Basel' 'Lugano' --limit 5")
        print("  python3 journey.py 'Zürich' 'Genève' --time 14:30")
        sys.exit(1)
    
    from_station = sys.argv[1]
    to_station = sys.argv[2]
    
    # Parse optional arguments
    limit = 3
    time = None
    date = None
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--limit' and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--time' and i + 1 < len(sys.argv):
            time = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--date' and i + 1 < len(sys.argv):
            date = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Get and print connections
    data = get_connections(from_station, to_station, limit, time, date)
    print_connections(data)

if __name__ == '__main__':
    main()
