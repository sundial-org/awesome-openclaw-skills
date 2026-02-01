---
name: mbta
description: Real-time MBTA transit predictions for Boston-area subway, bus, commuter rail, and ferry. Query departure times, search stops/routes, check service alerts, and run a live dashboard. Use when asked about Boston transit, T schedules, when to leave for the train, or MBTA service status.
metadata: {"clawdbot":{"requires":{"bins":["python3"],"pip":["requests"]}}}
---

# MBTA Transit

Query real-time MBTA predictions via the v3 API.

## Setup

```bash
# Optional but recommended for higher rate limits
export MBTA_API_KEY=your_key_here  # Free at https://api-v3.mbta.com/portal

# Install dependencies
pip install requests pyyaml flask  # flask only needed for dashboard
```

## Quick Commands

```bash
cd skills/mbta

# Next departures from a stop
python scripts/mbta.py next --stop place-alfcl  # Alewife
python scripts/mbta.py next --stop place-harsq --route Red  # Harvard, Red Line only

# Search for stop IDs
python scripts/mbta.py stops --search "Porter"
python scripts/mbta.py stops --search "Kendall"

# List routes
python scripts/mbta.py routes              # All routes
python scripts/mbta.py routes --type rail  # Subway only
python scripts/mbta.py routes --type bus   # Buses

# Service alerts
python scripts/mbta.py alerts              # All alerts
python scripts/mbta.py alerts --route Red  # Red Line alerts

# All configured departures (uses config.yaml)
python scripts/mbta.py departures --config config.yaml

# Start web dashboard
python scripts/mbta.py dashboard --config config.yaml --port 6639
```

## Configuration

Edit `config.yaml` to set up your stops:

```yaml
panels:
  - title: "My Station"
    walk_minutes: 5  # Filter out trains you can't catch
    services:
      - label: "Red Line"
        destination: "to Alewife"
        route_id: "Red"
        stop_id: "place-harsq"
        direction_id: 0  # 0 or 1 for direction
        limit: 3
```

Key fields:
- `walk_minutes`: Trains departing sooner than this are filtered out
- `direction_id`: 0 = outbound/north, 1 = inbound/south (varies by line)
- `headsign_contains`: Optional filter (e.g., "Ashmont" to exclude Braintree)

## Finding Stop/Route IDs

```bash
# Search stops
python scripts/mbta.py stops --search "Davis"
# Returns: place-davis: Davis

# Get routes
python scripts/mbta.py routes --type rail
# Returns route IDs like "Red", "Orange", "Green-E"
```

## JSON Output

Add `--json` for machine-readable output:

```bash
python scripts/mbta.py next --stop place-alfcl --json
python scripts/mbta.py departures --config config.yaml --json
```

## Common Stop IDs

| Station | Stop ID |
|---------|---------|
| Alewife | place-alfcl |
| Harvard | place-harsq |
| Kendall/MIT | place-knncl |
| Park Street | place-pktrm |
| South Station | place-sstat |
| North Station | place-north |
| Back Bay | place-bbsta |
| Downtown Crossing | place-dwnxg |

## Answering User Questions

**"When's the next Red Line train?"**
```bash
python scripts/mbta.py next --stop place-alfcl --route Red
```

**"Should I leave now to catch the T?"**
Check departures against their walk time. If next train is ≤ walk_minutes, say "leave now!"

**"Are there any delays on the Orange Line?"**
```bash
python scripts/mbta.py alerts --route Orange
```

**"What buses go to Harvard?"**
```bash
python scripts/mbta.py stops --search "Harvard"
# Then check routes at that stop
python scripts/mbta.py next --stop <stop_id>
```
