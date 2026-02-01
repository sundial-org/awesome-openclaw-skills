#!/usr/bin/env python3
"""
Extended Garmin data fetching - training metrics, body composition, time-series data.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from garmin_auth import get_client


def fetch_training_readiness(client, date=None):
    """Fetch daily training readiness score."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_training_readiness(date)
        return {"training_readiness": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_training_status(client, date=None):
    """Fetch training status (load, VO2 max, etc.)."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_training_status(date)
        return {"training_status": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_body_composition(client, date=None):
    """Fetch body composition (weight, body fat %, muscle mass, etc.)."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_body_composition(date)
        return {"body_composition": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_weigh_ins(client, start_date=None, end_date=None):
    """Fetch weight measurements over time."""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_weigh_ins(start_date, end_date)
        return {"weigh_ins": data, "start": start_date, "end": end_date}
    except Exception as e:
        return {"error": str(e)}


def fetch_spo2(client, date=None):
    """Fetch blood oxygen (SPO2) data."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_spo2_data(date)
        return {"spo2": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_respiration(client, date=None):
    """Fetch respiration data throughout the day."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_respiration_data(date)
        return {"respiration": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_steps_detailed(client, date=None):
    """Fetch detailed step data."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_steps_data(date)
        return {"steps": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_floors(client, date=None):
    """Fetch floors climbed data."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_floors(date)
        return {"floors": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_intensity_minutes(client, date=None):
    """Fetch intensity minutes (vigorous/moderate activity)."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_intensity_minutes_data(date)
        return {"intensity_minutes": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_hydration(client, date=None):
    """Fetch hydration/water intake data."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_hydration_data(date)
        return {"hydration": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_all_day_stress(client, date=None):
    """Fetch detailed stress data throughout the day (time-series)."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_all_day_stress(date)
        return {"stress_detailed": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_max_metrics(client, date=None):
    """Fetch max metrics (VO2 max, etc.)."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        data = client.get_max_metrics(date)
        return {"max_metrics": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def fetch_fitness_age(client):
    """Fetch fitness age data."""
    try:
        data = client.get_fitnessage_data()
        return {"fitness_age": data}
    except Exception as e:
        return {"error": str(e)}


def fetch_endurance_score(client):
    """Fetch endurance score."""
    try:
        data = client.get_endurance_score()
        return {"endurance_score": data}
    except Exception as e:
        return {"error": str(e)}


def fetch_hill_score(client):
    """Fetch hill score."""
    try:
        data = client.get_hill_score()
        return {"hill_score": data}
    except Exception as e:
        return {"error": str(e)}


def fetch_intraday_heart_rate(client, date=None):
    """Fetch heart rate data throughout the day with timestamps."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # get_heart_rates returns time-series data
        data = client.get_heart_rates(date)
        return {"heart_rate_intraday": data, "date": date}
    except Exception as e:
        return {"error": str(e), "date": date}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch extended Garmin health data")
    parser.add_argument("metric", choices=[
        "training_readiness", "training_status", "body_composition", 
        "weigh_ins", "spo2", "respiration", "steps", "floors", 
        "intensity_minutes", "hydration", "stress_detailed", 
        "max_metrics", "fitness_age", "endurance_score", "hill_score",
        "hr_intraday"
    ], help="Type of data to fetch")
    parser.add_argument("--date", help="Date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--start", help="Start date for date ranges (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date for date ranges (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    client = get_client()
    if not client:
        print('{"error": "Not authenticated"}')
        sys.exit(1)
    
    # Route to appropriate function
    if args.metric == "training_readiness":
        result = fetch_training_readiness(client, args.date)
    elif args.metric == "training_status":
        result = fetch_training_status(client, args.date)
    elif args.metric == "body_composition":
        result = fetch_body_composition(client, args.date)
    elif args.metric == "weigh_ins":
        result = fetch_weigh_ins(client, args.start, args.end)
    elif args.metric == "spo2":
        result = fetch_spo2(client, args.date)
    elif args.metric == "respiration":
        result = fetch_respiration(client, args.date)
    elif args.metric == "steps":
        result = fetch_steps_detailed(client, args.date)
    elif args.metric == "floors":
        result = fetch_floors(client, args.date)
    elif args.metric == "intensity_minutes":
        result = fetch_intensity_minutes(client, args.date)
    elif args.metric == "hydration":
        result = fetch_hydration(client, args.date)
    elif args.metric == "stress_detailed":
        result = fetch_all_day_stress(client, args.date)
    elif args.metric == "max_metrics":
        result = fetch_max_metrics(client, args.date)
    elif args.metric == "fitness_age":
        result = fetch_fitness_age(client)
    elif args.metric == "endurance_score":
        result = fetch_endurance_score(client)
    elif args.metric == "hill_score":
        result = fetch_hill_score(client)
    elif args.metric == "hr_intraday":
        result = fetch_intraday_heart_rate(client, args.date)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
