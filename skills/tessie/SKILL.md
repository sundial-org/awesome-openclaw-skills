---
name: tessie
---

# Tessie Skill

Control your Tesla vehicles via Tessie API - a Tesla management platform with 500,000+ users.

## Setup

Get your Tessie API credentials:
1. Go to https://tessie.com/developers
2. Sign up and create an API key
3. Configure in Clawdbot:

```yaml
skills:
  entries:
    tessie:
      apiKey: "your-tessie-api-key-here"
```

Or via environment variable:
```bash
export TESSIE_API_KEY="your-tessie-api-key-here"
```

**Note**: Vehicle ID and VIN are auto-detected from API. No manual configuration needed.

## Capabilities

### Vehicle Status
- **Battery level**: Current state of charge percentage
- **Range**: Estimated driving range
- **Location**: Current vehicle coordinates
- **Vehicle state**: Locked/unlocked, charging status, sleep mode
- **Connection**: Is the car online/offline?

### Climate Control
- **Start/stop**: Turn climate on or off
- **Preheat/precool**: Set cabin temperature (auto-detects Fahrenheit/Celsius)
- **Defrost**: Defrost windows/mirrors

### Charging
- **Start/stop**: Control charging remotely
- **Charge limit**: Set daily/standard charge limit
- **Charging status**: Current rate, time to complete, battery level

### Drives
- **Recent drives**: Last trips with distance, energy, locations

## Usage Examples

```
# Check battery and range
"tessie battery"
"tessie how much charge"
"tessie range"

# Preheat the car (assumes Fahrenheit if > 50)
"tessie preheat 72"
"tessie precool"
"tessie turn on climate"

# Check drives
"tessie show my drives"
"tessie recent drives"
"tessie drives 5"

# Charging commands
"tessie start charging"
"tessie stop charging"
"tessie set charge limit to 90%"
"tessie charging status"

# Vehicle location
"tessie where is my car"
"tessie location"

# Vehicle state
"tessie is the car locked?"
"tessie vehicle status"
```

## API Endpoints (Tessie)

### Authentication
All requests require:
```
Authorization: Bearer <api-key>
```

### Get Vehicles
```
GET https://api.tessie.com/vehicles
```
Returns full vehicle list with `last_state` embedded

### Get Drives
```
GET https://api.tessie.com/{VIN}/drives?limit=10
```
Returns recent drive history

### Get Idles
```
GET https://api.tessie.com/{VIN}/idles?limit=10
```
Returns parked sessions with climate/sentry usage

### Commands
All control commands use VIN (not vehicle_id):
```
POST https://api.tessie.com/{VIN}/command/{command}
```

**Available commands**:
- `start_climate`, `stop_climate`, `set_temperatures`
- `start_charging`, `stop_charging`, `set_charge_limit`
- `lock`, `unlock`, `enable_sentry`, `disable_sentry`
- `activate_front_trunk`, `activate_rear_trunk`
- `open_windows`, `close_windows`, `vent_windows`

Full list: See https://developer.tessie.com

## Notes

- Tessie acts as a middleman between you and Tesla's API
- Provides richer data and analytics than raw Tesla API
- Requires Tesla account to be linked to Tessie first
- API uses VIN for commands (auto-detected)
- All temperatures in Celsius internally
- **NOT YET DEPLOYED** - Prepared for deployment pending user review
