#!/usr/bin/env python3
"""
Fetch health data from Garmin Connect.
Outputs JSON to stdout for parsing by the agent.
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Import auth helper
sys.path.insert(0, str(Path(__file__).parent))
from garmin_auth import get_client

try:
    from garminconnect import Garmin
except ImportError:
    print('{"error": "garminconnect not installed. Run: pip3 install garminconnect"}', file=sys.stderr)
    sys.exit(1)


def get_date_range(days=None, start=None, end=None):
    """Calculate date range for queries."""
    if start and end:
        return start, end
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days or 7)
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def fetch_sleep(client, days=7, start=None, end=None):
    """Fetch sleep data."""
    start_date, end_date = get_date_range(days, start, end)
    
    try:
        sleep_data = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            try:
                data = client.get_sleep_data(date_str)
                if data:
                    # Sleep data is nested inside dailySleepDTO
                    sleep_dto = data.get("dailySleepDTO", {})
                    if sleep_dto:
                        sleep_data.append({
                            "date": date_str,
                            "sleep_time_seconds": sleep_dto.get("sleepTimeSeconds"),
                            "deep_sleep_seconds": sleep_dto.get("deepSleepSeconds"),
                            "light_sleep_seconds": sleep_dto.get("lightSleepSeconds"),
                            "rem_sleep_seconds": sleep_dto.get("remSleepSeconds"),
                            "awake_seconds": sleep_dto.get("awakeSleepSeconds"),
                            "sleep_score": sleep_dto.get("sleepScores", {}).get("overall", {}).get("value"),
                            "restless_periods": data.get("restlessMomentsCount"),  # This is on root
                            "avg_hr": sleep_dto.get("averageHeartRate"),
                            "avg_hrv": data.get("avgOvernightHrv"),  # This is on root
                            "avg_respiration": sleep_dto.get("averageRespirationValue")
                        })
            except Exception as e:
                print(f"⚠️  No sleep data for {date_str}: {e}", file=sys.stderr)
            
            current += timedelta(days=1)
        
        return {"sleep": sleep_data, "start": start_date, "end": end_date}
    
    except Exception as e:
        return {"error": str(e)}


def fetch_hrv(client, days=7, start=None, end=None):
    """Fetch HRV data."""
    start_date, end_date = get_date_range(days, start, end)
    
    try:
        hrv_data = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            try:
                data = client.get_hrv_data(date_str)
                if data and "hrvSummary" in data:
                    summary = data["hrvSummary"]
                    hrv_data.append({
                        "date": date_str,
                        "last_night_avg": summary.get("lastNightAvg"),
                        "last_night_5min_high": summary.get("lastNight5MinHigh"),
                        "last_night_5min_low": summary.get("lastNight5MinLow"),
                        "weekly_avg": summary.get("weeklyAvg"),
                        "baseline_balanced_low": summary.get("baselineBalancedLow"),
                        "baseline_balanced_high": summary.get("baselineBalancedHigh"),
                        "status": summary.get("status")
                    })
            except Exception:
                pass
            
            current += timedelta(days=1)
        
        return {"hrv": hrv_data, "start": start_date, "end": end_date}
    
    except Exception as e:
        return {"error": str(e)}


def fetch_body_battery(client, days=7, start=None, end=None):
    """Fetch Body Battery data (Garmin's recovery metric)."""
    start_date, end_date = get_date_range(days, start, end)
    
    try:
        bb_data = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            try:
                data = client.get_body_battery(date_str)
                if data and len(data) > 0:
                    day_data = data[0]
                    charged = day_data.get("charged")
                    drained = day_data.get("drained")
                    
                    # Parse bodyBatteryValuesArray to get highest/lowest
                    values_array = day_data.get("bodyBatteryValuesArray", [])
                    values = [v[1] for v in values_array if len(v) > 1]  # Extract values from [timestamp, value] pairs
                    
                    highest = max(values) if values else None
                    lowest = min(values) if values else None
                    
                    bb_data.append({
                        "date": date_str,
                        "charged": charged,
                        "drained": drained,
                        "highest": highest,
                        "lowest": lowest
                    })
            except Exception:
                pass
            
            current += timedelta(days=1)
        
        return {"body_battery": bb_data, "start": start_date, "end": end_date}
    
    except Exception as e:
        return {"error": str(e)}


def fetch_heart_rate(client, days=7, start=None, end=None):
    """Fetch heart rate data."""
    start_date, end_date = get_date_range(days, start, end)
    
    try:
        hr_data = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            try:
                data = client.get_heart_rates(date_str)
                if data:
                    hr_data.append({
                        "date": date_str,
                        "resting_hr": data.get("restingHeartRate"),
                        "max_hr": data.get("maxHeartRate"),
                        "min_hr": data.get("minHeartRate")
                    })
            except Exception:
                pass
            
            current += timedelta(days=1)
        
        return {"heart_rate": hr_data, "start": start_date, "end": end_date}
    
    except Exception as e:
        return {"error": str(e)}


def fetch_activities(client, days=7, start=None, end=None):
    """Fetch activities/workouts."""
    start_date, end_date = get_date_range(days, start, end)
    
    try:
        # Garmin API uses offset-based pagination
        activities = client.get_activities_by_date(start_date, end_date, activitytype="")
        
        activity_list = []
        for activity in activities:
            activity_list.append({
                "date": activity.get("startTimeLocal", "").split(" ")[0],
                "activity_type": activity.get("activityType", {}).get("typeKey"),
                "activity_name": activity.get("activityName"),
                "duration_seconds": activity.get("duration"),
                "distance_meters": activity.get("distance"),
                "calories": activity.get("calories"),
                "avg_hr": activity.get("averageHR"),
                "max_hr": activity.get("maxHR"),
                "elevation_gain": activity.get("elevationGain"),
                "avg_speed": activity.get("averageSpeed")
            })
        
        return {"activities": activity_list, "start": start_date, "end": end_date, "count": len(activity_list)}
    
    except Exception as e:
        return {"error": str(e)}


def fetch_stress(client, days=7, start=None, end=None):
    """Fetch stress levels."""
    start_date, end_date = get_date_range(days, start, end)
    
    try:
        stress_data = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            try:
                data = client.get_stress_data(date_str)
                if data:
                    stress_data.append({
                        "date": date_str,
                        "avg_stress": data.get("avgStressLevel"),
                        "max_stress": data.get("maxStressLevel"),
                        "rest_stress": data.get("restStressLevel"),
                        "activity_stress": data.get("activityStressLevel"),
                        "low_stress_duration": data.get("lowStressDuration"),
                        "medium_stress_duration": data.get("mediumStressDuration"),
                        "high_stress_duration": data.get("highStressDuration")
                    })
            except Exception:
                pass
            
            current += timedelta(days=1)
        
        return {"stress": stress_data, "start": start_date, "end": end_date}
    
    except Exception as e:
        return {"error": str(e)}


def fetch_summary(client, days=7, start=None, end=None):
    """Fetch combined summary with key metrics."""
    start_date, end_date = get_date_range(days, start, end)
    
    try:
        # Fetch multiple data types
        sleep = fetch_sleep(client, days, start, end).get("sleep", [])
        hrv = fetch_hrv(client, days, start, end).get("hrv", [])
        bb = fetch_body_battery(client, days, start, end).get("body_battery", [])
        hr = fetch_heart_rate(client, days, start, end).get("heart_rate", [])
        activities = fetch_activities(client, days, start, end).get("activities", [])
        
        # Calculate averages (handle None values)
        sleep_times = [s.get("sleep_time_seconds") for s in sleep if s.get("sleep_time_seconds")]
        avg_sleep_hours = (sum(sleep_times) / len(sleep_times) / 3600) if sleep_times else 0
        
        sleep_scores = [s.get("sleep_score") for s in sleep if s.get("sleep_score") is not None]
        avg_sleep_score = (sum(sleep_scores) / len(sleep_scores)) if sleep_scores else 0
        
        hrv_values = [h.get("last_night_avg") for h in hrv if h.get("last_night_avg") is not None]
        avg_hrv = (sum(hrv_values) / len(hrv_values)) if hrv_values else 0
        
        rhr_values = [h.get("resting_hr") for h in hr if h.get("resting_hr") is not None]
        avg_rhr = (sum(rhr_values) / len(rhr_values)) if rhr_values else 0
        
        bb_charged_values = [b.get("charged") for b in bb if b.get("charged") is not None]
        avg_bb_charged = (sum(bb_charged_values) / len(bb_charged_values)) if bb_charged_values else 0
        
        return {
            "summary": {
                "period": f"{start_date} to {end_date}",
                "days": days,
                "avg_sleep_hours": round(avg_sleep_hours, 1),
                "avg_sleep_score": round(avg_sleep_score, 1),
                "avg_hrv_ms": round(avg_hrv, 1),
                "avg_resting_hr": round(avg_rhr, 1),
                "avg_body_battery_charged": round(avg_bb_charged, 1),
                "total_activities": len(activities),
                "total_calories": sum(a.get("calories", 0) for a in activities if a.get("calories"))
            },
            "sleep": sleep,
            "hrv": hrv,
            "body_battery": bb,
            "heart_rate": hr,
            "activities": activities
        }
    
    except Exception as e:
        return {"error": str(e)}


def fetch_profile(client):
    """Fetch user profile."""
    try:
        profile = client.get_full_name()
        stats = client.get_user_summary(datetime.now().strftime("%Y-%m-%d"))
        
        return {
            "profile": {
                "name": profile,
                "display_name": stats.get("displayName"),
                "email": stats.get("email")
            }
        }
    
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Fetch Garmin health data")
    parser.add_argument("metric", choices=["sleep", "hrv", "body_battery", "heart_rate", "activities", "stress", "summary", "profile"],
                       help="Type of data to fetch")
    parser.add_argument("--days", type=int, default=7, help="Number of days to fetch (default: 7)")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    # Get authenticated client
    client = get_client()
    if not client:
        print('{"error": "Not authenticated. Run: python3 scripts/garmin_auth.py login --email YOUR_EMAIL --password YOUR_PASSWORD"}')
        sys.exit(1)
    
    # Fetch requested data
    if args.metric == "sleep":
        result = fetch_sleep(client, args.days, args.start, args.end)
    elif args.metric == "hrv":
        result = fetch_hrv(client, args.days, args.start, args.end)
    elif args.metric == "body_battery":
        result = fetch_body_battery(client, args.days, args.start, args.end)
    elif args.metric == "heart_rate":
        result = fetch_heart_rate(client, args.days, args.start, args.end)
    elif args.metric == "activities":
        result = fetch_activities(client, args.days, args.start, args.end)
    elif args.metric == "stress":
        result = fetch_stress(client, args.days, args.start, args.end)
    elif args.metric == "summary":
        result = fetch_summary(client, args.days, args.start, args.end)
    elif args.metric == "profile":
        result = fetch_profile(client)
    
    # Output JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
