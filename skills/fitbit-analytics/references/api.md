# Fitbit Web API Reference

## Authentication

1. Register app: https://dev.fitbit.com/apps
2. OAuth 2.0 flow required
3. Tokens expire, need refresh

```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

## Endpoints

### Activity (Steps, Calories, Distance)
`GET /1/user/[user-id]/activities/steps/date/[start-date]/[end-date].json`
`GET /1/user/[user-id]/activities/calories/date/[start-date]/[end-date].json`
`GET /1/user/[user-id]/activities/distance/date/[start-date]/[end-date].json`

Returns daily activity summary:
- `steps` - Daily step count
- `calories` - Calories burned
- `caloriesOut` - Active calories
- `distance` - Distance in miles/km
- `floors` - Floors climbed
- `minutesSedentary` - Sedentary minutes
- `minutesLightlyActive` - Light activity minutes
- `minutesFairlyActive` - Moderate activity minutes
- `minutesVeryActive` - Vigorous activity minutes

### Heart Rate
`GET /1/user/[user-id]/activities/heart/date/[start-date]/[end-date].json`

Returns heart rate data:
- `restingHeartRate` - Resting heart rate (RHR)
- `heartRateZones` - Time in each zone:
  - `outOfRange`
  - `fatBurn`
  - `cardio`
  - `peak`
- `intraday` (if enabled) - Minute-by-minute data

### Sleep
`GET /1.2/user/[user-id]/sleep/date/[start-date]/[end-date].json`

Returns sleep data:
- `sleep` - Sleep periods (main + naps)
- `summary` - Sleep stage summary:
  - `totalMinutesAsleep`
  - `totalTimeInBed`
  - `minutesToFallAsleep`
  - `minutesAwake`
  - `startTime`, `endTime`
  - `efficiency` - Sleep efficiency %

### Sleep Stages (Detailed)
`GET /1.3/user/[user-id]/sleep/date/[start-date]/[end-date].json`

Returns sleep stages:
- `levels` - Sleep stage breakdown:
  - `deep` - Deep sleep minutes
  - `light` - Light sleep minutes
  - `rem` - REM minutes
  - `wake` - Wake minutes

### SpO2 (Blood Oxygen)
`GET /1/user/[user-id]/spo2/date/[start-date]/[end-date].json`

Returns:
- `average` - Average SpO2 %
- `min`, `max` - Range

### Respiratory Rate
`GET /1/user/[user-id]/br/date/[start-date]/[end-date].json`

Returns breathing rate during sleep.

### Weight
`GET /1/user/[user-id]/body/weight/date/[start-date]/[end-date].json`

Returns weight data.

### Devices
`GET /1/user/[user-id]/devices.json`

Returns connected device info.

## Rate Limits

- 150 requests/hour
- Requests per endpoint vary

## Example Response

```json
{
  "activities-steps": [{
    "dateTime": "2026-01-16",
    "value": "8543"
  }],
  "summary": {
    "steps": 8543,
    "caloriesOut": 1923,
    "activityCalories": 520,
    "marginalCalories": 380,
    "distance": 4.2,
    "floors": 8,
    "minutesSedentary": 720,
    "minutesLightlyActive": 180,
    "minutesFairlyActive": 45,
    "minutesVeryActive": 30,
    "activeScore": 42
  }
}
```
