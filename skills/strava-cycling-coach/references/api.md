## Strava API Reference

## Authentication

Strava uses OAuth 2.0 for authentication.

### OAuth Flow

1. **Authorize**: Direct user to authorization URL
2. **Exchange code**: Trade authorization code for access/refresh tokens
3. **Refresh**: Use refresh token to get new access token when expired

### Tokens

- **Access Token**: Valid for 6 hours
- **Refresh Token**: Long-lived, use to get new access tokens
- **Expires At**: Unix timestamp when access token expires

## Base URL

```
https://www.strava.com/api/v3
```

## Key Endpoints

### Get Athlete

```
GET /athlete
```

Returns the currently authenticated athlete.

### List Activities

```
GET /athlete/activities
```

**Parameters:**
- `before` - Seconds since epoch (filter activities before this date)
- `after` - Seconds since epoch (filter activities after this date)
- `page` - Page number (default 1)
- `per_page` - Number per page (default 30, max 200)

### Get Activity

```
GET /activities/{id}
```

Returns detailed information about an activity.

**Optional parameters:**
- `include_all_efforts` - Include segment efforts (boolean)

### Activity Streams

```
GET /activities/{id}/streams
```

Get detailed time-series data for an activity.

**Parameters:**
- `keys` - Comma-separated list: time, latlng, distance, altitude, velocity_smooth, heartrate, cadence, watts, temp, moving, grade_smooth
- `key_by_type` - Boolean (default true)

### Activity Object

Key fields:
- `id` - Activity ID
- `name` - Activity name
- `type` - Activity type (Ride, VirtualRide, Run, etc.)
- `start_date` - ISO 8601 timestamp
- `start_date_local` - Local time
- `distance` - Meters
- `moving_time` - Seconds
- `elapsed_time` - Seconds
- `total_elevation_gain` - Meters
- `average_speed` - m/s
- `max_speed` - m/s
- `average_watts` - Watts (requires power meter)
- `weighted_average_watts` - Normalized Power
- `max_watts` - Peak power
- `average_heartrate` - BPM
- `max_heartrate` - BPM
- `average_cadence` - RPM
- `suffer_score` - Relative effort (proprietary)
- `calories` - Estimated calories
- `device_watts` - True if power from device (vs estimated)
- `has_heartrate` - Boolean

### Segment Efforts

Included in activity detail:
- `segment_efforts` - Array of segment efforts
  - `name` - Segment name
  - `elapsed_time` - Time for segment
  - `pr_rank` - Personal record rank (1, 2, 3, null)
  - `kom_rank` - KOM/QOM rank if applicable

## Rate Limits

- **Short-term**: 100 requests per 15 minutes
- **Daily**: 1,000 requests per day

Monitor headers:
- `X-RateLimit-Limit`
- `X-RateLimit-Usage`

## Best Practices

1. **Cache data** - Don't re-fetch unchanged activities
2. **Use webhooks** - For real-time activity updates
3. **Respect limits** - Handle 429 responses gracefully
4. **Refresh tokens** - Check expiry before each request

## Documentation

Full API docs: https://developers.strava.com/docs/reference/
