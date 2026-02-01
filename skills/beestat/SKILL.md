---
name: beestat
description: Query ecobee thermostat data via Beestat API including temperature, humidity, air quality (CO2, VOC), sensors, and HVAC runtime. Use when user asks about home temperature, thermostat status, air quality, or heating/cooling usage.
homepage: https://beestat.io
metadata:
  clawdbot:
    emoji: "🌡️"
    requires:
      bins: ["beestat"]
      env: ["BEESTAT_API_KEY"]
---

# Beestat CLI

CLI for the Beestat API (ecobee thermostat analytics). Query temperature, humidity, air quality, and HVAC runtime.

## Installation

```bash
npm install -g beestat-cli
```

## Setup

1. Create account at [beestat.io](https://beestat.io) and link your ecobee
2. Email contact@beestat.io with your thermostat serial number to get an API key
3. Set environment variable: `export BEESTAT_API_KEY="your-key"`

## Commands

### Status

```bash
beestat status             # Current temps, humidity, setpoints, weather
beestat status --json
```

### Sensors

```bash
beestat sensors            # All sensors with temperature and occupancy
beestat sensors --json
```

### Air Quality

```bash
beestat air-quality        # CO2, VOC, and air quality score
beestat aq                 # Short alias
beestat aq --json
```

Requires ecobee Smart Thermostat Premium (has built-in air quality sensors).

**CO2 Levels:**
- < 800 ppm: Excellent
- 800-1000 ppm: Good
- 1000-1500 ppm: Fair (consider ventilation)
- > 1500 ppm: High (ventilate!)

**VOC Levels:**
- < 0.5 ppm: Excellent
- 0.5-1.0 ppm: Good
- 1.0-3.0 ppm: Fair
- > 3.0 ppm: High

### Thermostats

```bash
beestat thermostats        # Model info, HVAC details
beestat thermostats --json
```

### Runtime Summary

```bash
beestat summary            # Runtime history (default 7 days)
beestat summary --days 14  # Last 14 days
beestat summary --json
```

### Force Sync

```bash
beestat sync               # Force sync with ecobee
```

## Usage Examples

**User: "What's the temperature in the house?"**
```bash
beestat status
```

**User: "Is the air quality okay?"**
```bash
beestat aq
```

**User: "Is anyone in the bedrooms?"**
```bash
beestat sensors
```

**User: "How much did we heat the house this week?"**
```bash
beestat summary --days 7
```

**User: "What thermostats do we have?"**
```bash
beestat thermostats
```

## Notes

- Air quality data comes from ecobee runtime, not sensor capabilities
- All commands support `--json` for scripting/automation
- Use `beestat sync` if data seems stale
