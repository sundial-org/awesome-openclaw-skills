---
name: dirigera-control
description: Control IKEA Dirigera smart home devices (lights, outlets, scenes, controllers). Use when the user asks to control smart home devices, check device status, turn lights on/off, adjust brightness/color, control outlets, trigger scenes, check battery levels, or work with IKEA smart home automation. Accessible via Cloudflare tunnel on VPS.
---

# IKEA Dirigera Smart Home Control

Control lights, outlets, scenes, and other IKEA smart home devices through the Dirigera hub.

## Prerequisites

```python
pip install dirigera
```

## Hub Connection

```python
import dirigera

hub = dirigera.Hub(
    token="token",
    ip_address="ip_address"
)
```

## CRITICAL: Attribute Access

**Device state is in `.attributes`, not top-level.**

```python
# CORRECT
light.attributes.is_on
light.attributes.light_level

# WRONG - raises AttributeError
light.is_on
light.light_level
```

Top-level: `device.id`, `device.is_reachable`, `device.room`
State: `device.attributes.is_on`, `device.attributes.light_level`

## Quick Commands

### Discovery
```python
lights = hub.get_lights()
outlets = hub.get_outlets()
controllers = hub.get_controllers()
scenes = hub.get_scenes()
```

### Light Control
```python
light = hub.get_light_by_name(lamp_name="bedroom light")

# Check reachability first
if light.is_reachable:
    light.set_light(lamp_on=True)
    light.set_light_level(light_level=75)
    light.set_color_temperature(color_temp=2700)  # Warm white

# Reload after changes
light.reload()
```

### Outlet Control
```python
outlet = hub.get_outlet_by_name(outlet_name="living room")
outlet.set_on(outlet_on=True)
outlet.reload()
```

### Scene Triggering
```python
scene = hub.get_scene_by_name(scene_name="Sove tid")
scene.trigger()
```

### Check Capabilities
```python
# Verify device supports feature before using
if 'colorTemperature' in light.capabilities.can_receive:
    light.set_color_temperature(color_temp=3000)
```

## Common Patterns

See [references/patterns.md](references/patterns.md) for room-based control, batch operations, status reports, and battery monitoring.

## Helper Scripts

Use `scripts/helpers.py` for common operations: get lights by room, check battery levels, find unreachable devices.

## Complete Reference

See [references/api.md](references/api.md) for:
- Complete attribute reference
- All control methods
- Device capabilities
- Color temperature/hue values
- Troubleshooting

## Best Practices

1. Always check `device.is_reachable` before control
2. Call `device.reload()` after control commands
3. Use `.attributes` for all state access
4. Add 0.5s delays between rapid commands
5. Check capabilities before using features
