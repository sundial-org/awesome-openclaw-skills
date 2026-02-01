#!/usr/bin/env python3
"""Tesla vehicle commands.

Usage:
    command.py climate start
    command.py flash climate stop           # vehicle by name
    command.py charge limit 80
    command.py seat-heater -l high -p driver
    command.py precondition add -t 08:00 -d weekdays
    command.py precondition remove --id 123
"""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from store import (
    default_dir,
    ensure_migrated,
    get_auth,
    get_config,
    get_places,
    get_vehicles,
    load_env_file,
    save_places,
    save_vehicles,
)

DEFAULT_DIR = default_dir()
VEHICLE_CACHE_MAX_AGE = 86400  # 24 hours


# ─────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────────────────────────

def http_json(
    method: str,
    url: str,
    token: str,
    json_body: Optional[Dict[str, Any]] = None,
    ca_cert: Optional[str] = None,
) -> Any:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    
    body = None
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, method=method, data=body, headers=headers)

    ctx = None
    if url.startswith("https://"):
        ctx = ssl.create_default_context(cafile=ca_cert) if ca_cert else ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        try:
            err = json.loads(text)
            raise RuntimeError(f"HTTP {e.code}: {err}")
        except json.JSONDecodeError:
            raise RuntimeError(f"HTTP {e.code}: {text}")


# ─────────────────────────────────────────────────────────────────────────────
# Vehicle resolution (VIN/name/auto-select)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_vehicles(base_url: str, token: str, ca_cert: Optional[str] = None) -> List[Dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/api/1/vehicles"
    data = http_json("GET", url, token, ca_cert=ca_cert)
    return data.get("response", [])


def get_vehicles_cached(
    dir_path: str,
    base_url: str,
    token: str,
    ca_cert: Optional[str] = None,
) -> List[Dict[str, Any]]:
    store = get_vehicles(dir_path)
    cache = store.get("vehicles_cache", store)
    cached_at = cache.get("cached_at", 0)
    vehicles = cache.get("vehicles", [])

    if vehicles and (time.time() - cached_at) < VEHICLE_CACHE_MAX_AGE:
        return vehicles

    vehicles = fetch_vehicles(base_url, token, ca_cert)
    cache = {
        "cached_at": int(time.time()),
        "vehicles": [{"vin": v.get("vin"), "display_name": v.get("display_name")} for v in vehicles],
    }
    save_vehicles(dir_path, cache)
    return cache["vehicles"]


