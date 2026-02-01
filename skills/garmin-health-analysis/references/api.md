# Garmin Connect API Reference (Unofficial)

This documents the unofficial Garmin Connect API accessed via the `garminconnect` Python library.

## Important Notes

- **Unofficial API**: Garmin does not provide a public API for personal use. This library reverse-engineers their web interface.
- **May break**: Garmin can change their API anytime, which may break the library
- **Rate limits**: Garmin implements rate limiting; excessive requests may temporarily block your account
- **Official alternative**: Garmin Health API exists for enterprise partnerships only

## Authentication

### Library: `garminconnect`
```bash
pip3 install garminconnect
```

### Authentication Flow
1. Login with email/password
2. Library handles OAuth token exchange
3. Tokens stored for session persistence
4. Tokens auto-refresh when expired

### Session Management
```python
from garminconnect import Garmin

# Initial login
client = Garmin(email, password)
client.login()

# Save tokens for reuse
oauth1 = client.garth.oauth1_token
oauth2 = client.garth.oauth2_token

# Restore session
client = Garmin()
client.garth.oauth1_token = oauth1
client.garth.oauth2_token = oauth2
```

## Core Endpoints

### User Profile
```python
# Full name
client.get_full_name()

# User summary (daily stats)
client.get_user_summary("2026-01-25")
```

### Sleep Data
```python
# Daily sleep details
client.get_sleep_data("2026-01-25")
```

**Response structure:**
```json
{
  "sleepTimeSeconds": 28800,      // Total sleep duration
  "deepSleepSeconds": 7200,       // Deep sleep
  "lightSleepSeconds": 14400,     // Light sleep
  "remSleepSeconds": 7200,        // REM sleep
  "awakeSleepSeconds": 1800,      // Awake time
  "sleepScores": {
    "overall": {"value": 85},     // Overall sleep score (0-100)
    "duration": {...},
    "quality": {...}
  },
  "restlessMoments": 12,          // Number of restless periods
  "avgSleepHeartRate": 52,        // Average HR during sleep
  "avgSleepHRV": 45,              // Average HRV during sleep
  "avgSleepRespiration": 14       // Respiration rate (breaths/min)
}
```

### HRV Data
```python
# Daily HRV summary
client.get_hrv_data("2026-01-25")
```

**Response structure:**
```json
{
  "hrvSummary": {
    "lastNightAvg": 45,             // Last night's average HRV (ms)
    "lastNight5MinHigh": 68,        // 5-min high
    "lastNight5MinLow": 28,         // 5-min low
    "weeklyAvg": 42,                // 7-day rolling average
    "baselineBalancedLow": 38,      // Personal baseline low
    "baselineBalancedHigh": 48,     // Personal baseline high
    "status": "BALANCED"            // Status: BALANCED, UNBALANCED, POOR, LOW
  }
}
```

### Body Battery
```python
# Daily Body Battery readings (time series)
client.get_body_battery("2026-01-25")
```

**Response structure:**
```json
[
  {
    "timestamp": 1737849600000,     // Unix timestamp (ms)
    "value": 85,                    // Body Battery level (0-100)
    "charged": 45,                  // Amount charged overnight
    "drained": 15                   // Amount drained from previous
  },
  // ... more readings throughout the day
]
```

### Heart Rate
```python
# Daily heart rate summary
client.get_heart_rates("2026-01-25")
```

**Response structure:**
```json
{
  "restingHeartRate": 52,           // Resting HR (bpm)
  "maxHeartRate": 165,              // Max HR of the day
  "minHeartRate": 48                // Min HR of the day
}
```

### Stress Levels
```python
# Daily stress data
client.get_stress_data("2026-01-25")
```

**Response structure:**
```json
{
  "avgStressLevel": 35,             // Average all-day stress (0-100)
  "maxStressLevel": 78,             // Peak stress
  "restStressLevel": 15,            // Stress during rest
  "activityStressLevel": 65,        // Stress during activity
  "lowStressDuration": 14400,       // Seconds in low stress (0-25)
  "mediumStressDuration": 28800,    // Seconds in medium stress (26-50)
  "highStressDuration": 7200        // Seconds in high stress (51-100)
}
```

### Activities
```python
# Activities in date range
client.get_activities_by_date("2026-01-01", "2026-01-31", activitytype="")
```

