#!/usr/bin/env python3
"""
Birthday reminder script for cron jobs.
Checks for upcoming birthdays and outputs reminder messages.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

BIRTHDAYS_FILE = Path("/home/clawd/clawd/data/birthdays.json")

def load_birthdays():
    if not BIRTHDAYS_FILE.exists():
        return {}
    return json.loads(BIRTHDAYS_FILE.read_text())

def days_until_birthday(day, month):
    today = datetime.now()
    birthday = today.replace(month=month, day=day)
    if birthday < today:
        birthday = birthday.replace(year=today.year + 1)
    return (birthday - today).days

def calculate_age(year_born, target_year):
    if not year_born:
        return None
    return target_year - year_born

def check_reminders():
    birthdays = load_birthdays()
    if not birthdays:
        return []
    
    today = datetime.now()
    reminders = []
    
    for name, data in birthdays.items():
        days_left = days_until_birthday(data["day"], data["month"])
        
        # Reminder: 7 days before and 1 day before
        if days_left in [7, 1, 0]:
            target_year = today.year + (1 if days_left < 365 else 0)
            age = calculate_age(data.get("year"), target_year)
            turning = age + 1 if age else None
            
            reminders.append({
                "name": name,
                "days_left": days_left,
                "turning": turning,
                "date": f"{data['day']:02d}.{data['month']:02d}."
            })
    
    return reminders

def main():
    reminders = check_reminders()
    
    if not reminders:
        sys.exit(0)
    
    # Output for messaging
    for r in reminders:
        age_str = f" (wird {r['turning']})" if r['turning'] else ""
        if r["days_left"] == 0:
            print(f"🎉 Geburtstagserinnerung: **{r['name']}** hat HEUTE Geburtstag{age_str}!")
        elif r["days_left"] == 1:
            print(f"🎈 Geburtstagserinnerung: **{r['name']}** hat morgen Geburtstag{age_str}!")
        elif r["days_left"] == 7:
            print(f"📅 Geburtstagserinnerung: **{r['name']}** hat in einer Woche Geburtstag{age_str} ({r['date']})!")

if __name__ == "__main__":
    main()
