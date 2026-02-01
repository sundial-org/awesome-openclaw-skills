---
name: fitbit-analytics
description: Fitbit health and fitness data integration. Fetch steps, heart rate, sleep, activity, calories, and trends from Fitbit Web API. Generate automated health reports and alerts. Requires FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET, FITBIT_ACCESS_TOKEN, FITBIT_REFRESH_TOKEN.
metadata: {"openclaw":{"requires":{"bins":["python3"],"env":["FITBIT_CLIENT_ID","FITBIT_CLIENT_SECRET","FITBIT_ACCESS_TOKEN","FITBIT_REFRESH_TOKEN"]},"homepage":"https://github.com/kesslerio/fitbit-analytics-openclaw-skill"}}
---

# Fitbit Analytics

## Quick Start

```bash
# Set Fitbit API credentials
export FITBIT_CLIENT_ID="your_client_id"
export FITBIT_CLIENT_SECRET="your_client_secret"
export FITBIT_ACCESS_TOKEN="your_access_token"
export FITBIT_REFRESH_TOKEN="your_refresh_token"

# Generate morning briefing with Active Zone Minutes
python scripts/fitbit_briefing.py

# Fetch daily steps
python scripts/fitbit_api.py steps --days 7

# Get heart rate data
python scripts/fitbit_api.py heartrate --days 7

# Sleep summary
python scripts/fitbit_api.py sleep --days 7

# Generate weekly health report
python scripts/fitbit_api.py report --type weekly

# Get activity summary
python scripts/fitbit_api.py summary --days 7
```

## When to Use

Use this skill when:
- Fetching Fitbit metrics (steps, calories, heart rate, sleep)
- Analyzing activity trends over time
- Setting up alerts for inactivity or abnormal heart rate
- Generating daily/weekly health reports

## Core Workflows

### 1. Daily Briefing
```bash
# Generate morning health briefing (includes Active Zone Minutes)
python scripts/fitbit_briefing.py                    # Today's briefing
python scripts/fitbit_briefing.py --date 2026-01-20  # Specific date
python scripts/fitbit_briefing.py --format brief     # 3-line summary
python scripts/fitbit_briefing.py --format json      # JSON output

# Example output includes:
# - Yesterday's activities (logged exercises)
# - Yesterday's Active Zone Minutes (total, Fat Burn, Cardio, Peak)
# - Today's activity summary (steps, calories, floors, distance)
# - Heart rate (resting, average, zones)
# - Sleep (duration, efficiency, awake episodes)
# - Trends vs 7-day average
```

**Example JSON output:**
```json
{
  "date": "2026-01-21",
  "steps_today": 8543,
  "calories_today": 2340,
  "distance_today": 6.8,
  "floors_today": 12,
  "active_minutes": 47,
  "resting_hr": 58,
  "avg_hr": 72,
  "sleep_hours": 7.2,
  "sleep_efficiency": 89,
  "awake_minutes": 12,
  "yesterday_activities": [
    {"name": "Run", "duration": 35, "calories": 320}
  ],
  "yesterday_azm": {
    "activeZoneMinutes": 61,
    "fatBurnActiveZoneMinutes": 39,
    "cardioActiveZoneMinutes": 22
  }
}
```

**Note:** Cardio Load is NOT available via Fitbit API - it's a Fitbit Premium feature only visible in the mobile app.

### 2. Data Fetching (CLI)
```bash
# Available commands:
python scripts/fitbit_api.py steps --days 7
python scripts/fitbit_api.py calories --days 7
python scripts/fitbit_api.py heartrate --days 7
python scripts/fitbit_api.py sleep --days 7
python scripts/fitbit_api.py summary --days 7
python scripts/fitbit_api.py report --type weekly
```

### 3. Data Fetching (Python API)
```bash
export PYTHONPATH="{baseDir}/scripts"
python - <<'PY'
from fitbit_api import FitbitClient

client = FitbitClient()  # Uses env vars for credentials

# Fetch data (requires start_date and end_date)
steps_data = client.get_steps(start_date="2026-01-01", end_date="2026-01-16")
hr_data = client.get_heartrate(start_date="2026-01-01", end_date="2026-01-16")
sleep_data = client.get_sleep(start_date="2026-01-01", end_date="2026-01-16")
activity_summary = client.get_activity_summary(start_date="2026-01-01", end_date="2026-01-16")
PY
```

### 4. Analysis
```bash
export PYTHONPATH="{baseDir}/scripts"
python - <<'PY'
from fitbit_api import FitbitAnalyzer

analyzer = FitbitAnalyzer(steps_data, hr_data)
summary = analyzer.summary()
print(summary)  # Returns: avg_steps, avg_resting_hr, step_trend
PY
```

### 5. Alerts
```bash
python {baseDir}/scripts/alerts.py --days 7 --steps 8000 --sleep 7
```

## Scripts

- `scripts/fitbit_api.py` - Fitbit Web API wrapper, CLI, and analysis
- `scripts/fitbit_briefing.py` - Morning briefing CLI (text/brief/json output)
- `scripts/alerts.py` - Threshold-based notifications

## Available API Methods

| Method | Description |
|--------|-------------|
| `get_steps(start, end)` | Daily step counts |
| `get_calories(start, end)` | Daily calories burned |
| `get_distance(start, end)` | Daily distance |
| `get_activity_summary(start, end)` | Activity summary |
| `get_heartrate(start, end)` | Heart rate data |
| `get_sleep(start, end)` | Sleep data |
| `get_sleep_stages(start, end)` | Detailed sleep stages |
| `get_spo2(start, end)` | Blood oxygen levels |
| `get_weight(start, end)` | Weight measurements |
| `get_active_zone_minutes(start, end)` | Active Zone Minutes (AZM) breakdown |

## References

- `references/api.md` - Fitbit Web API documentation
- `references/metrics.md` - Metric definitions and interpretations

## Authentication

Fitbit API requires OAuth 2.0 authentication:
1. Create app at: https://dev.fitbit.com/apps
2. Get client_id and client_secret
3. Complete OAuth flow to get access_token and refresh_token
4. Set environment variables or pass to scripts

## Environment

Required:
- `FITBIT_CLIENT_ID`
- `FITBIT_CLIENT_SECRET`
- `FITBIT_ACCESS_TOKEN`
- `FITBIT_REFRESH_TOKEN`

## Automation (Cron Jobs)

Cron jobs are configured in OpenClaw's gateway, not in this repo. Add these to your OpenClaw setup:

### Daily Morning Briefing (8:00 AM)
```bash
openclaw cron add \
  --name "Morning Fitbit Health Report" \
  --cron "0 8 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --wake next-heartbeat \
  --deliver \
  --channel telegram \
  --target "<YOUR_TELEGRAM_CHAT_ID>" \
  --message "python3 /path/to/your/scripts/fitbit_briefing.py --format text"
```

**Note:** Replace `/path/to/your/` with your actual path and `<YOUR_TELEGRAM_CHAT_ID>` with your Telegram channel/group ID.
