# Fitbit Analytics Skill for OpenClaw 🦞

[![OpenClaw Community Skill](https://img.shields.io/badge/openclaw-community%20skill-blue)](https://github.com/openclaw/openclaw)
[![ClawdHub Listed](https://img.shields.io/badge/clawdhub-listed-green)](https://clawdhub.com/skills/fitbit-analytics)

Fitbit health and fitness data integration for OpenClaw. Fetch steps, heart rate, sleep, activity, calories, and trends from Fitbit Web API. Generate automated health reports, correlations, and alerts.

## Features

- **Activity Tracking**: Fetch daily steps, distance, calories, and active minutes.
- **Heart Rate**: Access continuous heart rate data and resting heart rate trends.
- **Sleep Analytics**: Analyze sleep stages (Deep, Light, REM, Wake) and efficiency.
- **Reports**: Generate daily/weekly health reports with trend analysis.
- **Automation**: Scripts ready for cron jobs (e.g., daily summaries).

## Setup

### 1. Create a Fitbit Developer App
1.  Go to [dev.fitbit.com/apps](https://dev.fitbit.com/apps) and log in.
2.  Click **"Register an App"**.
3.  Fill in the details:
    *   **Application Name:** `Personal Assistant` (or your choice)
    *   **Description:** `Personal AI analytics.`
    *   **OAuth 2.0 Application Type:** `Personal`
    *   **Redirect URL:** `http://localhost:8080/`
    *   **Default Access Type:** `Read & Write`
4.  **Save** and note your **Client ID** and **Client Secret**.

### 2. Configure Credentials
Add keys to your `secrets.conf` or environment variables:
```bash
export FITBIT_CLIENT_ID="YOUR_CLIENT_ID"
export FITBIT_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

### 3. Authorization Flow
1.  Construct the URL:
    ```
    https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800
    ```
2.  Authorize in browser.
3.  Copy the `code` from the redirect URL (`http://localhost:8080/?code=...`).
4.  Exchange code for tokens:
    ```bash
    curl -X POST https://api.fitbit.com/oauth2/token \
      -u "CLIENT_ID:CLIENT_SECRET" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "grant_type=authorization_code" \
      -d "code=YOUR_CODE" \
      -d "redirect_uri=http://localhost:8080/"
    ```
5.  Save `access_token` and `refresh_token` to `FITBIT_ACCESS_TOKEN` and `FITBIT_REFRESH_TOKEN`.

## Usage

> Note: For Python imports, set `PYTHONPATH` to the `scripts/` folder:
>
> ```bash
> export PYTHONPATH="$(pwd)/scripts"
> ```

### Fetch Daily Stats
```bash
# Get steps for today
python scripts/fitbit_api.py steps --days 1

# Get sleep data
python scripts/fitbit_api.py sleep --days 1
```

### Generate Weekly Report
```bash
python scripts/fitbit_api.py report --type weekly
```

### Daily Morning Briefing
```bash
# Text format (for Telegram)
python scripts/fitbit_briefing.py --format text

# Brief format (3-line summary)
python scripts/fitbit_briefing.py --format brief

# JSON format (for programmatic use)
python scripts/fitbit_briefing.py --format json
```

**Example brief output:**
```
📊 8,543 steps • 2,340 cal
❤️ Resting HR: 58 • 💤 7.2h sleep
🏃 Moderate • ↑ 12% vs avg
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
  "activity_level": "Moderate",
  "steps_trend": 12,
  "yesterday_azm": {
    "activeZoneMinutes": 61,
    "fatBurnActiveZoneMinutes": 39,
    "cardioActiveZoneMinutes": 22
  }
}
```

## Structure
- `scripts/fitbit_api.py`: Main API wrapper and CLI tool.
- `scripts/fitbit_briefing.py`: Morning briefing CLI (text/brief/json output).
- `scripts/alerts.py`: Threshold-based notifications.
- `references/`: API and metrics documentation.
- `docs/`: Privacy Policy and Terms of Service.

## License
Apache 2.0
