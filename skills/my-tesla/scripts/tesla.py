#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "teslapy>=2.0.0",
# ]
# ///
"""
Tesla vehicle control via unofficial API.
Supports multiple vehicles.
"""

import argparse
import json
import os
import sys
import sqlite3
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Keep the repo clean: don't write __pycache__/ bytecode files when running the CLI.
# (Also helps keep private repos from accumulating noisy artifacts.)
sys.dont_write_bytecode = True

CACHE_FILE = Path.home() / ".tesla_cache.json"
DEFAULTS_FILE = Path.home() / ".my_tesla.json"
SKILL_DIR = Path(__file__).resolve().parent.parent


def _invocation(extra: str = "") -> str:
    """Return a copy/pastable invocation string for help/error messages.

    Use the absolute path to this script so the suggestion works even when the
    current working directory is not the repo root.
    """
    prog = str(Path(__file__).resolve())
    return f"python3 {prog}{(' ' + extra) if extra else ''}"


def read_skill_version() -> str:
    """Read the skill version from VERSION.txt/VERSION in the repo.

    ClawdHub ignores extensionless files like `VERSION`, so published artifacts
    also include `VERSION.txt`. Prefer VERSION.txt when present.
    """
    for name in ("VERSION.txt", "VERSION"):
        p = SKILL_DIR / name
        try:
            if p.exists():
                v = p.read_text().strip()
                if v:
                    return v
        except Exception:
            continue
    return "(unknown)"


def resolve_email(args, prompt: bool = True) -> str:
    """Resolve Tesla account email from args/env, optionally prompting."""
    email = getattr(args, "email", None) or os.environ.get("TESLA_EMAIL")
    if isinstance(email, str) and email.strip():
        return email.strip()
    if not prompt:
        return None
    return input("Tesla email: ").strip()


def require_email(args) -> str:
    """Require a Tesla email to be provided via --email or TESLA_EMAIL."""
    email = resolve_email(args, prompt=False)
    if not email:
        print(
            "❌ Missing Tesla email. Set TESLA_EMAIL or pass --email\n"
            f"   Example: TESLA_EMAIL=\"you@email.com\" {_invocation('list')}",
            file=sys.stderr,
        )
        sys.exit(2)
    return email


def get_tesla(email: str):
    """Get authenticated Tesla instance."""
    import teslapy
    
    def custom_auth(url):
        print(f"\n🔐 Open this URL in your browser:\n{url}\n")
        print("Log in to Tesla, then paste the final URL here")
        print("(it will start with https://auth.tesla.com/void/callback?...)")
        return input("\nCallback URL: ").strip()
    
    tesla = teslapy.Tesla(email, authenticator=custom_auth, cache_file=str(CACHE_FILE))
    
    if not tesla.authorized:
        tesla.fetch_token()
        print("✅ Authenticated successfully!")

    # Best-effort: keep the local OAuth cache file private.
    if CACHE_FILE.exists():
        _chmod_0600(CACHE_FILE)

    return tesla


def load_defaults():
    """Load optional user defaults from ~/.my_tesla.json (local only)."""
    try:
        if DEFAULTS_FILE.exists():
            return json.loads(DEFAULTS_FILE.read_text())
    except Exception:
        pass
    return {}


def _chmod_0600(path: Path):
    """Best-effort: set file permissions to user read/write only."""
    try:
        path.chmod(0o600)
    except Exception:
        # Non-POSIX FS or permission error; ignore.
        pass


def save_defaults(obj: dict):
    # Defaults can include human-readable vehicle names; keep them private.
    DEFAULTS_FILE.write_text(json.dumps(obj, indent=2) + "\n")
    _chmod_0600(DEFAULTS_FILE)


def resolve_default_car_name():
    # Highest priority: env var
    env_name = os.environ.get("MY_TESLA_DEFAULT_CAR")
    if env_name:
        return env_name.strip()

    defaults = load_defaults()
    name = defaults.get("default_car")
    return name.strip() if isinstance(name, str) and name.strip() else None


def _select_vehicle(vehicles, target_name: str):
    """Select a vehicle from a list by name (exact/partial) or 1-based index.

    - Exact match is case-insensitive.
    - If no exact match, a case-insensitive *substring* match is attempted.
    - If target_name is a digit (e.g., "1"), it's treated as a 1-based index.
    """
    if not vehicles:
        return None

    if not target_name:
        return vehicles[0]

    s = target_name.strip()
    if s.isdigit():
        idx = int(s) - 1
        if 0 <= idx < len(vehicles):
            return vehicles[idx]
        return None

    s_l = s.lower()

    # 1) Exact match (case-insensitive)
    for v in vehicles:
        if v.get('display_name', '').lower() == s_l:
            return v

    # 2) Substring match (case-insensitive)
    matches = [v for v in vehicles if s_l in v.get('display_name', '').lower()]
    if len(matches) == 1:
        return matches[0]

    # Ambiguous / not found
    return None


def get_vehicle(tesla, name: str = None):
    """Get vehicle by name/index, else default car, else first vehicle."""
    vehicles = tesla.vehicle_list()
    if not vehicles:
        print("❌ No vehicles found on this account", file=sys.stderr)
        sys.exit(1)

    target_name = name or resolve_default_car_name()

    if target_name:
        selected = _select_vehicle(vehicles, target_name)
        if selected:
            return selected

        # Give a more helpful error (and show numeric indices too).
        s = str(target_name).strip()
        ambiguous = False
        matches = []
        if s and not s.isdigit():
            s_l = s.lower()
            matches = [
                (i + 1, v) for i, v in enumerate(vehicles)
                if s_l in v.get('display_name', '').lower()
            ]
            ambiguous = len(matches) > 1

        options = "\n".join(
            f"   {i+1}. {v.get('display_name')}" for i, v in enumerate(vehicles)
        )

        if ambiguous:
            match_lines = "\n".join(
                f"   {idx}. {v.get('display_name')}" for idx, v in matches
            )
            print(
                f"❌ Vehicle '{target_name}' is ambiguous (matched multiple vehicles).\n"
                "   Tip: use a more specific name, or choose by index: --car <N>\n"
                f"Matches:\n{match_lines}\n\n"
                f"All vehicles:\n{options}",
                file=sys.stderr,
            )
        else:
            print(
                f"❌ Vehicle '{target_name}' not found.\n"
                "   Tip: you can pass --car with a partial name (substring match) or a 1-based index.\n"
                f"Available vehicles:\n{options}",
                file=sys.stderr,
            )
        sys.exit(1)

    return vehicles[0]


