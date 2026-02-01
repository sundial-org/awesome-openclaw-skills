---
name: context
description: "Get comprehensive context about a location including nearby places, area description, and optional weather. Use when you need to understand what's around a location or provide location-aware recommendations."
metadata: {"clawdbot":{"emoji":"📍","requires":{"env":["CAMINO_API_KEY"]},"primaryEnv":"CAMINO_API_KEY"}}
---

# Context - Location Analysis

Get comprehensive context about a location including nearby places, area description, and optional weather.

## Setup

1. Get your API key from [https://app.getcamino.ai](https://app.getcamino.ai)
2. Add to your `~/.claude/settings.json`:

```json
{
  "env": {
    "CAMINO_API_KEY": "your-api-key-here"
  }
}
```

3. Restart Claude Code

## Usage

### Via Shell Script

```bash
# Get context about a location
./scripts/context.sh '{
  "location": {"lat": 40.7589, "lon": -73.9851},
  "radius": 500
}'

# With specific context for tailored insights
./scripts/context.sh '{
  "location": {"lat": 40.7589, "lon": -73.9851},
  "radius": 500,
  "context": "lunch options"
}'

# Include weather data
./scripts/context.sh '{
  "location": {"lat": 40.7589, "lon": -73.9851},
  "include_weather": true,
  "weather_forecast": "hourly"
}'
```

### Via curl

```bash
curl -X POST -H "X-API-Key: $CAMINO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"location": {"lat": 40.7589, "lon": -73.9851}, "radius": 500, "context": "lunch options"}' \
  "https://api.getcamino.ai/context"
```

## Parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| location | object | Yes | - | Coordinate with lat/lon |
| radius | int | No | 500 | Search radius in meters |
| context | string | No | - | Context for tailored insights (e.g., "outdoor dining") |
| time | string | No | - | Temporal query format |
| include_weather | bool | No | false | Include weather data |
| weather_forecast | string | No | "daily" | "daily" or "hourly" |

## Response Format

```json
{
  "area_description": "Busy commercial district in Midtown Manhattan...",
  "relevant_places": {
    "restaurants": [...],
    "cafes": [...],
    "transit": [...]
  },
  "location": {"lat": 40.7589, "lon": -73.9851},
  "search_radius": 500,
  "total_places_found": 47,
  "context_insights": "For lunch, you have many options including..."
}
```

## Examples

### Tourist context
```bash
./scripts/context.sh '{
  "location": {"lat": 48.8584, "lon": 2.2945},
  "radius": 1000,
  "context": "tourist visiting Paris"
}'
```

### Business meeting location
```bash
./scripts/context.sh '{
  "location": {"lat": 40.7589, "lon": -73.9851},
  "radius": 500,
  "context": "business meeting",
  "include_weather": true
}'
```

### Outdoor activity planning
```bash
./scripts/context.sh '{
  "location": {"lat": 37.7749, "lon": -122.4194},
  "context": "outdoor activities",
  "include_weather": true,
  "weather_forecast": "hourly"
}'
```

## Use Cases

- **Trip planning**: Understand what's around a destination before visiting
- **Meeting locations**: Find suitable venues for different types of meetings
- **Local recommendations**: Provide context-aware suggestions based on user needs
- **Weather-aware planning**: Include weather data for outdoor activity planning
