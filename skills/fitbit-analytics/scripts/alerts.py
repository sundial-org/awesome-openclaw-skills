#!/usr/bin/env python3
"""
Fitbit Alerts - Threshold-based notifications

Usage:
    python alerts.py --days 7 --steps 8000 --sleep 7
"""

import os
import json
from datetime import datetime, timedelta

try:
    from fitbit_api import FitbitClient
except ImportError:
    from scripts.fitbit_api import FitbitClient


class FitbitAlerts:
    """Alert on threshold breaches"""
    
    DEFAULT_THRESHOLDS = {
        "steps": 8000,
        "calories": 1800,
        "sleep_hours": 7,
        "resting_hr_high": 80,
        "resting_hr_low": 45,
        "active_minutes": 30,
        "sedentary_hours": 10
    }
    
    def __init__(self, thresholds=None):
        self.thresholds = {**self.DEFAULT_THRESHOLDS, **(thresholds or {})}
    
    def _safe_float(self, value, default=0):
        """Safely convert Fitbit string values to float"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def _safe_int(self, value, default=0):
        """Safely convert Fitbit string values to int"""
        try:
            return int(float(value)) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def check_steps(self, steps_value):
        """Check daily steps"""
        steps = self._safe_int(steps_value)
        if steps < self.thresholds["steps"]:
            return f"Low steps: {steps:,} (< {self.thresholds['steps']:,})"
        return None
    
    def check_sleep(self, sleep_minutes):
        """Check sleep duration"""
        minutes = self._safe_float(sleep_minutes)
        sleep_hours = minutes / 60
        if sleep_hours < self.thresholds["sleep_hours"]:
            return f"Low sleep: {sleep_hours:.1f}h (< {self.thresholds['sleep_hours']}h)"
        return None
    
    def check_resting_hr(self, rhr):
        """Check resting heart rate"""
        hr = self._safe_int(rhr)
        if hr > self.thresholds["resting_hr_high"]:
            return f"Elevated RHR: {hr} bpm (> {self.thresholds['resting_hr_high']})"
        if hr < self.thresholds["resting_hr_low"] and hr > 0:
            return f"Low RHR: {hr} bpm (< {self.thresholds['resting_hr_low']})"
        return None
    
    def find_low_days(self, steps_data, sleep_data=None, hr_data=None):
        """
        Find all days below thresholds.
        
        Checks multiple signals:
        - Steps below threshold
        - Sleep duration below threshold
        - Resting HR above/below thresholds
        
        Returns list of alert dicts with date, type, and alert message.
        """
        alerts = []
        
        # Build lookup dicts for sleep and HR by date
        sleep_by_date = {}
        hr_by_date = {}
        
        if sleep_data:
            for entry in sleep_data.get("sleep", []):
                date = entry.get("dateOfSleep")
                if date:
                    sleep_by_date[date] = entry.get("minutesAsleep", 0)
        
        if hr_data:
            for entry in hr_data.get("activities-heart", []):
                date = entry.get("dateTime")
                rhr = entry.get("value", {}).get("restingHeartRate")
                if date and rhr:
                    hr_by_date[date] = rhr
        
        # Process steps and cross-reference with other signals
        for day in steps_data.get("activities-steps", []):
            date = day.get("dateTime")
            steps_value = day.get("value", 0)
            
            day_alerts = []
            
            # Check steps
            step_alert = self.check_steps(steps_value)
            if step_alert:
                day_alerts.append({"type": "steps", "alert": step_alert})
            
            # Check sleep for this date
            if date in sleep_by_date:
                sleep_alert = self.check_sleep(sleep_by_date[date])
                if sleep_alert:
                    day_alerts.append({"type": "sleep", "alert": sleep_alert})
            
            # Check HR for this date
            if date in hr_by_date:
                hr_alert = self.check_resting_hr(hr_by_date[date])
                if hr_alert:
                    day_alerts.append({"type": "resting_hr", "alert": hr_alert})
            
            # Add alerts for this day
            for alert in day_alerts:
                alerts.append({"date": date, **alert})
        
        # Multi-signal detection: flag days with multiple issues
        dates_with_issues = {}
        for alert in alerts:
            date = alert["date"]
            dates_with_issues[date] = dates_with_issues.get(date, 0) + 1
        
        # Mark critical days (2+ signals)
        for alert in alerts:
            if dates_with_issues[alert["date"]] >= 2:
                alert["severity"] = "warning"
            else:
                alert["severity"] = "info"
        
        return alerts
    
    def get_recovery_status(self, steps_data, sleep_data, hr_data):
        """
        Get overall recovery status based on multiple signals.
        
        Returns: 'green', 'yellow', or 'red'
        """
        alerts = self.find_low_days(steps_data, sleep_data, hr_data)
        
        if not alerts:
            return "green"
        
        # Check most recent day
        recent_alerts = [a for a in alerts if a.get("severity") == "warning"]
        if recent_alerts:
            return "red"
        
        return "yellow"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fitbit Alerts")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--steps", type=int, default=8000)
    parser.add_argument("--sleep", type=float, default=7)
    parser.add_argument("--resting-hr", type=int, default=80)
    parser.add_argument("--client-id", help="Fitbit client ID")
    parser.add_argument("--client-secret", help="Fitbit client secret")
    parser.add_argument("--access-token", help="Fitbit access token")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    client = FitbitClient(
        client_id=args.client_id,
        client_secret=args.client_secret,
        access_token=args.access_token
    )
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    steps = client.get_steps(start_date, end_date)
    sleep = client.get_sleep(start_date, end_date)
    hr = client.get_heartrate(start_date, end_date)
    
    alerts_checker = FitbitAlerts({
        "steps": args.steps,
        "sleep_hours": args.sleep,
        "resting_hr_high": args.resting_hr
    })
    
    low_days = alerts_checker.find_low_days(steps, sleep, hr)
    
    if args.json:
        print(json.dumps({"alerts": low_days}, indent=2))
    elif low_days:
        print("⚠️  Fitbit Alerts:")
        for day in low_days:
            severity_icon = "🔴" if day.get("severity") == "warning" else "⚠️"
            print(f"  {severity_icon} {day['date']}: {day['alert']}")
    else:
        print("✅ All metrics above thresholds")
    
    return low_days


if __name__ == "__main__":
    main()
