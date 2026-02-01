#!/usr/bin/env python3
"""
Example usage of Dirigera control helpers

Run this script to see all helper functions in action
"""
import sys
from helpers import (
    init_hub,
    get_lights_by_room,
    get_lights_by_state,
    get_unreachable_devices,
    get_low_battery_controllers,
    safe_light_control,
    safe_outlet_control,
    turn_off_room_lights,
    status_report,
    battery_report
)

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def main():
    hub = init_hub()

    print("="*80)
    print(" Dirigera Control - Example Usage")
    print("="*80)

    # Example 1: Get lights by room
    print("\n1. Get all kitchen lights:")
    kitchen_lights = get_lights_by_room(hub, "Køkken")
    for light in kitchen_lights:
        state = "ON" if light.attributes.is_on else "OFF"
        print(f"  - {light.attributes.custom_name}: {state}")

    # Example 2: Get lights by state
    print("\n2. Get all lights that are ON:")
    lights_on = get_lights_by_state(hub, on=True)
    print(f"  Found {len(lights_on)} lights ON")

    # Example 3: Get unreachable devices
    print("\n3. Check for offline devices:")
    unreachable = get_unreachable_devices(hub)
    if unreachable:
        print(f"  {len(unreachable)} devices offline:")
        for device in unreachable:
            print(f"    - {device.attributes.custom_name}")
    else:
        print("  All devices are online")

    # Example 4: Check battery levels
    print("\n4. Battery status:")
    batteries = battery_report(hub)
    for ctrl in batteries:
        print(f"  {ctrl['name']}: {ctrl['battery']}% - {ctrl['status']}")

    # Example 5: Low battery warning
    print("\n5. Low battery controllers:")
    low_battery = get_low_battery_controllers(hub, threshold=20)
    if low_battery:
        for ctrl in low_battery:
            print(f"  ⚠️  {ctrl.attributes.custom_name}: {ctrl.attributes.battery_percentage}%")
    else:
        print("  All controllers have sufficient battery")

    # Example 6: Complete status report
    print("\n6. Complete home status:")
    status = status_report(hub)
    print(f"  Lights: {status['lights']['on']}/{status['lights']['total']} ON")
    print(f"  Outlets: {status['outlets']['on']}/{status['outlets']['total']} ON")
    print(f"  Controllers: {status['controllers']['total']} total")
    print(f"  Offline devices: {status['unreachable_devices']}")

    # Example 7: Safe light control (commented to avoid changing state)
    print("\n7. Safe light control example (commented out):")
    print("  # result = safe_light_control(hub, 'bedroom light', turn_on=True, brightness=50)")
    print("  # print(result)")

    # Example 8: Safe outlet control (commented to avoid changing state)
    print("\n8. Safe outlet control example (commented out):")
    print("  # result = safe_outlet_control(hub, 'living room', turn_on=True)")
    print("  # print(result)")

    print("\n" + "="*80)
    print(" Examples complete!")
    print("="*80)


if __name__ == "__main__":
    main()
