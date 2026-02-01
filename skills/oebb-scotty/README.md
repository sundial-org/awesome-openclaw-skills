# ÖBB Scotty Skill

Austrian rail travel planner using the ÖBB Scotty HAFAS API.

## Tools

### search-station.sh
Search for stations by name.

```bash
./search-station.sh "Wien Hbf"
./search-station.sh "Salzburg"
./search-station.sh "Flughafen Wien"
```

### trip.sh
Plan a journey between two stations.

```bash
# Basic usage
./trip.sh "Wien Hbf" "Salzburg Hbf"

# With date and time
./trip.sh "Wien Hbf" "Salzburg Hbf" 20260109 0800

# With custom number of results
./trip.sh "Graz Hbf" "Innsbruck Hbf" 20260109 1200 10
```

### departures.sh
Get departures from a station.

```bash
# Next departures
./departures.sh "Wien Hbf"

# Specific date/time
./departures.sh "Wien Hbf" 20260109 0800 20
```

### arrivals.sh
Get arrivals at a station.

```bash
# Next arrivals
./arrivals.sh "Salzburg Hbf"

# Specific date/time
./arrivals.sh "Linz Hbf" 20260109 1200 15
```

### disruptions.sh
Get current service disruptions.

```bash
./disruptions.sh
./disruptions.sh 50  # Get more results
```

## Example Output

### Trip Search
```json
{
  "date": "20260109",
  "departure": {
    "time": "07:57",
    "platform": "8A-B",
    "station": "Wien Hbf"
  },
  "arrival": {
    "time": "10:49",
    "platform": "7",
    "station": "Salzburg Hbf"
  },
  "duration": "02h 52m",
  "changes": 0,
  "legs": [{
    "train": "IC 544",
    "category": "InterCity",
    "direction": "Salzburg Hbf"
  }]
}
```

### Departures
```json
{
  "station": "Wien Hbf",
  "departures": [{
    "time": "08:00",
    "platform": "N2",
    "train": "Bus 200",
    "direction": "Eisenstadt Busbahnhof"
  }]
}
```

## Common Stations

| Station | Notes |
|---------|-------|
| Wien Hbf | Vienna main station |
| Wien Meidling | Vienna south |
| Wien Westbahnhof | Vienna west |
| Salzburg Hbf | Salzburg main |
| Linz Hbf | Linz main |
| Graz Hbf | Graz main |
| Innsbruck Hbf | Innsbruck main |
| Klagenfurt Hbf | Klagenfurt main |
| Flughafen Wien | Vienna Airport |
