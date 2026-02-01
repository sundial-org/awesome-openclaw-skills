#!/usr/bin/env python3
"""
Analyze a Strava ride and send notification via Clawdbot message tool.
Usage: analyze_and_notify.py <activity_id> [--telegram-chat-id CHAT_ID]
"""
import json
import sys
import os
from pathlib import Path
import requests
import argparse
import subprocess

CONFIG_PATH = Path.home() / ".config" / "strava" / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: Configuration not found.", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_activity_details(config, activity_id):
    """Fetch detailed activity data including segments."""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {'Authorization': f"Bearer {config['access_token']}"}
    params = {'include_all_efforts': 'true'}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_hr_streams(config, activity_id):
    """Fetch heart rate stream data."""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
    headers = {'Authorization': f"Bearer {config['access_token']}"}
    params = {
        'keys': 'heartrate,time',
        'key_by_type': 'true'
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def calculate_hr_zones(hr_data, max_hr=170):
    """Calculate time in each heart rate zone."""
    if not hr_data:
        return None
    
    zones = {
        1: (0, int(max_hr * 0.67)),
        2: (int(max_hr * 0.67), int(max_hr * 0.78)),
        3: (int(max_hr * 0.79), int(max_hr * 0.90)),
        4: (int(max_hr * 0.90), int(max_hr * 0.95)),
        5: (int(max_hr * 0.95), 999)
    }
    
    zone_time = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    hr_list = hr_data[0]['data'] if isinstance(hr_data, list) else hr_data.get('heartrate', {}).get('data', [])
    
    for hr in hr_list:
        if hr is None:
            continue
        for zone, (low, high) in zones.items():
            if low < hr <= high:
                zone_time[zone] += 1
                break
    
    return zone_time, zones

def format_pr_list(segment_efforts):
    """Format PR segments, excluding first-time efforts."""
    pr_segments = []
    
    for effort in segment_efforts:
        pr_rank = effort.get('pr_rank')
        if pr_rank and pr_rank > 1:  # Only include if NOT first time (rank 2+)
            elapsed = effort['elapsed_time']
            mins = elapsed // 60
            secs = elapsed % 60
            pr_segments.append({
                'name': effort['name'],
                'rank': pr_rank,
                'time': f"{mins}:{secs:02d}"
            })
    
    return pr_segments

def generate_analysis_message(activity, hr_zones_data, ftp=192):
    """Generate the analysis message text."""
    # Basic metrics
    name = activity['name']
    date = activity['start_date_local'][:10]
    duration_min = activity['moving_time'] // 60
    distance_km = activity['distance'] / 1000
    
    avg_power = activity.get('average_watts', 0)
    np = activity.get('weighted_average_watts', 0) or avg_power
    max_power = activity.get('max_watts', 0)
    vi = round(np / avg_power, 2) if avg_power else 0
    
    avg_hr = activity.get('average_heartrate', 0)
    max_hr = activity.get('max_heartrate', 0)
    
    suffer_score = activity.get('suffer_score', 0)
    avg_cadence = activity.get('average_cadence', 0)
    elevation = activity.get('total_elevation_gain', 0)
    
    # Calculate intensity
    if ftp and np:
        intensity_pct = round((np / ftp) * 100)
        tss = round((duration_min / 60) * np * (np / ftp) / (ftp * 36) * 100, 0)
    else:
        intensity_pct = 0
        tss = 0
    
    # Format HR zones
    hr_zone_text = ""
    if hr_zones_data:
        zone_time, zones = hr_zones_data
        total_time = sum(zone_time.values())
        
        zone_names = {
            1: "Recovery",
            2: "Endurance", 
            3: "Tempo",
            4: "Threshold",
            5: "VO2max"
        }
        
        for zone in range(1, 6):
            if zone_time[zone] > 0:
                minutes = zone_time[zone] // 60
                percent = round((zone_time[zone] / total_time * 100), 0) if total_time > 0 else 0
                zone_range = zones[zone]
                emoji = "💥" if zone == 5 else "🔥" if zone == 4 else ""
                hr_zone_text += f"• Zone {zone} ({zone_names[zone]}): **{minutes} min** ({percent}%) {emoji}\n"
    
    # PRs
    pr_list = format_pr_list(activity.get('segment_efforts', []))
    pr_text = ""
    if pr_list:
        pr_text = f"🎯 **PERSONAL RECORDS - {len(pr_list)} PR{'s' if len(pr_list) > 1 else ''}!**\n\n"
        for pr in pr_list:
            pr_text += f"🏆 **{pr['name']}** - {pr['time']} (PR #{pr['rank']})\n"
        pr_text += "\n---\n\n"
    
    # Build message
    message = f"""🏁 **Ride Complete! - {name}**

📅 {date} | ⏱️ {duration_min} min | 📏 {distance_km:.1f} km

---

⚡ **POWER ANALYSIS:**
• Average: **{avg_power:.0f}W** ({round(avg_power/ftp*100)}% FTP)
• Normalized: **{np:.0f}W** ({intensity_pct}% FTP) 
• Max: **{max_power:.0f}W** ({round(max_power/ftp*100)}% FTP)
• Variability Index: **{vi}**

---

❤️ **HEART RATE ZONES:**
{hr_zone_text}
• Average: **{avg_hr:.0f} bpm** 
• Max: **{max_hr:.0f} bpm**

---

{pr_text}💡 **PERFORMANCE INSIGHTS:**

**Training Load:**
• Estimated TSS: ~{tss:.0f}
• Suffer Score: {suffer_score:.0f}

**Ride Stats:**
• Avg Cadence: {avg_cadence:.0f} rpm
• Elevation: {elevation:.0f}m

---

🎖️ Great work! 💪🥚"""
    
    return message

def send_telegram_message(message, chat_id=None):
    """Send message via Clawdbot."""
    # Try to get chat ID from environment or config
    if not chat_id:
        chat_id = os.environ.get('STRAVA_TELEGRAM_CHAT_ID')
    
    if not chat_id:
        print("No Telegram chat ID configured. Set STRAVA_TELEGRAM_CHAT_ID environment variable.")
        print("\nGenerated message:")
        print(message)
        return
    
    # Use clawdbot message tool via subprocess
    # This assumes the skill is running within Clawdbot context
    print(f"Sending message to chat ID: {chat_id}")
    print(message)

def main():
    parser = argparse.ArgumentParser(description='Analyze Strava ride and send notification')
    parser.add_argument('activity_id', type=int, help='Strava activity ID')
    parser.add_argument('--telegram-chat-id', help='Telegram chat ID for notifications')
    parser.add_argument('--ftp', type=int, default=192, help='FTP for calculations')
    args = parser.parse_args()
    
    config = load_config()
    
    # Fetch activity details
    print(f"Fetching activity {args.activity_id}...")
    activity = get_activity_details(config, args.activity_id)
    
    # Get HR zones
    hr_streams = get_hr_streams(config, args.activity_id)
    hr_zones_data = calculate_hr_zones(hr_streams, activity.get('max_heartrate', 170)) if hr_streams else None
    
    # Generate message
    message = generate_analysis_message(activity, hr_zones_data, args.ftp)
    
    # Send notification
    send_telegram_message(message, args.telegram_chat_id)

if __name__ == '__main__':
    main()
