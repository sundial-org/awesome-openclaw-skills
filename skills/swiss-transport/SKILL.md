---
name: swiss-transport
description: Swiss Public Transport real-time information. Use when querying train, bus, tram, or boat schedules in Switzerland. Supports station search, departure boards, journey planning from A to B, and connection details. Use for queries like "When does the next train leave from Zürich?" or "How do I get from Bern to Geneva?" or "Show departures at Basel SBB".
homepage: https://transport.opendata.ch
---

# Swiss Public Transport

Query Swiss public transport (SBB, BLS, ZVV, etc.) using the official transport.opendata.ch API.

## Quick Commands

### Search stations
```bash
curl -s "https://transport.opendata.ch/v1/locations?query=Zürich" | jq -r '.stations[] | "\(.name) (\(.id))"'
```

### Get next departures
```bash
curl -s "https://transport.opendata.ch/v1/stationboard?station=Zürich%20HB&limit=10" | \
  jq -r '.stationboard[] | "\(.stop.departure[11:16]) \(.category) \(.number) → \(.to)"'
```

### Plan journey from A to B
```bash
curl -s "https://transport.opendata.ch/v1/connections?from=Zürich&to=Bern&limit=3" | \
  jq -r '.connections[] | "Departure: \(.from.departure[11:16]) | Arrival: \(.to.arrival[11:16]) | Duration: \(.duration[3:]) | Changes: \(.transfers)"'
```

### Get connection details with sections
```bash
curl -s "https://transport.opendata.ch/v1/connections?from=Zürich%20HB&to=Bern&limit=1" | \
  jq '.connections[0].sections[] | {from: .departure.station.name, to: .arrival.station.name, departure: .departure.departure, arrival: .arrival.arrival, transport: .journey.category, line: .journey.number}'
```

## API Endpoints

### `/v1/locations` - Search stations
```bash
curl "https://transport.opendata.ch/v1/locations?query=<station-name>"
```

Parameters:
- `query` (required): Station name to search
- `type` (optional): Filter by type (station, address, poi)

### `/v1/stationboard` - Departure board
```bash
curl "https://transport.opendata.ch/v1/stationboard?station=<station>&limit=<number>"
```

Parameters:
- `station` (required): Station name or ID
- `limit` (optional): Number of results (default 40)
- `transportations[]` (optional): Filter by type (ice_tgv_rj, ec_ic, ir, re_d, ship, s_sn_r, bus, cableway, arz_ext, tramway_underground)
- `datetime` (optional): Date/time in ISO format

### `/v1/connections` - Journey planner
```bash
curl "https://transport.opendata.ch/v1/connections?from=<start>&to=<destination>&limit=<number>"
```

Parameters:
- `from` (required): Starting station
- `to` (required): Destination station
- `via[]` (optional): Intermediate station(s)
- `date` (optional): Date (YYYY-MM-DD)
- `time` (optional): Time (HH:MM)
- `isArrivalTime` (optional): 0 (departure, default) or 1 (arrival)
- `limit` (optional): Number of connections (max 16)

## Helper Script

Use `scripts/journey.py` for formatted journey planning:

```bash
python3 scripts/journey.py "Zürich HB" "Bern"
python3 scripts/journey.py "Basel" "Lugano" --limit 5
```

## Notes

- All times are in Swiss local time (CET/CEST)
- Station names support autocomplete (e.g., "Zürich" finds "Zürich HB")
- API returns JSON by default
- No API key required
- Real-time data includes delays and platform changes
