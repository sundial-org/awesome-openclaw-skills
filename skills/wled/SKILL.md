---
name: wled
description: Control WLED LED controllers via HTTP API. Use when a user asks to control WLED lights, LED strips, or ESP-based LED controllers. Supports power on/off, brightness, colors (RGB), effects, palettes, presets, and device status.
---

# WLED Control

Control WLED LED strips and matrices via the HTTP JSON API.

## Requirements

- WLED device on the same network
- Device IP address or hostname
- Python 3 (no external dependencies)

## Usage

All commands require `--host` (or `-H`) with the WLED device IP/hostname.

### Power Control

```bash
python3 scripts/wled.py -H <ip> power          # Get power state
python3 scripts/wled.py -H <ip> power on       # Turn on
python3 scripts/wled.py -H <ip> power off      # Turn off
```

### Brightness

```bash
python3 scripts/wled.py -H <ip> brightness          # Get current brightness
python3 scripts/wled.py -H <ip> brightness 255      # Max brightness
python3 scripts/wled.py -H <ip> brightness 128      # 50% brightness
```

### Colors

```bash
python3 scripts/wled.py -H <ip> color 255 0 0       # Red
python3 scripts/wled.py -H <ip> color 0 255 0       # Green
python3 scripts/wled.py -H <ip> color 0 0 255       # Blue
python3 scripts/wled.py -H <ip> color 255 255 255   # White
```

### Effects

```bash
python3 scripts/wled.py -H <ip> effects             # List all effects with IDs
python3 scripts/wled.py -H <ip> effect 0            # Solid color
python3 scripts/wled.py -H <ip> effect 9            # Rainbow
python3 scripts/wled.py -H <ip> effect 9 -s 200     # Rainbow, fast speed
python3 scripts/wled.py -H <ip> effect 9 -i 128     # Rainbow, medium intensity
```

### Palettes

```bash
python3 scripts/wled.py -H <ip> palettes            # List all palettes with IDs
python3 scripts/wled.py -H <ip> palette 6           # Set Party palette
```

### Presets

```bash
python3 scripts/wled.py -H <ip> presets             # List saved presets
python3 scripts/wled.py -H <ip> preset 1            # Load preset #1
```

### Status

```bash
python3 scripts/wled.py -H <ip> status              # Full device status
```

## Reference

See [references/api.md](references/api.md) for complete API documentation.

## Configuration

Avoid passing `--host` every time by creating a config file at `~/.wled/config.json`:

```json
{
  "bedroom": "192.168.1.100",
  "kitchen": "192.168.1.101",
  "living_room": "wled-abc123.local"
}
```

Then use aliases:
```bash
python3 scripts/wled.py -H bedroom brightness 255
python3 scripts/wled.py -H kitchen color 255 0 0
```

Or set the `WLED_HOST` environment variable:
```bash
export WLED_HOST=192.168.1.100
python3 scripts/wled.py brightness 255
```

## Finding Your WLED Device

WLED devices can typically be found via:
- Router admin panel (look for ESP device)
- mDNS/Bonjour: `wled-<mac>.local`
- WLED app discovery

## Static IP Recommendation

IP addresses change over time. To avoid updating your config, **set a static IP** on your WLED device:

**Option 1: Router-based (easiest)**
1. Open your router admin panel
2. Find the WLED device by MAC address
3. Reserve/assign a static IP

**Option 2: On-device**
1. Access WLED web UI at `http://<current-ip>`
2. Go to Settings → WiFi Settings
3. Set static IP manually
4. Save and reboot

Using mDNS hostnames (e.g., `wled-abc123.local`) also avoids IP tracking—routers resolve these automatically.
