# Common Usage Patterns

## Room-Based Control

```python
# Turn off all lights in a room
for light in hub.get_lights():
    if light.room and light.room.name == "bedroom":
        if light.is_reachable and light.attributes.is_on:
            light.set_light(lamp_on=False)
```

```python
# Set kitchen lights to 80% warm white
import time

for light in hub.get_lights():
    if light.room and light.room.name == "Køkken" and light.is_reachable:
        light.set_light(lamp_on=True)
        time.sleep(0.3)

        if 'lightLevel' in light.capabilities.can_receive:
            light.set_light_level(light_level=80)
            time.sleep(0.3)

        if 'colorTemperature' in light.capabilities.can_receive:
            light.set_color_temperature(color_temp=2700)
            time.sleep(0.3)
```

## Batch Operations

```python
# Turn off ALL lights
for light in hub.get_lights():
    if light.is_reachable and light.attributes.is_on:
        light.set_light(lamp_on=False)
        time.sleep(0.2)  # Small delay between commands
```

```python
# Turn off all outlets
for outlet in hub.get_outlets():
    if outlet.is_reachable and outlet.attributes.is_on:
        outlet.set_on(outlet_on=False)
        time.sleep(0.2)
```

```python
# Set all lights to specific brightness
target_level = 50

for light in hub.get_lights():
    if light.is_reachable and light.attributes.is_on:
        if 'lightLevel' in light.capabilities.can_receive:
            light.set_light_level(light_level=target_level)
            time.sleep(0.2)
```

## Status Reports

```python
# Complete home status
all_lights = hub.get_lights()
all_outlets = hub.get_outlets()
all_devices = hub.get_all_devices()

lights_on = [l for l in all_lights if l.attributes.is_on]
outlets_on = [o for o in all_outlets if o.attributes.is_on]
unreachable = [d for d in all_devices if not d.is_reachable]

print(f"Lights: {len(all_lights)} total, {len(lights_on)} ON")
print(f"Outlets: {len(all_outlets)} total, {len(outlets_on)} ON")

if unreachable:
    print(f"\nUnreachable devices:")
    for d in unreachable:
        print(f"  - {d.attributes.custom_name} ({d.device_type})")
```

```python
# Battery status report
controllers = hub.get_controllers()

for ctrl in controllers:
    battery = ctrl.attributes.battery_percentage
    name = ctrl.attributes.custom_name

    status = "LOW" if battery < 20 else "OK"
    print(f"{name}: {battery}% - {status}")
```

```python
# Room-by-room status
rooms = {}
for light in hub.get_lights():
    if light.room:
        room_name = light.room.name
        if room_name not in rooms:
            rooms[room_name] = {'total': 0, 'on': 0}

        rooms[room_name]['total'] += 1
        if light.attributes.is_on:
            rooms[room_name]['on'] += 1

for room, stats in rooms.items():
    print(f"{room}: {stats['on']}/{stats['total']} lights ON")
```

## Conditional Control

```python
# Turn on only lights that are off
for light in hub.get_lights():
    if light.is_reachable and not light.attributes.is_on:
        light.set_light(lamp_on=True)
        light.set_light_level(light_level=50)
        time.sleep(0.3)
```

```python
# Dim all lights above 80%
for light in hub.get_lights():
    if light.is_reachable and light.attributes.light_level:
        if light.attributes.light_level > 80:
            light.set_light_level(light_level=50)
            time.sleep(0.2)
```

## Scene-Based Automation

```python
# Nighttime mode
for light in hub.get_lights():
    if light.is_reachable and light.attributes.is_on:
        # Dim to 20%
        if 'lightLevel' in light.capabilities.can_receive:
            light.set_light_level(light_level=20)

        # Warm white
        if 'colorTemperature' in light.capabilities.can_receive:
            light.set_color_temperature(color_temp=2700)

        time.sleep(0.3)
```

```python
# Energy saving mode - turn off non-essential devices
essential_rooms = ["refrigerator room", "security room"]

for outlet in hub.get_outlets():
    if outlet.room and outlet.room.name not in essential_rooms:
        if outlet.is_reachable and outlet.attributes.is_on:
            outlet.set_on(outlet_on=False)
            time.sleep(0.2)

# Turn off all lights
for light in hub.get_lights():
    if light.is_reachable and light.attributes.is_on:
        light.set_light(lamp_on=False)
        time.sleep(0.2)
```

## Helper Functions

```python
def get_lights_by_room(hub, room_name):
    """Get all lights in a specific room"""
    return [l for l in hub.get_lights()
            if l.room and l.room.name == room_name]

def get_devices_by_state(hub, device_type='lights', on=True):
    """Get all lights/outlets that are ON or OFF"""
    if device_type == 'lights':
        devices = hub.get_lights()
    else:
        devices = hub.get_outlets()

    return [d for d in devices if d.attributes.is_on == on]

def get_low_battery_controllers(hub, threshold=20):
    """Get controllers with battery below threshold"""
    return [c for c in hub.get_controllers()
            if c.attributes.battery_percentage < threshold]

def get_unreachable_devices(hub):
    """Get all offline devices"""
    return [d for d in hub.get_all_devices()
            if not d.is_reachable]
```

Usage:
```python
kitchen_lights = get_lights_by_room(hub, "Køkken")
lights_on = get_devices_by_state(hub, 'lights', on=True)
low_battery = get_low_battery_controllers(hub, threshold=20)
offline = get_unreachable_devices(hub)
```

## Safe Control Pattern

```python
import time

def safe_light_control(hub, light_name, turn_on, brightness=None, color_temp=None):
    """Safely control a light with error handling"""
    try:
        light = hub.get_light_by_name(lamp_name=light_name)

        if not light.is_reachable:
            return f"Error: {light_name} is offline"

        # Turn on/off
        light.set_light(lamp_on=turn_on)
        time.sleep(0.5)

        # Set brightness if specified
        if brightness and 'lightLevel' in light.capabilities.can_receive:
            light.set_light_level(light_level=brightness)
            time.sleep(0.5)

        # Set color temperature if specified
        if color_temp and 'colorTemperature' in light.capabilities.can_receive:
            light.set_color_temperature(color_temp=color_temp)
            time.sleep(0.5)

        # Verify
        light.reload()
        state = "ON" if light.attributes.is_on else "OFF"
        level = light.attributes.light_level or "N/A"

        return f"Success: {light_name} is {state} at {level}%"

    except Exception as e:
        return f"Error: {e}"
```

Usage:
```python
result = safe_light_control(hub, "bedroom light", turn_on=True, brightness=50, color_temp=2700)
print(result)
```

## Finding Controller Links

```python
# Show which devices a controller operates
controller = hub.get_controller_by_name(controller_name="bedroom remote")

all_lights = hub.get_lights()
linked_lights = [l for l in all_lights if controller.id in l.remote_links]

print(f"{controller.attributes.custom_name} controls:")
for light in linked_lights:
    print(f"  - {light.attributes.custom_name}")
```

## Working with Device Groups

```python
# Find all lights in a device group
group_name = "Køkken lamper"
group_lights = []

for light in hub.get_lights():
    if light.device_set:
        for group in light.device_set:
            if group['name'] == group_name:
                group_lights.append(light)

print(f"Lights in '{group_name}':")
for light in group_lights:
    print(f"  - {light.attributes.custom_name}")
```
