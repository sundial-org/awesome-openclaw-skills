---
name: places
description: "Locate places using flexible query formats - free-form search or structured address components. Returns coordinates, addresses, and optional street-level photos. Use for geocoding addresses or finding specific named places."
metadata: {"clawdbot":{"emoji":"📌","requires":{"env":["CAMINO_API_KEY"]},"primaryEnv":"CAMINO_API_KEY"}}
---

# Places - Flexible Place Lookup

Locate places using free-form queries or structured address components. Supports geocoding, place lookup, and optional street-level imagery.

## Places vs Query

| Feature | `/places` | `/query` |
|---------|-----------|----------|
| Method | POST | GET |
| Input | Free-form OR structured address | Natural language with context |
| Coordinates | Returns them (geocoding) | Can auto-generate for search center |
| AI Ranking | No | Yes |
| Photos | Optional street-level imagery | No |
| Best For | "Eiffel Tower", address lookup | "quiet cafes near Times Square" |

**Use `/places`** for geocoding addresses or finding specific named places.
**Use `/query`** for natural language queries with AI ranking.

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
# Free-form search for a landmark
./scripts/places.sh '{"query": "Eiffel Tower"}'

# Search with street-level photos
./scripts/places.sh '{"query": "Empire State Building", "include_photos": true}'

# Structured address search
./scripts/places.sh '{"street": "1600 Pennsylvania Avenue", "city": "Washington", "state": "DC", "country": "USA"}'

# Search by city
./scripts/places.sh '{"city": "San Francisco", "state": "California", "limit": 5}'
```

### Via curl (direct API calls)

The skill is named `places` but calls the `/search` API endpoint. For direct API calls:

```bash
curl -X POST -H "X-API-Key: $CAMINO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "Eiffel Tower", "include_photos": true}' \
  "https://api.getcamino.ai/search"
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | No* | - | Free-form search (e.g., "Eiffel Tower", "Central Park") |
| amenity | string | No | - | Amenity/POI type |
| street | string | No | - | Street name and number |
| city | string | No | - | City name |
| county | string | No | - | County name |
| state | string | No | - | State or province |
| country | string | No | - | Country name or code |
| postalcode | string | No | - | Postal/ZIP code |
| limit | int | No | 10 | Maximum results (1-50) |
| include_photos | bool | No | false | Include street-level imagery |
| photo_radius | int | No | 100 | Photo search radius in meters (10-500) |
| mode | string | No | "basic" | "basic" or "advanced" search depth |

*Either `query` or at least one address component is required.

## Response Format

```json
[
  {
    "display_name": "Eiffel Tower, 5 Avenue Anatole France, 75007 Paris, France",
    "lat": 48.8584,
    "lon": 2.2945,
    "type": "tourism",
    "importance": 0.95,
    "address": {
      "tourism": "Eiffel Tower",
      "road": "Avenue Anatole France",
      "city": "Paris",
      "country": "France",
      "postcode": "75007"
    },
    "photos": [
      {
        "url": "https://...",
        "lat": 48.8580,
        "lon": 2.2948,
        "heading": 45
      }
    ],
    "has_street_imagery": true
  }
]
```

## Examples

### Geocode an address
```bash
./scripts/places.sh '{"street": "350 Fifth Avenue", "city": "New York", "state": "NY"}'
```

### Find a landmark with photos
```bash
./scripts/places.sh '{"query": "Statue of Liberty", "include_photos": true, "photo_radius": 200}'
```

### Search by postal code
```bash
./scripts/places.sh '{"postalcode": "90210", "country": "USA"}'
```

### Advanced mode for richer data
```bash
./scripts/places.sh '{"query": "Times Square", "mode": "advanced", "include_photos": true}'
```

## Best Practices

- Use `query` for landmarks, POIs, and well-known places
- Use structured address fields for precise geocoding
- Enable `include_photos` when you need visual context
- Use `mode: "advanced"` for web-enriched place data
- Combine address components for more accurate results
