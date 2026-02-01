#!/usr/bin/env python3
"""Fetch Tesla vehicle data with human-readable output.

Usage:
    vehicle_data.py                  # single vehicle, all data
    vehicle_data.py flash            # by name (case-insensitive)
    vehicle_data.py XP7Y... -c       # by VIN, charge only
    vehicle_data.py -c -l            # charge + location
    vehicle_data.py --json           # raw JSON output
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from store import default_dir, ensure_migrated, get_auth, get_config, get_vehicles, load_env_file, save_vehicles

DEFAULT_DIR = default_dir()
VEHICLE_CACHE_MAX_AGE = 86400  # 24 hours


def fetch_vehicles(base_url: str, token: str, ca_cert: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch vehicle list from API."""
    url = f"{base_url.rstrip('/')}/api/1/vehicles"
    data = http_json("GET", url, token, ca_cert)
    return data.get("response", [])


def get_vehicles_cached(
    dir_path: str,
    base_url: str,
    token: str,
    ca_cert: Optional[str] = None,
    force_refresh: bool = False,
) -> List[Dict[str, Any]]:
    """Get vehicles from cache (vehicles.json) or fetch if stale."""
    store = get_vehicles(dir_path)
    cache = store.get("vehicles_cache", store)
    cached_at = cache.get("cached_at", 0)
    vehicles = cache.get("vehicles", [])

    if not force_refresh and vehicles and (time.time() - cached_at) < VEHICLE_CACHE_MAX_AGE:
        return vehicles

    vehicles = fetch_vehicles(base_url, token, ca_cert)

    cache = {
        "cached_at": int(time.time()),
        "vehicles": [{"vin": v.get("vin"), "display_name": v.get("display_name")} for v in vehicles],
    }
    save_vehicles(dir_path, cache)

    return vehicles


def resolve_vehicle(
    identifier: Optional[str],
    dir_path: str,
    base_url: str,
    token: str,
    ca_cert: Optional[str] = None,
) -> Tuple[str, str]:
    """Resolve vehicle identifier to (vin, display_name).
    
    - If identifier is None and only one vehicle, use it
    - If identifier looks like a VIN (17 chars, alphanumeric), use directly
    - Otherwise, match by display_name (case-insensitive)
    
    Returns (vin, display_name) or exits with error.
    """
    vehicles = get_vehicles_cached(dir_path, base_url, token, ca_cert)
    
    if not vehicles:
        print("No vehicles found on this account.", file=sys.stderr)
        sys.exit(1)
    
    # No identifier provided
    if not identifier:
        if len(vehicles) == 1:
            v = vehicles[0]
            return v.get("vin"), v.get("display_name", "Tesla")
        else:
            print("Multiple vehicles found. Specify VIN or name:", file=sys.stderr)
            for v in vehicles:
                print(f"  - {v.get('display_name', 'Unknown')} ({v.get('vin')})", file=sys.stderr)
            sys.exit(1)
    
    # Check if it looks like a VIN (17 alphanumeric chars)
    if len(identifier) == 17 and identifier.isalnum():
        # Find display_name if cached
        for v in vehicles:
            if v.get("vin", "").upper() == identifier.upper():
                return v.get("vin"), v.get("display_name", "Tesla")
        # Not in cache, use as-is
        return identifier.upper(), "Tesla"
    
    # Match by name (case-insensitive)
    identifier_lower = identifier.lower()
    matches = [v for v in vehicles if (v.get("display_name") or "").lower() == identifier_lower]
    
    if len(matches) == 1:
        v = matches[0]
        return v.get("vin"), v.get("display_name", "Tesla")
    elif len(matches) > 1:
        print(f"Multiple vehicles match '{identifier}':", file=sys.stderr)
        for v in matches:
            print(f"  - {v.get('display_name')} ({v.get('vin')})", file=sys.stderr)
        sys.exit(1)
    else:
        # No match - maybe partial match?
        partial = [v for v in vehicles if identifier_lower in (v.get("display_name") or "").lower()]
        if partial:
            print(f"No exact match for '{identifier}'. Did you mean:", file=sys.stderr)
            for v in partial:
                print(f"  - {v.get('display_name')} ({v.get('vin')})", file=sys.stderr)
        else:
            print(f"No vehicle found matching '{identifier}'.", file=sys.stderr)
            print("Available vehicles:", file=sys.stderr)
            for v in vehicles:
                print(f"  - {v.get('display_name', 'Unknown')} ({v.get('vin')})", file=sys.stderr)
        sys.exit(1)


