#!/usr/bin/env python3
"""
Fitbit Morning Briefing CLI

Generate concise morning health briefings from Fitbit data.

Usage:
    python fitbit_briefing.py                    # Today's briefing
    python fitbit_briefing.py --date 2026-01-20  # Specific date
    python fitbit_briefing.py --format json      # JSON output
    python fitbit_briefing.py --format brief     # 3-line brief
"""

import argparse
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fitbit_api import FitbitClient


def _calculate_activity_level(steps, calories, active_minutes):
    """Determine activity level from day's metrics."""
    if steps >= 10000 and active_minutes >= 30:
        return "Active"
    elif steps >= 7500 and active_minutes >= 20:
        return "Moderate"
    elif steps >= 5000:
        return "Light"
    else:
        return "Sedentary"


def _format_brief_briefing(data, baseline=None):
    """Format a 3-line brief summary."""
    lines = []
    
    # Line 1: Steps and activity
    steps = data.get("steps_today", 0)
    calories = data.get("calories_today", 0)
    lines.append(f"📊 {steps:,} steps • {calories:,} cal")
    
    # Line 2: Heart rate and sleep
    resting_hr = data.get("resting_hr", "N/A")
    sleep_hours = data.get("sleep_hours", "N/A")
    if sleep_hours and sleep_hours != "N/A":
        lines.append(f"❤️ Resting HR: {resting_hr} • 💤 {sleep_hours}h sleep")
    else:
        lines.append(f"❤️ Resting HR: {resting_hr} • 💤 Sleep: N/A")
    
    # Line 3: Activity level and trends
    activity_level = data.get("activity_level", "Unknown")
    steps_trend = data.get("steps_trend", 0)
    if steps_trend > 0:
        trend = f"↑ +{steps_trend:.0f}% vs avg"
    elif steps_trend < 0:
        trend = f"↓ {steps_trend:.0f}% vs avg"
    else:
        trend = "→ flat"
    
    lines.append(f"🏃 {activity_level} • {trend}")
    
    return "\n".join(lines)


