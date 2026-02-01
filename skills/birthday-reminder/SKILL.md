---
name: birthday-reminder
description: Manage birthdays with natural language. Store birthdays in /home/clawd/clawd/data/birthdays.md, get upcoming reminders, calculate ages. Use when the user mentions birthdays, wants to add/remember someone's birthday, check upcoming birthdays, or asks about someone's age/birthday. Understands phrases like "X hat am DD.MM. Geburtstag", "Wann hat X Geburtstag?", "Nächste Geburtstage".
---

# Birthday Reminder Skill

Manage birthdays naturally. Store in `data/birthdays.md`, query with natural language.

## Storage

Birthdays are stored in `/home/clawd/clawd/data/birthdays.md`:

```markdown
# Geburtstage

- **Valentina** - 14.02.2000 (wird 26)
- **Max** - 15.03.1990
```

## Natural Language Patterns

### Adding Birthdays
When user says things like:
- "Valentina hat am 14. Februar Geburtstag"
- "Füge hinzu: Max, 15.03.1990"
- "X wurde am 10.05.1985 geboren"

**Action:**
1. Parse name and date
2. Extract year if provided
3. Calculate upcoming age: `birthday_year - birth_year`
4. Append to `/home/clawd/clawd/data/birthdays.md`
5. Confirm with age info

### Querying Birthdays
When user asks:
- "Wann hat Valentina Geburtstag?"
- "Welche Geburtstage kommen als Nächstes?"
- "Wie alt wird Valentina?"
- "Nächster Geburtstag"

**Action:**
1. Read `/home/clawd/clawd/data/birthdays.md`
2. Parse all entries
3. Calculate days until each birthday
4. Sort by upcoming date
5. Show age turning if year is known

### Listing All
When user says:
- "Zeige alle Geburtstage"
- "Liste meine Geburtstage"

**Action:**
1. Read the file
2. Show formatted list with days until each

## Date Parsing

Support various formats:
- "14. Februar" → 14.02
- "14.02." → 14.02
- "14.02.2000" → 14.02.2000
- "14.2.2000" → 14.02.2000

## Age Calculation

```python
from datetime import datetime

def calculate_turning_age(birth_year, birthday_month, birthday_day):
    today = datetime.now()
    birthday_this_year = today.replace(month=birthday_month, day=birthday_day)
    
    if today.date() <= birthday_this_year.date():
        birthday_year = today.year
    else:
        birthday_year = today.year + 1
    
    return birthday_year - birth_year
```

## Days Until Birthday

```python
def days_until(month, day):
    today = datetime.now()
    birthday = today.replace(month=month, day=day)
    if birthday < today:
        birthday = birthday.replace(year=today.year + 1)
    return (birthday - today).days
```

## Automatic Reminders

For cron/reminders, check birthdays daily and notify if:
- 7 days before
- 1 day before  
- On the day

Use the `check_reminders()` logic from `scripts/reminder.py`.

## File Format

Each line: `- **Name** - DD.MM.YYYY (wird X)` or `- **Name** - DD.MM.`

Keep the file sorted by date (month/day) for easier reading.
