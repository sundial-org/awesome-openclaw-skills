#!/usr/bin/env python3
"""
Dirigera Helper Utilities
Reusable functions for common smart home operations
"""
import dirigera
import time
from typing import List, Optional


def init_hub() -> dirigera.Hub:
    """Initialize and return hub connection"""
    return dirigera.Hub(
        token="token_goes_here",
        ip_address="ip_address_goes_here"
    )


def get_lights_by_room(hub: dirigera.Hub, room_name: str) -> List:
    """Get all lights in a specific room"""
    return [light for light in hub.get_lights()
            if light.room and light.room.name == room_name]


def get_lights_by_state(hub: dirigera.Hub, on: bool = True) -> List:
    """Get all lights that are ON or OFF"""
    return [light for light in hub.get_lights()
            if light.attributes.is_on == on]


def get_outlets_by_state(hub: dirigera.Hub, on: bool = True) -> List:
    """Get all outlets that are ON or OFF"""
    return [outlet for outlet in hub.get_outlets()
            if outlet.attributes.is_on == on]


def get_unreachable_devices(hub: dirigera.Hub) -> List:
    """Get all offline/unreachable devices"""
    return [device for device in hub.get_all_devices()
            if not device.is_reachable]


def get_low_battery_controllers(hub: dirigera.Hub, threshold: int = 20) -> List:
    """Get controllers with battery below threshold percentage"""
    return [ctrl for ctrl in hub.get_controllers()
            if ctrl.attributes.battery_percentage < threshold]


def safe_light_control(hub: dirigera.Hub,
                      light_name: str,
                      turn_on: bool,
                      brightness: Optional[int] = None,
                      color_temp: Optional[int] = None) -> str:
    """
    Safely control a light with error handling

    Args:
        hub: Dirigera hub instance
        light_name: Name of the light
        turn_on: True to turn on, False to turn off
        brightness: Optional brightness level (1-100)
        color_temp: Optional color temperature in Kelvin

    Returns:
        Status message string
    """
    try:
        light = hub.get_light_by_name(lamp_name=light_name)

        if not light.is_reachable:
            return f"Error: {light_name} is offline"

        # Turn on/off
        light.set_light(lamp_on=turn_on)
        time.sleep(0.5)

        # Set brightness if specified and supported
        if brightness is not None and 'lightLevel' in light.capabilities.can_receive:
            light.set_light_level(light_level=brightness)
            time.sleep(0.5)

        # Set color temperature if specified and supported
        if color_temp is not None and 'colorTemperature' in light.capabilities.can_receive:
            light.set_color_temperature(color_temp=color_temp)
            time.sleep(0.5)

        # Verify state
        light.reload()
        state = "ON" if light.attributes.is_on else "OFF"
        level = light.attributes.light_level or "N/A"

        return f"Success: {light_name} is {state} at {level}%"

    except Exception as e:
        return f"Error controlling {light_name}: {e}"


def safe_outlet_control(hub: dirigera.Hub,
                       outlet_name: str,
                       turn_on: bool) -> str:
    """
    Safely control an outlet with error handling

    Args:
        hub: Dirigera hub instance
        outlet_name: Name of the outlet
        turn_on: True to turn on, False to turn off

    Returns:
        Status message string
    """
    try:
        outlet = hub.get_outlet_by_name(outlet_name=outlet_name)

        if not outlet.is_reachable:
            return f"Error: {outlet_name} is offline"

        outlet.set_on(outlet_on=turn_on)
        time.sleep(1)

        outlet.reload()
        state = "ON" if outlet.attributes.is_on else "OFF"

        return f"Success: {outlet_name} is {state}"

    except Exception as e:
        return f"Error controlling {outlet_name}: {e}"


def turn_off_room_lights(hub: dirigera.Hub, room_name: str) -> str:
    """Turn off all lights in a specific room"""
    lights = get_lights_by_room(hub, room_name)
    count = 0

    for light in lights:
        if light.is_reachable and light.attributes.is_on:
            light.set_light(lamp_on=False)
            count += 1
            time.sleep(0.2)

    return f"Turned off {count} lights in {room_name}"


def turn_off_all_lights(hub: dirigera.Hub) -> str:
    """Turn off all lights in the home"""
    count = 0

    for light in hub.get_lights():
        if light.is_reachable and light.attributes.is_on:
            light.set_light(lamp_on=False)
            count += 1
            time.sleep(0.2)

    return f"Turned off {count} lights"


def turn_off_all_outlets(hub: dirigera.Hub) -> str:
    """Turn off all outlets in the home"""
    count = 0

    for outlet in hub.get_outlets():
        if outlet.is_reachable and outlet.attributes.is_on:
            outlet.set_on(outlet_on=False)
            count += 1
            time.sleep(0.2)

    return f"Turned off {count} outlets"


def status_report(hub: dirigera.Hub) -> dict:
    """
    Generate complete home status report

    Returns:
        Dictionary with status information
    """
    all_lights = hub.get_lights()
    all_outlets = hub.get_outlets()
    all_controllers = hub.get_controllers()
    all_devices = hub.get_all_devices()

    lights_on = [l for l in all_lights if l.attributes.is_on]
    outlets_on = [o for o in all_outlets if o.attributes.is_on]
    unreachable = [d for d in all_devices if not d.is_reachable]
    low_battery = [c for c in all_controllers if c.attributes.battery_percentage < 20]

    return {
        'lights': {
            'total': len(all_lights),
            'on': len(lights_on),
            'off': len(all_lights) - len(lights_on)
        },
        'outlets': {
            'total': len(all_outlets),
            'on': len(outlets_on),
            'off': len(all_outlets) - len(outlets_on)
        },
        'controllers': {
            'total': len(all_controllers),
            'low_battery': len(low_battery)
        },
        'unreachable_devices': len(unreachable),
        'unreachable_list': [
            {'name': d.attributes.custom_name, 'type': d.device_type}
            for d in unreachable
        ],
        'low_battery_list': [
            {'name': c.attributes.custom_name, 'battery': c.attributes.battery_percentage}
            for c in low_battery
        ]
    }


def battery_report(hub: dirigera.Hub) -> List[dict]:
    """
    Get battery status for all controllers

    Returns:
        List of dictionaries with controller name and battery percentage
    """
    controllers = hub.get_controllers()

    return [
        {
            'name': ctrl.attributes.custom_name,
            'battery': ctrl.attributes.battery_percentage,
            'status': 'LOW' if ctrl.attributes.battery_percentage < 20 else 'OK'
        }
        for ctrl in controllers
    ]


if __name__ == "__main__":
    # Example usage
    hub = init_hub()

    print("=== Status Report ===")
    status = status_report(hub)
    print(f"Lights: {status['lights']['on']}/{status['lights']['total']} ON")
    print(f"Outlets: {status['outlets']['on']}/{status['outlets']['total']} ON")

    if status['unreachable_devices'] > 0:
        print(f"\nUnreachable devices: {status['unreachable_devices']}")
        for device in status['unreachable_list']:
            print(f"  - {device['name']} ({device['type']})")

    print("\n=== Battery Report ===")
    batteries = battery_report(hub)
    for ctrl in batteries:
        print(f"{ctrl['name']}: {ctrl['battery']}% - {ctrl['status']}")
