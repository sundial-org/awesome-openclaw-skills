---
name: journey
description: "Plan multi-waypoint journeys with route optimization, feasibility analysis, and time budget constraints. Use when you need to plan trips with multiple stops or check if an itinerary is achievable."
metadata: {"clawdbot":{"emoji":"🗺️","requires":{"env":["CAMINO_API_KEY"]},"primaryEnv":"CAMINO_API_KEY"}}
---

# Journey - Multi-Stop Planning

Plan multi-waypoint journeys with route optimization, feasibility analysis, and time budget constraints.

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
# Plan a simple journey
./scripts/journey.sh '{
  "waypoints": [
    {"lat": 40.7128, "lon": -74.0060, "purpose": "Start at hotel"},
    {"lat": 40.7484, "lon": -73.9857, "purpose": "Visit Empire State Building"},
    {"lat": 40.7614, "lon": -73.9776, "purpose": "Lunch in Midtown"}
  ]
}'

# With transport mode and time budget
./scripts/journey.sh '{
  "waypoints": [
    {"lat": 40.7128, "lon": -74.0060, "purpose": "Start"},
    {"lat": 40.7484, "lon": -73.9857, "purpose": "Empire State"},
    {"lat": 40.7614, "lon": -73.9776, "purpose": "MoMA"}
  ],
  "constraints": {
    "transport": "foot",
    "time_budget": "3 hours"
  }
}'
```

### Via curl

```bash
curl -X POST -H "X-API-Key: $CAMINO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "waypoints": [
      {"lat": 40.7128, "lon": -74.0060, "purpose": "Start"},
      {"lat": 40.7484, "lon": -73.9857, "purpose": "Empire State"}
    ],
    "constraints": {"transport": "foot"}
  }' \
  "https://api.getcamino.ai/journey"
```

## Parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| waypoints | array | Yes | - | List of waypoints with lat, lon, and purpose (min 2) |
| constraints.transport | string | No | "walking" | Transport mode: "walking", "car", or "bike" |
| constraints.time_budget | string | No | - | Time constraint (e.g., "2 hours", "90 minutes") |
| constraints.preferences | array | No | [] | Route preferences |

### Waypoint Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| lat | float | Yes | Latitude of the waypoint |
| lon | float | Yes | Longitude of the waypoint |
| purpose | string | No | Description of why you're visiting this waypoint |

## Response Format

```json
{
  "feasible": true,
  "total_distance_km": 4.2,
  "total_time_minutes": 52,
  "total_time_formatted": "52 minutes",
  "transport_mode": "foot",
  "route_segments": [
    {
      "from": "Start",
      "to": "Empire State",
      "distance_km": 4.2,
      "duration_minutes": 52
    }
  ],
  "analysis": {
    "summary": "This walking journey is feasible...",
    "optimization_opportunities": []
  }
}
```

## Examples

### Day trip planning
```bash
./scripts/journey.sh '{
  "waypoints": [
    {"lat": 48.8584, "lon": 2.2945, "purpose": "Eiffel Tower"},
    {"lat": 48.8606, "lon": 2.3376, "purpose": "Louvre Museum"},
    {"lat": 48.8530, "lon": 2.3499, "purpose": "Notre-Dame"},
    {"lat": 48.8867, "lon": 2.3431, "purpose": "Sacré-Cœur"}
  ],
  "constraints": {
    "transport": "foot",
    "time_budget": "6 hours"
  }
}'
```

### Business meeting route
```bash
./scripts/journey.sh '{
  "waypoints": [
    {"lat": 40.7128, "lon": -74.0060, "purpose": "Office"},
    {"lat": 40.7580, "lon": -73.9855, "purpose": "Client meeting"},
    {"lat": 40.7614, "lon": -73.9776, "purpose": "Lunch"},
    {"lat": 40.7128, "lon": -74.0060, "purpose": "Return to office"}
  ],
  "constraints": {
    "transport": "car",
    "time_budget": "2 hours"
  }
}'
```

### Cycling tour
```bash
./scripts/journey.sh '{
  "waypoints": [
    {"lat": 37.7749, "lon": -122.4194, "purpose": "Start downtown SF"},
    {"lat": 37.8199, "lon": -122.4783, "purpose": "Golden Gate Bridge"},
    {"lat": 37.8270, "lon": -122.4230, "purpose": "Sausalito"}
  ],
  "constraints": {
    "transport": "bike"
  }
}'
```

## Use Cases

- **Trip itinerary validation**: Check if a planned itinerary is feasible within time constraints
- **Route optimization**: Get suggestions for optimizing multi-stop journeys
- **Travel time estimation**: Understand total journey time across multiple destinations
- **Tour planning**: Plan walking tours, cycling routes, or driving trips