def wake_vehicle(vehicle, allow_wake: bool = True) -> bool:
    """Wake vehicle if asleep.

    Returns True if the vehicle is (or becomes) online.
    If allow_wake is False and the vehicle is not online, returns False.
    """
    state = vehicle.get('state')
    if state == 'online':
        return True

    if not allow_wake:
        return False

    try:
        print("⏳ Waking vehicle...", file=sys.stderr)
        vehicle.sync_wake_up()
        return True
    except Exception as e:
        print(
            f"❌ Failed to wake vehicle (state was: {state}). Try again, or run: {_invocation('wake')}\n"
            f"   Details: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def cmd_auth(args):
    """Authenticate with Tesla."""
    email = resolve_email(args)
    if not email:
        print("❌ Missing Tesla email. Set TESLA_EMAIL or pass --email", file=sys.stderr)
        sys.exit(2)

    tesla = get_tesla(email)
    vehicles = tesla.vehicle_list()
    print(f"\n✅ Authentication cached at {CACHE_FILE}")
    print(f"\n🚗 Found {len(vehicles)} vehicle(s):")
    for v in vehicles:
        # Avoid printing VINs by default.
        print(f"   - {v['display_name']} ({v['state']})")


def cmd_list(args):
    """List all vehicles."""
    tesla = get_tesla(require_email(args))
    vehicles = tesla.vehicle_list()

    default_name = resolve_default_car_name()

    if getattr(args, "json", False):
        # Keep JSON output small + privacy-safe (no VINs).
        out = []
        for i, v in enumerate(vehicles):
            name = v.get('display_name')
            out.append({
                'index': i + 1,
                'display_name': name,
                'state': v.get('state'),
                'is_default': bool(default_name and isinstance(name, str) and name.lower() == default_name.lower()),
            })
        print(json.dumps({'vehicles': out, 'default_car': default_name}, indent=2))
        return

    print(f"Found {len(vehicles)} vehicle(s):\n")
    for i, v in enumerate(vehicles):
        star = " (default)" if default_name and v['display_name'].lower() == default_name.lower() else ""
        print(f"{i+1}. {v['display_name']}{star}")
        # Avoid printing VIN in normal output (privacy).
        print(f"   State: {v['state']}")
        print()

    if default_name:
        print(f"Default car: {default_name}")
    else:
        print(f"Default car: (none) — set with: {_invocation('default-car "Name"')}")


def _c_to_f(c):
    try:
        return c * 9 / 5 + 32
    except Exception:
        return None


def _fmt_bool(b, yes="Yes", no="No"):
    return yes if b else no


def _short_status(vehicle, data):
    charge = data.get('charge_state', {})
    climate = data.get('climate_state', {})
    vs = data.get('vehicle_state', {})

    batt = charge.get('battery_level')
    rng = charge.get('battery_range')
    charging = charge.get('charging_state')
    locked = vs.get('locked')
    inside_c = climate.get('inside_temp')
    inside_f = _c_to_f(inside_c) if inside_c is not None else None
    climate_on = climate.get('is_climate_on')

    parts = [f"🚗 {vehicle['display_name']}"]
    if locked is not None:
        parts.append(f"🔒 {_fmt_bool(locked, 'Locked', 'Unlocked')}")
    if batt is not None:
        if rng is not None:
            parts.append(f"🔋 {batt}% ({rng:.0f} mi)")
        else:
            parts.append(f"🔋 {batt}%")
    if charging:
        parts.append(f"⚡ {charging}")
    if inside_c is not None and inside_f is not None:
        parts.append(f"🌡️ {inside_f:.0f}°F")
    if climate_on is not None:
        parts.append(f"❄️ {_fmt_bool(climate_on, 'On', 'Off')}")

    return " • ".join(parts)


def _summary_json(vehicle, data: dict) -> dict:
    """Sanitized, machine-readable one-line summary.

    Unlike `status --json`, this does NOT emit raw vehicle_data (which may include location).
    """
    charge = data.get('charge_state', {})
    climate = data.get('climate_state', {})
    vs = data.get('vehicle_state', {})

    inside_c = climate.get('inside_temp')
    inside_f = _c_to_f(inside_c) if inside_c is not None else None

    out = {
        "vehicle": {
            "display_name": vehicle.get("display_name"),
            "state": vehicle.get("state"),
        },
        "summary": _short_status(vehicle, data),
        "security": {
            "locked": vs.get("locked"),
        },
        "battery": {
            "level_percent": charge.get("battery_level"),
            "range_mi": charge.get("battery_range"),
            "usable_level_percent": charge.get("usable_battery_level"),
        },
        "charging": {
            "charging_state": charge.get("charging_state"),
        },
        "climate": {
            "inside_temp_c": inside_c,
            "inside_temp_f": inside_f,
            "is_climate_on": climate.get("is_climate_on"),
        },
    }

    # Drop empty nested dicts / None values.
    for k in list(out.keys()):
        v = out[k]
        if isinstance(v, dict):
            v2 = {kk: vv for kk, vv in v.items() if vv is not None}
            if v2:
                out[k] = v2
            else:
                del out[k]
        elif v is None:
            del out[k]

    return out


def _fmt_temp_pair(c):
    if c is None:
        return None
    f = _c_to_f(c)
    if f is None:
        return None
    return f"{c}°C ({f:.0f}°F)"


def _bar_to_psi(bar):
    """Convert bar to PSI.

    Tesla APIs commonly return tire pressures in bar.
    """
    try:
        return float(bar) * 14.5037738
    except Exception:
        return None


def _fmt_tire_pressure(bar):
    """Format tire pressure as "X.X bar (Y psi)"."""
    if bar is None:
        return None
    try:
        b = float(bar)
    except Exception:
        return None
    psi = _bar_to_psi(b)
    if psi is None:
        return None
    return f"{b:.2f} bar ({psi:.0f} psi)"


def _fmt_minutes_hhmm(minutes):
    """Format minutes-from-midnight as HH:MM.

    Tesla endpoints commonly represent scheduled times as minutes after midnight.
    """
    try:
        m = int(minutes)
    except Exception:
        return None
    if m < 0:
        return None
    hh = (m // 60) % 24
    mm = m % 60
    return f"{hh:02d}:{mm:02d}"


def _report(vehicle, data):
    """One-screen status report (safe for chat)."""
    charge = data.get('charge_state', {})
    climate = data.get('climate_state', {})
    vs = data.get('vehicle_state', {})

    lines = []
    lines.append(f"🚗 {vehicle['display_name']}")
    lines.append(f"State: {vehicle.get('state')}")

    locked = vs.get('locked')
    if locked is not None:
        lines.append(f"Locked: {_fmt_bool(locked, 'Yes', 'No')}")

    sentry = vs.get('sentry_mode')
    if sentry is not None:
        lines.append(f"Sentry: {_fmt_bool(sentry, 'On', 'Off')}")

    openings = _openings_one_line(vs)
    if openings:
        lines.append(f"Openings: {openings}")

    batt = charge.get('battery_level')
    usable = charge.get('usable_battery_level')
    rng = charge.get('battery_range')
    if batt is not None and rng is not None:
        lines.append(f"Battery: {batt}% ({rng:.0f} mi)")
    elif batt is not None:
        lines.append(f"Battery: {batt}%")

    # Some vehicles report usable battery level separately (helpful for health/degradation).
    if usable is not None:
        try:
            lines.append(f"Usable battery: {int(usable)}%")
        except Exception:
            lines.append(f"Usable battery: {usable}%")

    charging_state = charge.get('charging_state')
    if charging_state is not None:
        extra = []
        limit = charge.get('charge_limit_soc')
        if limit is not None:
            extra.append(f"limit {limit}%")
        if charging_state == 'Charging':
            ttf = charge.get('time_to_full_charge')
            if ttf is not None:
                extra.append(f"{ttf:.1f}h to full")
            rate = charge.get('charge_rate')
            if rate is not None:
                extra.append(f"{rate} mph")
        suffix = f" ({', '.join(extra)})" if extra else ""
        lines.append(f"Charging: {charging_state}{suffix}")

        # When actively charging, show power details if available.
        # This is useful to sanity-check a slow/fast charge session at a glance.
        if charging_state == 'Charging':
            p = charge.get('charger_power')
            v = charge.get('charger_voltage')
            a = charge.get('charger_actual_current')
            bits = []
            if p is not None:
                bits.append(f"{p} kW")
            if v is not None:
                bits.append(f"{v}V")
            if a is not None:
                bits.append(f"{a}A")
            if bits:
                lines.append(f"Charging power: {' '.join(bits)}")

    # Charge port / cable state
    cpd = charge.get('charge_port_door_open')
    if cpd is not None:
        lines.append(f"Charge port door: {_fmt_bool(cpd, 'Open', 'Closed')}")
    cable = charge.get('conn_charge_cable')
    if cable is not None:
        lines.append(f"Charge cable: {cable}")

    sched_time = charge.get('scheduled_charging_start_time')
    sched_mode = charge.get('scheduled_charging_mode')
    sched_pending = charge.get('scheduled_charging_pending')
    if sched_time is not None or sched_mode is not None or sched_pending is not None:
        bits = []
        if isinstance(sched_mode, str) and sched_mode.strip():
            bits.append(sched_mode.strip())
        elif sched_pending is not None:
            bits.append('On' if sched_pending else 'Off')
        hhmm = _fmt_minutes_hhmm(sched_time)
        if hhmm:
            bits.append(hhmm)
        if bits:
            lines.append(f"Scheduled charging: {' '.join(bits)}")

    # Scheduled departure / off-peak charging (read-only)
    dep_enabled = charge.get('scheduled_departure_enabled')
    dep_time = charge.get('scheduled_departure_time')
    precond = charge.get('preconditioning_enabled')
    off_peak = charge.get('off_peak_charging_enabled')
    if dep_enabled is not None or dep_time is not None or precond is not None or off_peak is not None:
        bits = []
        if dep_enabled is not None:
            bits.append('On' if dep_enabled else 'Off')
        hhmm = _fmt_minutes_hhmm(dep_time)
        if hhmm:
            bits.append(hhmm)
        if precond is not None:
            bits.append(f"precond {'On' if precond else 'Off'}")
        if off_peak is not None:
            bits.append(f"off-peak {'On' if off_peak else 'Off'}")
        if bits:
            lines.append(f"Scheduled departure: {' '.join(bits)}")

    inside = _fmt_temp_pair(climate.get('inside_temp'))
    outside = _fmt_temp_pair(climate.get('outside_temp'))
    if inside:
        lines.append(f"Inside: {inside}")
    if outside:
        lines.append(f"Outside: {outside}")

    climate_on = climate.get('is_climate_on')
    if climate_on is not None:
        lines.append(f"Climate: {_fmt_bool(climate_on, 'On', 'Off')}")

    heaters = _seat_heater_fields(climate)
    if heaters:
        lines.append(f"Seat heaters: {_seat_heaters_one_line(heaters)}")

    # Tire pressures (TPMS) if available
    fl = _fmt_tire_pressure(vs.get('tpms_pressure_fl'))
    fr = _fmt_tire_pressure(vs.get('tpms_pressure_fr'))
    rl = _fmt_tire_pressure(vs.get('tpms_pressure_rl'))
    rr = _fmt_tire_pressure(vs.get('tpms_pressure_rr'))
    if any([fl, fr, rl, rr]):
        lines.append(
            "Tires (TPMS): "
            f"FL {fl or '(?)'} | FR {fr or '(?)'} | RL {rl or '(?)'} | RR {rr or '(?)'}"
        )

    odo = vs.get('odometer')
    if odo is not None:
        lines.append(f"Odometer: {odo:.0f} mi")

    return "\n".join(lines)


def _report_json(vehicle, data: dict) -> dict:
    """Sanitized JSON equivalent of `_report`.

    Intentionally excludes location/drive_state.
    """
    charge = data.get('charge_state', {})
    climate = data.get('climate_state', {})
    vs = data.get('vehicle_state', {})

    out = {
        "vehicle": {
            "display_name": vehicle.get('display_name'),
            "state": vehicle.get('state'),
        },
        "battery": {
            "level_percent": charge.get('battery_level'),
            "range_mi": charge.get('battery_range'),
            "usable_battery_level_percent": charge.get('usable_battery_level'),
        },
        "charging": {
            "charging_state": charge.get('charging_state'),
            "charge_limit_percent": charge.get('charge_limit_soc'),
            "minutes_to_full_charge": charge.get('minutes_to_full_charge'),
            "time_to_full_charge_hours": charge.get('time_to_full_charge'),
            "charge_rate_mph": charge.get('charge_rate'),
            "charger_power_kw": charge.get('charger_power'),
            "charger_voltage_v": charge.get('charger_voltage'),
            "charger_actual_current_a": charge.get('charger_actual_current'),
            "charge_current_request_a": charge.get('charge_current_request'),
            "charge_current_request_max_a": charge.get('charge_current_request_max'),
            "charging_amps": charge.get('charging_amps'),
            "charge_port_door_open": charge.get('charge_port_door_open'),
            "conn_charge_cable": charge.get('conn_charge_cable'),
        },
        "scheduled_charging": {
            "mode": charge.get('scheduled_charging_mode'),
            "pending": charge.get('scheduled_charging_pending'),
            "start_time_hhmm": _fmt_minutes_hhmm(charge.get('scheduled_charging_start_time')),
        },
        "scheduled_departure": {
            "enabled": charge.get('scheduled_departure_enabled'),
            "time_hhmm": _fmt_minutes_hhmm(charge.get('scheduled_departure_time')),
            "preconditioning_enabled": charge.get('preconditioning_enabled'),
            "off_peak_charging_enabled": charge.get('off_peak_charging_enabled'),
        },
        "climate": {
            "inside_temp_c": climate.get('inside_temp'),
            "outside_temp_c": climate.get('outside_temp'),
            "is_climate_on": climate.get('is_climate_on'),
            "seat_heaters": _seat_heater_fields(climate) or None,
        },
        "security": {
            "locked": vs.get('locked'),
            "sentry_mode": vs.get('sentry_mode'),
        },
        "openings": _openings_json(vs),
        "tpms": {
            "pressure_fl": vs.get('tpms_pressure_fl'),
            "pressure_fr": vs.get('tpms_pressure_fr'),
            "pressure_rl": vs.get('tpms_pressure_rl'),
            "pressure_rr": vs.get('tpms_pressure_rr'),
        },
        "odometer_mi": vs.get('odometer'),
    }

    # Drop empty nested dicts for cleaner output.
    for k in list(out.keys()):
        v = out[k]
        if isinstance(v, dict):
            v2 = {kk: vv for kk, vv in v.items() if vv is not None}
            if v2:
                out[k] = v2
            else:
                del out[k]
        elif v is None:
            del out[k]

    return out


def _ensure_online_or_exit(vehicle, allow_wake: bool):
    if wake_vehicle(vehicle, allow_wake=allow_wake):
        return

    state = vehicle.get('state')
    name = vehicle.get('display_name', 'Vehicle')
    print(
        f"ℹ️ {name} is currently '{state}'. Skipping wake because --no-wake was set.\n"
        f"   Re-run without --no-wake, or run: {_invocation('wake')}",
        file=sys.stderr,
    )
    sys.exit(3)


def cmd_report(args):
    """One-screen status report."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    _ensure_online_or_exit(vehicle, allow_wake=not getattr(args, 'no_wake', False))
    data = vehicle.get_vehicle_data()

    if args.json:
        # Default JSON output is a structured, sanitized report object.
        # Use --raw-json if you explicitly want the full vehicle_data payload
        # (which may include location/drive_state).
        if getattr(args, "raw_json", False):
            print(json.dumps(data, indent=2))
        else:
            print(json.dumps(_report_json(vehicle, data), indent=2))
        return

    print(_report(vehicle, data))


def cmd_status(args):
    """Get vehicle status."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    _ensure_online_or_exit(vehicle, allow_wake=not getattr(args, 'no_wake', False))
    data = vehicle.get_vehicle_data()

    # When --json is requested, print *only* JSON (no extra human text), so it can
    # be reliably piped/parsed.
    if args.json:
        print(json.dumps(data, indent=2))
        return

    charge = data.get('charge_state', {})
    climate = data.get('climate_state', {})
    vehicle_state = data.get('vehicle_state', {})

    if getattr(args, 'summary', False):
        # Print a one-line summary *in addition* to the detailed view.
        # (If you only want the one-liner, use the `summary` command.)
        print(_short_status(vehicle, data))
        print()

    # Human-friendly detailed view
    print(f"🚗 {vehicle['display_name']}")
    print(f"   State: {vehicle.get('state')}")

    batt = charge.get('battery_level')
    rng = charge.get('battery_range')
    if batt is not None and rng is not None:
        print(f"   Battery: {batt}% ({rng:.0f} mi)")
    elif batt is not None:
        print(f"   Battery: {batt}%")

    charging_state = charge.get('charging_state')
    if charging_state is not None:
        print(f"   Charging: {charging_state}")

    inside_c = climate.get('inside_temp')
    outside_c = climate.get('outside_temp')
    if inside_c is not None:
        inside_f = _c_to_f(inside_c)
        if inside_f is not None:
            print(f"   Inside temp: {inside_c}°C ({inside_f:.0f}°F)")
    if outside_c is not None:
        outside_f = _c_to_f(outside_c)
        if outside_f is not None:
            print(f"   Outside temp: {outside_c}°C ({outside_f:.0f}°F)")

    climate_on = climate.get('is_climate_on')
    if climate_on is not None:
        print(f"   Climate on: {climate_on}")

    locked = vehicle_state.get('locked')
    if locked is not None:
        print(f"   Locked: {locked}")

    odo = vehicle_state.get('odometer')
    if odo is not None:
        print(f"   Odometer: {odo:.0f} mi")


def cmd_lock(args):
    """Lock the vehicle."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('LOCK')
    print(f"🔒 {vehicle['display_name']} locked")


def cmd_unlock(args):
    """Unlock the vehicle."""
    require_yes(args, 'unlock')
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('UNLOCK')
    print(f"🔓 {vehicle['display_name']} unlocked")


def cmd_climate(args):
    """Control climate.

    Actions:
    - status (read-only)
    - on/off
    - temp <value> [--celsius|--fahrenheit]
    - defrost <on|off> (max defrost / preconditioning)
    """
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    if args.action == 'status':
        # Read-only action can skip waking the car.
        allow_wake = not getattr(args, 'no_wake', False)
        _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

        data = vehicle.get_vehicle_data()
        climate = data.get('climate_state', {})

        out = {
            'is_climate_on': climate.get('is_climate_on'),
            'inside_temp_c': climate.get('inside_temp'),
            'outside_temp_c': climate.get('outside_temp'),
            'driver_temp_setting_c': climate.get('driver_temp_setting'),
            'passenger_temp_setting_c': climate.get('passenger_temp_setting'),
        }

        if args.json:
            print(json.dumps(out, indent=2))
            return

        inside = _fmt_temp_pair(climate.get('inside_temp'))
        outside = _fmt_temp_pair(climate.get('outside_temp'))
        print(f"🚗 {vehicle['display_name']}")
        if out.get('is_climate_on') is not None:
            print(f"Climate: {_fmt_bool(out.get('is_climate_on'), 'On', 'Off')}")
        if inside:
            print(f"Inside: {inside}")
        if outside:
            print(f"Outside: {outside}")

        driver = _fmt_temp_pair(climate.get('driver_temp_setting'))
        passenger = _fmt_temp_pair(climate.get('passenger_temp_setting'))
        if driver or passenger:
            print(f"Setpoint: driver {driver or '(unknown)'} | passenger {passenger or '(unknown)'}")
        return

    # Mutating actions (wake is allowed)
    wake_vehicle(vehicle)

    if args.action == 'on':
        vehicle.command('CLIMATE_ON')
        print(f"❄️ {vehicle['display_name']} climate turned on")
    elif args.action == 'off':
        vehicle.command('CLIMATE_OFF')
        print(f"🌡️ {vehicle['display_name']} climate turned off")
    elif args.action == 'temp':
        if args.value is None:
            raise ValueError("Missing temperature value (e.g., climate temp 72 or climate temp 22 --celsius)")

        value = float(args.value)
        # Default is Fahrenheit unless --celsius is provided.
        in_f = True
        if getattr(args, "celsius", False):
            in_f = False
        elif getattr(args, "fahrenheit", False):
            in_f = True

        temp_c = (value - 32) * 5 / 9 if in_f else value
        vehicle.command('CHANGE_CLIMATE_TEMPERATURE_SETTING', driver_temp=temp_c, passenger_temp=temp_c)
        print(f"🌡️ {vehicle['display_name']} temperature set to {value:g}°{'F' if in_f else 'C'}")
    elif args.action == 'defrost':
        if args.value is None or str(args.value).strip().lower() not in ('on', 'off'):
            raise ValueError("Missing defrost value. Use: climate defrost on|off")

        on = str(args.value).strip().lower() == 'on'
        vehicle.command('SET_PRECONDITIONING_MAX', on=on)
        print(f"🧊 {vehicle['display_name']} max defrost {('enabled' if on else 'disabled')}")
    else:
        raise ValueError(f"Unknown action: {args.action}")



def _charge_status_json(charge: dict) -> dict:
    """Small, privacy-safe charging status object.

    Intended for piping/parsing via `charge status --json`.
    """
    charge = charge or {}
    return {
        'battery_level': charge.get('battery_level'),
        'battery_range': charge.get('battery_range'),
        'usable_battery_level': charge.get('usable_battery_level'),
        'charging_state': charge.get('charging_state'),
        'charge_limit_soc': charge.get('charge_limit_soc'),
        'time_to_full_charge': charge.get('time_to_full_charge'),
        'charge_rate': charge.get('charge_rate'),
        'charger_power': charge.get('charger_power'),
        'charger_voltage': charge.get('charger_voltage'),
        'charger_actual_current': charge.get('charger_actual_current'),
        'scheduled_charging_start_time': charge.get('scheduled_charging_start_time'),
        'scheduled_charging_mode': charge.get('scheduled_charging_mode'),
        'scheduled_charging_pending': charge.get('scheduled_charging_pending'),
        'charge_port_door_open': charge.get('charge_port_door_open'),
        'conn_charge_cable': charge.get('conn_charge_cable'),
    }


def cmd_charge(args):
    """Control charging."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    # Read-only action can skip waking the car.
    allow_wake = True
    if args.action == 'status':
        allow_wake = not getattr(args, 'no_wake', False)

    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

    if args.action == 'status':
        data = vehicle.get_vehicle_data()
        charge = data['charge_state']

        if args.json:
            # Print *only* JSON (no extra human text) so it can be piped/parsed.
            # Keep it focused to avoid leaking unrelated vehicle details.
            out = _charge_status_json(charge)
            # Drop nulls for cleanliness.
            out = {k: v for k, v in out.items() if v is not None}
            print(json.dumps(out, indent=2))
            return

        print(f"🔋 {vehicle['display_name']} Battery: {charge['battery_level']}%")
        print(f"   Range: {charge['battery_range']:.0f} mi")

        usable = charge.get('usable_battery_level')
        if usable is not None:
            try:
                print(f"   Usable: {int(usable)}%")
            except Exception:
                print(f"   Usable: {usable}%")

        print(f"   State: {charge['charging_state']}")
        print(f"   Limit: {charge['charge_limit_soc']}%")

        cpd = charge.get('charge_port_door_open')
        if cpd is not None:
            print(f"   Charge port door: {_fmt_bool(cpd, 'Open', 'Closed')}")
        cable = charge.get('conn_charge_cable')
        if cable is not None:
            print(f"   Charge cable: {cable}")

        if charge['charging_state'] == 'Charging':
            if charge.get('time_to_full_charge') is not None:
                print(f"   Time left: {charge['time_to_full_charge']:.1f} hrs")
            if charge.get('charge_rate') is not None:
                print(f"   Rate: {charge['charge_rate']} mph")

            # Power details when available
            p = charge.get('charger_power')
            v = charge.get('charger_voltage')
            a = charge.get('charger_actual_current')
            bits = []
            if p is not None:
                bits.append(f"{p} kW")
            if v is not None:
                bits.append(f"{v}V")
            if a is not None:
                bits.append(f"{a}A")
            if bits:
                print(f"   Power: {' '.join(bits)}")
        return

    if args.action == 'start':
        require_yes(args, 'charge start')
        vehicle.command('START_CHARGE')
        print(f"⚡ {vehicle['display_name']} charging started")
        return

    if args.action == 'stop':
        require_yes(args, 'charge stop')
        vehicle.command('STOP_CHARGE')
        print(f"🛑 {vehicle['display_name']} charging stopped")
        return

    if args.action == 'limit':
        require_yes(args, 'charge limit')
        if args.value is None:
            raise ValueError("Missing charge limit percent (e.g., charge limit 80)")
        pct = int(args.value)
        if pct < 50 or pct > 100:
            raise ValueError("Invalid charge limit percent. Expected 50–100")
        vehicle.command('CHANGE_CHARGE_LIMIT', percent=pct)
        print(f"🎚️ {vehicle['display_name']} charge limit set to {pct}%")
        return

    if args.action == 'amps':
        require_yes(args, 'charge amps')
        if args.value is None:
            raise ValueError("Missing amps value (e.g., charge amps 16)")
        amps = int(args.value)
        if amps < 1 or amps > 48:
            # Conservative guardrail. Many cars support 5-48A depending on setup.
            raise ValueError("Invalid amps. Expected 1–48")
        vehicle.command('CHARGING_AMPS', charging_amps=amps)
        print(f"🔌 {vehicle['display_name']} charging amps set to {amps}A")
        return

    raise ValueError(f"Unknown action: {args.action}")


def _parse_hhmm(value: str):
    """Parse HH:MM into minutes after midnight."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing time. Expected HH:MM (e.g., 23:30)")
    s = value.strip()
    if ":" not in s:
        raise ValueError("Invalid time. Expected HH:MM (e.g., 23:30)")
    hh_s, mm_s = s.split(":", 1)
    hh = int(hh_s)
    mm = int(mm_s)
    if hh < 0 or hh > 23 or mm < 0 or mm > 59:
        raise ValueError("Invalid time. Expected HH:MM using 24-hour time")
    return hh * 60 + mm


def cmd_scheduled_charging(args):
    """Get/set scheduled charging (requires --yes to change)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    # Read-only action can skip waking the car.
    allow_wake = True
    if args.action == 'status':
        allow_wake = not getattr(args, 'no_wake', False)

    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

    if args.action == 'status':
        data = vehicle.get_vehicle_data()
        charge = data.get('charge_state', {})
        sched_time = charge.get('scheduled_charging_start_time')
        sched_mode = charge.get('scheduled_charging_mode')
        sched_pending = charge.get('scheduled_charging_pending')

        if args.json:
            print(json.dumps({'scheduled_charging_start_time': sched_time,
                              'scheduled_charging_mode': sched_mode,
                              'scheduled_charging_pending': sched_pending}, indent=2))
            return

        hhmm = _fmt_minutes_hhmm(sched_time)
        mode = (sched_mode.strip() if isinstance(sched_mode, str) else None)
        if not mode and sched_pending is not None:
            mode = 'On' if sched_pending else 'Off'

        print(f"🚗 {vehicle['display_name']}")
        print(f"Scheduled charging: {mode or '(unknown)'}")
        if hhmm:
            print(f"Start time: {hhmm}")
        return

    # Mutating actions
    require_yes(args, 'scheduled-charging')

    if args.action == 'off':
        vehicle.command('SCHEDULED_CHARGING', enable=False, time=0)
        print(f"⏱️ {vehicle['display_name']} scheduled charging disabled")
        return

    if args.action == 'set':
        minutes = _parse_hhmm(args.time)
        vehicle.command('SCHEDULED_CHARGING', enable=True, time=minutes)
        print(f"⏱️ {vehicle['display_name']} scheduled charging set to {_fmt_minutes_hhmm(minutes)}")
        return

    raise ValueError(f"Unknown action: {args.action}")


def _scheduled_departure_status_json(charge: dict) -> dict:
    """Small, privacy-safe scheduled departure status object."""
    charge = charge or {}
    return {
        'scheduled_departure_enabled': charge.get('scheduled_departure_enabled'),
        'scheduled_departure_time': charge.get('scheduled_departure_time'),
        'scheduled_departure_time_hhmm': _fmt_minutes_hhmm(charge.get('scheduled_departure_time')),
        'preconditioning_enabled': charge.get('preconditioning_enabled'),
        'off_peak_charging_enabled': charge.get('off_peak_charging_enabled'),
    }


def cmd_scheduled_departure(args):
    """Get scheduled departure / off-peak charging / preconditioning status (read-only)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    allow_wake = not getattr(args, 'no_wake', False)
    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

    data = vehicle.get_vehicle_data()
    charge = data.get('charge_state', {})
    out = _scheduled_departure_status_json(charge)

    if getattr(args, 'json', False):
        print(json.dumps(out, indent=2))
        return

    print(f"🚗 {vehicle['display_name']}")
    if out.get('scheduled_departure_enabled') is not None:
        print(f"Scheduled departure: {_fmt_bool(out.get('scheduled_departure_enabled'), 'On', 'Off')}")
    else:
        print("Scheduled departure: (unknown)")

    hhmm = out.get('scheduled_departure_time_hhmm')
    if hhmm:
        print(f"Departure time: {hhmm}")

    if out.get('preconditioning_enabled') is not None:
        print(f"Preconditioning: {_fmt_bool(out.get('preconditioning_enabled'), 'On', 'Off')}")

    if out.get('off_peak_charging_enabled') is not None:
        print(f"Off-peak charging: {_fmt_bool(out.get('off_peak_charging_enabled'), 'On', 'Off')}")


def _round_coord(x, digits: int = 2):
    """Round a coordinate for safer display.

    digits=2 is roughly ~1km precision (varies with latitude) and is intended
    as a non-sensitive default.

    We cap digits to a small range to avoid accidentally producing overly
    precise coordinates.
    """
    try:
        d = int(digits)
    except Exception:
        return None

    # 0..6 is still plenty for display; tighter by default.
    if d < 0 or d > 6:
        return None

    try:
        return round(float(x), d)
    except Exception:
        return None


def cmd_location(args):
    """Get vehicle location.

    Default output is *approximate* (rounded) to reduce accidental leakage.
    Use --yes for precise coordinates.

    Use --digits N (0–6) to control rounding precision for approximate output.
    """
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    _ensure_online_or_exit(vehicle, allow_wake=not getattr(args, 'no_wake', False))

    data = vehicle.get_vehicle_data()
    drive = data['drive_state']

    lat, lon = drive['latitude'], drive['longitude']

    if getattr(args, "yes", False):
        print(f"📍 {vehicle['display_name']} Location (precise): {lat}, {lon}")
        print(f"   https://www.google.com/maps?q={lat},{lon}")
        return

    digits = getattr(args, 'digits', 2)
    lat_r = _round_coord(lat, digits)
    lon_r = _round_coord(lon, digits)
    if lat_r is None or lon_r is None:
        raise ValueError("Invalid or missing location coordinates (try --digits 0..6)")

    print(f"📍 {vehicle['display_name']} Location (approx): {lat_r}, {lon_r}")
    print(f"   https://www.google.com/maps?q={lat_r},{lon_r}")
    print("   (Use --yes for precise coordinates)")


def cmd_tires(args):
    """Show tire pressures (TPMS) (read-only)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    # Read-only action can skip waking the car.
    allow_wake = not getattr(args, 'no_wake', False)
    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

    data = vehicle.get_vehicle_data()
    vs = data.get('vehicle_state', {})

    fl = _fmt_tire_pressure(vs.get('tpms_pressure_fl'))
    fr = _fmt_tire_pressure(vs.get('tpms_pressure_fr'))
    rl = _fmt_tire_pressure(vs.get('tpms_pressure_rl'))
    rr = _fmt_tire_pressure(vs.get('tpms_pressure_rr'))

    if args.json:
        print(json.dumps({
            'tpms_pressure_fl': vs.get('tpms_pressure_fl'),
            'tpms_pressure_fr': vs.get('tpms_pressure_fr'),
            'tpms_pressure_rl': vs.get('tpms_pressure_rl'),
            'tpms_pressure_rr': vs.get('tpms_pressure_rr'),
        }, indent=2))
        return

    print(f"🚗 {vehicle['display_name']}")
    print("Tire pressures (TPMS):")
    print(f"  FL: {fl or '(unknown)'}")
    print(f"  FR: {fr or '(unknown)'}")
    print(f"  RL: {rl or '(unknown)'}")
    print(f"  RR: {rr or '(unknown)'}")



def _fmt_open(v):
    if v is None:
        return None
    # Tesla often uses 0/1 ints for open states.
    if isinstance(v, bool):
        return 'Open' if v else 'Closed'
    try:
        i = int(v)
        return 'Open' if i else 'Closed'
    except Exception:
        return None


def _openings_one_line(vs: dict) -> str:
    """Return a one-line openings summary from vehicle_state.

    Returns None if no openings fields are present.
    """
    out = _openings_json(vs)
    if out is None:
        return None
    if out.get("all_closed"):
        return "All closed"
    if out.get("open"):
        # This is a human-facing string; keep it readable.
        title = {
            "driver_front_door": "Driver front door",
            "driver_rear_door": "Driver rear door",
            "passenger_front_door": "Passenger front door",
            "passenger_rear_door": "Passenger rear door",
            "frunk": "Frunk",
            "trunk": "Trunk",
            "front_driver_window": "Front driver window",
            "front_passenger_window": "Front passenger window",
            "rear_driver_window": "Rear driver window",
            "rear_passenger_window": "Rear passenger window",
        }
        labels = [title.get(x, x) for x in out["open"]]
        return "Open: " + ", ".join(labels)
    return None


def _openings_json(vs: dict) -> dict:
    """Sanitized openings JSON from vehicle_state.

    Returns None if no openings fields are present.
    """
    if not isinstance(vs, dict):
        return None

    fields = [
        ("df", "driver_front_door"),
        ("dr", "driver_rear_door"),
        ("pf", "passenger_front_door"),
        ("pr", "passenger_rear_door"),
        ("ft", "frunk"),
        ("rt", "trunk"),
        ("fd_window", "front_driver_window"),
        ("fp_window", "front_passenger_window"),
        ("rd_window", "rear_driver_window"),
        ("rp_window", "rear_passenger_window"),
    ]

    any_known = False
    open_items = []
    for key, label in fields:
        raw = vs.get(key)
        if raw is None:
            continue
        any_known = True
        if _fmt_open(raw) == 'Open':
            open_items.append(label)

    if not any_known:
        return None

    return {
        "open": open_items,
        "all_closed": len(open_items) == 0,
    }


def cmd_openings(args):
    """Show which doors/trunks/windows are open (read-only)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    allow_wake = not getattr(args, 'no_wake', False)
    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

    data = vehicle.get_vehicle_data()
    vs = data.get('vehicle_state', {})

    out = {
        'doors': {
            'driver_front': _fmt_open(vs.get('df')),
            'driver_rear': _fmt_open(vs.get('dr')),
            'passenger_front': _fmt_open(vs.get('pf')),
            'passenger_rear': _fmt_open(vs.get('pr')),
        },
        'trunks': {
            'frunk': _fmt_open(vs.get('ft')),
            'trunk': _fmt_open(vs.get('rt')),
        },
        'windows': {
            'front_driver': _fmt_open(vs.get('fd_window')),
            'front_passenger': _fmt_open(vs.get('fp_window')),
            'rear_driver': _fmt_open(vs.get('rd_window')),
            'rear_passenger': _fmt_open(vs.get('rp_window')),
        },
    }

    # Drop unknown keys for cleaner output.
    for k in list(out.keys()):
        out[k] = {kk: vv for kk, vv in out[k].items() if vv is not None}
        if not out[k]:
            del out[k]

    if args.json:
        print(json.dumps(out, indent=2))
        return

    print(f"🚗 {vehicle['display_name']}")
    if not out:
        print("Openings: (unavailable)")
        return

    def _section(title, d):
        if not d:
            return
        print(f"{title}:")
        for kk, vv in d.items():
            print(f"  - {kk.replace('_',' ')}: {vv}")

    _section('Doors', out.get('doors'))
    _section('Trunks', out.get('trunks'))
    _section('Windows', out.get('windows'))


def cmd_trunk(args):
    """Toggle frunk/trunk (requires --yes)."""
    require_yes(args, 'trunk')
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)

    which = 'front' if args.which == 'frunk' else 'rear'
    vehicle.command('ACTUATE_TRUNK', which_trunk=which)
    label = 'Frunk' if which == 'front' else 'Trunk'
    print(f"🧳 {vehicle['display_name']} {label} toggled")


def cmd_windows(args):
    """Windows: status (read-only) or vent/close (requires --yes)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    # Read-only action can skip waking the car.
    if args.action == 'status':
        allow_wake = not getattr(args, 'no_wake', False)
        _ensure_online_or_exit(vehicle, allow_wake=allow_wake)
        data = vehicle.get_vehicle_data()
        vs = data.get('vehicle_state', {})

        out = {
            'front_driver': _fmt_open(vs.get('fd_window')),
            'front_passenger': _fmt_open(vs.get('fp_window')),
            'rear_driver': _fmt_open(vs.get('rd_window')),
            'rear_passenger': _fmt_open(vs.get('rp_window')),
        }
        # Drop unknowns for cleaner output
        out = {k: v for k, v in out.items() if v is not None}

        if getattr(args, 'json', False):
            print(json.dumps(out, indent=2))
            return

        print(f"🚗 {vehicle['display_name']}")
        if not out:
            print("Windows: (unavailable)")
            return
        print("Windows:")
        for k, v in out.items():
            print(f"  - {k.replace('_',' ')}: {v}")
        return

    # Mutating actions
    require_yes(args, 'windows')
    wake_vehicle(vehicle)

    # Tesla API requires lat/lon parameters; 0/0 works for this endpoint.
    if args.action == 'vent':
        vehicle.command('WINDOW_CONTROL', command='vent', lat=0, lon=0)
        print(f"🪟 {vehicle['display_name']} windows vented")
        return
    if args.action == 'close':
        vehicle.command('WINDOW_CONTROL', command='close', lat=0, lon=0)
        print(f"🪟 {vehicle['display_name']} windows closed")
        return

    raise ValueError(f"Unknown action: {args.action}")


def _seat_heater_fields(climate_state: dict) -> dict:
    """Extract seat heater levels from climate_state (if present)."""
    if not isinstance(climate_state, dict):
        return {}

    # Common Tesla API fields (may vary by model/firmware).
    keys = [
        "seat_heater_left",  # driver
        "seat_heater_right",  # passenger
        "seat_heater_rear_left",
        "seat_heater_rear_center",
        "seat_heater_rear_right",
        "seat_heater_third_row_left",
        "seat_heater_third_row_right",
    ]
    out = {k: climate_state.get(k) for k in keys if k in climate_state}
    # Drop unknown/nulls for clean output.
    return {k: v for k, v in out.items() if v is not None}


def _seat_heaters_one_line(fields: dict) -> str:
    """Format seat heater levels in a compact one-line form.

    Example: "D 3 | P 2 | RL 1".
    """
    if not isinstance(fields, dict) or not fields:
        return ""

    labels = {
        "seat_heater_left": "D",
        "seat_heater_right": "P",
        "seat_heater_rear_left": "RL",
        "seat_heater_rear_center": "RC",
        "seat_heater_rear_right": "RR",
        "seat_heater_third_row_left": "3L",
        "seat_heater_third_row_right": "3R",
    }

    parts = []
    for k in [
        "seat_heater_left",
        "seat_heater_right",
        "seat_heater_rear_left",
        "seat_heater_rear_center",
        "seat_heater_rear_right",
        "seat_heater_third_row_left",
        "seat_heater_third_row_right",
    ]:
        if k in fields and fields.get(k) is not None:
            parts.append(f"{labels.get(k, k)} {fields.get(k)}")

    return " | ".join(parts)


_SEAT_NAME_TO_HEATER_ID = {
    # Tesla's REMOTE_SEAT_HEATER_REQUEST uses numeric "heater" ids.
    # These mappings are the common convention used by community clients.
    "driver": 0,
    "front-left": 0,
    "front_left": 0,
    "left": 0,
    "passenger": 1,
    "front-right": 1,
    "front_right": 1,
    "right": 1,
    "rear-left": 2,
    "rear_left": 2,
    "rear-center": 3,
    "rear_center": 3,
    "rear-right": 4,
    "rear_right": 4,
    "3rd-left": 5,
    "3rd_left": 5,
    "third-left": 5,
    "third_left": 5,
    "3rd-right": 6,
    "3rd_right": 6,
    "third-right": 6,
    "third_right": 6,
}


def _parse_seat_heater(seat: str) -> int:
    """Parse a seat name into a Tesla heater id.

    Accepts friendly names (driver/passenger/rear-left/etc) or a numeric id.
    """
    if seat is None:
        raise ValueError("Missing seat. Example: seats set driver 3")

    s = str(seat).strip().lower()
    if not s:
        raise ValueError("Missing seat. Example: seats set driver 3")

    if s.isdigit():
        hid = int(s)
        if hid < 0 or hid > 6:
            raise ValueError("Invalid seat heater id. Expected 0–6")
        return hid

    hid = _SEAT_NAME_TO_HEATER_ID.get(s)
    if hid is None:
        raise ValueError(
            "Unknown seat. Use one of: driver, passenger, rear-left, rear-center, rear-right, 3rd-left, 3rd-right (or 0–6)"
        )
    return hid


def cmd_seats(args):
    """Seat heaters: status (read-only) or set (requires --yes)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    if args.action == "status":
        allow_wake = not getattr(args, "no_wake", False)
        _ensure_online_or_exit(vehicle, allow_wake=allow_wake)
        data = vehicle.get_vehicle_data()
        climate = data.get("climate_state", {})
        out = _seat_heater_fields(climate)

        if getattr(args, "json", False):
            print(json.dumps(out, indent=2))
            return

        print(f"🚗 {vehicle['display_name']}")
        if not out:
            print("Seat heaters: (unavailable)")
            return
        print("Seat heaters (0=off .. 3=high):")
        for k, v in out.items():
            label = k.replace("seat_heater_", "").replace("_", " ")
            print(f"  - {label}: {v}")
        return

    if args.action == "set":
        require_yes(args, "seats set")
        wake_vehicle(vehicle)

        heater = _parse_seat_heater(getattr(args, "seat", None))
        if getattr(args, "level", None) is None:
            raise ValueError("Missing level. Expected 0–3")
        level = int(getattr(args, "level"))
        if level < 0 or level > 3:
            raise ValueError("Invalid level. Expected 0–3")

        vehicle.command("REMOTE_SEAT_HEATER_REQUEST", heater=heater, level=level)
        print(f"🔥 {vehicle['display_name']} seat heater {heater} set to {level}")
        return

    raise ValueError(f"Unknown action: {args.action}")


def cmd_sentry(args):
    """Get/set Sentry Mode (on/off requires --yes)."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    # Read-only action can skip waking the car.
    allow_wake = True
    if args.action == 'status':
        allow_wake = not getattr(args, 'no_wake', False)

    _ensure_online_or_exit(vehicle, allow_wake=allow_wake)

    if args.action == 'status':
        data = vehicle.get_vehicle_data()
        sentry = data.get('vehicle_state', {}).get('sentry_mode')
        if args.json:
            print(json.dumps({'sentry_mode': sentry}, indent=2))
            return
        if sentry is None:
            print(f"🚗 {vehicle['display_name']}\nSentry: (unknown)")
        else:
            print(f"🚗 {vehicle['display_name']}\nSentry: {_fmt_bool(sentry, 'On', 'Off')}")
        return

    # Mutating actions
    require_yes(args, 'sentry')
    wake_vehicle(vehicle)

    if args.action == 'on':
        vehicle.command('SET_SENTRY_MODE', on=True)
        print(f"🛡️ {vehicle['display_name']} Sentry turned on")
        return

    if args.action == 'off':
        vehicle.command('SET_SENTRY_MODE', on=False)
        print(f"🛡️ {vehicle['display_name']} Sentry turned off")
        return

    raise ValueError(f"Unknown action: {args.action}")


def cmd_honk(args):
    """Honk the horn."""
    require_yes(args, 'honk')
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('HONK_HORN')
    print(f"📢 {vehicle['display_name']} honked!")


def require_yes(args, action: str):
    if not getattr(args, "yes", False):
        print(f"❌ Refusing to run '{action}' without --yes (safety gate)", file=sys.stderr)
        sys.exit(2)


def cmd_flash(args):
    """Flash the lights."""
    require_yes(args, 'flash')
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    wake_vehicle(vehicle)
    vehicle.command('FLASH_LIGHTS')
    print(f"💡 {vehicle['display_name']} flashed lights!")


def _charge_port_status_json(vehicle, data: dict) -> dict:
    """Small, privacy-safe charge port status object."""
    charge = (data or {}).get('charge_state', {})
    return {
        'display_name': (vehicle or {}).get('display_name'),
        'state': (vehicle or {}).get('state'),
        'charge_port_door_open': charge.get('charge_port_door_open'),
        'charge_port_latch': charge.get('charge_port_latch'),
        'conn_charge_cable': charge.get('conn_charge_cable'),
        'charging_state': charge.get('charging_state'),
    }


def cmd_charge_port(args):
    """Charge port operations.

    - status: read-only (supports --no-wake)
    - open/close: requires --yes
    """
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    if args.action == 'status':
        _ensure_online_or_exit(vehicle, allow_wake=not getattr(args, 'no_wake', False))
        data = vehicle.get_vehicle_data()
        out = _charge_port_status_json(vehicle, data)

        if getattr(args, 'json', False):
            # Keep this privacy-safe + stable.
            print(json.dumps(out, indent=2))
            return

        print(f"🔌 {vehicle.get('display_name')}")
        print(f"   State: {vehicle.get('state')}")
        if out.get('charge_port_door_open') is not None:
            print(f"   Port door open: {_fmt_bool(out.get('charge_port_door_open'))}")
        if out.get('charge_port_latch') is not None:
            print(f"   Port latch: {out.get('charge_port_latch')}")
        if out.get('conn_charge_cable') is not None:
            print(f"   Cable: {out.get('conn_charge_cable')}")
        if out.get('charging_state') is not None:
            print(f"   Charging: {out.get('charging_state')}")
        return

    # open/close
    require_yes(args, 'charge-port')
    wake_vehicle(vehicle)

    if args.action == 'open':
        vehicle.command('CHARGE_PORT_DOOR_OPEN')
        print(f"🔌 {vehicle['display_name']} charge port opened")
    elif args.action == 'close':
        vehicle.command('CHARGE_PORT_DOOR_CLOSE')
        print(f"🔌 {vehicle['display_name']} charge port closed")
    else:
        raise ValueError(f"Unknown action: {args.action}")


def cmd_wake(args):
    """Wake up the vehicle."""
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)
    print(f"⏳ Waking {vehicle['display_name']}...")
    vehicle.sync_wake_up()
    print(f"✅ {vehicle['display_name']} is awake")


def cmd_summary(args):
    """One-line status summary.

    - default (human): prints a single line for chat
    - with --json: prints a sanitized JSON object (privacy-safe)
    - with --json --raw-json: prints raw vehicle_data (may include location)
    """
    tesla = get_tesla(require_email(args))
    vehicle = get_vehicle(tesla, args.car)

    _ensure_online_or_exit(vehicle, allow_wake=not getattr(args, 'no_wake', False))
    data = vehicle.get_vehicle_data()

    if getattr(args, 'json', False):
        if getattr(args, 'raw_json', False):
            print(json.dumps(data, indent=2))
        else:
            print(json.dumps(_summary_json(vehicle, data), indent=2))
        return

    print(_short_status(vehicle, data))


# ----------------------------
# Mileage tracking (SQLite)
# ----------------------------

MILEAGE_DIR = Path.home() / ".my_tesla"
MILEAGE_DB_DEFAULT = MILEAGE_DIR / "mileage.sqlite"


def resolve_mileage_db_path(args=None) -> Path:
    """Resolve mileage DB path.

    Priority:
    1) --db (for mileage commands)
    2) MY_TESLA_MILEAGE_DB env var
    3) ~/.my_tesla/mileage.sqlite
    """
    if args is not None and getattr(args, "db", None):
        return Path(getattr(args, "db")).expanduser()
    env = os.environ.get("MY_TESLA_MILEAGE_DB")
    if env and env.strip():
        return Path(env.strip()).expanduser()
    return MILEAGE_DB_DEFAULT


def resolve_since_ts(*, since_ts: int | None = None, since_days: float | None = None) -> int | None:
    """Resolve a cutoff timestamp (UTC epoch seconds) for mileage export.

    - since_ts wins if provided.
    - since_days is interpreted as "now - N days".

    Returns None when no cutoff is requested.
    """
    if since_ts is not None:
        try:
            return int(since_ts)
        except Exception:
            raise ValueError("--since-ts must be an integer epoch timestamp (seconds)")

    if since_days is None:
        return None

    try:
        days = float(since_days)
    except Exception:
        raise ValueError("--since-days must be a number (e.g., 7 or 0.5)")

    if days < 0:
        raise ValueError("--since-days must be >= 0")

    return int(time.time() - days * 86400)


def mileage_fetch_points(conn, *, since_ts: int | None = None):
    """Fetch mileage points ordered by timestamp asc, optionally filtered."""
    if since_ts is None:
        cur = conn.execute(
            "SELECT ts_utc, vehicle_id, vehicle_name, odometer_mi, state, source, note FROM mileage_points ORDER BY ts_utc ASC"
        )
        return cur.fetchall()

    cur = conn.execute(
        "SELECT ts_utc, vehicle_id, vehicle_name, odometer_mi, state, source, note FROM mileage_points WHERE ts_utc >= ? ORDER BY ts_utc ASC",
        (int(since_ts),),
    )
    return cur.fetchall()


def _db_connect(path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def mileage_init_db(path: Path):
    conn = _db_connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mileage_points (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ts_utc INTEGER NOT NULL,
              vehicle_id TEXT,
              vehicle_name TEXT,
              odometer_mi REAL,
              state TEXT,
              source TEXT,
              note TEXT
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_mileage_points_vehicle_ts ON mileage_points(vehicle_id, ts_utc);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_mileage_points_ts ON mileage_points(ts_utc);"
        )
        conn.commit()
    finally:
        conn.close()


def _vehicle_identity(vehicle) -> tuple[str, str]:
    vid = vehicle.get("id_s") or str(vehicle.get("vehicle_id") or "")
    name = vehicle.get("display_name") or "Vehicle"
    return (vid, name)


def mileage_last_success_ts(conn, vehicle_id: str) -> int | None:
    cur = conn.execute(
        "SELECT ts_utc FROM mileage_points WHERE vehicle_id=? AND odometer_mi IS NOT NULL ORDER BY ts_utc DESC LIMIT 1",
        (vehicle_id,),
    )
    row = cur.fetchone()
    return int(row[0]) if row else None


def mileage_insert_point(
    conn,
    *,
    ts_utc: int,
    vehicle_id: str,
    vehicle_name: str,
    odometer_mi: float | None,
    state: str | None,
    source: str,
    note: str | None = None,
):
    conn.execute(
        """
        INSERT INTO mileage_points(ts_utc, vehicle_id, vehicle_name, odometer_mi, state, source, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (ts_utc, vehicle_id, vehicle_name, odometer_mi, state, source, note),
    )


def _fmt_dt(ts_utc: int) -> str:
    dt = datetime.fromtimestamp(ts_utc, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def cmd_mileage(args):
    """Mileage tracking commands."""
    db_path = resolve_mileage_db_path(args)

    if args.action == "init":
        mileage_init_db(db_path)
        print(f"✅ Mileage DB ready: {db_path}")
        return

    # record/status/export require DB
    mileage_init_db(db_path)

    if args.action == "record":
        tesla = get_tesla(require_email(args))
        vehicles = tesla.vehicle_list()
        if not vehicles:
            print("❌ No vehicles found on this account", file=sys.stderr)
            sys.exit(1)

        ts = int(time.time())
        allow_any_wake = not getattr(args, "no_wake", False)
        wake_after_hours = float(getattr(args, "auto_wake_after_hours", 24.0) or 24.0)
        wake_after_sec = int(wake_after_hours * 3600)

        results = []

        conn = _db_connect(db_path)
        try:
            for v in vehicles:
                vid, name = _vehicle_identity(v)
                state = v.get("state")

                # Determine if we should allow waking based on last successful capture.
                last_ts = mileage_last_success_ts(conn, vid) if vid else None
                too_old = last_ts is None or (ts - last_ts) >= wake_after_sec

                allow_wake = allow_any_wake and bool(too_old)

                # Try to avoid waking unless threshold exceeded.
                if not wake_vehicle(v, allow_wake=allow_wake):
                    mileage_insert_point(
                        conn,
                        ts_utc=ts,
                        vehicle_id=vid,
                        vehicle_name=name,
                        odometer_mi=None,
                        state=state,
                        source="skip",
                        note=(
                            f"skipped (state={state}); no_wake={getattr(args,'no_wake',False)}; "
                            f"last_ok={_fmt_dt(last_ts) if last_ts else 'never'}"
                        ),
                    )
                    results.append({
                        "vehicle": name,
                        "vehicle_id": vid,
                        "state": state,
                        "recorded": False,
                        "reason": "asleep_or_offline",
                        "last_success_ts_utc": last_ts,
                        "woke": False,
                    })
                    continue

                # Online now.
                data = v.get_vehicle_data()
                vs = data.get("vehicle_state", {})
                odo = vs.get("odometer")

                mileage_insert_point(
                    conn,
                    ts_utc=ts,
                    vehicle_id=vid,
                    vehicle_name=name,
                    odometer_mi=float(odo) if odo is not None else None,
                    state=v.get("state"),
                    source="vehicle_data",
                    note=None,
                )

                results.append({
                    "vehicle": name,
                    "vehicle_id": vid,
                    "state": v.get("state"),
                    "recorded": odo is not None,
                    "odometer_mi": float(odo) if odo is not None else None,
                    "woke": bool(allow_wake and state != 'online'),
                })

            conn.commit()
        finally:
            conn.close()

        if args.json:
            print(json.dumps({"db": str(db_path), "ts_utc": ts, "results": results}, indent=2))
            return

        ok = sum(1 for r in results if r.get("recorded"))
        print(f"✅ Recorded mileage: {ok}/{len(results)} vehicles")
        for r in results:
            if r.get("recorded"):
                print(f"- {r['vehicle']}: {r.get('odometer_mi'):.1f} mi")
            else:
                print(f"- {r['vehicle']}: skipped ({r.get('reason')})")
        return

    if args.action == "status":
        conn = _db_connect(db_path)
        try:
            cur = conn.execute(
                """
                SELECT vehicle_name, vehicle_id, ts_utc, odometer_mi
                FROM mileage_points
                WHERE odometer_mi IS NOT NULL
                ORDER BY ts_utc DESC
                """
            )
            rows = cur.fetchall()
        finally:
            conn.close()

        # latest per vehicle
        latest = {}
        for name, vid, ts, odo in rows:
            if vid not in latest:
                latest[vid] = {"vehicle": name, "vehicle_id": vid, "ts_utc": int(ts), "odometer_mi": float(odo)}

        out = {"db": str(db_path), "vehicles": list(latest.values())}
        if args.json:
            print(json.dumps(out, indent=2))
            return

        print(f"Mileage DB: {db_path}")
        if not latest:
            print("No mileage points recorded yet. Run: " + _invocation("mileage record"))
            return
        for v in out["vehicles"]:
            print(f"- {v['vehicle']}: {v['odometer_mi']:.1f} mi (last: {_fmt_dt(v['ts_utc'])})")
        return

    if args.action == "export":
        fmt = getattr(args, "format", "csv")

        since_ts = resolve_since_ts(
            since_ts=getattr(args, "since_ts", None),
            since_days=getattr(args, "since_days", None),
        )

        conn = _db_connect(db_path)
        try:
            rows = mileage_fetch_points(conn, since_ts=since_ts)
        finally:
            conn.close()

        if fmt == "json":
            items = [
                {
                    "ts_utc": int(ts),
                    "vehicle_id": vid,
                    "vehicle": name,
                    "odometer_mi": odo,
                    "state": state,
                    "source": source,
                    "note": note,
                }
                for (ts, vid, name, odo, state, source, note) in rows
            ]
            print(json.dumps({"db": str(db_path), "since_ts_utc": since_ts, "items": items}, indent=2))
            return

        # csv
        import csv
        w = csv.writer(sys.stdout)
        w.writerow(["ts_utc", "vehicle_id", "vehicle", "odometer_mi", "state", "source", "note"])
        for (ts, vid, name, odo, state, source, note) in rows:
            w.writerow([int(ts), vid, name, odo, state, source, note or ""])
        return

    raise ValueError(f"Unknown mileage action: {args.action}")


def cmd_version(args):
    """Print the installed skill version."""
    # Keep output simple for scripts.
    print(read_skill_version())


def cmd_default_car(args):
    """Set or show the default car used when --car is not provided."""
    if not args.name:
        name = resolve_default_car_name()
        if name:
            print(f"Default car: {name}")
        else:
            print("Default car: (none)")
        return

    defaults = load_defaults()
    defaults["default_car"] = args.name
    save_defaults(defaults)
    print(f"✅ Default car set to: {args.name}")
    print(f"Saved to: {DEFAULTS_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Tesla vehicle control")
    parser.add_argument("--email", "-e", help="Tesla account email")
    parser.add_argument("--car", "-c", help="Vehicle name (default: first vehicle)")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON")
    parser.add_argument(
        "--raw-json",
        action="store_true",
        help=(
            "When used with --json on supported commands, output raw vehicle_data (may include location). "
            "Default JSON output is sanitized/summary for safety."
        ),
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help=(
            "Safety confirmation for sensitive/disruptive actions "
            "(unlock/charge start|stop|limit|amps/trunk/windows/seats set/honk/flash/charge-port open|close/"
            "scheduled-charging set|off/sentry on|off/location precise)"
        ),
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print a full Python traceback on errors (also enabled by MY_TESLA_DEBUG=1)",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Print skill version and exit",
    )

    subparsers = parser.add_subparsers(dest="command")

    # Auth
    subparsers.add_parser("auth", help="Authenticate with Tesla")

    # List
    subparsers.add_parser("list", help="List all vehicles")

    # Version
    subparsers.add_parser("version", help="Print skill version")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Get vehicle status")
    status_parser.add_argument("--summary", action="store_true", help="Also print a one-line summary")
    status_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Summary (alias)
    summary_parser = subparsers.add_parser("summary", help="One-line status summary")
    summary_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Report (one-screen)
    report_parser = subparsers.add_parser("report", help="One-screen status report")
    report_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Default car
    default_parser = subparsers.add_parser("default-car", help="Set/show default vehicle name")
    default_parser.add_argument("name", nargs="?", help="Vehicle display name to set as default")
    
    # Mileage tracking (odometer)
    mileage_parser = subparsers.add_parser("mileage", help="Record odometer mileage to a local SQLite DB")
    mileage_parser.add_argument("action", choices=["init", "record", "status", "export"], help="init|record|status|export")
    mileage_parser.add_argument("--json", action="store_true", help="Output JSON (record/status only)")
    mileage_parser.add_argument("--db", help="Path to the SQLite DB (default: ~/.my_tesla/mileage.sqlite)")
    mileage_parser.add_argument("--no-wake", action="store_true", help="Do not wake sleeping cars")
    mileage_parser.add_argument(
        "--auto-wake-after-hours",
        type=float,
        default=24.0,
        help="If a car hasn't recorded mileage in this many hours, allow waking it (default: 24)",
    )
    mileage_parser.add_argument("--format", choices=["csv", "json"], default="csv", help="For export: csv|json")
    mileage_parser.add_argument(
        "--since-ts",
        type=int,
        help="(export only) Only include points with ts_utc >= this epoch timestamp (seconds)",
    )
    mileage_parser.add_argument(
        "--since-days",
        type=float,
        help="(export only) Only include points from the last N days (e.g., 7 or 0.5)",
    )

    # Lock/unlock
    subparsers.add_parser("lock", help="Lock the vehicle")
    subparsers.add_parser("unlock", help="Unlock the vehicle")
    
    # Climate
    climate_parser = subparsers.add_parser("climate", help="Climate control")
    climate_parser.add_argument("action", choices=["status", "on", "off", "temp", "defrost"])
    climate_parser.add_argument(
        "value",
        nargs="?",
        help="For 'temp': temperature value. For 'defrost': on|off.",
    )
    climate_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")
    temp_units = climate_parser.add_mutually_exclusive_group()
    temp_units.add_argument("--fahrenheit", "-f", action="store_true", help="Temperature value is in °F (default)")
    temp_units.add_argument("--celsius", action="store_true", help="Temperature value is in °C")
    
    # Charge
    charge_parser = subparsers.add_parser("charge", help="Charging control")
    charge_parser.add_argument("action", choices=["status", "start", "stop", "limit", "amps"])
    charge_parser.add_argument(
        "value",
        nargs="?",
        help="For 'limit': percent (e.g., 80). For 'amps': amps (e.g., 16).",
    )
    charge_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")

    # Scheduled charging
    sched_parser = subparsers.add_parser("scheduled-charging", help="Get/set scheduled charging (set/off requires --yes)")
    sched_parser.add_argument("action", choices=["status", "set", "off"], help="status|set|off")
    sched_parser.add_argument("time", nargs="?", help="Start time for 'set' as HH:MM (24-hour)")
    sched_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")

    # Scheduled departure (read-only)
    dep_parser = subparsers.add_parser(
        "scheduled-departure",
        help="Scheduled departure / preconditioning / off-peak charging status (read-only)",
    )
    dep_parser.add_argument("action", choices=["status"], help="status")
    dep_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Location
    location_parser = subparsers.add_parser(
        "location",
        help="Get vehicle location (approx by default; use --yes for precise)",
    )
    location_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")
    location_parser.add_argument(
        "--digits",
        type=int,
        default=2,
        help="(approx output) Rounding precision for latitude/longitude (0–6). Default: 2",
    )

    # Tire pressures (TPMS)
    tires_parser = subparsers.add_parser("tires", help="Show tire pressures (TPMS)")
    tires_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Openings (doors/trunks/windows)
    openings_parser = subparsers.add_parser("openings", help="Show which doors/trunks/windows are open")
    openings_parser.add_argument("--no-wake", action="store_true", help="Do not wake the car (fails if asleep)")

    # Trunk / frunk
    trunk_parser = subparsers.add_parser("trunk", help="Toggle trunk/frunk (requires --yes)")
    trunk_parser.add_argument("which", choices=["trunk", "frunk"], help="Which to actuate")

    # Windows
    windows_parser = subparsers.add_parser("windows", help="Windows status (read-only) or vent/close (requires --yes)")
    windows_parser.add_argument("action", choices=["status", "vent", "close"], help="status|vent|close")
    windows_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")
    windows_parser.add_argument("--json", action="store_true", help="(status only) Output JSON")

    # Seat heaters
    seats_parser = subparsers.add_parser("seats", help="Seat heater status (read-only) or set level (requires --yes)")
    seats_parser.add_argument("action", choices=["status", "set"], help="status|set")
    seats_parser.add_argument("seat", nargs="?", help="For 'set': driver|passenger|rear-left|rear-center|rear-right|3rd-left|3rd-right (or 0–6)")
    seats_parser.add_argument("level", nargs="?", help="For 'set': 0–3 (0=off)")
    seats_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")
    seats_parser.add_argument("--json", action="store_true", help="(status only) Output JSON")

    # Sentry
    sentry_parser = subparsers.add_parser("sentry", help="Get/set Sentry Mode (on/off requires --yes)")
    sentry_parser.add_argument("action", choices=["status", "on", "off"], help="status|on|off")
    sentry_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")

    # Honk/flash
    subparsers.add_parser("honk", help="Honk the horn")
    subparsers.add_parser("flash", help="Flash the lights")

    # Charge port
    charge_port_parser = subparsers.add_parser(
        "charge-port",
        help="Charge port status (read-only) or open/close (requires --yes)",
    )
    charge_port_parser.add_argument("action", choices=["status", "open", "close"], help="status|open|close")
    charge_port_parser.add_argument("--no-wake", action="store_true", help="(status only) Do not wake the car")

    # Wake
    subparsers.add_parser("wake", help="Wake up the vehicle")
    
    args = parser.parse_args()

    if getattr(args, "version", False):
        cmd_version(args)
        return

    if not getattr(args, "command", None):
        parser.print_help(sys.stderr)
        sys.exit(2)

    commands = {
        "auth": cmd_auth,
        "list": cmd_list,
        "version": cmd_version,
        "status": cmd_status,
        "summary": cmd_summary,
        "report": cmd_report,
        "lock": cmd_lock,
        "unlock": cmd_unlock,
        "climate": cmd_climate,
        "charge": cmd_charge,
        "scheduled-charging": cmd_scheduled_charging,
        "scheduled-departure": cmd_scheduled_departure,
        "location": cmd_location,
        "tires": cmd_tires,
        "openings": cmd_openings,
        "trunk": cmd_trunk,
        "windows": cmd_windows,
        "seats": cmd_seats,
        "sentry": cmd_sentry,
        "honk": cmd_honk,
        "flash": cmd_flash,
        "charge-port": cmd_charge_port,
        "wake": cmd_wake,
        "default-car": cmd_default_car,
        "mileage": cmd_mileage,
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\n⛔ Interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        debug = bool(getattr(args, "debug", False)) or os.environ.get("MY_TESLA_DEBUG") == "1"
        if debug:
            # Print both a friendly line and a full traceback.
            print(f"❌ Error: {e}", file=sys.stderr)
            traceback.print_exc()
        else:
            print(f"❌ Error: {e}", file=sys.stderr)
            print("   Tip: re-run with --debug for a full traceback", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