def resolve_vehicle(
    identifier: Optional[str],
    dir_path: str,
    base_url: str,
    token: str,
    ca_cert: Optional[str] = None,
) -> Tuple[str, str]:
    """Resolve vehicle identifier to (vin, display_name)."""
    vehicles = get_vehicles_cached(dir_path, base_url, token, ca_cert)
    
    if not vehicles:
        print("No vehicles found.", file=sys.stderr)
        sys.exit(1)
    
    if not identifier:
        if len(vehicles) == 1:
            v = vehicles[0]
            return v.get("vin"), v.get("display_name", "Tesla")
        print("Multiple vehicles. Specify name or VIN:", file=sys.stderr)
        for v in vehicles:
            print(f"  - {v.get('display_name')} ({v.get('vin')})", file=sys.stderr)
        sys.exit(1)
    
    # VIN (17 alphanumeric)
    if len(identifier) == 17 and identifier.isalnum():
        for v in vehicles:
            if v.get("vin", "").upper() == identifier.upper():
                return v.get("vin"), v.get("display_name", "Tesla")
        return identifier.upper(), "Tesla"
    
    # Name match (case-insensitive)
    id_lower = identifier.lower()
    matches = [v for v in vehicles if (v.get("display_name") or "").lower() == id_lower]
    if len(matches) == 1:
        return matches[0].get("vin"), matches[0].get("display_name")
    
    if not matches:
        print(f"No vehicle matching '{identifier}'.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Multiple vehicles match '{identifier}'.", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Command execution
# ─────────────────────────────────────────────────────────────────────────────

def api_url(base_url: str, vin: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/api/1/vehicles/{urllib.parse.quote(vin)}/{path}"


def send_command(
    base_url: str,
    token: str,
    vin: str,
    endpoint: str,
    body: Optional[Dict[str, Any]] = None,
    ca_cert: Optional[str] = None,
) -> Dict[str, Any]:
    url = api_url(base_url, vin, f"command/{endpoint}")
    return http_json("POST", url, token, json_body=body or {}, ca_cert=ca_cert)


def format_result(result: Dict[str, Any], action: str, vehicle_name: str) -> str:
    response = result.get("response", {})
    success = response.get("result", False)
    reason = response.get("reason", "")
    
    if success:
        return f"✅ {action} — {vehicle_name}"
    else:
        return f"❌ {action} failed — {reason or 'unknown error'}"


def parse_time(time_str: str) -> int:
    """Parse HH:MM to minutes since midnight."""
    match = re.match(r"^(\d{1,2}):(\d{2})$", time_str)
    if not match:
        raise ValueError(f"Invalid time format: {time_str} (use HH:MM)")
    hours, mins = int(match.group(1)), int(match.group(2))
    if hours > 23 or mins > 59:
        raise ValueError(f"Invalid time: {time_str}")
    return hours * 60 + mins


# ─────────────────────────────────────────────────────────────────────────────
# Command handlers
# ─────────────────────────────────────────────────────────────────────────────

def cmd_climate(args, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    action = args.climate_action
    
    if action == "start":
        result = send_command(base_url, token, vin, "auto_conditioning_start", ca_cert=ca_cert)
        print(format_result(result, "Climate started", name))
    elif action == "stop":
        result = send_command(base_url, token, vin, "auto_conditioning_stop", ca_cert=ca_cert)
        print(format_result(result, "Climate stopped", name))
    elif action == "temps":
        driver = args.driver_temp
        passenger = args.passenger_temp if args.passenger_temp is not None else driver
        body = {"driver_temp": driver, "passenger_temp": passenger}
        result = send_command(base_url, token, vin, "set_temps", body, ca_cert)
        print(format_result(result, f"Temperature set to {driver}°C", name))
    elif action == "keeper":
        modes = {"off": 0, "keep": 1, "dog": 2, "camp": 3}
        mode = modes.get(args.mode.lower())
        if mode is None:
            print(f"Invalid mode: {args.mode}. Use: off, keep, dog, camp", file=sys.stderr)
            return 1
        result = send_command(base_url, token, vin, "set_climate_keeper_mode", {"climate_keeper_mode": mode}, ca_cert)
        print(format_result(result, f"Climate keeper: {args.mode}", name))
    else:
        print(f"Unknown climate action: {action}", file=sys.stderr)
        return 1
    return 0


def parse_days(days_str: str) -> str:
    """Convert days string to Tesla API format. Returns 'All', 'Weekdays', or 'Thursday,Saturday' etc."""
    days_str = days_str.lower().strip()
    
    if days_str == "all":
        return "All"
    
    if days_str == "weekdays":
        return "Weekdays"
    
    if days_str == "weekends":
        return "Saturday,Sunday"
    
    # Map short names to full capitalized names
    day_map = {
        "sun": "Sunday", "sunday": "Sunday",
        "mon": "Monday", "monday": "Monday",
        "tue": "Tuesday", "tuesday": "Tuesday",
        "wed": "Wednesday", "wednesday": "Wednesday",
        "thu": "Thursday", "thursday": "Thursday",
        "fri": "Friday", "friday": "Friday",
        "sat": "Saturday", "saturday": "Saturday",
    }
    
    days = []
    for part in days_str.split(","):
        part = part.strip().lower()
        if part in day_map:
            days.append(day_map[part])
        else:
            raise ValueError(f"Invalid day: {part}. Use: sun,mon,tue,wed,thu,fri,sat or all/weekdays/weekends")
    
    return ",".join(days)


def get_vehicle_location(base_url: str, token: str, vin: str, ca_cert: Optional[str]) -> Optional[Tuple[float, float]]:
    """Fetch current vehicle location. Returns (lat, lon) or None."""
    url = f"{base_url.rstrip('/')}/api/1/vehicles/{urllib.parse.quote(vin)}/vehicle_data?endpoints=location_data"
    try:
        data = http_json("GET", url, token, ca_cert=ca_cert)
        drive_state = data.get("response", {}).get("drive_state", {})
        lat = drive_state.get("latitude")
        lon = drive_state.get("longitude")
        if lat and lon:
            return (float(lat), float(lon))
    except Exception:
        pass
    return None


def cmd_places_list(dir_path: str) -> int:
    places = get_places(dir_path)
    if not places:
        print("(no places)")
        return 0
    for k in sorted(places.keys()):
        v = places.get(k) or {}
        lat = v.get("lat")
        lon = v.get("lon")
        print(f"{k}: {lat}, {lon}")
    return 0


def cmd_places_set(args, dir_path: str, base_url: str, token: Optional[str], vin: Optional[str], ca_cert: Optional[str]) -> int:
    places = get_places(dir_path)

    lat = args.lat
    lon = args.lon

    if args.here:
        if not token or not vin:
            print("--here requires an authenticated vehicle context (run auth first).", file=sys.stderr)
            return 1
        loc = get_vehicle_location(base_url, token, vin, ca_cert)
        if not loc:
            print("Could not fetch vehicle location. Wake vehicle or provide --lat/--lon.", file=sys.stderr)
            return 1
        lat, lon = loc

    if lat is None or lon is None:
        print("Specify --lat and --lon (or --here).", file=sys.stderr)
        return 1

    places[args.name] = {"lat": float(lat), "lon": float(lon)}
    save_places(dir_path, places)
    print(f"✅ Saved place '{args.name}': {float(lat)}, {float(lon)}")
    return 0


def cmd_places_remove(args, dir_path: str) -> int:
    places = get_places(dir_path)
    if args.name not in places:
        print(f"No such place: {args.name}", file=sys.stderr)
        return 1
    places.pop(args.name, None)
    save_places(dir_path, places)
    print(f"✅ Removed place '{args.name}'")
    return 0


def cmd_precondition_add(args, dir_path: str, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    try:
        minutes = parse_time(args.time)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    
    try:
        days_str = parse_days(args.days)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    
    # Location priority:
    # 1) explicit --lat/--lon
    # 2) --place <name> (from places.json)
    # 3) fetch current vehicle location
    lat = args.lat
    lon = args.lon

    if (not lat or not lon) and getattr(args, "place", None):
        places = get_places(dir_path)
        p = places.get(args.place)
        if not isinstance(p, dict):
            print(
                f"Unknown place '{args.place}'. Add it via: command.py places set {args.place} --lat X --lon Y",
                file=sys.stderr,
            )
            return 1
        lat = p.get("lat")
        lon = p.get("lon")
        print(f"Using place '{args.place}': {lat}, {lon}", file=sys.stderr)

    if not lat or not lon:
        print("Fetching vehicle location...", file=sys.stderr)
        loc = get_vehicle_location(base_url, token, vin, ca_cert)
        if loc:
            lat, lon = loc
            print(f"Using current location: {lat}, {lon}", file=sys.stderr)
        else:
            print("Could not get vehicle location. Use --lat/--lon, set a --place, or wake vehicle first.", file=sys.stderr)
            return 1
    
    body = {
        "days_of_week": days_str,
        "precondition_time": minutes,
        "enabled": not args.disabled,
        "lat": float(lat),
        "lon": float(lon),
    }
    
    if args.id:
        body["id"] = int(args.id)
        action_desc = f"Precondition schedule {args.id} updated"
    else:
        action_desc = f"Precondition schedule added"
    
    if args.one_time:
        body["one_time"] = True
    
    result = send_command(base_url, token, vin, "add_precondition_schedule", body, ca_cert)
    print(format_result(result, f"{action_desc}: {args.time} ({args.days})", name))
    return 0


def cmd_precondition_remove(args, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    if not args.id:
        print("Specify --id to remove", file=sys.stderr)
        return 1
    
    body = {"id": int(args.id)}
    result = send_command(base_url, token, vin, "remove_precondition_schedule", body, ca_cert)
    print(format_result(result, f"Precondition schedule {args.id} removed", name))
    return 0


def cmd_precondition_list(args, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    url = f"{base_url.rstrip('/')}/api/1/vehicles/{urllib.parse.quote(vin)}/vehicle_data?endpoints=preconditioning_schedule_data"
    
    try:
        data = http_json("GET", url, token, ca_cert=ca_cert)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    sched_data = data.get("response", {}).get("preconditioning_schedule_data", {})
    schedules = sched_data.get("precondition_schedules", [])
    
    if getattr(args, "raw_json", False):
        print(json.dumps(sched_data, indent=2))
        return 0
    
    print(f"🚗 {name} — Precondition Schedules")
    print("─" * 40)
    
    if not schedules:
        print("  (no schedules)")
        return 0
    
    for s in schedules:
        sched_id = s.get("id", "?")
        time_mins = s.get("precondition_time", 0)
        hours, mins = divmod(time_mins, 60)
        time_str = f"{hours:02d}:{mins:02d}"
        
        enabled = "✓" if s.get("enabled") else "✗"
        one_time = "one-time" if s.get("one_time") else "repeating"
        
        days = s.get("days_of_week", 0)
        if days == 127:
            days_str = "all"
        elif days == 62:
            days_str = "weekdays"
        elif days == 65:
            days_str = "weekends"
        else:
            # Decode bitmask
            day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            days_str = ",".join(day_names[i] for i in range(7) if days & (1 << i))
        
        print(f"  [{enabled}] {time_str} — {days_str} ({one_time})")
        print(f"      ID: {sched_id}")
    
    return 0


SEAT_POSITIONS = {
    "driver": 0, "front_left": 0, "front-left": 0, "fl": 0,
    "passenger": 1, "front_right": 1, "front-right": 1, "fr": 1,
    "rear_left": 2, "rear-left": 2, "rl": 2,
    "rear_left_back": 3, "rear-left-back": 3,
    "rear_center": 4, "rear-center": 4, "rc": 4,
    "rear_right": 5, "rear-right": 5, "rr": 5,
    "rear_right_back": 6, "rear-right-back": 6,
    "third_left": 7, "third-left": 7,
    "third_right": 8, "third-right": 8,
}

HEAT_LEVELS = {"off": 0, "low": 1, "medium": 2, "med": 2, "high": 3}


def parse_seat_position(value: str) -> int:
    """Parse seat position from name or number."""
    if value.isdigit():
        return int(value)
    pos = SEAT_POSITIONS.get(value.lower())
    if pos is None:
        raise ValueError(f"Invalid position: {value}. Use: driver, passenger, rear_left, rear_center, rear_right (or 0-8)")
    return pos


def parse_heat_level(value: str) -> int:
    """Parse heat level from name or number."""
    if value.isdigit():
        level = int(value)
        if 0 <= level <= 3:
            return level
        raise ValueError(f"Invalid level: {value}. Must be 0-3")
    level = HEAT_LEVELS.get(value.lower())
    if level is None:
        raise ValueError(f"Invalid level: {value}. Use: off, low, medium, high (or 0-3)")
    return level


def cmd_seat_heater(args, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    try:
        position = parse_seat_position(args.position)
        level = parse_heat_level(args.level)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    
    body = {"heater": position, "level": level}
    result = send_command(base_url, token, vin, "remote_seat_heater_request", body, ca_cert)
    pos_name = args.position
    level_name = args.level
    print(format_result(result, f"Seat heater {pos_name}: {level_name}", name))
    return 0


def cmd_seat_cooler(args, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    try:
        position = parse_seat_position(args.position)
        level = parse_heat_level(args.level)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    
    body = {"seat_position": position, "seat_cooler_level": level}
    result = send_command(base_url, token, vin, "remote_seat_cooler_request", body, ca_cert)
    print(format_result(result, f"Seat cooler {args.position}: {args.level}", name))
    return 0


def cmd_seat_climate(args, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    try:
        position = parse_seat_position(args.position)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    
    auto_on = args.mode.lower() in ("auto", "on", "1", "true")
    body = {"auto_seat_position": position, "auto_climate_on": auto_on}
    result = send_command(base_url, token, vin, "remote_auto_seat_climate_request", body, ca_cert)
    state = "auto" if auto_on else "off"
    print(format_result(result, f"Seat climate {args.position}: {state}", name))
    return 0


def cmd_steering_heater(args, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    on = args.state.lower() in ("on", "1", "true")
    body = {"on": on}
    result = send_command(base_url, token, vin, "remote_steering_wheel_heater_request", body, ca_cert)
    state = "on" if on else "off"
    print(format_result(result, f"Steering wheel heater {state}", name))
    return 0


def cmd_charge(args, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    action = args.charge_action
    
    if action == "start":
        result = send_command(base_url, token, vin, "charge_start", ca_cert=ca_cert)
        print(format_result(result, "Charging started", name))
    elif action == "stop":
        result = send_command(base_url, token, vin, "charge_stop", ca_cert=ca_cert)
        print(format_result(result, "Charging stopped", name))
    elif action == "limit":
        percent = args.percent
        if percent < 50 or percent > 100:
            print("Charge limit must be 50-100%", file=sys.stderr)
            return 1
        body = {"percent": percent}
        result = send_command(base_url, token, vin, "set_charge_limit", body, ca_cert)
        print(format_result(result, f"Charge limit set to {percent}%", name))
    else:
        print(f"Unknown charge action: {action}", file=sys.stderr)
        return 1
    return 0


def cmd_simple(args, base_url: str, token: str, vin: str, name: str, ca_cert: Optional[str]) -> int:
    """Handle simple commands: honk, flash, lock, unlock, wake"""
    cmd = args.command
    
    endpoints = {
        "honk": ("honk_horn", "Horn honked"),
        "flash": ("flash_lights", "Lights flashed"),
        "lock": ("door_lock", "Doors locked"),
        "unlock": ("door_unlock", "Doors unlocked"),
    }
    
    if cmd == "wake":
        url = api_url(base_url, vin, "wake_up")
        result = http_json("POST", url, token, json_body={}, ca_cert=ca_cert)
        state = result.get("response", {}).get("state", "unknown")
        print(f"✅ Wake — {name} ({state})")
        return 0
    
    if cmd in endpoints:
        endpoint, action = endpoints[cmd]
        result = send_command(base_url, token, vin, endpoint, ca_cert=ca_cert)
        print(format_result(result, action, name))
        return 0
    
    print(f"Unknown command: {cmd}", file=sys.stderr)
    return 1


# ─────────────────────────────────────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

KNOWN_COMMANDS = {"climate", "precondition", "places", "seat-heater", "seat-cooler", "seat-climate", "steering-heater", "charge", "honk", "flash", "lock", "unlock", "wake"}


def build_parser(vehicle: Optional[str] = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="command.py",
        description="Tesla vehicle commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  command.py climate start
  command.py flash climate stop              # vehicle by name
  command.py charge limit 80
  command.py seat-heater -l high             # driver (default)
  command.py seat-heater -l medium -p passenger
  command.py seat-climate -p driver auto
  command.py steering-heater on
  command.py precondition add -t 08:00       # all days
  command.py precondition add -t 08:00 -d weekdays
  command.py precondition add -t 08:00 --id 1  # modify existing
  command.py precondition remove --id 1
"""
    )
    
    parser.add_argument("--dir", default=DEFAULT_DIR, help="Config directory (default: ~/.clawdbot/tesla-fleet-api)")
    parser.add_argument("--json", action="store_true", dest="raw_json", help="Output raw JSON")
    parser.set_defaults(vehicle=vehicle)
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # climate start|stop|temps|keeper
    p_climate = subparsers.add_parser("climate", help="Climate control")
    climate_sub = p_climate.add_subparsers(dest="climate_action", required=True)
    climate_sub.add_parser("start", help="Start climate")
    climate_sub.add_parser("stop", help="Stop climate")
    p_temps = climate_sub.add_parser("temps", help="Set temperature")
    p_temps.add_argument("driver_temp", type=float, help="Driver temperature (°C)")
    p_temps.add_argument("passenger_temp", type=float, nargs="?", help="Passenger temp (default: same as driver)")
    p_keeper = climate_sub.add_parser("keeper", help="Climate keeper mode")
    p_keeper.add_argument("mode", choices=["off", "keep", "dog", "camp"], help="Mode")
    
    # precondition add|remove
    p_precond = subparsers.add_parser("precondition", help="Precondition schedules")
    precond_sub = p_precond.add_subparsers(dest="precondition_action", required=True)
    
    p_precond_add = precond_sub.add_parser("add", help="Add or modify precondition schedule")
    p_precond_add.add_argument("--time", "-t", required=True, help="Departure time (HH:MM)")
    p_precond_add.add_argument("--days", "-d", default="all", help="Days: all, weekdays, weekends, or mon,tue,wed...")
    p_precond_add.add_argument("--place", help="Named place from places.json")
    p_precond_add.add_argument("--lat", help="Latitude (optional)")
    p_precond_add.add_argument("--lon", help="Longitude (optional)")
    p_precond_add.add_argument("--id", help="Schedule ID (to modify existing)")
    p_precond_add.add_argument("--one-time", action="store_true", help="One-time schedule")
    p_precond_add.add_argument("--disabled", action="store_true", help="Create disabled schedule")
    
    p_precond_remove = precond_sub.add_parser("remove", help="Remove precondition schedule")
    p_precond_remove.add_argument("--id", required=True, help="Schedule ID to remove")
    
    p_precond_list = precond_sub.add_parser("list", help="List precondition schedules")
    p_precond_list.add_argument("--json", action="store_true", dest="raw_json", help="Output raw JSON")
    
    # places
    p_places = subparsers.add_parser("places", help="Manage named places (lat/lon)")
    places_sub = p_places.add_subparsers(dest="places_action", required=True)

    places_sub.add_parser("list", help="List places")

    p_place_set = places_sub.add_parser("set", help="Set a place")
    p_place_set.add_argument("name", help="Place name")
    p_place_set.add_argument("--lat", help="Latitude")
    p_place_set.add_argument("--lon", help="Longitude")
    p_place_set.add_argument("--here", action="store_true", help="Use current vehicle location")

    p_place_rm = places_sub.add_parser("remove", help="Remove a place")
    p_place_rm.add_argument("name", help="Place name")

    # seat-heater --level X --position Y
    p_seat_heater = subparsers.add_parser("seat-heater", help="Seat heater")
    p_seat_heater.add_argument("-l", "--level", required=True, help="Level: off, low, medium, high (or 0-3)")
    p_seat_heater.add_argument("-p", "--position", default="driver", help="Position: driver, passenger, rear_left, etc. (default: driver)")
    
    # seat-cooler --level X --position Y
    p_seat_cooler = subparsers.add_parser("seat-cooler", help="Seat cooler (ventilation)")
    p_seat_cooler.add_argument("-l", "--level", required=True, help="Level: off, low, medium, high (or 0-3)")
    p_seat_cooler.add_argument("-p", "--position", default="driver", help="Position: driver, passenger, etc. (default: driver)")
    
    # seat-climate --position Y auto|off
    p_seat_climate = subparsers.add_parser("seat-climate", help="Seat auto climate")
    p_seat_climate.add_argument("-p", "--position", default="driver", help="Position (default: driver)")
    p_seat_climate.add_argument("mode", choices=["auto", "on", "off"], help="Auto climate mode")
    
    # steering-heater on|off
    p_steering = subparsers.add_parser("steering-heater", help="Steering wheel heater")
    p_steering.add_argument("state", choices=["on", "off"], help="On or off")
    
    # charge start|stop|limit
    p_charge = subparsers.add_parser("charge", help="Charging control")
    charge_sub = p_charge.add_subparsers(dest="charge_action", required=True)
    charge_sub.add_parser("start", help="Start charging")
    charge_sub.add_parser("stop", help="Stop charging")
    p_limit = charge_sub.add_parser("limit", help="Set charge limit")
    p_limit.add_argument("percent", type=int, help="Charge limit (50-100)")
    
    # Simple commands
    subparsers.add_parser("honk", help="Honk the horn")
    subparsers.add_parser("flash", help="Flash the lights")
    subparsers.add_parser("lock", help="Lock the doors")
    subparsers.add_parser("unlock", help="Unlock the doors")
    subparsers.add_parser("wake", help="Wake the vehicle")
    
    return parser


def main() -> int:
    # Check if first arg is a vehicle name (not a known command)
    # Handle case where vehicle name matches a command (e.g., "flash flash" = vehicle "flash" + command "flash")
    argv = sys.argv[1:]
    vehicle = None
    
    # Skip any leading flags
    idx = 0
    while idx < len(argv) and argv[idx].startswith("-"):
        if argv[idx] in ("--dir",):
            idx += 2  # skip flag and value
        else:
            idx += 1  # skip flag
    
    non_flag_args = argv[idx:]
    
    # If first non-flag arg is not a command, or if it IS a command but the second arg is also a command,
    # then the first is a vehicle name
    if len(non_flag_args) >= 1:
        first = non_flag_args[0]
        second = non_flag_args[1] if len(non_flag_args) > 1 else None
        
        # First is a vehicle if: it's not a command, OR (it could be a command but second is also a command)
        if first not in KNOWN_COMMANDS or (second and second in KNOWN_COMMANDS):
            vehicle = first
            # Remove vehicle from sys.argv
            for i, arg in enumerate(sys.argv):
                if arg == vehicle and i > 0:
                    sys.argv = sys.argv[:i] + sys.argv[i+1:]
                    break
    
    parser = build_parser(vehicle)
    args = parser.parse_args()
    
    # Load state
    dir_path = args.dir
    load_env_file(dir_path)
    ensure_migrated(dir_path)

    cfg = get_config(dir_path)
    auth = get_auth(dir_path)

    token = auth.get("access_token")
    audience = cfg.get("audience") or "https://fleet-api.prd.eu.vn.cloud.tesla.com"
    base_url = cfg.get("base_url") or audience
    ca_cert = cfg.get("ca_cert")

    # Dispatch command
    cmd = args.command

    # Places commands can be used without auth (unless --here)
    if cmd == "places":
        try:
            if args.places_action == "list":
                return cmd_places_list(dir_path)
            if args.places_action == "remove":
                return cmd_places_remove(args, dir_path)
            if args.places_action == "set":
                vin = None
                if args.here:
                    if not token:
                        print("No access token. Run auth.py to authenticate.", file=sys.stderr)
                        return 1
                    vin, _ = resolve_vehicle(args.vehicle, dir_path, base_url, token, ca_cert)
                return cmd_places_set(args, dir_path, base_url, token, vin, ca_cert)
            print("Unknown places action", file=sys.stderr)
            return 1
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    if not token:
        print("No access token. Run auth.py to authenticate.", file=sys.stderr)
        return 1

    # Resolve vehicle for all other commands
    vin, name = resolve_vehicle(args.vehicle, dir_path, base_url, token, ca_cert)
    
    try:
        if cmd == "climate":
            return cmd_climate(args, base_url, token, vin, name, ca_cert)
        elif cmd == "precondition":
            if args.precondition_action == "add":
                return cmd_precondition_add(args, dir_path, base_url, token, vin, name, ca_cert)
            elif args.precondition_action == "remove":
                return cmd_precondition_remove(args, base_url, token, vin, name, ca_cert)
            elif args.precondition_action == "list":
                return cmd_precondition_list(args, base_url, token, vin, name, ca_cert)
        elif cmd == "seat-heater":
            return cmd_seat_heater(args, base_url, token, vin, name, ca_cert)
        elif cmd == "seat-cooler":
            return cmd_seat_cooler(args, base_url, token, vin, name, ca_cert)
        elif cmd == "seat-climate":
            return cmd_seat_climate(args, base_url, token, vin, name, ca_cert)
        elif cmd == "steering-heater":
            return cmd_steering_heater(args, base_url, token, vin, name, ca_cert)
        elif cmd == "charge":
            return cmd_charge(args, base_url, token, vin, name, ca_cert)
        elif cmd in ("honk", "flash", "lock", "unlock", "wake"):
            return cmd_simple(args, base_url, token, vin, name, ca_cert)
        else:
            print(f"Unknown command: {cmd}", file=sys.stderr)
            return 1
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
