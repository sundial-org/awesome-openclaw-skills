# My Tesla

Tesla control skill for Clawdbot.

Author: Parth Maniar — [@officialpm](https://github.com/officialpm)

## What’s inside

- `SKILL.md` — the skill instructions
- `scripts/tesla.py` — the CLI implementation (teslapy)
- `VERSION` + `CHANGELOG.md` — versioning for ClawdHub publishing

## Install / auth

Set `TESLA_EMAIL` and run:

```bash
TESLA_EMAIL="you@email.com" python3 scripts/tesla.py auth
```

This uses a browser-based login flow and stores tokens locally in `~/.tesla_cache.json` (best-effort chmod `0600`).

Optional defaults:
- `MY_TESLA_DEFAULT_CAR` — default vehicle display name (overrides `default-car` setting)
- `python3 scripts/tesla.py default-car "Name"` stores a local default in `~/.my_tesla.json` (best-effort chmod `0600`)

## Usage

```bash
# List vehicles (shows which one is default)
python3 scripts/tesla.py list
python3 scripts/tesla.py list --json   # machine-readable, privacy-safe

# Version
python3 scripts/tesla.py version
python3 scripts/tesla.py --version

# Debugging
# If something fails unexpectedly, add --debug for a full traceback
# (or set MY_TESLA_DEBUG=1)
python3 scripts/tesla.py --debug status --no-wake

# Pick a car (optional)
# --car accepts: exact name, partial name (substring match), or a 1-based index from `list`
python3 scripts/tesla.py --car "Model" report
python3 scripts/tesla.py --car 1 status

# Set default car (used when you don't pass --car)
python3 scripts/tesla.py default-car "My Model 3"

# One-line summary (best for chat)
python3 scripts/tesla.py summary
python3 scripts/tesla.py summary --no-wake   # don't wake a sleeping car

# Summary as JSON (privacy-safe)
# Unlike `status --json`, this emits a small sanitized object (no location).
# Includes `usable_level_percent` when the vehicle reports it.
python3 scripts/tesla.py summary --json
python3 scripts/tesla.py summary --json --raw-json   # raw vehicle_data (may include location)

# One-screen report (chat friendly, more detail)
# Includes battery/charging/climate + charge port/cable + (when available) TPMS tire pressures.
# Includes "Usable battery" when the vehicle reports it (helpful for health/degradation).
# Also includes a quick openings summary (doors/trunk/frunk/windows) when the vehicle reports it.
# When available, includes a compact seat heater summary line.
# When actively charging, also shows charging power details when available (kW / V / A).
# When the vehicle reports it, includes scheduled departure / preconditioning / off-peak charging status.
python3 scripts/tesla.py report
python3 scripts/tesla.py report --no-wake

# Detailed status
python3 scripts/tesla.py status
python3 scripts/tesla.py status --no-wake
python3 scripts/tesla.py status --summary   # include one-line summary + detailed output

# JSON output (prints ONLY JSON; good for piping/parsing)
# NOTE: `status --json` outputs *raw* `vehicle_data`, which may include location/drive_state.
# Prefer `summary --json` (sanitized) or `report --json` (sanitized) unless you explicitly need the raw payload.
python3 scripts/tesla.py summary --json              # sanitized summary object (no location)
python3 scripts/tesla.py report --json               # sanitized report object (no location)
python3 scripts/tesla.py status --json               # raw vehicle_data (may include location)
python3 scripts/tesla.py report --json --raw-json    # raw vehicle_data (may include location)
python3 scripts/tesla.py summary --json --raw-json   # raw vehicle_data (may include location)
python3 scripts/tesla.py charge status --json   # includes usable battery + (when charging) power details (kW/V/A)

python3 scripts/tesla.py --car "My Model 3" lock
# Climate (status is read-only)
python3 scripts/tesla.py climate status
python3 scripts/tesla.py climate status --no-wake
python3 scripts/tesla.py climate on
python3 scripts/tesla.py climate off
python3 scripts/tesla.py climate defrost on
python3 scripts/tesla.py climate defrost off
python3 scripts/tesla.py climate temp 72      # default: °F
python3 scripts/tesla.py climate temp 22 --celsius
python3 scripts/tesla.py charge limit 80 --yes   # 50–100
python3 scripts/tesla.py charge amps 16 --yes     # 1–48 (conservative guardrail)

# Scheduled charging (set/off are safety gated)
python3 scripts/tesla.py scheduled-charging status
python3 scripts/tesla.py scheduled-charging set 23:30 --yes
python3 scripts/tesla.py scheduled-charging off --yes

# Scheduled departure (read-only)
python3 scripts/tesla.py scheduled-departure status
python3 scripts/tesla.py scheduled-departure status --no-wake
python3 scripts/tesla.py --json scheduled-departure status

# Trunk / frunk (safety gated)
python3 scripts/tesla.py trunk trunk --yes
python3 scripts/tesla.py trunk frunk --yes

# Windows
python3 scripts/tesla.py windows status
python3 scripts/tesla.py windows status --no-wake
python3 scripts/tesla.py windows status --json

# Windows (safety gated)
python3 scripts/tesla.py windows vent  --yes
python3 scripts/tesla.py windows close --yes

# Seat heaters
python3 scripts/tesla.py seats status
python3 scripts/tesla.py seats status --no-wake
python3 scripts/tesla.py seats status --json

# Seat heaters (safety gated)
# seat: driver|passenger|rear-left|rear-center|rear-right|3rd-left|3rd-right (or 0–6)
# level: 0–3 (0=off)
python3 scripts/tesla.py seats set driver 3 --yes

# Charge port door
python3 scripts/tesla.py charge-port status
python3 scripts/tesla.py charge-port status --no-wake
python3 scripts/tesla.py charge-port status --json

# Charge port door open/close (safety gated)
python3 scripts/tesla.py charge-port open  --yes
python3 scripts/tesla.py charge-port close --yes

# Sentry Mode (status is read-only; on/off safety gated)
python3 scripts/tesla.py sentry status
python3 scripts/tesla.py sentry status --no-wake
python3 scripts/tesla.py sentry on  --yes
python3 scripts/tesla.py sentry off --yes

# Location (approx by default; use --yes for precise coordinates)
python3 scripts/tesla.py location
python3 scripts/tesla.py location --no-wake
python3 scripts/tesla.py location --digits 1   # coarser rounding
python3 scripts/tesla.py location --digits 3   # a bit more precise (still approximate)
python3 scripts/tesla.py location --yes

# Tire pressures (TPMS)
python3 scripts/tesla.py tires
python3 scripts/tesla.py tires --no-wake

# Openings (doors/trunks/windows)
python3 scripts/tesla.py openings
python3 scripts/tesla.py openings --no-wake
python3 scripts/tesla.py openings --json

# Mileage tracking (odometer) — local SQLite
python3 scripts/tesla.py mileage init
python3 scripts/tesla.py mileage record --no-wake --auto-wake-after-hours 24
python3 scripts/tesla.py mileage status
python3 scripts/tesla.py mileage export --format csv > mileage.csv
python3 scripts/tesla.py mileage export --format json > mileage.json

# Export a time window
python3 scripts/tesla.py mileage export --format csv --since-days 7 > mileage_last_7d.csv
python3 scripts/tesla.py mileage export --format json --since-ts 1738195200 > mileage_since_ts.json
```

## Mileage tracking (hourly)

This feature records each vehicle’s **odometer miles** to a **local SQLite database** so we can build analytics later.

Defaults:
- DB path: `~/.my_tesla/mileage.sqlite` (override with `MY_TESLA_MILEAGE_DB` or `mileage --db ...`)
- Wake behavior: **no wake by default**. The recorder will only allow waking a car **if it hasn’t recorded mileage in 24h**.

### Quick start
```bash
python3 scripts/tesla.py mileage init
python3 scripts/tesla.py mileage record --no-wake --auto-wake-after-hours 24
python3 scripts/tesla.py mileage status
```

### Run every hour (macOS launchd example)
Create `~/Library/LaunchAgents/com.mytesla.mileage.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key><string>com.mytesla.mileage</string>
    <key>StartInterval</key><integer>3600</integer>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>/ABS/PATH/TO/scripts/tesla.py</string>
      <string>mileage</string>
      <string>record</string>
      <string>--no-wake</string>
      <string>--auto-wake-after-hours</string><string>24</string>
      <string>--json</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
      <key>TESLA_EMAIL</key><string>you@email.com</string>
    </dict>
    <key>StandardOutPath</key><string>~/.my_tesla/mileage.log</string>
    <key>StandardErrorPath</key><string>~/.my_tesla/mileage.err.log</string>
  </dict>
</plist>
```
Load it:
```bash
launchctl load -w ~/Library/LaunchAgents/com.mytesla.mileage.plist
```

## Tests

```bash
# (Recommended) avoid writing __pycache__/ bytecode files into the repo
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v

# Or use the helper (cleans stray bytecode first and fails if any is produced):
./scripts/run_tests.sh
```

## Privacy / safety

- Never commit tokens, VINs, or location outputs.
- Some commands (unlock/charge start|stop|limit|amps/trunk/windows/seats set/sentry on|off/honk/flash/charge-port open|close/scheduled-charging set|off) require `--yes`.
- Read-only commands support `--no-wake` to avoid waking the car (will fail if the vehicle is asleep/offline).
- `location` shows *approximate* coords by default; add `--yes` for precise coordinates.
