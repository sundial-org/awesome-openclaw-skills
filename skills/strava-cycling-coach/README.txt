# Strava Cycling Performance Analysis Skill

Automatically track and analyze your Strava cycling rides with detailed power, heart rate, and performance insights.

## Features

- **Automatic Monitoring**: Checks for new rides every 30 minutes
- **Detailed Analysis**: Power metrics (avg, normalized, max, VI)
- **Heart Rate Zones**: Time in each zone with percentages
- **PR Tracking**: Only reports actual improvements (not first-time segments)
- **Training Load**: TSS estimation and suffer score
- **Local Caching**: Efficient API usage with local activity cache
- **Telegram Notifications**: Get analysis messages after each ride

## What You Get After Each Ride

- Power analysis (average, normalized, max, variability index)
- Heart rate zone distribution
- Personal records (only actual improvements)
- Training stress score (TSS) estimation
- Performance insights and comparisons
- Elevation and cadence stats

## Requirements

- Strava account with activity data
- Strava API application (free to create)
- Python 3.7+ with requests library
- Cron (for automatic monitoring)
- Optional: Telegram for notifications

## Quick Start

1. Create Strava API app at https://www.strava.com/settings/api
2. Run `./scripts/setup.sh` and follow prompts
3. Complete OAuth with `./scripts/complete_auth.py CODE`
4. Test with `./scripts/analyze_rides.py --days 30`
5. Optional: Set up cron job for automatic monitoring

## Configuration

- Config: `~/.config/strava/config.json`
- Cache: `~/.cache/strava/activities.json`
- Logs: `~/.cache/strava/monitor.log`

## Notes

- First 100 activities are cached on initial setup
- Respects Strava API rate limits (100/15min, 1000/day)
- PRs only reported for segments you've ridden before
- Heart rate zones calculated based on max HR from activities
- FTP can be customized via --ftp flag

## Support

For issues or questions, visit: https://github.com/clawdbot/clawdbot