**Response structure:**
```json
[
  {
    "activityId": 123456789,
    "activityType": {
      "typeKey": "running",
      "typeId": 1
    },
    "activityName": "Morning Run",
    "startTimeLocal": "2026-01-25 07:30:00",
    "duration": 3600,               // Duration in seconds
    "distance": 10000,              // Distance in meters
    "calories": 650,                // Calories burned
    "averageHR": 152,               // Average heart rate
    "maxHR": 178,                   // Max heart rate
    "elevationGain": 120,           // Elevation gain (meters)
    "averageSpeed": 2.78,           // Speed (m/s)
    "averageRunningCadence": 165    // Cadence (steps/min)
  }
]
```

### Steps & Daily Totals
```python
# Daily stats summary
client.get_user_summary("2026-01-25")
```

**Response structure:**
```json
{
  "totalSteps": 12543,
  "totalKilocalories": 2456,
  "activeKilocalories": 856,
  "bmrKilocalories": 1600,
  "intensityMinutesGoal": 150,
  "vigorousIntensityMinutes": 35,
  "moderateIntensityMinutes": 85
}
```

## Data Availability

### Required Device Features

| Metric | Required Hardware |
|--------|------------------|
| **Sleep stages** | Newer Garmin watches (2018+) |
| **Body Battery** | Firstbeat-enabled devices with HRV |
| **HRV** | Devices with optical HR sensor |
| **Stress** | Devices with all-day HR monitoring |
| **VO2 Max** | GPS + HR-enabled activities |
| **Respiration** | Newer devices (Fenix 6+, Venu 2+, etc.) |

### Historical Data
- Most metrics: Available for full account history
- HRV: May be limited on older devices
- Body Battery: Requires compatible device

## Rate Limits

Garmin enforces rate limits on their API:

**Observed limits:**
- ~50-100 requests per 10 minutes (varies)
- Excessive requests trigger temporary IP/account blocks
- Blocks typically last 15-60 minutes

**Best practices:**
- Cache data locally when possible
- Don't poll excessively (once per hour max for updates)
- Use date range queries instead of day-by-day loops when possible
- Add delays between bulk requests (1-2 seconds)

## Error Handling

### Common Errors

**Authentication Failed**
```
GarminConnectAuthenticationError
```
- Invalid credentials
- Account locked
- Two-factor authentication enabled (not supported)

**Connection Error**
```
GarminConnectConnectionError
```
- Network issues
- Garmin servers down
- Rate limit hit

**No Data**
- Returns `None` or empty list
- Device not worn
- Metric not supported on user's device
- Date has no data

## Library Documentation

**GitHub**: https://github.com/cyberjunky/python-garminconnect

**PyPI**: https://pypi.org/project/garminconnect/

## Alternative: Official Garmin Health API

For enterprise/commercial use:
- **Garmin Health API**: Requires partnership agreement
- **Use case**: App integration, health platforms
- **Not for**: Personal hobby projects

More info: https://www.garmin.com/en-US/health-enterprise/

## Comparison to Whoop API

| Feature | Garmin (unofficial) | Whoop (official) |
|---------|-------------------|------------------|
| **Authentication** | Email/password | OAuth 2.0 |
| **Stability** | May break anytime | Stable, versioned |
| **Rate limits** | Undocumented (~50/10min) | Documented (200/hr) |
| **Data access** | Full history | Full history |
| **Support** | Community library | Official support |
| **Terms of Service** | Gray area | Officially supported |

## Terms of Service Considerations

**Important**: Using the unofficial API may violate Garmin's Terms of Service. Use at your own risk:

- For **personal use** only
- Don't build commercial products on this
- Don't scrape excessively
- Consider official Garmin Health API for production use

## Tips for Reliability

1. **Cache aggressively**: Store data locally, only fetch new dates
2. **Error recovery**: Retry with exponential backoff on failures
3. **Monitor library updates**: Watch GitHub for breaking changes
4. **Have a fallback**: Manual CSV export from Garmin Connect web if API breaks
5. **Test before relying**: Verify data accuracy against Garmin Connect web UI

## Useful Resources

- [Garmin Connect Web](https://connect.garmin.com): Official interface
- [python-garminconnect GitHub](https://github.com/cyberjunky/python-garminconnect): Library source
- [Garmin Forums](https://forums.garmin.com): Community support
- [r/Garmin](https://reddit.com/r/Garmin): Reddit community
