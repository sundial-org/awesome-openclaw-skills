#!/usr/bin/env python3
"""
Analyze Strava rides and generate performance insights.
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import requests
import time

CONFIG_PATH = Path.home() / ".config" / "strava" / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: Configuration not found. Run scripts/setup.sh first.", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_PATH) as f:
        return json.load(f)

def refresh_token_if_needed(config):
    """Refresh access token if expired."""
    if config['expires_at'] < time.time():
        print("Refreshing access token...")
        url = "https://www.strava.com/oauth/token"
        data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'refresh_token': config['refresh_token'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        config['access_token'] = token_data['access_token']
        config['refresh_token'] = token_data['refresh_token']
        config['expires_at'] = token_data['expires_at']
        
        # Save updated config
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    
    return config

def get_activities(config, days=90):
    """Fetch activities from Strava."""
    config = refresh_token_if_needed(config)
    
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f"Bearer {config['access_token']}"}
    
    # Get activities after a certain date
    after_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
    
    params = {
        'after': after_timestamp,
        'per_page': 100
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    activities = response.json()
    
    # Filter for virtual rides
    virtual_rides = [a for a in activities if a.get('type') == 'VirtualRide']
    
    return virtual_rides

def analyze_activity(activity):
    """Extract key metrics from an activity."""
    return {
        'id': activity.get('id'),
        'name': activity.get('name'),
        'date': activity.get('start_date_local'),
        'duration': activity.get('moving_time', 0) / 60,  # minutes
        'distance': activity.get('distance', 0) / 1000,  # km
        'avg_power': activity.get('average_watts'),
        'weighted_avg_power': activity.get('weighted_average_watts'),
        'max_power': activity.get('max_watts'),
        'avg_hr': activity.get('average_heartrate'),
        'max_hr': activity.get('max_heartrate'),
        'suffer_score': activity.get('suffer_score'),
        'calories': activity.get('calories'),
        'elevation_gain': activity.get('total_elevation_gain'),
        'avg_cadence': activity.get('average_cadence'),
        'has_heartrate': activity.get('has_heartrate', False),
        'device_watts': activity.get('device_watts', False),
    }

def calculate_tss(duration_hours, normalized_power, ftp):
    """Calculate Training Stress Score."""
    if not normalized_power or not ftp or ftp == 0:
        return None
    
    intensity_factor = normalized_power / ftp
    tss = (duration_hours * normalized_power * intensity_factor) / (ftp * 36) * 100
    return round(tss, 1)

def analyze_fitness_trends(rides, estimated_ftp=190):
    """Calculate fitness metrics and trends."""
    if not rides:
        return None
    
    # Sort by date
    rides_sorted = sorted(rides, key=lambda x: x['date'])
    
    # Calculate TSS for each ride
    for ride in rides_sorted:
        duration_hours = ride['duration'] / 60
        np = ride.get('weighted_avg_power') or ride.get('avg_power')
        ride['tss'] = calculate_tss(duration_hours, np, estimated_ftp)
    
    # Recent periods
    recent_7d = [r for r in rides_sorted if r['date'] >= (datetime.now() - timedelta(days=7)).isoformat()]
    recent_28d = [r for r in rides_sorted if r['date'] >= (datetime.now() - timedelta(days=28)).isoformat()]
    
    # Power statistics
    powers_all = [r['avg_power'] for r in rides_sorted if r.get('avg_power')]
    powers_recent = [r['avg_power'] for r in recent_28d if r.get('avg_power')]
    
    avg_power_all = sum(powers_all) / len(powers_all) if powers_all else 0
    avg_power_recent = sum(powers_recent) / len(powers_recent) if powers_recent else 0
    
    # TSS statistics
    tss_values = [r['tss'] for r in rides_sorted if r.get('tss')]
    total_tss = sum(tss_values)
    
    return {
        'total_rides': len(rides),
        'total_duration_hours': sum(r['duration'] for r in rides) / 60,
        'total_distance_km': sum(r['distance'] for r in rides),
        'total_tss': total_tss,
        'avg_power_all_time': round(avg_power_all),
        'avg_power_recent_28d': round(avg_power_recent),
        'rides_last_7d': len(recent_7d),
        'rides_last_28d': len(recent_28d),
        'power_trend': 'improving' if avg_power_recent > avg_power_all else 'declining' if avg_power_recent < avg_power_all else 'stable',
        'estimated_ftp': estimated_ftp
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Analyze Strava rides')
    parser.add_argument('--days', type=int, default=90, help='Number of days to analyze')
    parser.add_argument('--ftp', type=int, default=190, help='Estimated FTP for TSS calculation')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()
    
    config = load_config()
    
    print(f"Fetching activities from last {args.days} days...")
    rides = get_activities(config, args.days)
    
    print(f"Found {len(rides)} virtual rides")
    
    # Analyze each ride
    analyzed_rides = [analyze_activity(r) for r in rides]
    
    # Calculate fitness metrics
    fitness = analyze_fitness_trends(analyzed_rides, args.ftp)
    
    if args.json:
        output = {
            'rides': analyzed_rides,
            'fitness': fitness
        }
        print(json.dumps(output, indent=2))
    else:
        if fitness:
            print("\n=== Fitness Summary ===")
            print(f"Total rides: {fitness['total_rides']}")
            print(f"Total duration: {fitness['total_duration_hours']:.1f} hours")
            print(f"Total distance: {fitness['total_distance_km']:.1f} km")
            print(f"Total TSS: {fitness['total_tss']:.0f}")
            print(f"Average power (all): {fitness['avg_power_all_time']}W")
            print(f"Average power (28d): {fitness['avg_power_recent_28d']}W")
            print(f"Power trend: {fitness['power_trend']}")
            print(f"Estimated FTP: {fitness['estimated_ftp']}W")
            print(f"\nRecent activity:")
            print(f"  Last 7 days: {fitness['rides_last_7d']} rides")
            print(f"  Last 28 days: {fitness['rides_last_28d']} rides")
            
            print("\n=== Recent Rides ===")
            for ride in analyzed_rides[-5:]:
                print(f"\n{ride['date'][:10]} - {ride['name']}")
                print(f"  Duration: {ride['duration']:.0f} min")
                if ride.get('avg_power'):
                    print(f"  Avg Power: {ride['avg_power']:.0f}W")
                if ride.get('tss'):
                    print(f"  TSS: {ride['tss']:.0f}")

if __name__ == '__main__':
    main()