def _format_text_briefing(data, yesterday_activities=None, yesterday_azm=None, baseline=None):
    """Format detailed text briefing."""
    lines = []
    date = data.get("date", "Today")
    lines.append(f"📅 *Fitbit Morning Briefing — {date}*")
    lines.append("")
    
    # Yesterday's activities (if any)
    if yesterday_activities:
        lines.append("*Yesterday's Activity*")
        for act in yesterday_activities:
            name = act.get("name", "Unknown")
            duration_ms = act.get("duration", 0)
            duration_min = round(duration_ms / 60000, 1)
            calories = act.get("calories", 0)
            lines.append(f"  • {name}: {duration_min} min • {calories} cal")
        lines.append("")
    
    # Yesterday's Active Zone Minutes
    if yesterday_azm and yesterday_azm.get("activeZoneMinutes"):
        lines.append("*Yesterday's Active Zone Minutes*")
        total_azm = yesterday_azm.get("activeZoneMinutes", 0)
        fat_burn = yesterday_azm.get("fatBurnActiveZoneMinutes", 0)
        cardio = yesterday_azm.get("cardioActiveZoneMinutes", 0)
        peak = yesterday_azm.get("peakActiveZoneMinutes", 0)
        
        # Weekly goal tracking
        weekly_goal = 150
        daily_avg_needed = round(weekly_goal / 7, 1)
        
        lines.append(f"  • Total AZM: {total_azm} min (Daily avg needed: {daily_avg_needed}/day for 150/week)")
        if fat_burn:
            lines.append(f"  • Fat Burn zone: {fat_burn} min (1× credit)")
        if cardio:
            lines.append(f"  • Cardio zone: {cardio} min (2× credit)")
        if peak:
            lines.append(f"  • Peak zone: {peak} min (2× credit)")
        lines.append("")
        
        # Note: Cardio Load is not available via API
        # It's a Fitbit Premium feature visible only in the mobile app
    
    # Activity summary
    lines.append("*Activity*")
    steps = data.get("steps_today", 0)
    calories = data.get("calories_today", 0)
    floors = data.get("floors_today", 0)
    distance = data.get("distance_today", 0)
    active_minutes = data.get("active_minutes", 0)
    activity_level = data.get("activity_level", "Unknown")
    
    lines.append(f"  • Steps: {steps:,} / 10,000 goal")
    lines.append(f"  • Calories: {calories:,} burned")
    lines.append(f"  • Distance: {distance:.2f} km")
    lines.append(f"  • Floors: {floors}")
    lines.append(f"  • Active minutes: {active_minutes}")
    lines.append(f"  • Activity level: {activity_level}")
    lines.append("")
    
    # Heart Rate
    lines.append("*Heart Rate*")
    resting_hr = data.get("resting_hr", "N/A")
    avg_hr = data.get("avg_hr", "N/A")
    lines.append(f"  • Average HR: {avg_hr} bpm")
    lines.append(f"  • Resting HR: {resting_hr} bpm")
    
    hr_zones = data.get("hr_zones", {})
    if hr_zones:
        cardio = hr_zones.get("cardio", 0)
        peak = hr_zones.get("peak", 0)
        lines.append(f"  • Fat Burn: {hr_zones.get('fat_burn', 0)} min")
        lines.append(f"  • Cardio: {cardio} min")
        lines.append(f"  • Peak: {peak} min")
        lines.append(f"  • Active Zone: {cardio + peak} min")
    lines.append("")
    
    # Sleep
    lines.append("*Sleep*")
    sleep_hours = data.get("sleep_hours", "N/A")
    sleep_efficiency = data.get("sleep_efficiency", "N/A")
    awake_count = data.get("awake_count", "N/A")
    
    if sleep_hours and sleep_hours != "N/A":
        lines.append(f"  • Duration: {sleep_hours} hours")
    else:
        lines.append(f"  • Duration: No data")
    if sleep_efficiency and sleep_efficiency != "N/A":
        lines.append(f"  • Efficiency: {sleep_efficiency}%")
    lines.append(f"  • Awake episodes: {awake_count}")
    lines.append("")
    
    # Trends
    lines.append("*Trends (vs 7-day avg)*")
    steps_trend = data.get("steps_trend", 0)
    calories_trend = data.get("calories_trend", 0)
    
    if steps_trend > 0:
        lines.append(f"  • Steps: ↑ +{steps_trend:.0f}%")
    elif steps_trend < 0:
        lines.append(f"  • Steps: ↓ {steps_trend:.0f}%")
    else:
        lines.append(f"  • Steps: → flat")
    
    if calories_trend > 0:
        lines.append(f"  • Calories: ↑ +{calories_trend:.0f}%")
    elif calories_trend < 0:
        lines.append(f"  • Calories: ↓ {calories_trend:.0f}%")
    else:
        lines.append(f"  • Calories: → flat")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fitbit Morning Briefing")
    parser.add_argument("--date", help="Date for briefing (YYYY-MM-DD, default: today)")
    parser.add_argument("--format", choices=["text", "brief", "json"], default="text",
                       help="Output format (text=full briefing, brief=3 lines, json=structured)")
    
    args = parser.parse_args()
    
    try:
        # Initialize client
        client = FitbitClient()
        
        # Determine date
        if args.date:
            target_date = args.date
        else:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get data for target date
        steps_data = client.get_steps(target_date, target_date)
        calories_data = client.get_calories(target_date, target_date)
        activity_data = client.get_activity_summary(target_date, target_date)
        hr_data = client.get_heartrate(target_date, target_date)
        sleep_data = client.get_sleep(target_date, target_date)
        
        # Extract today's values
        today_steps = 0
        today_calories = 0
        today_distance = 0
        today_floors = 0
        today_active_minutes = 0
        resting_hr = None
        hr_zones = {}
        sleep_hours = None
        sleep_efficiency = None
        awake_count = None
        
        steps_list = steps_data.get("activities-steps", []) if steps_data else []
        calories_list = calories_data.get("activities-calories", []) if calories_data else []
        activity_list = [activity_data.get("summary", {})] if activity_data else []
        hr_list = hr_data.get("activities-heart", []) if hr_data else []
        
        if steps_list and len(steps_list) > 0:
            today_steps = int(steps_list[0].get("value", 0))
        if calories_list and len(calories_list) > 0:
            today_calories = int(calories_list[0].get("value", 0))
        if activity_list and len(activity_list) > 0:
            summary = activity_list[0]
            today_distance = summary.get("distance", 0)
            today_floors = summary.get("floors", 0)
            today_active_minutes = summary.get("veryActiveMinutes", 0) + summary.get("fairlyActiveMinutes", 0)
        if hr_list and len(hr_list) > 0:
            hr_value = hr_list[0].get("value", {})
            resting_hr = hr_value.get("restingHeartRate") if isinstance(hr_value, dict) else hr_value
            
            # Extract HR zones and calculate weighted average HR
            heart_rate_zones = hr_value.get("heartRateZones", []) if isinstance(hr_value, dict) else []
            hr_zones = {}
            total_minutes = 0
            weighted_hr_sum = 0
            
            for zone in heart_rate_zones:
                name = zone.get("name", "")
                minutes = zone.get("minutes", 0)
                max_hr = zone.get("max", 0)
                min_hr = zone.get("min", 0)
                
                if "Fat Burn" in name:
                    hr_zones["fat_burn"] = minutes
                    # Estimate avg HR in Fat Burn zone
                    weighted_hr_sum += ((min_hr + max_hr) / 2) * minutes
                    total_minutes += minutes
                elif "Cardio" in name:
                    hr_zones["cardio"] = minutes
                    weighted_hr_sum += ((min_hr + max_hr) / 2) * minutes
                    total_minutes += minutes
                elif "Peak" in name:
                    hr_zones["peak"] = minutes
                    weighted_hr_sum += ((min_hr + max_hr) / 2) * minutes
                    total_minutes += minutes
                elif "Out of Range" in name:
                    # Exclude from average (mostly resting/sedentary)
                    pass
            
            # Calculate average HR (weighted by time in each zone)
            if total_minutes > 0:
                avg_hr = round(weighted_hr_sum / total_minutes)
            else:
                avg_hr = resting_hr  # Fallback to resting HR
        else:
            resting_hr = None
            avg_hr = None
            hr_zones = {}
        sleep_list = sleep_data.get("sleep", []) if sleep_data else []
        if sleep_list and len(sleep_list) > 0:
            sleep_summary = sleep_list[0]
            sleep_duration = sleep_summary.get("duration", 0)
            sleep_hours = round(sleep_duration / 3600000, 1) if sleep_duration else None
            sleep_efficiency = sleep_summary.get("efficiency")
            awake_count = sleep_summary.get("minutesAwake")
        
        # Calculate trends vs 7-day average
        week_start = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
        week_steps = client.get_steps(week_start, target_date)
        week_calories = client.get_calories(week_start, target_date)
        
        week_steps_list = week_steps.get("activities-steps", []) if week_steps else []
        week_calories_list = week_calories.get("activities-calories", []) if week_calories else []
        
        avg_steps = 0
        avg_calories = 0
        valid_days = 0
        
        for entry in week_steps_list:
            val = entry.get("value", 0)
            # Skip today if it's partial
            if entry.get("dateTime") == target_date:
                continue
            avg_steps += int(val)
            valid_days += 1
        
        for entry in week_calories_list:
            if entry.get("dateTime") == target_date:
                continue
            avg_calories += int(entry.get("value", 0))
        
        if valid_days > 0:
            avg_steps = avg_steps // valid_days
            avg_calories = avg_calories // valid_days
            steps_trend = ((today_steps - avg_steps) / avg_steps * 100) if avg_steps > 0 else 0
            calories_trend = ((today_calories - avg_calories) / avg_calories * 100) if avg_calories > 0 else 0
        else:
            steps_trend = 0
            calories_trend = 0
        
        activity_level = _calculate_activity_level(today_steps, today_calories, today_active_minutes)
        
        # Get yesterday's activities
        yesterday = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_activities_raw = client._request(f"1/user/-/activities/date/{yesterday}.json")
        yesterday_activities = yesterday_activities_raw.get("activities", []) if yesterday_activities_raw else []
        
        # Get yesterday's Active Zone Minutes
        try:
            yesterday_azm_raw = client._request(f"1/user/-/activities/active-zone-minutes/date/{yesterday}/1d.json")
            azm_list = yesterday_azm_raw.get("activities-active-zone-minutes", []) if yesterday_azm_raw else []
            if azm_list and len(azm_list) > 0:
                yesterday_azm = azm_list[0].get("value", {})
            else:
                yesterday_azm = {}
        except Exception as e:
            logging.warning(f"Failed to fetch Active Zone Minutes for {yesterday}: {e}")
            yesterday_azm = {}
        
        # Build data dict
        data = {
            "date": target_date,
            "steps_today": today_steps,
            "calories_today": today_calories,
            "distance_today": today_distance,
            "floors_today": today_floors,
            "active_minutes": today_active_minutes,
            "activity_level": activity_level,
            "resting_hr": resting_hr,
            "avg_hr": avg_hr,
            "hr_zones": hr_zones,
            "sleep_hours": sleep_hours,
            "sleep_efficiency": sleep_efficiency,
            "awake_count": awake_count,
            "steps_trend": round(steps_trend, 1),
            "calories_trend": round(calories_trend, 1),
            "avg_steps_7d": avg_steps,
            "avg_calories_7d": avg_calories
        }
        
        # Format output
        if args.format == "json":
            print(json.dumps(data, indent=2))
        elif args.format == "brief":
            print(_format_brief_briefing(data))
        else:  # text
            print(_format_text_briefing(data, yesterday_activities=yesterday_activities, yesterday_azm=yesterday_azm))
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
