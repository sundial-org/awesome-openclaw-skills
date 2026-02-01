# WLED HTTP API Reference

WLED exposes a JSON API for controlling LED strips and matrices.

## Base URL
```
http://<device-ip>/
```

## Endpoints

### GET /json
Returns complete device state, info, effects, palettes, and presets.

### GET /json/state
Returns current state only (on/off, brightness, segments, etc.)

### POST /json/state
Update state. Common fields:

| Field | Type | Description |
|-------|------|-------------|
| `on` | bool | Power state |
| `bri` | int | Brightness 0-255 |
| `seg` | array | Segment settings |
| `ps` | int | Load preset by ID |

### Segment Fields (seg[n])
| Field | Type | Description |
|-------|------|-------------|
| `col` | array | RGB colors [[r,g,b]] |
| `fx` | int | Effect ID |
| `sx` | int | Effect speed 0-255 |
| `ix` | int | Effect intensity 0-255 |
| `pal` | int | Palette ID |

## Common Effect IDs
- 0: Solid
- 1: Blink
- 2: Breathe
- 3: Wipe
- 4: Wipe Random
- 5: Random Colors
- 6: Sweep
- 7: Dynamic
- 8: Colorloop
- 9: Rainbow

## Common Palette IDs
- 0: Default
- 1: Random Cycle
- 2: Primary Color
- 3: Based on Primary
- 4: Set Colors
- 5: Based on Set
- 6: Party
- 7: Cloud
- 8: Lava
- 9: Ocean

## Examples

Turn on:
```json
{"on": true}
```

Set red color:
```json
{"seg": [{"col": [[255, 0, 0]]}]}
```

Set rainbow effect with speed:
```json
{"seg": [{"fx": 9, "sx": 128}]}
```

Load preset #1:
```json
{"ps": 1}
```
