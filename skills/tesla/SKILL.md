---
name: tesla
description: Control your Tesla vehicles - lock/unlock, climate, location, charge status, and more. Supports multiple vehicles.
homepage: https://tesla-api.timdorr.com
metadata: {"clawdbot":{"emoji":"🚗","requires":{"env":["TESLA_EMAIL"]}}}
---

# Tesla

Control your Tesla vehicles from Clawdbot. Supports multiple cars on one account.

## Setup

### First-time authentication:

```bash
TESLA_EMAIL="you@email.com" python3 {baseDir}/scripts/tesla.py auth
```

This will:
1. Display a Tesla login URL
2. You log in and authorize in browser
3. Paste the callback URL back
4. Token cached for future use (~30 days, auto-refreshes)

### Environment variables:

- `TESLA_EMAIL` — Your Tesla account email
- Token cached in `~/.tesla_cache.json`

## Multi-Vehicle Support

Use `--car` or `-c` to specify which vehicle:

```bash
# List all vehicles
python3 {baseDir}/scripts/tesla.py list

# Commands for specific car
python3 {baseDir}/scripts/tesla.py --car "Snowflake" status
python3 {baseDir}/scripts/tesla.py -c "Stella" lock
```

Without `--car`, commands target your first vehicle.

## Commands

```bash
# List all vehicles
python3 {baseDir}/scripts/tesla.py list

# Get vehicle status
python3 {baseDir}/scripts/tesla.py status
python3 {baseDir}/scripts/tesla.py --car "Stella" status

# Lock/unlock
python3 {baseDir}/scripts/tesla.py lock
python3 {baseDir}/scripts/tesla.py unlock

# Climate
python3 {baseDir}/scripts/tesla.py climate on
python3 {baseDir}/scripts/tesla.py climate off
python3 {baseDir}/scripts/tesla.py climate temp 72

# Charging
python3 {baseDir}/scripts/tesla.py charge status
python3 {baseDir}/scripts/tesla.py charge start
python3 {baseDir}/scripts/tesla.py charge stop

# Location
python3 {baseDir}/scripts/tesla.py location

# Honk & flash
python3 {baseDir}/scripts/tesla.py honk
python3 {baseDir}/scripts/tesla.py flash

# Wake up (if asleep)
python3 {baseDir}/scripts/tesla.py wake
```

## Example Chat Usage

- "Is my Tesla locked?"
- "Lock Stella"
- "What's Snowflake's battery level?"
- "Where's my Model X?"
- "Turn on the AC in Stella"
- "Honk the horn on Snowflake"

## API Reference

Uses the unofficial Tesla Owner API documented at:
https://tesla-api.timdorr.com

## Privacy & Security

- Credentials stored locally only
- Refresh token cached in `~/.tesla_cache.json`
- No data sent to third parties
- Tokens auto-refresh for ~30 days
