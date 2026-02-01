---
name: trains
description: Query UK National Rail live departure boards, arrivals, delays, and train services. Use when asked about train times, departures, arrivals, delays, platforms, or "when is the next train" for UK railways. Supports all GB stations via Darwin/Huxley2 API.
---

# UK Trains

Query National Rail Darwin API for live train departures and arrivals.

## Setup

Requires free Darwin API token:
1. Register at https://realtime.nationalrail.co.uk/OpenLDBWSRegistration/
2. Set `NATIONAL_RAIL_TOKEN` in environment (or configure in skills.entries.uk-trains.apiKey)

## Commands

```bash
# Departures
./scripts/trains.py departures PAD
./scripts/trains.py departures PAD to OXF --rows 5

# Arrivals  
./scripts/trains.py arrivals MAN
./scripts/trains.py arrivals MAN from EUS

# Station search
./scripts/trains.py search paddington
./scripts/trains.py search kings
```

## Station Codes

Use 3-letter CRS codes:
- `PAD` = London Paddington
- `EUS` = London Euston  
- `KGX` = London Kings Cross
- `VIC` = London Victoria
- `WAT` = London Waterloo
- `MAN` = Manchester Piccadilly
- `BHM` = Birmingham New Street
- `EDB` = Edinburgh Waverley
- `GLC` = Glasgow Central
- `BRI` = Bristol Temple Meads
- `LDS` = Leeds
- `LIV` = Liverpool Lime Street
- `RDG` = Reading
- `OXF` = Oxford
- `CBG` = Cambridge

## Response Format

JSON with:
- `locationName`, `crs` - Station info
- `messages[]` - Service alerts
- `trainServices[]` - List of trains:
  - `std`/`sta` - Scheduled departure/arrival time
  - `etd`/`eta` - Expected time ("On time", "Delayed", or actual time)
  - `platform` - Platform number
  - `operator` - Train operating company
  - `destination[].name` - Final destination
  - `isCancelled`, `cancelReason`, `delayReason` - Disruption info

## Message Template

Use this compact format for WhatsApp/chat responses:

```
🚂 {Origin} → {Destination}

*{dep} → {arr}* │📍{platform} │ 🚃 {coaches}
{status}

*{dep} → {arr}* │📍{platform} │ 🚃 {coaches}
{status}
```

### Elements
- **Header:** 🚂 emoji + origin → destination
- **Time:** Bold, departure → arrival times
- **Platform:** 📍 + number (or "TBC" if unknown)
- **Coaches:** 🚃 + space + number
- **Status:**
  - ✅ On time
  - ⚠️ Delayed (exp {time})
  - ❌ Cancelled — {reason}
  - 🔄 Starts here

### Example

```
🚂 Hemel Hempstead → Euston

*20:18 → 20:55* │📍4 │ 🚃 4
✅ On time

*20:55 → 21:30* │📍4 │ 🚃 12
✅ On time

*21:11 → 21:41* │📍4 │ 🚃 8
✅ On time
```

### Getting Arrival Times
To show arrival times, make two API calls:
1. `departures {origin} to {dest}` — get departure times + service IDs
2. `arrivals {dest} from {origin}` — get arrival times

Match services by the numeric prefix in serviceID (e.g., `4748110HEMLHMP_` matches `4748110EUSTON__`).

### Notes
- Separate each service with a blank line
- Omit coaches if formation data unavailable
- For delays, show expected time: `⚠️ Delayed (exp 20:35)`
