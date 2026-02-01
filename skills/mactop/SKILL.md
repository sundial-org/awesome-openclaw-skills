---
name: mactop
description: |
  Retrieve real-time hardware metrics from Apple Silicon Macs using mactop's TOON format.
  Provides CPU, RAM, GPU, power, thermal, network, disk I/O, and Thunderbolt bus information.
  Use when the user wants system stats, hardware monitoring, or performance metrics on Apple Silicon Macs.
---

# Mactop Skill

Execute mactop in headless TOON mode and parse the output for hardware metrics.

## Prerequisites

- **mactop installed**: `brew install mactop`
- **PATH includes /usr/sbin**: Required for sysctl access

## Usage

### Get Full Metrics

```bash
mactop --format toon --headless --count 1
```

### Parse Key Metrics

**CPU Usage:**
```bash
mactop --format toon --headless --count 1 | grep "^cpu_usage:" | awk '{print $2}'
```

**RAM (used/total GB):**
```bash
mactop --format toon --headless --count 1 | grep -E "^  (Used|Total):" | awk '{printf "%.1f", $2/1073741824}'
```

**GPU Usage:**
```bash
mactop --format toon --headless --count 1 | grep "^gpu_usage:" | awk '{print $2}'
```

**Power (total/CPU/GPU):**
```bash
mactop --format toon --headless --count 1 | grep -E "^  (TotalPower|CPUPower|GPUPower):" | awk '{print $2}'
```

**Thermal State:**
```bash
mactop --format toon --headless --count 1 | grep "^thermal_state:" | awk '{print $2}'
```

**Temperature:**
```bash
mactop --format toon --headless --count 1 | grep "^  SocTemp:" | awk '{print $2}'
```

**Chip Info:**
```bash
mactop --format toon --headless --count 1 | grep "^  Name:" | awk '{print $2}'
```

**Network I/O (bytes/sec):**
```bash
mactop --format toon --headless --count 1 | grep -E "^(  InBytesPerSec|  OutBytesPerSec):" | awk '{print $2}'
```

**Thunderbolt Buses:**
```bash
mactop --format toon --headless --count 1 | grep "^    Name:" | awk '{print $2}'
```

## Options

| Option | Description |
|--------|-------------|
| `--count N` | Number of samples (default: 1) |
| `--interval MS` | Sample interval in milliseconds (default: 1000) |

## TOON Format

```
timestamp: "2026-01-25T20:00:00-07:00"
soc_metrics:
  CPUPower: 0.15
  GPUPower: 0.02
  TotalPower: 8.5
  SocTemp: 42.3
memory:
  Total: 25769803776
  Used: 14852408320
  Available: 10917395456
cpu_usage: 5.2
gpu_usage: 1.8
thermal_state: Normal
system_info:
  Name: Apple M4 Pro
  CoreCount: 12
```

## Response Example

Format metrics in a readable box:

```
┌─ Apple M4 Pro ──────────────────────┐
│ CPU:   5.2%  |  RAM: 13.8/24.0 GB  │
│ GPU:   1.8%  |  Power: 8.5W total  │
│ Thermal: Normal  |  SoC: 42.3°C    │
└─────────────────────────────────────┘
```

## Troubleshooting

- **"sysctl not found"** → Add `/usr/sbin` to PATH
- **No output** → Verify mactop is installed: `which mactop`
