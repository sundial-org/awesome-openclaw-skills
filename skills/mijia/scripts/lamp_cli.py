#!/usr/bin/env python3
"""Desk lamp control CLI for Mijia devices."""
import argparse
import os
import sys
from mijiaAPI import mijiaAPI, mijiaDevice

# Get device ID from environment variable
LAMP_DID = os.environ.get("MIJIA_LAMP_DID")

if not LAMP_DID:
    print("Error: MIJIA_LAMP_DID environment variable not set")
    print("Please set it with: export MIJIA_LAMP_DID='your_device_id'")
    sys.exit(1)

def get_lamp(api: mijiaAPI) -> mijiaDevice:
    """Get the lamp device."""
    return mijiaDevice(api, did=LAMP_DID)

def cmd_on(args, api):
    """Turn on the lamp."""
    lamp = get_lamp(api)
    lamp.on = True
    print("Lamp turned on")

def cmd_off(args, api):
    """Turn off the lamp."""
    lamp = get_lamp(api)
    lamp.on = False
    print("Lamp turned off")

def cmd_toggle(args, api):
    """Toggle lamp power."""
    lamp = get_lamp(api)
    lamp.run_action('toggle')
    print("Lamp toggled")

def cmd_status(args, api):
    """Show lamp status."""
    lamp = get_lamp(api)
    on_status = lamp.get('on')
    brightness = lamp.get('brightness')
    color_temp = lamp.get('color-temperature')

    status = "On" if on_status else "Off"
    print(f"Status: {status}")
    print(f"Brightness: {brightness}%")
    print(f"Color Temperature: {color_temp}K")

def cmd_brightness(args, api):
    """Set brightness."""
    lamp = get_lamp(api)
    lamp.brightness = args.value
    print(f"Brightness set to {args.value}%")

def cmd_temp(args, api):
    """Set color temperature."""
    lamp = get_lamp(api)
    lamp.color_temperature = args.value
    print(f"Color temperature set to {args.value}K")

def cmd_mode(args, api):
    """Set lighting mode."""
    modes = {
        'reading': 0,
        'computer': 1,
        'night': 2,
        'antiblue': 3,
        'work': 4,
        'candle': 5,
        'twinkle': 6
    }
    mode_names = {
        0: 'Reading',
        1: 'Computer',
        2: 'Night Reading',
        3: 'Anti-blue Light',
        4: 'Work',
        5: 'Candle',
        6: 'Twinkle'
    }

    if args.value in modes:
        mode_val = modes[args.value]
    else:
        try:
            mode_val = int(args.value)
            if mode_val not in mode_names:
                raise ValueError()
        except ValueError:
            print(f"Invalid mode: {args.value}")
            print("Available modes: reading, computer, night, antiblue, work, candle, twinkle (0-6)")
            sys.exit(1)

    lamp = get_lamp(api)
    lamp.set('mode', mode_val)
    print(f"Mode set to {mode_names[mode_val]}")

def main():
    parser = argparse.ArgumentParser(description='Desk Lamp Control CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # on
    subparsers.add_parser('on', help='Turn on the lamp')

    # off
    subparsers.add_parser('off', help='Turn off the lamp')

    # toggle
    subparsers.add_parser('toggle', help='Toggle lamp power')

    # status
    subparsers.add_parser('status', help='Show lamp status')

    # brightness
    p_brightness = subparsers.add_parser('brightness', help='Set brightness (1-100)')
    p_brightness.add_argument('value', type=int, choices=range(1, 101), metavar='1-100', help='Brightness value')

    # temp
    p_temp = subparsers.add_parser('temp', help='Set color temperature (2700-6500K)')
    p_temp.add_argument('value', type=int, help='Color temperature (2700-6500)')

    # mode
    p_mode = subparsers.add_parser('mode', help='Set lighting mode')
    p_mode.add_argument('value', help='Mode: reading/computer/night/antiblue/work/candle/twinkle or 0-6')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize API
    api = mijiaAPI()
    api.login()

    # Execute command
    cmd_map = {
        'on': cmd_on,
        'off': cmd_off,
        'toggle': cmd_toggle,
        'status': cmd_status,
        'brightness': cmd_brightness,
        'temp': cmd_temp,
        'mode': cmd_mode
    }

    cmd_map[args.command](args, api)

if __name__ == '__main__':
    main()
