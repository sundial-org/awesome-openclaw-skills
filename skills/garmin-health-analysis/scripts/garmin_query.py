#!/usr/bin/env python3
"""
Query Garmin data by time - "what was my heart rate at 3pm yesterday?"
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from garmin_auth import get_client


def parse_time(time_str, date_str=None):
    """Parse various time formats into datetime."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Try different formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%H:%M:%S",
        "%H:%M",
        "%I:%M %p",  # 3:00 PM
        "%I %p",     # 3 PM
    ]
    
    for fmt in formats:
        try:
            if "%Y" in fmt:
                return datetime.strptime(time_str, fmt)
            else:
                return datetime.strptime(f"{date_str} {time_str}", f"%Y-%m-%d {fmt}")
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse time: {time_str}")


def find_closest_datapoint(target_time, data_array, timestamp_key="startTimeInSeconds"):
    """Find the closest data point to a target time."""
    if not data_array:
        return None
    
    target_timestamp = int(target_time.timestamp())
    
    # Handle different timestamp formats
    def get_timestamp(item):
        if timestamp_key in item:
            ts = item[timestamp_key]
            # Handle milliseconds
            if ts > 10000000000:
                ts = ts // 1000
            return ts
        elif "startGMT" in item:
            # ISO format or timestamp
            start_gmt = item["startGMT"]
            if isinstance(start_gmt, str):
                return int(datetime.fromisoformat(start_gmt.replace("Z", "+00:00")).timestamp())
            else:
                return start_gmt // 1000 if start_gmt > 10000000000 else start_gmt
        return None
    
    closest = None
    min_diff = float('inf')
    
    for item in data_array:
        ts = get_timestamp(item)
        if ts is None:
            continue
        
        diff = abs(ts - target_timestamp)
        if diff < min_diff:
            min_diff = diff
            closest = item
    
    return closest


def query_heart_rate_at_time(client, time_str, date_str=None):
    """Get heart rate at a specific time."""
    target_time = parse_time(time_str, date_str)
    date = target_time.strftime("%Y-%m-%d")
    
    try:
        # Get intraday heart rate data
        data = client.get_heart_rates(date)
        
        if not data:
            return {"error": "No heart rate data for this date", "date": date}
        
        # Data format varies - try different keys
        hr_array = data.get("heartRateValues") or data.get("allDayHR") or []
        
        # heartRateValues format: [[timestamp_ms, hr_value], ...]
        # Convert to dict format for our function
        if hr_array and isinstance(hr_array[0], list):
            hr_array = [{"startTimeInSeconds": ts//1000, "heartRateValue": val} for ts, val in hr_array]
        
        closest = find_closest_datapoint(target_time, hr_array)
        
        if closest:
            return {
                "requested_time": time_str,
                "actual_time": datetime.fromtimestamp(
                    closest.get("startTimeInSeconds", 0)
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "heart_rate": closest.get("heartRateValue") or closest.get("value"),
                "date": date
            }
        else:
            return {"error": "No data point found near requested time", "date": date}
    
    except Exception as e:
        return {"error": str(e), "date": date}


def query_stress_at_time(client, time_str, date_str=None):
    """Get stress level at a specific time."""
    target_time = parse_time(time_str, date_str)
    date = target_time.strftime("%Y-%m-%d")
    
    try:
        data = client.get_all_day_stress(date)
        
        if not data:
            return {"error": "No stress data for this date", "date": date}
        
        stress_values = data.get("stressValuesArray") or []
        
        closest = find_closest_datapoint(target_time, stress_values)
        
        if closest:
            return {
                "requested_time": time_str,
                "stress_level": closest.get("stressLevel") or closest.get("value"),
                "date": date
            }
        else:
            return {"error": "No data point found near requested time", "date": date}
    
    except Exception as e:
        return {"error": str(e), "date": date}


def query_body_battery_at_time(client, time_str, date_str=None):
    """Get Body Battery level at a specific time."""
    target_time = parse_time(time_str, date_str)
    date = target_time.strftime("%Y-%m-%d")
    
    try:
        data = client.get_body_battery(date)
        
        if not data or len(data) == 0:
            return {"error": "No Body Battery data for this date", "date": date}
        
        # Body Battery is in bodyBatteryValuesArray
        bb_values = data[0].get("bodyBatteryValuesArray", [])
        
        # Convert [timestamp, value] pairs to dicts
        bb_dicts = [{"startTimeInSeconds": ts//1000, "value": val} for ts, val in bb_values]
        
        closest = find_closest_datapoint(target_time, bb_dicts)
        
        if closest:
            return {
                "requested_time": time_str,
                "body_battery": closest.get("value"),
                "date": date
            }
        else:
            return {"error": "No data point found near requested time", "date": date}
    
    except Exception as e:
        return {"error": str(e), "date": date}


def query_steps_at_time(client, time_str, date_str=None):
    """Get step count at a specific time."""
    target_time = parse_time(time_str, date_str)
    date = target_time.strftime("%Y-%m-%d")
    
    try:
        data = client.get_steps_data(date)
        
        if not data:
            return {"error": "No steps data for this date", "date": date}
        
        # Steps are usually cumulative throughout the day
        step_values = data.get("stepsArray") or []
        
        closest = find_closest_datapoint(target_time, step_values)
        
        if closest:
            return {
                "requested_time": time_str,
                "steps": closest.get("steps") or closest.get("value"),
                "date": date
            }
        else:
            return {"error": "No data point found near requested time", "date": date}
    
    except Exception as e:
        return {"error": str(e), "date": date}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Query Garmin data by time")
    parser.add_argument("metric", choices=["heart_rate", "stress", "body_battery", "steps"],
                       help="Metric to query")
    parser.add_argument("time", help="Time (e.g., '3:00 PM', '15:00', '2024-01-15 14:30')")
    parser.add_argument("--date", help="Date if not included in time (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    client = get_client()
    if not client:
        print('{"error": "Not authenticated"}')
        sys.exit(1)
    
    if args.metric == "heart_rate":
        result = query_heart_rate_at_time(client, args.time, args.date)
    elif args.metric == "stress":
        result = query_stress_at_time(client, args.time, args.date)
    elif args.metric == "body_battery":
        result = query_body_battery_at_time(client, args.time, args.date)
    elif args.metric == "steps":
        result = query_steps_at_time(client, args.time, args.date)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
