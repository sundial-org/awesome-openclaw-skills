# Dirigera API Complete Reference

## Table of Contents
- Device Attribute Structure
- Light Control Methods
- Outlet Control Methods
- Scene Methods
- Discovery Methods
- Device Capabilities
- Color Reference
- Troubleshooting

## Device Attribute Structure

### Top-Level Attributes (Direct Access)
```python
device.id                  # Unique identifier
device.is_reachable       # Online status (bool)
device.last_seen          # Last communication timestamp
device.room               # Room object (.name, .color, .icon)
device.capabilities       # Capabilities object
device.device_set         # List of groups device belongs to
device.remote_links       # List of controller IDs
device.device_type        # Device type string
```

### State Attributes (via .attributes)
```python
device.attributes.custom_name        # Device name
device.attributes.is_on             # On/off state
device.attributes.light_level       # Brightness 1-100 (lights)
device.attributes.color_temperature # Kelvin (lights)
device.attributes.color_hue         # 0-360 (color lights)
device.attributes.color_saturation  # 0.0-1.0 (color lights)
device.attributes.battery_percentage # Battery level (controllers)
device.attributes.model             # Device model
device.attributes.firmware_version  # Firmware version
device.attributes.startup_on_off    # Startup behavior
```

## Light Control Methods

```python
light.set_light(lamp_on=True/False)
light.set_light_level(light_level=1-100)
light.set_color_temperature(color_temp=2200-6500)
light.set_light_color(hue=0-360, saturation=0.0-1.0)
light.set_name(name="new name")
light.reload()  # Refresh state from hub
```

## Outlet Control Methods

```python
outlet.set_on(outlet_on=True/False)
outlet.set_name(name="new name")
outlet.reload()  # Refresh state from hub
```

## Scene Methods

```python
scene.trigger()  # Activate scene

# Scene attributes
scene.id
scene.info.name
scene.info.icon
scene.last_triggered
scene.actions  # List of device actions
```

## Discovery Methods

```python
# Get all devices
hub.get_all_devices()
hub.get_lights()
hub.get_outlets()
hub.get_controllers()
hub.get_blinds()
hub.get_environment_sensors()
hub.get_motion_sensors()
hub.get_open_close_sensors()
hub.get_scenes()

# Get specific device
hub.get_light_by_name(lamp_name="kitchen")
hub.get_light_by_id(id_="device-id")
hub.get_outlet_by_name(outlet_name="bedroom")
hub.get_outlet_by_id(id_="device-id")
hub.get_controller_by_name(controller_name="remote")
hub.get_controller_by_id(id_="device-id")
hub.get_scene_by_name(scene_name="Sleep time")
hub.get_scene_by_id(scene_id="scene-id")
```

## Device Capabilities

Check what a device supports:

```python
light.capabilities.can_receive
# Example: ['customName', 'isOn', 'lightLevel', 'colorTemperature']

controller.capabilities.can_send
# Example: ['isOn', 'lightLevel']

# Check before using feature
if 'colorTemperature' in light.capabilities.can_receive:
    light.set_color_temperature(color_temp=3000)
```

## Color Reference

### Color Temperatures (Kelvin)
- 2700K - Warm white (cozy, evening)
- 3000K - Soft white
- 4000K - Neutral white (task lighting)
- 6500K - Cool white (daylight)

Note: Some IKEA bulbs have inverted min/max ranges (e.g., min=4000, max=2202). This is normal.

### Hue Values (0-360)
- 0 - Red
- 30 - Orange
- 60 - Yellow
- 120 - Green
- 180 - Cyan
- 240 - Blue
- 300 - Magenta

## Troubleshooting

### AttributeError: 'Light' object has no attribute 'is_on'
Use `light.attributes.is_on` instead of `light.is_on`. All state is in `.attributes`.

### Device doesn't respond
Check `device.is_reachable` first. If False, device is offline.

### State doesn't update after control
Call `device.reload()` to refresh cached state from hub. Add `time.sleep(1)` before reload.

### Power monitoring returns None
Basic TRADFRI outlets don't support power measurement. Only certain models have `current_active_power`, `total_energy_consumed` attributes.

### Commands are slow or fail
Add delays between rapid commands:
```python
import time
light.set_light(lamp_on=True)
time.sleep(0.5)
light.set_light_level(light_level=50)
```

### Color temperature doesn't work
Not all lights support color temperature. Check capabilities first:
```python
if 'colorTemperature' in light.capabilities.can_receive:
    light.set_color_temperature(color_temp=3000)
```

## Controller (Remote) Specifics

```python
controllers = hub.get_controllers()

for ctrl in controllers:
    name = ctrl.attributes.custom_name
    battery = ctrl.attributes.battery_percentage
    model = ctrl.attributes.model

    # Find devices this controller controls
    all_lights = hub.get_lights()
    linked = [l for l in all_lights if ctrl.id in l.remote_links]
```

## Device Groups/Sets

```python
light = hub.get_light_by_name(lamp_name="kitchen")

# Check if light is in any groups
if light.device_set:
    for group in light.device_set:
        print(f"Group: {group['name']}")
        print(f"Icon: {group['icon']}")
```

Device groups are used in scenes for batch control.

## State Reload Pattern

Always reload after control commands if you need to verify state:

```python
light.set_light(lamp_on=True)
time.sleep(1)  # Wait for hub to process
light.reload()  # Fetch fresh state

# Now state is current
print(f"Light is: {'ON' if light.attributes.is_on else 'OFF'}")
```

## Error Handling Pattern

```python
try:
    light = hub.get_light_by_name(lamp_name="bedroom")

    if not light.is_reachable:
        print("Device is offline")
    else:
        light.set_light(lamp_on=True)
        light.reload()

except Exception as e:
    print(f"Error: {e}")
```
