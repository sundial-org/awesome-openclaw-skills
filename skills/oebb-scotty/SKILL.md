---
name: oebb-scotty
description: Austrian rail travel planner (ÖBB Scotty). Use when planning train journeys in Austria, checking departures/arrivals at stations, or looking for service disruptions. Covers ÖBB trains, S-Bahn, regional trains, and connections to neighboring countries.
---

# ÖBB Scotty API

Query Austria's public transport for trip planning, station departures, and service alerts via the HAFAS mgate API.

## Quick Reference

| Method | Purpose |
|--------|---------|
| `LocMatch` | Search for stations/stops by name |
| `TripSearch` | Plan a journey between two locations |
| `StationBoard` | Get departures/arrivals at a station |
| `HimSearch` | Get service alerts and disruptions |

**Base URL:** `https://fahrplan.oebb.at/bin/mgate.exe`

---

## Authentication

All requests require these headers in the JSON body:

```json
{
  "id": "1",
  "ver": "1.67",
  "lang": "deu",
  "auth": {"type": "AID", "aid": "OWDL4fE4ixNiPBBm"},
  "client": {"id": "OEBB", "type": "WEB", "name": "webapp", "l": "vs_webapp"},
  "formatted": false,
  "svcReqL": [...]
}
```

---

## 1. Location Search (`LocMatch`)

Search for stations, stops, addresses, or POIs by name.

### Request

```bash
curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{"input":{"field":"S","loc":{"name":"Wien Hbf","type":"ALL"},"maxLoc":10}},
      "meth":"LocMatch"
    }]
  }'
```

### Response Structure

```json
{
  "svcResL": [{
    "res": {
      "match": {
        "locL": [{
          "lid": "A=1@O=Wien Hbf (U)@X=16377950@Y=48184986@U=181@L=1290401@",
          "type": "S",
          "name": "Wien Hbf (U)",
          "extId": "1290401",
          "crd": { "x": 16377950, "y": 48184986 },
          "pCls": 6015
        }]
      }
    }
  }]
}
```

### Location Types

| Type | Description |
|------|-------------|
| `S` | Station/Stop |
| `A` | Address |
| `P` | POI (Point of Interest) |

### Key Fields

| Field | Description |
|-------|-------------|
| `lid` | Location ID string (use in TripSearch) |
| `extId` | External station ID |
| `name` | Station name |
| `crd.x/y` | Coordinates (x=lon, y=lat, scaled by 10^6) |
| `pCls` | Product class bitmask |

---

## 2. Trip Search (`TripSearch`)

Plan a journey between two locations.

### Request

```bash
curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{
        "depLocL":[{"lid":"A=1@O=Wien Hbf@L=8103000@","type":"S"}],
        "arrLocL":[{"lid":"A=1@O=Salzburg Hbf@L=8100002@","type":"S"}],
        "jnyFltrL":[{"type":"PROD","mode":"INC","value":"1023"}],
        "getPolyline":false,
        "getPasslist":true,
        "outDate":"20260109",
        "outTime":"080000",
        "outFrwd":true,
        "numF":5
      },
      "meth":"TripSearch"
    }]
  }'
```

### Parameters

| Param | Description |
|-------|-------------|
| `depLocL` | Departure location(s) - use `lid` from LocMatch |
| `arrLocL` | Arrival location(s) |
| `outDate` | Departure date (YYYYMMDD) |
| `outTime` | Departure time (HHMMSS) |
| `outFrwd` | `true` = search forward, `false` = search backward |
| `numF` | Number of connections to return |
| `jnyFltrL` | Product filter (see below) |
| `getPasslist` | Include intermediate stops |

### Product Filter Values

| Bit | Value | Product |
|-----|-------|---------|
| 0 | 1 | ICE/RJX (High-speed) |
| 1 | 2 | IC/EC (InterCity) |
| 2 | 4 | NJ (Night trains) |
| 3 | 8 | D/EN (Express) |
| 4 | 16 | REX/R (Regional Express) |
| 5 | 32 | S-Bahn |
| 6 | 64 | Bus |
| 7 | 128 | Ferry |
| 8 | 256 | U-Bahn |
| 9 | 512 | Tram |

Use `1023` for all products, or sum specific bits.

### Response Structure

```json
{
  "svcResL": [{
    "res": {
      "outConL": [{
        "date": "20260109",
        "dur": "025200",
        "chg": 0,
        "dep": {
          "dTimeS": "075700",
          "dPltfS": {"txt": "8A-B"}
        },
        "arr": {
          "aTimeS": "104900",
          "aPltfS": {"txt": "7"}
        },
        "secL": [{
          "type": "JNY",
          "jny": {
            "prodX": 0,
            "dirTxt": "Salzburg Hbf",
            "stopL": [...]
          }
        }]
      }],
      "common": {
        "locL": [...],
        "prodL": [...]
      }
    }
  }]
}
```

### Key Connection Fields

