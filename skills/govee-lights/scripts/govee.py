#!/usr/bin/env python3
"""Govee API wrapper for controlling smart lights."""

import argparse
import json
import os
import sys
import uuid
import requests

# Get API key from environment variable
API_KEY = os.environ.get("GOVEE_API_KEY")
if not API_KEY:
    raise ValueError("GOVEE_API_KEY environment variable not set. "
                     "Get your key from https://developer.govee.com/")

BASE_URL = "https://openapi.api.govee.com/router/api/v1"

HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def get_devices():
    """Fetch all devices linked to your Govee account."""
    response = requests.get(f"{BASE_URL}/user/devices", headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    if data.get("code") == 200:
        data_list = data.get("data", [])
        # data is a list directly, not wrapped in a dict
        if isinstance(data_list, list):
            return data_list
        return data_list.get("devices", [])
    raise Exception(f"Failed to get devices: {data}")


def get_device_by_name(devices, name):
    """Find a device by partial name match (case-insensitive)."""
    name_lower = name.lower()
    for device in devices:
        device_name = device.get("deviceName", "").lower()
        if name_lower in device_name:
            return device
    return None


def control_device(sku, device_id, capability):
    """Send control command to a device."""
    payload = {
        "requestId": str(uuid.uuid4()),
        "payload": {
            "sku": sku,
            "device": device_id,
            "capability": capability
        }
    }
    response = requests.post(
        f"{BASE_URL}/device/control",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") == 200:
        return True
    raise Exception(f"Control failed: {data}")


def turn_on(sku, device_id):
    """Turn device on."""
    return control_device(sku, device_id, {
        "type": "devices.capabilities.on_off",
        "instance": "powerSwitch",
        "value": 1
    })


def turn_off(sku, device_id):
    """Turn device off."""
    return control_device(sku, device_id, {
        "type": "devices.capabilities.on_off",
        "instance": "powerSwitch",
        "value": 0
    })


def set_brightness(sku, device_id, brightness):
    """Set brightness (0-100)."""
    return control_device(sku, device_id, {
        "type": "devices.capabilities.brightness",
        "instance": "brightness",
        "value": brightness
    })


def set_color(sku, device_id, rgb_tuple):
    """Set color by RGB tuple (r, g, b)."""
    r, g, b = rgb_tuple
    color_value = (r << 16) + (g << 8) + b
    return control_device(sku, device_id, {
        "type": "devices.capabilities.color_setting",
        "instance": "colorRgb",
        "value": color_value
    })


def set_color_temperature(sku, device_id, kelvin):
    """Set color temperature in Kelvin."""
    return control_device(sku, device_id, {
        "type": "devices.capabilities.color_setting",
        "instance": "colorTemp",
        "value": kelvin
    })


def list_devices():
    """List all devices in a user-friendly format."""
    devices = get_devices()
    for device in devices:
        print(f"- {device.get('deviceName')}: {device.get('device')}")
    return devices


def main():
    parser = argparse.ArgumentParser(description="Govee Light Control")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List devices
    subparsers.add_parser("list", help="List all Govee devices")

    # Turn on/off
    on_parser = subparsers.add_parser("on", help="Turn device on")
    on_parser.add_argument("device", help="Device name or ID")

    off_parser = subparsers.add_parser("off", help="Turn device off")
    off_parser.add_argument("device", help="Device name or ID")

    # Brightness
    bright_parser = subparsers.add_parser("brightness", help="Set brightness")
    bright_parser.add_argument("device", help="Device name or ID")
    bright_parser.add_argument("level", type=int, help="Brightness 0-100")

    # Color
    color_parser = subparsers.add_parser("color", help="Set RGB color")
    color_parser.add_argument("device", help="Device name or ID")
    color_parser.add_argument("r", type=int, help="Red (0-255)")
    color_parser.add_argument("g", type=int, help="Green (0-255)")
    color_parser.add_argument("b", type=int, help="Blue (0-255)")

    args = parser.parse_args()

    try:
        if args.command == "list":
            list_devices()

        elif args.command == "on" or args.command == "off":
            devices = get_devices()
            device = get_device_by_name(devices, args.device)
            if not device:
                print(f"Device not found: {args.device}")
                sys.exit(1)

            if args.command == "on":
                turn_on(device.get("sku"), device.get("device"))
                print(f"Turned on: {device.get('deviceName')}")
            else:
                turn_off(device.get("sku"), device.get("device"))
                print(f"Turned off: {device.get('deviceName')}")

        elif args.command == "brightness":
            devices = get_devices()
            device = get_device_by_name(devices, args.device)
            if not device:
                print(f"Device not found: {args.device}")
                sys.exit(1)

            brightness = max(0, min(100, args.level))
            set_brightness(device.get("sku"), device.get("device"), brightness)
            print(f"Set brightness to {brightness}%: {device.get('deviceName')}")

        elif args.command == "color":
            devices = get_devices()
            device = get_device_by_name(devices, args.device)
            if not device:
                print(f"Device not found: {args.device}")
                sys.exit(1)

            rgb = (max(0, min(255, args.r)),
                   max(0, min(255, args.g)),
                   max(0, min(255, args.b)))
            set_color(device.get("sku"), device.get("device"), rgb)
            print(f"Set color to RGB{rgb}: {device.get('deviceName')}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
