---
name: homey
description: Control Athom Homey smart home devices via local (LAN/VPN) or cloud APIs. List/control devices, trigger flows, query zones. Works with Homey Pro, Cloud, and Bridge.
metadata: {"clawdbot":{"requires":{"bins":["homeycli"]},"install":[{"id":"homey-npm","kind":"node","package":".","bins":["homeycli"],"label":"Install Homey CLI"}]}}
---

# Homey Smart Home Control

Control Athom Homey devices via local (LAN/VPN) or cloud APIs using token authentication.

## Setup

Requires Node.js >= 18.

1. **Decide local vs cloud**

   - **Local (LAN/VPN):** use a local API key from the Homey Web App + Homey IP address
   - **Cloud (remote/headless):** use a cloud token from Developer Tools

2. **Configure**

   **Local (recommended when the agent runs on your home network):**

   ```bash
   homeycli auth discover-local --save --pick 1
   echo "<LOCAL_API_KEY>" | homeycli auth set-local --stdin
   # or interactive (hidden input): homeycli auth set-local --prompt
   ```

   **Cloud (recommended for VPS/headless hosting):**

   ```bash
   echo "<CLOUD_TOKEN>" | homeycli auth set-token --stdin
   # or interactive (hidden input): homeycli auth set-token --prompt
   ```

   Check status:

   ```bash
   homeycli auth status
   ```

3. **Test connection**

   ```bash
   homeycli status
   ```

## Commands

### Snapshot (recommended for agents)
```bash
homeycli snapshot --json
homeycli snapshot --json --include-flows
```

### List Devices
```bash
homeycli devices              # Pretty table output
homeycli devices --json       # JSON output for AI parsing (includes latest values)

# Filter by name (returns multiple matches)
homeycli devices --match "kitchen" --json
```

### Control Devices
Turn devices on/off:
```bash
homeycli device "Living Room Light" on
homeycli device "Bedroom Lamp" off
```

Set specific capabilities:
```bash
homeycli device "Dimmer" set dim 0.5                    # 50% brightness
homeycli device "Thermostat" set target_temperature 21  # Set temperature
homeycli device "RGB Light" set light_hue 0.5           # Hue (0-1)
homeycli device "Lock" set locked true                  # Lock device
```

Get capability values:
```bash
homeycli device "Thermostat" get measure_temperature
homeycli device "Motion Sensor" get alarm_motion

# Get all values for a device (multi-sensors)
homeycli device "Living Room Air" values
homeycli device "Living Room Air" get
```

### Flows (Automations)
```bash
homeycli flows                        # List all flows
homeycli flows --json                 # JSON output
homeycli flows --match "good" --json  # Filter flows by name
homeycli flow trigger "Good Night"    # Trigger by name
homeycli flow trigger <flow-id>       # Trigger by ID
```

### Zones (Rooms)
```bash
homeycli zones           # List all zones/rooms
homeycli zones --json    # JSON output
```

### Status
```bash
homeycli status    # Show Homey connection info
```

## Common Capabilities

| Capability | Type | Description | Example |
|------------|------|-------------|---------|
| `onoff` | boolean | Power on/off | `true`, `false` |
| `dim` | number | Brightness (0-1) | `0.5` (50%) |
| `light_hue` | number | Color hue (0-1) | `0.33` (green) |
| `light_saturation` | number | Color saturation (0-1) | `1.0` (full) |
| `light_temperature` | number | Color temp (0-1) | `0.5` (neutral) |
| `target_temperature` | number | Thermostat target (°C) | `21` |
| `measure_temperature` | number | Current temp (read-only) | - |
| `locked` | boolean | Lock state | `true`, `false` |
| `alarm_motion` | boolean | Motion detected (read-only) | - |
| `alarm_contact` | boolean | Contact sensor (read-only) | - |
| `volume_set` | number | Volume (0-1) | `0.5` |

Use `homeycli devices` to see what capabilities each device supports.

## Fuzzy Matching

Device and flow names support fuzzy matching:
- **Exact match:** "Living Room Light" → finds "Living Room Light"
- **Substring:** "living light" → finds "Living Room Light"  
- **Levenshtein distance:** "livng light" → finds "Living Room Light" (typo-tolerant)

## JSON Mode

Add `--json` to any command for machine-readable output:
```bash
homeycli devices --json | jq '.[] | select(.class == "light")'
homeycli status --json
```

## Examples

**Morning routine:**
```bash
homeycli device "Bedroom Light" on
homeycli device "Bedroom Light" set dim 0.3
homeycli device "Thermostat" set target_temperature 20
```

**Check temperature:**
```bash
homeycli device "Living Room" get measure_temperature
```

**Trigger scene:**
```bash
homeycli flow trigger "Movie Time"
```

**List all lights:**
```bash
homeycli devices --json | jq '.[] | select(.class == "light") | .name'
```

## Troubleshooting

**"No auth configured"**

Local (LAN/VPN):
- Save local config: `echo "<LOCAL_API_KEY>" | homeycli auth set-local --address http://<homey-ip> --stdin`

Cloud (remote/headless):
- Save cloud token: `echo "<CLOUD_TOKEN>" | homeycli auth set-token --stdin`
- Cloud tokens can be created in Homey Developer Tools: https://tools.developer.homey.app/api/clients

**"Device not found" / ambiguous match**
- List devices with `homeycli devices --json` (or `homeycli devices --match <query> --json`) to find the right `id`
- If a query matches more than one device, the CLI returns candidate IDs and asks you to specify the device by ID

**"Capability not supported"**
- Check available capabilities: `homeycli devices` shows what each device supports
- Common issue: trying to turn on a sensor (use `get` instead of `set`)

## API Reference

The CLI uses the official `homey-api` npm package (v3.15.0).

**Auth/connection modes:**

- **Local mode:** `HomeyAPI.createLocalAPI({ address, token })` using the Homey Web App local API key.
- **Cloud mode:** `AthomCloudAPI` using a cloud bearer token (PAT) to create a session and access devices/flows/zones.