| Field | Description |
|-------|-------------|
| `dur` | Duration (HHMMSS) |
| `chg` | Number of changes |
| `dTimeS` | Scheduled departure |
| `dTimeR` | Real-time departure (if available) |
| `aTimeS` | Scheduled arrival |
| `aTimeR` | Real-time arrival (if available) |
| `dPltfS.txt` | Departure platform |
| `aPltfS.txt` | Arrival platform |
| `secL` | Journey sections (legs) |
| `secL[].jny.prodX` | Index into `common.prodL[]` for train name |

### Understanding prodX (Product Index)

**Important:** The `prodX` field in journey sections is an index into the `common.prodL[]` array, NOT the train name itself. To get the actual train name (e.g., "S7", "RJX 662"), you must look up `common.prodL[prodX].name`.

### Extracting Trip Summaries with jq

The raw TripSearch response is very verbose. Use this jq filter to extract a concise summary with resolved train names:

```bash
curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{ ... }' | jq '
    .svcResL[0].res as $r |
    $r.common.prodL as $prods |
    [$r.outConL[] | {
      dep: .dep.dTimeS,
      arr: .arr.aTimeS,
      depPlatform: .dep.dPltfS.txt,
      arrPlatform: .arr.aPltfS.txt,
      dur: .dur,
      chg: .chg,
      legs: [.secL[] | select(.type == "JNY") | {
        train: $prods[.jny.prodX].name,
        dir: .jny.dirTxt,
        dep: .dep.dTimeS,
        arr: .arr.aTimeS,
        depPlatform: .dep.dPltfS.txt,
        arrPlatform: .arr.aPltfS.txt
      }]
    }]'
```

Example output:
```json
[
  {
    "dep": "213900",
    "arr": "221100",
    "depPlatform": "1",
    "arrPlatform": "3A-B",
    "dur": "003200",
    "chg": 0,
    "legs": [{"train": "S 7", "dir": "Flughafen Wien Bahnhof", "dep": "213900", "arr": "221100", ...}]
  }
]
```

---

## 3. Station Board (`StationBoard`)

Get departures or arrivals at a station.

### Request

```bash
curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{
        "stbLoc":{"lid":"A=1@O=Wien Hbf@L=8103000@","type":"S"},
        "date":"20260109",
        "time":"080000",
        "type":"DEP",
        "maxJny":20
      },
      "meth":"StationBoard"
    }]
  }'
```

### Parameters

| Param | Description |
|-------|-------------|
| `stbLoc` | Station location |
| `date` | Date (YYYYMMDD) |
| `time` | Time (HHMMSS) |
| `type` | `DEP` (departures) or `ARR` (arrivals) |
| `maxJny` | Maximum number of journeys |

### Response Structure

```json
{
  "svcResL": [{
    "res": {
      "jnyL": [{
        "prodX": 0,
        "dirTxt": "Salzburg Hbf",
        "stbStop": {
          "dTimeS": "080000",
          "dPltfS": {"txt": "8A-B"}
        }
      }],
      "common": {
        "prodL": [{
          "name": "RJX 662",
          "cls": 1,
          "prodCtx": {"catOutL": "Railjet Xpress"}
        }]
      }
    }
  }]
}
```

---

## 4. Service Alerts (`HimSearch`)

Get current disruptions and service information.

### Request

```bash
curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{
        "himFltrL":[{"type":"PROD","mode":"INC","value":"255"}],
        "maxNum":20
      },
      "meth":"HimSearch"
    }]
  }'
```

### Response Structure

```json
{
  "svcResL": [{
    "res": {
      "msgL": [{
        "hid": "HIM_FREETEXT_843858",
        "head": "Verringertes Sitzplatzangebot",
        "text": "Wegen einer technischen Störung...",
        "prio": 0,
        "sDate": "20260108",
        "eDate": "20260108"
      }]
    }
  }]
}
```

---

## Common Station IDs

| Station | extId |
|---------|-------|
| Wien Hbf | 8103000 |
| Wien Meidling | 8100514 |
| Wien Westbahnhof | 8101003 |
| Salzburg Hbf | 8100002 |
| Linz Hbf | 8100013 |
| Graz Hbf | 8100173 |
| Innsbruck Hbf | 8100108 |
| Klagenfurt Hbf | 8100085 |
| St. Pölten Hbf | 8100008 |
| Wr. Neustadt Hbf | 8100516 |

---

## Time Format

- Dates: `YYYYMMDD` (e.g., `20260109`)
- Times: `HHMMSS` (e.g., `080000` = 08:00:00)
- Duration: `HHMMSS` (e.g., `025200` = 2h 52m)

---

## Error Handling

Check `err` field in response:

```json
{
  "err": "OK",           // Success
  "err": "PARSE",        // Invalid request format
  "err": "NO_MATCH",     // No results found
  "errTxt": "..."        // Error details
}
```

---

## Product Classes (cls values)

| cls | Product |
|-----|---------|
| 1 | ICE/RJX |
| 2 | IC/EC |
| 4 | Night trains |
| 8 | NJ/EN |
| 16 | REX/Regional |
| 32 | S-Bahn |
| 64 | Bus |
| 128 | Ferry |
| 256 | U-Bahn |
| 512 | Tram |
| 1024 | On-demand |
| 2048 | Other |
