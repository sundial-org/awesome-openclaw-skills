#!/usr/bin/env python3
"""
LG ThinQ CLI - Control LG smart appliances.
"""
import asyncio
import os
import sys
import json
import uuid
from pathlib import Path
from aiohttp import ClientSession

# Try to import thinqconnect
try:
    from thinqconnect.thinq_api import ThinQApi
except ImportError:
    print("❌ thinqconnect not installed. Run: pip install thinqconnect")
    sys.exit(1)

CONFIG_DIR = Path.home() / ".config" / "lg-thinq"
TOKEN_FILE = CONFIG_DIR / "token"
COUNTRY_FILE = CONFIG_DIR / "country"
DEVICES_CACHE = CONFIG_DIR / "devices.json"

def get_config():
    """Load token and country from config files."""
    if not TOKEN_FILE.exists():
        print(f"❌ Token not found. Save it to: {TOKEN_FILE}")
        sys.exit(1)
    
    token = TOKEN_FILE.read_text().strip()
    country = COUNTRY_FILE.read_text().strip() if COUNTRY_FILE.exists() else "US"
    return token, country

def get_cached_devices():
    """Get cached device list."""
    if DEVICES_CACHE.exists():
        return json.loads(DEVICES_CACHE.read_text())
    return None

def cache_devices(devices):
    """Cache device list."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DEVICES_CACHE.write_text(json.dumps(devices, indent=2))

def find_device_id(alias_or_id, devices):
    """Find device by alias or partial ID."""
    alias_lower = alias_or_id.lower()
    
    # Common aliases
    aliases = {
        'fridge': ['refrigerator', 'fridge'],
        'washer': ['washer', 'washing'],
        'dryer': ['dryer', 'washtower_dryer'],
        'ac': ['air_conditioner', 'aircon'],
    }
    
    # Expand search terms
    search_terms = [alias_lower]
    for key, vals in aliases.items():
        if alias_lower == key or alias_lower in vals:
            search_terms.extend(vals)
    
    for d in devices:
        info = d.get('deviceInfo', {})
        device_alias = info.get('alias', '').lower()
        device_type = info.get('deviceType', '').lower()
        
        for term in search_terms:
            if term in device_alias or term in device_type:
                return d['deviceId']
        
        if d['deviceId'].startswith(alias_or_id):
            return d['deviceId']
    
    return alias_or_id  # Return as-is if no match

async def list_devices(token, country):
    """List all devices."""
    client_id = str(uuid.uuid4())
    async with ClientSession() as session:
        api = ThinQApi(session=session, access_token=token, country_code=country, client_id=client_id)
        devices = await api.async_get_device_list()
        cache_devices(devices)
        return devices

async def get_status(token, country, device_id):
    """Get device status."""
    client_id = str(uuid.uuid4())
    async with ClientSession() as session:
        api = ThinQApi(session=session, access_token=token, country_code=country, client_id=client_id)
        return await api.async_get_device_status(device_id)

async def control_device(token, country, device_id, payload):
    """Send control command to device."""
    client_id = str(uuid.uuid4())
    async with ClientSession() as session:
        api = ThinQApi(session=session, access_token=token, country_code=country, client_id=client_id)
        return await api.async_post_device_control(device_id, payload)

def print_devices(devices):
    """Pretty print device list."""
    print(f"\n🏠 Found {len(devices)} device(s):\n")
    for d in devices:
        info = d.get('deviceInfo', {})
        print(f"  📦 {info.get('alias', 'Unknown')}")
        print(f"     Type: {info.get('deviceType', 'Unknown')}")
        print(f"     Model: {info.get('modelName', 'Unknown')}")
        print(f"     ID: {d['deviceId'][:16]}...")
        print()

def print_fridge_status(status):
    """Pretty print refrigerator status."""
    print("\n🧊 Refrigerator Status:\n")
    
    # Temperature
    temps = status.get('temperature', [])
    for t in temps:
        loc = t.get('locationName', 'Unknown')
        temp = t.get('targetTemperature', '?')
        unit = t.get('unit', 'C')
        emoji = "❄️" if loc == "FREEZER" else "🌡️"
        print(f"  {emoji} {loc}: {temp}°{unit}")
    
    # Door
    doors = status.get('doorStatus', [])
    for d in doors:
        state = d.get('doorState', 'Unknown')
        emoji = "🚪" if state == "CLOSE" else "⚠️"
        print(f"  {emoji} Door: {state}")
    
    # Modes
    refrig = status.get('refrigeration', {})
    eco = status.get('ecoFriendly', {})
    
    express_fridge = "ON" if refrig.get('expressFridge') else "OFF"
    express_mode = "ON" if refrig.get('expressMode') else "OFF"
    eco_mode = "ON" if eco.get('ecoFriendlyMode') else "OFF"
    
    print(f"\n  ⚡ Express Fridge: {express_fridge}")
    print(f"  ⚡ Express Freeze: {express_mode}")
    print(f"  🌿 Eco Mode: {eco_mode}")
    print()

def print_washer_status(status):
    """Pretty print washer/dryer status."""
    print("\n🧺 Washer/Dryer Status:\n")
    
    run_state = status.get('runState', {})
    state = run_state.get('currentState', 'Unknown')
    print(f"  📍 State: {state}")
    
    timer = status.get('timer', {})
    remain_h = timer.get('remainHour', 0)
    remain_m = timer.get('remainMinute', 0)
    if remain_h or remain_m:
        print(f"  ⏱️ Remaining: {remain_h}h {remain_m}m")
    
    remote = status.get('remoteControlEnable', {})
    if remote:
        enabled = "Yes" if remote.get('remoteControlEnabled') else "No"
        print(f"  📱 Remote Control: {enabled}")
    print()

def main():
    if len(sys.argv) < 2:
        print("Usage: thinq.py <command> [args]")
        print("\nCommands:")
        print("  devices              List all devices")
        print("  status <device>      Get device status")
        print("  fridge-temp <temp>   Set fridge temperature (0-6°C)")
        print("  freezer-temp <temp>  Set freezer temperature")
        print("  express-fridge on|off")
        print("  express-freeze on|off")
        print("  eco on|off")
        print("  raw <device> <json>  Send raw command")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    token, country = get_config()
    
    # List devices
    if cmd == "devices":
        devices = asyncio.run(list_devices(token, country))
        print_devices(devices)
        return
    
    # Get cached devices for lookups
    devices = get_cached_devices()
    if not devices:
        devices = asyncio.run(list_devices(token, country))
    
    # Status
    if cmd == "status":
        if len(sys.argv) < 3:
            print("Usage: thinq.py status <device>")
            sys.exit(1)
        
        device_id = find_device_id(sys.argv[2], devices)
        try:
            status = asyncio.run(get_status(token, country, device_id))
            
            # Detect device type and print accordingly
            if 'temperature' in status and 'refrigeration' in status:
                print_fridge_status(status)
            elif 'runState' in status:
                print_washer_status(status)
            else:
                print(json.dumps(status, indent=2))
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        return
    
    # Find fridge device for control commands
    fridge_id = None
    for d in devices:
        if 'REFRIGERATOR' in d.get('deviceInfo', {}).get('deviceType', ''):
            fridge_id = d['deviceId']
            break
    
    if not fridge_id and cmd in ['fridge-temp', 'freezer-temp', 'express-fridge', 'express-freeze', 'eco']:
        print("❌ No refrigerator found")
        sys.exit(1)
    
    # Fridge temperature
    if cmd == "fridge-temp":
        if len(sys.argv) < 3:
            print("Usage: thinq.py fridge-temp <0-6>")
            sys.exit(1)
        temp = int(sys.argv[2])
        if not 0 <= temp <= 6:
            print("❌ Fridge temp must be 0-6°C")
            sys.exit(1)
        payload = {"temperature": {"targetTemperature": temp, "locationName": "FRIDGE", "unit": "C"}}
        asyncio.run(control_device(token, country, fridge_id, payload))
        print(f"✅ Fridge set to {temp}°C")
        return
    
    # Freezer temperature
    if cmd == "freezer-temp":
        if len(sys.argv) < 3:
            print("Usage: thinq.py freezer-temp <temp>")
            sys.exit(1)
        temp = int(sys.argv[2])
        payload = {"temperature": {"targetTemperature": temp, "locationName": "FREEZER", "unit": "C"}}
        asyncio.run(control_device(token, country, fridge_id, payload))
        print(f"✅ Freezer set to {temp}°C")
        return
    
    # Express fridge
    if cmd == "express-fridge":
        if len(sys.argv) < 3:
            print("Usage: thinq.py express-fridge on|off")
            sys.exit(1)
        value = sys.argv[2].lower() == "on"
        payload = {"refrigeration": {"expressFridge": value}}
        asyncio.run(control_device(token, country, fridge_id, payload))
        print(f"✅ Express Fridge: {'ON' if value else 'OFF'}")
        return
    
    # Express freeze
    if cmd == "express-freeze":
        if len(sys.argv) < 3:
            print("Usage: thinq.py express-freeze on|off")
            sys.exit(1)
        value = sys.argv[2].lower() == "on"
        payload = {"refrigeration": {"expressMode": value}}
        asyncio.run(control_device(token, country, fridge_id, payload))
        print(f"✅ Express Freeze: {'ON' if value else 'OFF'}")
        return
    
    # Eco mode
    if cmd == "eco":
        if len(sys.argv) < 3:
            print("Usage: thinq.py eco on|off")
            sys.exit(1)
        value = sys.argv[2].lower() == "on"
        payload = {"ecoFriendly": {"ecoFriendlyMode": value}}
        asyncio.run(control_device(token, country, fridge_id, payload))
        print(f"✅ Eco Mode: {'ON' if value else 'OFF'}")
        return
    
    # Raw command
    if cmd == "raw":
        if len(sys.argv) < 4:
            print("Usage: thinq.py raw <device> <json>")
            sys.exit(1)
        device_id = find_device_id(sys.argv[2], devices)
        payload = json.loads(sys.argv[3])
        result = asyncio.run(control_device(token, country, device_id, payload))
        print(f"✅ Done: {result}")
        return
    
    print(f"❌ Unknown command: {cmd}")
    sys.exit(1)

if __name__ == "__main__":
    main()
