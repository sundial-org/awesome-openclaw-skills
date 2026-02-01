---
name: starlink
version: 1.0.0
description: Control Starlink dish via local gRPC API. Get status, list WiFi clients, run speed tests, stow/unstow dish, reboot, and get GPS location. Use when the user asks about Starlink, internet status, connected devices, or satellite connectivity.
homepage: https://github.com/danfedick/starlink-cli
metadata: {"clawdbot":{"emoji":"📡","requires":{"bins":["starlink"]},"install":[{"id":"cargo","kind":"cargo","git":"https://github.com/danfedick/starlink-cli","bins":["starlink"],"label":"Install starlink-cli (cargo)"}]}}
---

# Starlink CLI

Control your Starlink dish from the command line via its local gRPC API at `192.168.100.1:9200`.

## Installation

```bash
cargo install --git https://github.com/danfedick/starlink-cli
```

Requires Rust and `protoc` (Protocol Buffers compiler).

## Commands

### Status
Get dish state, uptime, SNR, latency, throughput, obstructions:
```bash
starlink status
starlink status --json
```

### WiFi Clients
List devices connected to the Starlink router:
```bash
starlink clients
starlink clients --json
```

Output includes: name, MAC, IP, signal strength, interface (2.4GHz/5GHz/ETH), connection time.

### Speed Test
Run a speed test through the dish:
```bash
starlink speedtest
starlink speedtest --json
```

Returns download/upload Mbps and latency.

### Stow/Unstow
Stow dish flat for transport or storage:
```bash
starlink stow           # stow
starlink stow --unstow  # unstow and resume
```

### Reboot
Reboot the dish:
```bash
starlink reboot
```

### Location
Get GPS coordinates (must be enabled in Starlink app → Settings → Advanced → Debug Data → "allow access on local network"):
```bash
starlink location
starlink location --json
```

## Output Formats

- **Default**: Human-readable colored output
- **--json**: JSON for scripting/parsing

Example JSON parsing:
```bash
starlink status --json | jq '.latency_ms'
starlink clients --json | jq '.[] | .name'
```

## Requirements

- Connected to Starlink network
- Dish reachable at `192.168.100.1:9200`
- For location: enable in Starlink app first

## Troubleshooting

**"Failed to connect to Starlink dish"**
- Verify you're on the Starlink WiFi or wired to the router
- Check: `ping 192.168.100.1`
- If using bypass mode with your own router, ensure 192.168.100.1 is still routable

**Location returns empty**
- Enable in Starlink app: Settings → Advanced → Debug Data → "allow access on local network"

## Limitations

- Device pause/unpause is NOT available (cloud-only feature via Starlink app)
- Only works on local network, not remotely

## Source

https://github.com/danfedick/starlink-cli
