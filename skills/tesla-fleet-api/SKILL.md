---
name: tesla-fleet-api
description: Use when integrating with Tesla's official Fleet API to read vehicle/energy device data or issue remote commands (e.g. start HVAC preconditioning, wake vehicle, charge controls). Covers onboarding (developer app registration, regions/base URLs), OAuth token flows (third-party + partner tokens, refresh rotation), required domain/public-key hosting, and using Tesla's official vehicle-command/tesla-http-proxy for signed vehicle commands.
version: 1.1.3
metadata: {"clawdbot":{"requires":{"bins":["python3"]}}}
---

# Tesla Fleet API

Control Tesla vehicles via the official Fleet API.

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `command.py` | Vehicle commands (climate, charging, locks, etc.) |
| `vehicle_data.py` | Read vehicle data (battery, climate, location, etc.) |
| `vehicles.py` | List vehicles + refresh cache |
| `auth.py` | Authentication and configuration |
| `tesla_oauth_local.py` | OAuth helper with local callback server |

---

## Setup / Configuration

Setup is documented in **`SETUP.md`**:

- [SETUP.md](SETUP.md)

(It covers `.env`, `config.json`/`auth.json`, proxy setup, and key enrollment.)

---

## command.py — Vehicle Commands

Execute commands on your Tesla. Vehicle is auto-selected if you only have one.

### Usage

```bash
command.py [VEHICLE] <command> [options]
```

- `VEHICLE` — Vehicle name or VIN (optional if single vehicle)
- Commands can be run without specifying vehicle: `command.py honk`
- Or with vehicle name: `command.py flash honk` (vehicle "flash", command "honk")

---

### Climate Control

#### Start/Stop Climate
```bash
command.py climate start
command.py climate stop
command.py flash climate start          # specific vehicle
```

#### Set Temperature
```bash
command.py climate temps <driver_temp> [passenger_temp]
command.py climate temps 21             # both seats 21°C
command.py climate temps 22 20          # driver 22°C, passenger 20°C
```

#### Climate Keeper Mode
```bash
command.py climate keeper <mode>
```
Modes: `off`, `keep`, `dog`, `camp`

---

### Seat Heater

```bash
command.py seat-heater --level <level> [--position <position>]
command.py seat-heater -l <level> [-p <position>]
```

**Levels:**
| Value | Name |
|-------|------|
| 0 | off |
| 1 | low |
| 2 | medium |
| 3 | high |

**Positions:**
| Value | Names |
|-------|-------|
| 0 | `driver`, `front_left`, `fl` |
| 1 | `passenger`, `front_right`, `fr` |
| 2 | `rear_left`, `rl` |
| 3 | `rear_left_back` |
| 4 | `rear_center`, `rc` |
| 5 | `rear_right`, `rr` |
| 6 | `rear_right_back` |
| 7 | `third_left` |
| 8 | `third_right` |

**Examples:**
```bash
command.py seat-heater -l high                    # driver (default)
command.py seat-heater -l medium -p passenger
command.py seat-heater --level low --position rear_left
command.py seat-heater -l 2 -p 4                  # medium, rear center
command.py seat-heater -l off -p driver           # turn off
```

---

### Seat Cooler (Ventilation)

```bash
command.py seat-cooler --level <level> [--position <position>]
command.py seat-cooler -l <level> [-p <position>]
```

Same levels and positions as seat heater.

**Examples:**
```bash
command.py seat-cooler -l medium -p driver
command.py seat-cooler -l high -p passenger
```

---

### Seat Auto Climate

```bash
command.py seat-climate [--position <position>] <mode>
command.py seat-climate [-p <position>] <mode>
```

Modes: `auto`, `on`, `off`

**Examples:**
```bash
command.py seat-climate auto                      # driver auto
command.py seat-climate -p passenger auto
command.py seat-climate -p driver off             # disable auto
```

---

### Steering Wheel Heater

```bash
command.py steering-heater <on|off>
```

**Examples:**
```bash
command.py steering-heater on
command.py steering-heater off
```

---

### Precondition Schedules

Modern API for scheduling departure preconditioning (replaces deprecated `set_scheduled_departure`).

#### Add Schedule
```bash
command.py precondition add --time <HH:MM> [--days <days>] [--id <id>] [--one-time] [--disabled]
command.py precondition add -t <HH:MM> [-d <days>] [--id <id>]
```

**Days options:**
| Value | Description |
|-------|-------------|
| `all` | Every day (default) |
| `weekdays` | Monday through Friday |
| `weekends` | Saturday and Sunday |
| `mon,tue,wed,...` | Specific days (comma-separated) |

Day names: `sun`, `mon`, `tue`, `wed`, `thu`, `fri`, `sat` (or full names)

**Examples:**
```bash
command.py precondition add -t 08:00              # every day at 8am
command.py precondition add -t 08:00 -d weekdays  # Mon-Fri
command.py precondition add -t 07:30 -d mon,wed,fri
command.py precondition add -t 09:00 --one-time   # one-time only
command.py precondition add -t 08:30 --id 123     # modify existing schedule
command.py precondition add -t 08:00 --disabled   # create but disabled
```

#### Remove Schedule
```bash
command.py precondition remove --id <id>
```

**Examples:**
```bash
command.py precondition remove --id 123
command.py precondition remove --id 1
```

---

### Charging Control

#### Start/Stop Charging
```bash
command.py charge start
command.py charge stop
```

#### Set Charge Limit
```bash
command.py charge limit <percent>
```

Percent must be 50-100.

**Examples:**
```bash
command.py charge limit 80
command.py charge limit 90
command.py flash charge limit 70                  # specific vehicle
```

---

### Doors & Security

