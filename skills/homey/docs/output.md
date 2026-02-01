# Output contract (JSON)

This CLI is designed to be called by agents. When `--json` is set:

- **Success** outputs JSON to **stdout**.
- **Errors** output JSON to **stdout** in a stable shape (see below).
- Text output (without `--json`) is intended for humans and may change.

## Error JSON (stable)

All errors use this envelope:

```json
{
  "error": {
    "code": "AMBIGUOUS",
    "message": "...",
    "details": {
      "candidates": [{"id": "...", "name": "..."}]
    }
  }
}
```

Notes:
- `details` is optional.
- When present, `details.candidates` is an array of `{ id, name }` objects.

Exit codes are documented in `docs/errors.md`.

## Success JSON (stable fields)

### `homeycli auth status --json`

```json
{
  "modeWanted": "auto",
  "modeWantedSource": "config",
  "modeSelected": "local",
  "path": "/Users/.../.homey/config.json",
  "local": {
    "addressPresent": true,
    "tokenPresent": true,
    "address": "http://192.168.1.50",
    "addressSource": "config",
    "tokenSource": "config"
  },
  "cloud": {
    "tokenPresent": true,
    "tokenSource": "config"
  }
}
```

### `homeycli auth set-token ... --json` (cloud)

```json
{
  "saved": true,
  "kind": "cloud",
  "source": "config",
  "path": "/Users/.../.homey/config.json"
}
```

### `homeycli auth discover-local ... --json`

```json
{
  "discovered": true,
  "candidates": [{ "index": 1, "address": "http://192.168.1.50", "homeyId": "...", "host": "192.168.1.50", "port": 80 }]
}
```

### `homeycli auth set-local ... --json` (local)

```json
{
  "saved": true,
  "kind": "local",
  "address": "http://192.168.1.50",
  "path": "/Users/.../.homey/config.json"
}
```

### `homeycli status --json`

```json
{
  "name": "Homey",
  "platform": "local|cloud|...",
  "platformVersion": 2,
  "hostname": "...",
  "cloudId": "...",
  "homeyId": "...",
  "connected": true,
  "connectionMode": "local|cloud",
  "address": "http://192.168.1.50" 
}
```

Notes:
- `address` is only present in `local` mode.
- `cloudId` is kept for backwards compatibility; prefer `homeyId`.

### `homeycli zones --json`

Array of zones:

- `id` (string)
- `name` (string)
- `parent` (string|null)
- `icon` (string|null)

### `homeycli devices --json` / `homeycli device <id> ... --json`

Array of devices (or a single device depending on command). Stable fields per device:

- `id` (string)
- `name` (string)
- `zoneId` (string|null)
- `zoneName` (string|null)
- `zone` (string|null) – convenience display field
- `class` (string)
- `capabilities` (string[])
- `capabilitiesObj` (object) – Homey capability metadata + latest values
- `values` (object) – `{ [capabilityId]: value }`
- `available` (boolean)
- `ready` (boolean)

### `homeycli flows --json`

Array of flows:

- `id` (string)
- `name` (string)
- `enabled` (boolean)
- `folder` (string|null)

### `homeycli flow trigger <idOrName> --json`

Returns the triggered flow object (same shape as flows above).

### `homeycli snapshot --json`

```json
{
  "status": { /* same as status */ },
  "zones": [ /* same as zones */ ],
  "devices": [ /* same as devices */ ],
  "flows": [ /* optional; same as flows */ ]
}
```

## `--raw` (intentionally unstable)

When `--raw` is set, responses may include a `raw` field containing the underlying Homey API object.

- `raw` is **very verbose** and may change at any time.
- Agents should not depend on `raw` fields for core behavior.
