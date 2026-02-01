---
name: strava-cycling-coach
description: Track and analyze cycling performance from Strava. Use when analyzing ride data, reviewing fitness trends, understanding workout performance, or providing insights on cycling training. Automatically monitors new rides and provides performance analysis.
---

# Strava Cycling Coach

Track cycling performance, analyze rides, and monitor fitness progression using the Strava API.

## Setup

### 1. Create Strava API Application

Visit https://www.strava.com/settings/api and create an application:
- Application Name: Clawdbot (or your preferred name)
- Category: Data Importer
- Club: (leave blank)
- Website: http://localhost
- Authorization Callback Domain: localhost

Save your **Client ID** and **Client Secret**.

### 2. Run Setup Script

```bash
cd skills/strava
./scripts/setup.sh
```

You'll be prompted for:
1. Client ID
2. Client Secret
3. Visit an OAuth URL to authorize
4. Copy the authorization code and complete setup with:

```bash
./scripts/complete_auth.py YOUR_CODE_HERE
```

### 3. Configure Automatic Monitoring (Optional)

To receive automatic ride analysis after each workout:

```bash
# Set your Telegram chat ID
export STRAVA_TELEGRAM_CHAT_ID="your_telegram_chat_id"

# Add to your shell profile for persistence
echo 'export STRAVA_TELEGRAM_CHAT_ID="your_telegram_chat_id"' >> ~/.bashrc

# Set up cron job (checks every 30 minutes)
crontab -l > /tmp/cron_backup.txt
echo "*/30 * * * * $(pwd)/scripts/auto_analyze_new_rides.sh" >> /tmp/cron_backup.txt
crontab /tmp/cron_backup.txt
```

### 4. Test the Setup

Analyze your recent rides:
```bash
./scripts/analyze_rides.py --days 90 --ftp YOUR_FTP
```

## Usage

Get latest ride:
```bash
scripts/get_latest_ride.py
```

Analyze specific ride:
```bash
scripts/analyze_ride.py <activity-id>
```

Monitor for new rides (runs in background):
```bash
scripts/monitor_rides.sh
```

## Automatic Monitoring

The skill can automatically:
1. Check for new rides every 30 minutes
2. Analyze power, heart rate, and training load
3. Send insights about performance and fitness trends
4. Compare to recent training history

## Metrics Analyzed

- **Power**: Average, normalized, max, variability index
- **Heart rate**: Average, max, time in zones
- **Training load**: TSS estimation, intensity factor
- **Fitness progression**: Trends over time
- **Segments**: PR achievements and efforts
- **Comparative**: vs recent rides, vs personal bests

## Configuration

Edit `~/.config/strava/config.json` to customize:
- Monitoring frequency
- Analysis preferences
- Notification settings

## API Reference

See [references/api.md](references/api.md) for complete Strava API documentation.