```bash
command.py lock                   # lock all doors
command.py unlock                 # unlock all doors
command.py honk                   # honk the horn
command.py flash                  # flash the lights
command.py wake                   # wake vehicle from sleep
```

**With vehicle name:**
```bash
command.py flash wake             # wake vehicle named "flash"
command.py flash flash            # flash lights on vehicle "flash"
```

---

## vehicle_data.py — Read Vehicle Data

Fetch vehicle data with human-readable output by default.

### Usage

```bash
vehicle_data.py [VEHICLE] [flags] [--json]
```

- `VEHICLE` — Vehicle name or VIN (optional if single vehicle)
- No flags = all data
- `--json` = raw JSON output

### Flags

| Flag | Long | Data |
|------|------|------|
| `-c` | `--charge` | Battery level, charge limit, charging status |
| `-t` | `--climate` | Interior/exterior temp, HVAC status |
| `-d` | `--drive` | Gear, speed, power, heading |
| `-l` | `--location` | GPS coordinates |
| `-s` | `--state` | Locks, doors, windows, odometer, software |
| `-g` | `--gui` | GUI settings (units, 24h time) |
| | `--config-data` | Vehicle config (model, color, wheels) |

### Examples

```bash
# All data
vehicle_data.py
vehicle_data.py flash

# Specific data
vehicle_data.py -c                        # charge only
vehicle_data.py -c -t                     # charge + climate
vehicle_data.py flash -c -l               # charge + location

# Raw JSON
vehicle_data.py --json
vehicle_data.py -c --json
```

### Sample Output

```
🚗 My Tesla (online)
   VIN: 5YJ... (redacted)

⚡ Charge State
────────────────────────────────────────
  Battery:    [███████████████░░░░░] 78%
  Limit:      80%
  State:      Charging
  Power:      11 kW (16A × 234V × 3φ)
  Added:      37.2 kWh
  Remaining:  10m
  Range:      438 km (272 mi)
  Cable:      IEC

🌡️  Climate State
────────────────────────────────────────
  Inside:     11.9°C
  Outside:    6.0°C
  Set to:     20.5°C
  Climate:    Off
```

---

## auth.py — Authentication

Manage OAuth tokens and configuration.

### Usage

```bash
auth.py <command> [options]
```

### Commands

#### Login (OAuth Flow)
```bash
auth.py login
```
Interactive: generates auth URL, prompts for code, exchanges for tokens.

#### Exchange Code
```bash
auth.py exchange <code>
```
Exchange authorization code for tokens (non-interactive).

#### Refresh Tokens
```bash
auth.py refresh
```
Refresh access token. Note: refresh tokens rotate — the new one is saved automatically.

#### Register Domain
```bash
auth.py register --domain <domain>
```
Register your app domain with Tesla (required for signed commands).

After registration, enroll your virtual key:
```
https://tesla.com/_ak/<domain>
```

#### Show Config
```bash
auth.py config
```
Display current configuration (secrets redacted).

#### Set Config
```bash
auth.py config set [options]
```

Options:
- `--client-id <id>`
- `--client-secret <secret>`
- `--redirect-uri <uri>`
- `--audience <url>`
- `--base-url <url>`
- `--ca-cert <path>`
- `--domain <domain>`

**Examples:**
```bash
# Initial setup
auth.py config set \
  --client-id "abc123" \
  --client-secret "secret" \
  --redirect-uri "http://localhost:18080/callback"

# Configure proxy
auth.py config set \
  --base-url "https://localhost:4443" \
  --ca-cert "/path/to/tls-cert.pem"
```

---

## tesla_fleet.py — List Vehicles

List vehicles with human-readable output.

```bash
python3 scripts/tesla_fleet.py vehicles
python3 scripts/tesla_fleet.py vehicles --json
```

### Sample Output

```
🚗 Name:   My Tesla
🔖 VIN:    5YJ... (redacted)
🟢 Status: Online
👤 Access: Owner
```

---

## Configuration / Proxy / File layout

All setup + configuration is documented in **[SETUP.md](SETUP.md)**.

---

## Regional Base URLs

| Region | Audience URL |
|--------|--------------|
| Europe | `https://fleet-api.prd.eu.vn.cloud.tesla.com` |
| North America | `https://fleet-api.prd.na.vn.cloud.tesla.com` |
| China | `https://fleet-api.prd.cn.vn.cloud.tesla.cn` |

OAuth token endpoint (all regions):
```
https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token
```

---

## Troubleshooting

### "vehicle unavailable: vehicle is offline or asleep"
Wake the vehicle first:
```bash
command.py wake
```

### "command not signed" / "vehicle rejected"
Ensure the proxy is running and configured:
```bash
./scripts/start_proxy.sh <private-key.pem>
auth.py config set --base-url "https://localhost:4443" --ca-cert "<tls-cert.pem>"
```

### Token expired
```bash
auth.py refresh
```

### Multiple vehicles
Specify vehicle by name or VIN:
```bash
command.py flash climate start
command.py 5YJ... honk
```

---

## Complete Command Reference

### command.py

```
climate start|stop
climate temps <driver> [passenger]
climate keeper off|keep|dog|camp

seat-heater -l <level> [-p <position>]
seat-cooler -l <level> [-p <position>]
seat-climate [-p <position>] auto|on|off

steering-heater on|off

precondition add -t <HH:MM> [-d <days>] [--id <id>] [--one-time]
precondition remove --id <id>

charge start|stop
charge limit <percent>

lock
unlock
honk
flash
wake
```

### vehicle_data.py

```
[VEHICLE] [-c] [-t] [-d] [-l] [-s] [-g] [--config-data] [--json]
```

### auth.py

```
login
exchange <code>
refresh
register --domain <domain>
config
config set [--client-id] [--client-secret] [--redirect-uri] [--audience] [--base-url] [--ca-cert] [--domain]
```
