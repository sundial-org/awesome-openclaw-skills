#!/usr/bin/env python3
"""
WLED CLI controller - Control WLED devices via HTTP API
"""
import argparse
import json
import sys
import os
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from pathlib import Path


def wled_request(host: str, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Any:
    """Make a request to the WLED device."""
    url = f"http://{host}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        headers=headers,
        method=method
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_power(host: str, state: Optional[bool] = None) -> None:
    """Get or set power state."""
    if state is None:
        info = wled_request(host, "json/state")
        print("on" if info.get("on", False) else "off")
    else:
        wled_request(host, "json/state", "POST", {"on": state})
        print(f"Power {'on' if state else 'off'}")


def cmd_brightness(host: str, level: Optional[int] = None) -> None:
    """Get or set brightness (0-255)."""
    if level is None:
        info = wled_request(host, "json/state")
        print(info.get("bri", 128))
    else:
        wled_request(host, "json/state", "POST", {"bri": max(0, min(255, level))})
        print(f"Brightness set to {level}")


def cmd_color(host: str, r: int, g: int, b: int) -> None:
    """Set RGB color."""
    wled_request(host, "json/state", "POST", {
        "seg": [{"col": [[r, g, b]]}]
    })
    print(f"Color set to RGB({r}, {g}, {b})")


def cmd_effect(host: str, effect_id: Optional[int] = None, speed: Optional[int] = None, intensity: Optional[int] = None) -> None:
    """Get or set effect."""
    if effect_id is None:
        info = wled_request(host, "json/state")
        fx = info.get("seg", [{}])[0].get("fx", 0)
        print(fx)
    else:
        payload: Dict[str, Any] = {"seg": [{"fx": effect_id}]}
        if speed is not None:
            payload["seg"][0]["sx"] = max(0, min(255, speed))
        if intensity is not None:
            payload["seg"][0]["ix"] = max(0, min(255, intensity))
        wled_request(host, "json/state", "POST", payload)
        print(f"Effect set to ID {effect_id}")


def cmd_effects(host: str) -> None:
    """List available effects."""
    info = wled_request(host, "json")
    effects = info.get("effects", [])
    for i, name in enumerate(effects):
        print(f"{i}: {name}")


def cmd_palette(host: str, palette_id: Optional[int] = None) -> None:
    """Get or set color palette."""
    if palette_id is None:
        info = wled_request(host, "json/state")
        pal = info.get("seg", [{}])[0].get("pal", 0)
        print(pal)
    else:
        wled_request(host, "json/state", "POST", {"seg": [{"pal": palette_id}]})
        print(f"Palette set to ID {palette_id}")


def cmd_palettes(host: str) -> None:
    """List available palettes."""
    info = wled_request(host, "json")
    palettes = info.get("palettes", [])
    for i, name in enumerate(palettes):
        print(f"{i}: {name}")


def cmd_status(host: str) -> None:
    """Get full device status."""
    info = wled_request(host, "json")
    state = info.get("state", {})
    info_data = info.get("info", {})
    
    print(f"Device: {info_data.get('name', 'Unknown')}")
    print(f"Power: {'on' if state.get('on', False) else 'off'}")
    print(f"Brightness: {state.get('bri', 128)}")
    
    seg = state.get("seg", [{}])[0]
    print(f"Effect: {seg.get('fx', 0)} - {info.get('effects', [''])[seg.get('fx', 0)]}")
    print(f"Palette: {seg.get('pal', 0)} - {info.get('palettes', [''])[seg.get('pal', 0)]}")
    print(f"FPS: {info_data.get('fps', 'N/A')}")
    print(f"Uptime: {info_data.get('uptime', 'N/A')}s")


def cmd_presets(host: str) -> None:
    """List saved presets."""
    info = wled_request(host, "json")
    presets = info.get("presets", [])
    for preset in presets:
        pid = preset.get("id", "?")
        name = preset.get("n", f"Preset {pid}")
        print(f"{pid}: {name}")


def cmd_preset(host: str, preset_id: int) -> None:
    """Load a preset."""
    wled_request(host, "json/state", "POST", {"ps": preset_id})
    print(f"Loaded preset {preset_id}")


def load_config() -> Dict[str, str]:
    """Load device aliases from config file."""
    config_paths = [
        Path.home() / ".wled" / "config.json",
        Path.home() / ".config" / "wled" / "config.json",
        Path(".wled-config.json"),
    ]
    
    for path in config_paths:
        if path.exists():
            try:
                with open(path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                continue
    
    return {}


def main():
    config = load_config()
    
    parser = argparse.ArgumentParser(
        description="WLED Controller",
        epilog="Config: Set up ~/.wled/config.json with device aliases to avoid --host parameter.\n"
               "Example: {\"bedroom\": \"192.168.1.100\", \"kitchen\": \"192.168.1.101\"}"
    )
    parser.add_argument("--host", "-H", help="WLED device IP, hostname, or alias from config")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # power
    p_power = subparsers.add_parser("power", help="Control power")
    p_power.add_argument("state", nargs="?", choices=["on", "off"])
    
    # brightness
    p_bri = subparsers.add_parser("brightness", help="Control brightness")
    p_bri.add_argument("level", nargs="?", type=int)
    
    # color
    p_color = subparsers.add_parser("color", help="Set RGB color")
    p_color.add_argument("r", type=int)
    p_color.add_argument("g", type=int)
    p_color.add_argument("b", type=int)
    
    # effect
    p_effect = subparsers.add_parser("effect", help="Control effects")
    p_effect.add_argument("id", nargs="?", type=int)
    p_effect.add_argument("--speed", "-s", type=int, help="Effect speed (0-255)")
    p_effect.add_argument("--intensity", "-i", type=int, help="Effect intensity (0-255)")
    
    # effects
    subparsers.add_parser("effects", help="List effects")
    
    # palette
    p_palette = subparsers.add_parser("palette", help="Control palette")
    p_palette.add_argument("id", nargs="?", type=int)
    
    # palettes
    subparsers.add_parser("palettes", help="List palettes")
    
    # status
    subparsers.add_parser("status", help="Get device status")
    
    # presets
    subparsers.add_parser("presets", help="List presets")
    
    # preset
    p_preset = subparsers.add_parser("preset", help="Load preset")
    p_preset.add_argument("id", type=int)
    
    args = parser.parse_args()
    
    # Resolve host: alias from config, --host arg, or WLED_HOST env var
    host = None
    if args.host and args.host in config:
        host = config[args.host]
    elif args.host:
        host = args.host
    else:
        host = os.getenv("WLED_HOST")
    
    if not host:
        parser.error("--host required or set WLED_HOST env var or configure ~/.wled/config.json")
    
    if args.command == "power":
        state = {"on": True, "off": False}.get(args.state) if args.state else None
        cmd_power(host, state)
    elif args.command == "brightness":
        cmd_brightness(host, args.level)
    elif args.command == "color":
        cmd_color(host, args.r, args.g, args.b)
    elif args.command == "effect":
        cmd_effect(host, args.id, args.speed, args.intensity)
    elif args.command == "effects":
        cmd_effects(host)
    elif args.command == "palette":
        cmd_palette(host, args.id)
    elif args.command == "palettes":
        cmd_palettes(host)
    elif args.command == "status":
        cmd_status(host)
    elif args.command == "presets":
        cmd_presets(host)
    elif args.command == "preset":
        cmd_preset(host, args.id)


if __name__ == "__main__":
    main()