def http_json(
    method: str,
    url: str,
    token: str,
    ca_cert: Optional[str] = None,
) -> Any:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    req = urllib.request.Request(url=url, method=method, headers=headers)

    ctx = None
    if url.startswith("https://"):
        if ca_cert:
            ctx = ssl.create_default_context(cafile=ca_cert)
        else:
            ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        raise RuntimeError(f"HTTP {e.code}: {text}")


def format_charge_state(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("⚡ Charge State")
    lines.append("─" * 40)
    
    level = data.get("battery_level", "?")
    usable = data.get("usable_battery_level", level)
    limit = data.get("charge_limit_soc", "?")
    state = data.get("charging_state", "Unknown")
    
    # Battery bar
    bar_len = 20
    filled = int((level / 100) * bar_len) if isinstance(level, (int, float)) else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    lines.append(f"  Battery:    [{bar}] {level}%")
    lines.append(f"  Limit:      {limit}%")
    lines.append(f"  State:      {state}")
    
    if state == "Charging":
        power = data.get("charger_power", 0)
        amps = data.get("charger_actual_current", 0)
        volts = data.get("charger_voltage", 0)
        mins = data.get("minutes_to_full_charge", 0)
        added = data.get("charge_energy_added", 0)
        
        # Calculate phases from power (more reliable than API field)
        if amps and volts and power:
            calculated_phases = round((power * 1000) / (amps * volts))
            calculated_phases = max(1, min(3, calculated_phases))  # Clamp to 1-3
        else:
            calculated_phases = data.get("charger_phases", 1)
        
        lines.append(f"  Power:      {power} kW ({amps}A × {volts}V × {calculated_phases}φ)")
        lines.append(f"  Added:      {added:.1f} kWh")
        if mins > 0:
            hrs = mins // 60
            m = mins % 60
            time_str = f"{hrs}h {m}m" if hrs else f"{m}m"
            lines.append(f"  Remaining:  {time_str}")
    
    range_mi = data.get("battery_range", 0)
    range_km = range_mi * 1.60934 if range_mi else 0
    lines.append(f"  Range:      {range_km:.0f} km ({range_mi:.0f} mi)")
    
    cable = data.get("conn_charge_cable", "")
    if cable and cable != "<invalid>":
        lines.append(f"  Cable:      {cable}")
    
    return "\n".join(lines)


def format_climate_state(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("🌡️  Climate State")
    lines.append("─" * 40)
    
    inside = data.get("inside_temp")
    outside = data.get("outside_temp")
    driver_set = data.get("driver_temp_setting")
    is_on = data.get("is_climate_on", False)
    is_precon = data.get("is_preconditioning", False)
    
    if inside is not None:
        lines.append(f"  Inside:     {inside:.1f}°C")
    if outside is not None:
        lines.append(f"  Outside:    {outside:.1f}°C")
    if driver_set is not None:
        lines.append(f"  Set to:     {driver_set:.1f}°C")
    
    status = "On" if is_on else "Off"
    if is_precon:
        status += " (preconditioning)"
    lines.append(f"  Climate:    {status}")
    
    # Seat heaters
    seats = []
    seat_names = ["Driver", "Passenger", "Rear L", "Rear C", "Rear R"]
    for i, name in enumerate(seat_names):
        key = f"seat_heater_{'left' if i == 0 else 'right' if i == 1 else 'rear_left' if i == 2 else 'rear_center' if i == 3 else 'rear_right'}"
        # Try alternate key format
        level = data.get(f"seat_heater_{['left', 'right', 'rear_left', 'rear_center', 'rear_right'][i]}", 
                        data.get(f"seat_heater_{'driver' if i == 0 else 'passenger' if i == 1 else 'rear_left' if i == 2 else 'rear_center' if i == 3 else 'rear_right'}"))
        if level and level > 0:
            seats.append(f"{name}:{level}")
    if seats:
        lines.append(f"  Seat heat:  {', '.join(seats)}")
    
    return "\n".join(lines)


def format_drive_state(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("🚗 Drive State")
    lines.append("─" * 40)
    
    shift = data.get("shift_state") or "P"
    speed = data.get("speed") or 0
    power = data.get("power", 0)
    
    lines.append(f"  Gear:       {shift}")
    if speed:
        speed_kmh = speed * 1.60934
        lines.append(f"  Speed:      {speed_kmh:.0f} km/h ({speed} mph)")
    lines.append(f"  Power:      {power} kW")
    
    heading = data.get("heading")
    if heading is not None:
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        idx = int((heading + 22.5) / 45) % 8
        lines.append(f"  Heading:    {heading}° ({directions[idx]})")
    
    return "\n".join(lines)


def format_location(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("📍 Location")
    lines.append("─" * 40)
    
    lat = data.get("latitude")
    lon = data.get("longitude")
    
    if lat and lon:
        lines.append(f"  Coords:     {lat:.6f}, {lon:.6f}")
    else:
        lines.append("  (no location data)")
    
    return "\n".join(lines)


def format_vehicle_state(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("🔒 Vehicle State")
    lines.append("─" * 40)
    
    locked = data.get("locked", False)
    odometer = data.get("odometer", 0)
    odo_km = odometer * 1.60934
    
    lines.append(f"  Locked:     {'Yes' if locked else 'No'}")
    lines.append(f"  Odometer:   {odo_km:,.0f} km ({odometer:,.0f} mi)")
    
    # Doors
    doors = []
    if data.get("df"): doors.append("Driver front")
    if data.get("pf"): doors.append("Pass front")  
    if data.get("dr"): doors.append("Driver rear")
    if data.get("pr"): doors.append("Pass rear")
    if data.get("ft"): doors.append("Frunk")
    if data.get("rt"): doors.append("Trunk")
    if doors:
        lines.append(f"  Open:       {', '.join(doors)}")
    
    # Windows
    windows = []
    if data.get("fd_window"): windows.append("FD")
    if data.get("fp_window"): windows.append("FP")
    if data.get("rd_window"): windows.append("RD")
    if data.get("rp_window"): windows.append("RP")
    if windows:
        lines.append(f"  Windows:    {', '.join(windows)} open")
    
    sw_ver = data.get("car_version", "")
    if sw_ver:
        lines.append(f"  Software:   {sw_ver.split()[0]}")
    
    return "\n".join(lines)


def format_gui_settings(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("⚙️  GUI Settings")
    lines.append("─" * 40)
    
    lines.append(f"  Distance:   {data.get('gui_distance_units', '?')}")
    lines.append(f"  Temp:       {data.get('gui_temperature_units', '?')}")
    lines.append(f"  Charge:     {data.get('gui_charge_rate_units', '?')}")
    lines.append(f"  Range:      {data.get('gui_range_display', '?')}")
    lines.append(f"  24h time:   {data.get('gui_24_hour_time', '?')}")
    
    return "\n".join(lines)


def format_vehicle_config(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("🚙 Vehicle Config")
    lines.append("─" * 40)
    
    lines.append(f"  Model:      {data.get('car_type', '?')}")
    lines.append(f"  Trim:       {data.get('trim_badging', '?')}")
    lines.append(f"  Color:      {data.get('exterior_color', '?')}")
    lines.append(f"  Wheels:     {data.get('wheel_type', '?')}")
    lines.append(f"  Seats:      {data.get('seat_type', '?')}")
    
    if data.get("has_air_suspension"):
        lines.append("  Suspension: Air")
    
    return "\n".join(lines)


def format_response(response: Dict[str, Any], requested: List[str]) -> str:
    sections = []
    
    # Header with vehicle name
    display_name = response.get("display_name")
    state = response.get("state", "unknown")
    vin = response.get("vin", "")
    sections.append(f"🚗 {display_name} ({state})")
    sections.append(f"   VIN: {vin}")
    sections.append("")
    
    show_all = "all" in requested
    
    # Format each requested endpoint
    if "charge_state" in response and (show_all or "charge_state" in requested):
        sections.append(format_charge_state(response["charge_state"]))
        sections.append("")
    
    if "climate_state" in response and (show_all or "climate_state" in requested):
        sections.append(format_climate_state(response["climate_state"]))
        sections.append("")
    
    if "drive_state" in response and (show_all or "drive_state" in requested):
        sections.append(format_drive_state(response["drive_state"]))
        sections.append("")
    
    # Location is separate from drive_state display
    if "drive_state" in response and (show_all or "location_data" in requested):
        sections.append(format_location(response["drive_state"]))
        sections.append("")
    
    if "vehicle_state" in response and (show_all or "vehicle_state" in requested):
        sections.append(format_vehicle_state(response["vehicle_state"]))
        sections.append("")
    
    if "gui_settings" in response and (show_all or "gui_settings" in requested):
        sections.append(format_gui_settings(response["gui_settings"]))
        sections.append("")
    
    if "vehicle_config" in response and (show_all or "vehicle_config" in requested):
        sections.append(format_vehicle_config(response["vehicle_config"]))
        sections.append("")
    
    return "\n".join(sections).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch Tesla vehicle data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                  # single vehicle, all data
  %(prog)s flash            # by name (case-insensitive)
  %(prog)s XP7Y... -c       # by VIN, charge only
  %(prog)s -c -t            # charge + climate
  %(prog)s --json           # raw JSON output
"""
    )
    
    parser.add_argument("vehicle", metavar="VEHICLE", nargs="?", default=None,
                       help="Vehicle VIN or name (optional if only one vehicle)")
    parser.add_argument("--dir", default=DEFAULT_DIR, help="Config directory (default: ~/.clawdbot/tesla-fleet-api)")
    parser.add_argument("--json", action="store_true", dest="raw_json", help="Output raw JSON")
    
    # Endpoint flags
    parser.add_argument("-c", "--charge", action="store_true", help="Charge state")
    parser.add_argument("-t", "--climate", action="store_true", help="Climate state")
    parser.add_argument("-d", "--drive", action="store_true", help="Drive state")
    parser.add_argument("-l", "--location", action="store_true", help="Location data")
    parser.add_argument("-s", "--state", action="store_true", dest="vehicle_state", help="Vehicle state (locks, doors, odometer)")
    parser.add_argument("-g", "--gui", action="store_true", help="GUI settings")
    parser.add_argument("--config-data", action="store_true", dest="vehicle_config", help="Vehicle config")
    
    args = parser.parse_args()
    
    # Load state
    dir_path = args.dir
    load_env_file(dir_path)
    ensure_migrated(dir_path)

    cfg = get_config(dir_path)
    auth = get_auth(dir_path)

    token = auth.get("access_token")
    base_url = cfg.get("base_url") or cfg.get("audience") or "https://fleet-api.prd.eu.vn.cloud.tesla.com"
    ca_cert = cfg.get("ca_cert")

    if not token:
        print("No access token found. Run auth.py to authenticate.", file=sys.stderr)
        return 1

    # Resolve vehicle (by VIN, name, or auto-select if single)
    vin, display_name = resolve_vehicle(args.vehicle, dir_path, base_url, token, ca_cert)
    
    # Build endpoints list
    selected = []
    if args.charge: selected.append("charge_state")
    if args.climate: selected.append("climate_state")
    if args.drive: selected.append("drive_state")
    if args.location: selected.append("location_data")
    if args.vehicle_state: selected.append("vehicle_state")
    if args.gui: selected.append("gui_settings")
    if args.vehicle_config: selected.append("vehicle_config")
    
    # Build URL
    vin_encoded = urllib.parse.quote(vin)
    url = f"{base_url.rstrip('/')}/api/1/vehicles/{vin_encoded}/vehicle_data"
    
    if selected:
        endpoints_param = "%3B".join(selected)  # URL-encoded semicolon
        url += f"?endpoints={endpoints_param}"
        requested = selected
    else:
        # Fetch all endpoints by default (including location_data)
        all_endpoints = ["charge_state", "climate_state", "drive_state", "location_data", 
                        "vehicle_state", "gui_settings", "vehicle_config"]
        endpoints_param = "%3B".join(all_endpoints)
        url += f"?endpoints={endpoints_param}"
        requested = ["all"]
    
    # Fetch data
    try:
        data = http_json("GET", url, token, ca_cert)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    response = data.get("response", data)
    
    # Inject display_name if we have it from cache
    if display_name and not response.get("display_name"):
        response["display_name"] = display_name
    
    # Output
    if args.raw_json:
        print(json.dumps(data, indent=2))
    else:
        print(format_response(response, requested))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
