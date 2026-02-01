#!/usr/bin/env python3
"""
Birthday Reminder Skill - Main script for managing birthdays.
Usage:
  python3 birthday.py add "Name" DD.MM.YYYY [--year-born YYYY]
  python3 birthday.py list [--upcoming] [--days N]
  python3 birthday.py next
  python3 birthday.py remove "Name"
  python3 birthday.py check
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

BIRTHDAYS_FILE = Path("/home/clawd/clawd/data/birthdays.json")

def ensure_file():
    """Ensure the birthdays file exists."""
    BIRTHDAYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not BIRTHDAYS_FILE.exists():
        BIRTHDAYS_FILE.write_text(json.dumps({}, indent=2))

def load_birthdays():
    """Load birthdays from JSON file."""
    ensure_file()
    return json.loads(BIRTHDAYS_FILE.read_text())

def save_birthdays(data):
    """Save birthdays to JSON file."""
    BIRTHDAYS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def parse_date(date_str):
    """Parse DD.MM or DD.MM.YYYY format."""
    try:
        if len(date_str.split('.')) == 3:
            return datetime.strptime(date_str, "%d.%m.%Y")
        else:
            return datetime.strptime(date_str, "%d.%m")
    except ValueError:
        return None

def add_birthday(name, date_str, year_born=None):
    """Add a new birthday."""
    birthdays = load_birthdays()
    date = parse_date(date_str)
    if not date:
        print(f"❌ Ungültiges Datum: {date_str}. Verwende DD.MM. oder DD.MM.YYYY")
        return False
    
    birthdays[name] = {
        "day": date.day,
        "month": date.month,
        "year": year_born
    }
    save_birthdays(birthdays)
    print(f"✅ Geburtstag gespeichert: {name} - {date.day:02d}.{date.month:02d}." + (f"{year_born}" if year_born else ""))
    return True

def calculate_age(year_born, target_date=None, birthday_month=None, birthday_day=None):
    """Calculate age for a given year."""
    if not year_born:
        return None
    target = target_date or datetime.now()
    age = target.year - year_born
    # Check if birthday has occurred this year
    if birthday_month and birthday_day:
        birthday_this_year = target.replace(month=birthday_month, day=birthday_day)
        # If birthday hasn't occurred yet this year, subtract 1
        if target.date() < birthday_this_year.date():
            age -= 1
    return age

def days_until_birthday(day, month):
    """Calculate days until next birthday."""
    today = datetime.now()
    birthday = today.replace(month=month, day=day)
    if birthday < today:
        birthday = birthday.replace(year=today.year + 1)
    return (birthday - today).days

def list_birthdays(upcoming_only=False, days=30):
    """List all birthdays, optionally only upcoming ones."""
    birthdays = load_birthdays()
    if not birthdays:
        print("📭 Keine Geburtstage gespeichert.")
        return
    
    today = datetime.now()
    items = []
    
    for name, data in birthdays.items():
        days_left = days_until_birthday(data["day"], data["month"])
        # Calculate age turning
        year_born = data.get("year")
        if year_born:
            # Determine the year of the upcoming birthday
            # If birthday is later this year -> this year
            # If birthday was earlier this year -> next year
            birthday_this_year = today.replace(month=data["month"], day=data["day"])
            if today.date() <= birthday_this_year.date():
                birthday_year = today.year
            else:
                birthday_year = today.year + 1
            turning = birthday_year - year_born
        else:
            turning = None
        
        if upcoming_only and days_left > days:
            continue
            
        items.append({
            "name": name,
            "date": f"{data['day']:02d}.{data['month']:02d}.",
            "days_left": days_left,
            "turning": turning
        })
    
    # Sort by days left
    items.sort(key=lambda x: x["days_left"])
    
    print("🎂 **Geburtstage:**\n")
    for item in items:
        age_str = f" (wird {item['turning']})" if item["turning"] else ""
        if item["days_left"] == 0:
            print(f"🎉 **{item['name']}** - {item['date']}{age_str} - **HEUTE!**")
        elif item["days_left"] == 1:
            print(f"🎈 {item['name']} - {item['date']}{age_str} - morgen")
        else:
            print(f"📅 {item['name']} - {item['date']}{age_str} - in {item['days_left']} Tagen")

def next_birthday():
    """Show the next upcoming birthday."""
    birthdays = load_birthdays()
    if not birthdays:
        print("📭 Keine Geburtstage gespeichert.")
        return
    
    today = datetime.now()
    closest = None
    closest_days = 366
    
    for name, data in birthdays.items():
        days_left = days_until_birthday(data["day"], data["month"])
        if days_left < closest_days:
            closest_days = days_left
            closest = (name, data, days_left)
    
    if closest:
        name, data, days_left = closest
        year_born = data.get("year")
        if year_born:
            # Determine the year of the upcoming birthday
            birthday_this_year = today.replace(month=data["month"], day=data["day"])
            if today.date() <= birthday_this_year.date():
                birthday_year = today.year
            else:
                birthday_year = today.year + 1
            turning = birthday_year - year_born
        else:
            turning = None
        age_str = f" (wird {turning})" if turning else ""
        
        if days_left == 0:
            print(f"🎉 **{name}** hat HEUTE Geburtstag{age_str}! 🎂")
        elif days_left == 1:
            print(f"🎈 **{name}** hat morgen Geburtstag{age_str}!")
        else:
            print(f"📅 **{name}** hat in {days_left} Tagen Geburtstag{age_str} ({data['day']:02d}.{data['month']:02d}.)!")

def check_reminders(days_ahead=7):
    """Check for upcoming birthdays (for cron jobs)."""
    birthdays = load_birthdays()
    today = datetime.now()
    reminders = []
    
    for name, data in birthdays.items():
        days_left = days_until_birthday(data["day"], data["month"])
        if days_left <= days_ahead:
            age = calculate_age(data.get("year"), today.replace(year=today.year + (1 if days_left < 365 else 0)))
            turning = age + 1 if age else None
            reminders.append({
                "name": name,
                "days_left": days_left,
                "turning": turning,
                "date": f"{data['day']:02d}.{data['month']:02d}."
            })
    
    return reminders

def remove_birthday(name):
    """Remove a birthday."""
    birthdays = load_birthdays()
    if name in birthdays:
        del birthdays[name]
        save_birthdays(birthdays)
        print(f"✅ Geburtstag für {name} entfernt.")
        return True
    else:
        print(f"❌ Kein Geburtstag für {name} gefunden.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Birthday Reminder")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a birthday")
    add_parser.add_argument("name", help="Name of the person")
    add_parser.add_argument("date", help="Date (DD.MM. or DD.MM.YYYY)")
    add_parser.add_argument("--year-born", type=int, help="Year of birth (for age calculation)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List birthdays")
    list_parser.add_argument("--upcoming", action="store_true", help="Only show upcoming birthdays")
    list_parser.add_argument("--days", type=int, default=30, help="Days to look ahead")
    
    # Next command
    subparsers.add_parser("next", help="Show next birthday")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a birthday")
    remove_parser.add_argument("name", help="Name of the person")
    
    # Check command (for cron)
    check_parser = subparsers.add_parser("check", help="Check for reminders")
    check_parser.add_argument("--days", type=int, default=7, help="Days ahead to check")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_birthday(args.name, args.date, args.year_born)
    elif args.command == "list":
        list_birthdays(args.upcoming, args.days)
    elif args.command == "next":
        next_birthday()
    elif args.command == "remove":
        remove_birthday(args.name)
    elif args.command == "check":
        reminders = check_reminders(args.days)
        for r in reminders:
            age_str = f" (wird {r['turning']})" if r['turning'] else ""
            if r["days_left"] == 0:
                print(f"🎉 {r['name']} hat HEUTE Geburtstag{age_str}!")
            elif r["days_left"] == 1:
                print(f"🎈 {r['name']} hat morgen Geburtstag{age_str}!")
            else:
                print(f"📅 {r['name']} hat in {r['days_left']} Tagen Geburtstag{age_str}!")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
