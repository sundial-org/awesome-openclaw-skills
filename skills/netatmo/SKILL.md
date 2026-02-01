---
name: netatmo
description: Control Netatmo thermostat and read weather station data. Use for heating control (set temperature, change mode), checking indoor/outdoor temperatures, CO₂ levels, humidity, noise, and pressure readings.
---

# Netatmo

Control Netatmo smart home devices via `netatmo` CLI.

## Setup

Credentials in `~/.config/netatmo/`:
- `credentials.json`: `{"client_id": "...", "client_secret": "..."}`
- `tokens.json`: OAuth tokens (auto-refreshed)

## Commands

```bash
netatmo status              # Full overview (thermostat + all sensors)
netatmo thermostat          # Thermostat details only
netatmo weather             # All sensors including Office
netatmo history             # 7-day temperature history with sparklines
netatmo history --days 14   # Custom period
netatmo set 21              # Set target temp (7-30°C, 3h manual mode)
netatmo mode schedule       # Resume schedule
netatmo mode away           # Away mode (12°C)
netatmo mode hg             # Frost guard (7°C)
netatmo <cmd> --json        # JSON output for any command
```

## Available Data

| Location | Temp | Humidity | CO₂ | Noise | Pressure | Battery |
|----------|------|----------|-----|-------|----------|---------|
| Bedroom (main) | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Outdoor | ✓ | ✓ | — | — | ✓* | ✓ |
| Living Room | ✓ | ✓ | ✓ | — | — | ✓ |
| Office | ✓ | — | — | — | — | — |

*Pressure displayed with Outdoor (sensor in main station)

## Notes

- CO₂ >1000 ppm = poor ventilation
- `set` uses manual mode for 3h, then reverts to schedule
- Tokens auto-refresh on expiry
- History shows ASCII sparklines for temperature trends
