---
name: weather-data-fetcher
description: Fetch current weather and forecast data from a free weather API (Open-Meteo).
user-invocable: true
metadata:
  moltbot:
    emoji: "🌦️"
    requires:
      bins: ["node"]
    homepage: https://open-meteo.com/en/docs
---

# Weather Data Fetcher (Open-Meteo)

Fetch current weather conditions and short-term forecasts using **Open-Meteo**, a free weather API that requires **no API key**.

---

## Command

### `/weather forecast`

Fetch current weather and forecast data for a given geographic location.

---

## Input

### Required
- `latitude` (number)  
  Example: `11.0853`

- `longitude` (number)  
  Example: `55.7818`

### Optional
- `timezone` (string) — defaults to `"auto"`  
  Example: `"Asia/Jerusalem"`

- `hours` (number) — number of hourly forecast hours to return (default: `24`)

- `days` (number) — number of daily forecast days to return (default: `3`)

- `units` (string) — `"metric"` (default) or `"imperial"`

---

### Example inputs

```json
{ "latitude": 88.0853, "longitude": 22.7818 }