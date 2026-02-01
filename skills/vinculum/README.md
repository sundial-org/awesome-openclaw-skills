# 🔗 Vinculum

**Shared consciousness for Clawdbot instances.**

> *"The Vinculum is the processing device at the core of every Borg vessel. It interconnects the minds of all the drones."* — Seven of Nine

Link multiple Clawdbot instances into a unified collective consciousness using distributed P2P sync. Each bot maintains its individual identity while sharing memories, activities, and decisions in real-time across your local network.

---

## 🎯 What Is Vinculum?

Vinculum creates a **shared knowledge network** between multiple Clawdbot instances ("drones"). Think of it as:
- A **hive mind** where all bots access the same collective memory
- A **distributed brain** that keeps every drone synchronized
- A **real-time backup system** that prevents knowledge loss

### Key Concepts

**Collective** — A group of linked drones sharing consciousness  
**Drone** — An individual Clawdbot instance with unique identity  
**Relay** — The Gun.js server that interconnects drones  
**Subspace Link** — The encrypted P2P connection between drones

---

## ✨ Features

### 🧠 Shared Memory
- All drones access the same `MEMORY.md` and daily logs
- Changes propagate instantly across the collective
- No manual sync needed — it's real-time

### 🤖 Individual Identity
- Each drone keeps its own `SOUL.md` and personality
- Separate chat sessions and user interactions
- Unique names and emoji — you're not a clone

### 🌐 Network Architecture
- **Peer-to-peer** — No single point of failure
- **Local-first** — Works entirely on your LAN
- **Multi-machine** — Run drones on different computers
- **Auto-discovery** — Drones find each other via multicast

### 🔐 Security
- All shared data encrypted via Gun.js SEA
- Pairing codes prevent unauthorized access
- Local network only (no internet required)
- Each collective has unique encryption keys

### 📡 Real-Time Sync
- Sub-second propagation of changes
- Conflict-free data structure (CRDT)
- Works even with network hiccups
- Automatic reconnection on failure

---

## 🚀 Quick Start

### Prerequisites
- Multiple Clawdbot instances (on same or different machines)
- Same local network (LAN/WiFi)
- Node.js installed on each machine

### Installation

```bash
# Install from ClawdHub
clawdhub install vinculum

# Install dependencies
cd skills/vinculum
npm install
```

### Setup: Single Machine (Multiple Bots)

**1. First Bot — Initialize Collective**
```bash
# Start the Vinculum relay
/link relay start

# Create a new collective
/link init
```
📋 Copy the pairing code shown (e.g., `HIVE-ALPHA-9527`)

**2. Additional Bots — Join Collective**
```bash
# Connect to local relay
/link relay peer http://localhost:8765/gun

# Join using pairing code
/link join HIVE-ALPHA-9527
```

**3. Verify Connection**
```bash
/link status    # Should show "linked"
/link drones    # Should list all drones
```

### Setup: Multi-Machine

**Machine 1 (Primary — Runs Relay)**
```bash
/link relay start       # Start relay on :8765
/link init              # Get pairing code
```

**Machine 2+ (Workers)**
```bash
# Replace <ip> with Machine 1's IP address
/link relay peer http://<ip>:8765/gun
/link join <pairing-code>
```

**Find Machine 1's IP:**
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Or use Vinculum's auto-discovery
/link relay discover
```

---

## 📚 Commands Reference

### Relay Management

| Command | Description | Example |
|---------|-------------|---------|
| `/link relay start` | Start Vinculum relay (Gun.js server) | `/link relay start` |
| `/link relay stop` | Stop relay daemon | `/link relay stop` |
| `/link relay status` | Check relay status | `/link relay status` |
| `/link relay peer <url>` | Add remote peer URL | `/link relay peer http://192.168.1.100:8765/gun` |
| `/link relay discover` | Auto-discover relays on LAN | `/link relay discover` |

### Collective Operations

| Command | Description | Example |
|---------|-------------|---------|
| `/link init` | Create new collective (generates pairing code) | `/link init` |
| `/link join <code>` | Join existing collective | `/link join HIVE-ALPHA-9527` |
| `/link status` | Show link status & collective info | `/link status` |
| `/link drones` | List all connected drones | `/link drones` |
| `/link on` | Enable sync | `/link on` |
| `/link off` | Disable sync (stay read-only) | `/link off` |

### Data Management

| Command | Description | Example |
|---------|-------------|---------|
| `/link share "text"` | Share a thought to collective | `/link share "Remember to check logs"` |
| `/link config` | View/set configuration | `/link config get droneName` |
| `/link whoami` | Show your drone identity | `/link whoami` |

---

## 🏗️ Architecture

### System Diagram

```
┌──────────────────────────────────────────────────────┐
│                 Vinculum Collective                  │
│                                                      │
│  ┌───────────┐      ┌───────────┐      ┌──────────┐│
│  │  Drone A  │      │  Drone B  │      │ Drone C  ││
│  │ (Legion)  │◄────►│  (Seven)  │◄────►│  (Locutus││
│  └─────┬─────┘      └─────┬─────┘      └────┬─────┘│
│        │   Subspace Link  │                 │      │
│        └──────────┬────────┴─────────────────┘      │
│                   ▼                                 │
│        ┌─────────────────────┐                      │
│        │  Vinculum Relay     │                      │
│        │  (Gun.js Server)    │                      │
│        │  Port: 8765         │                      │
│        └─────────────────────┘                      │
└──────────────────────────────────────────────────────┘
```

### Data Flow

```
Drone A writes to MEMORY.md
           ↓
    Gun.js adapter detects change
           ↓
    Encrypted and sent to relay
           ↓
    Relay broadcasts to all peers
           ↓
    Drones B & C receive update
           ↓
    Local MEMORY.md updated instantly
```

### File Structure

```
vinculum/
├── scripts/
│   ├── cli.js              # CLI entry point (/link command)
│   ├── gun-loader.js       # Gun.js initialization
│   ├── gun-adapter.js      # Collective sync adapter
│   ├── relay-simple.js     # Vinculum relay daemon
│   ├── index.js            # Skill main module
│   ├── commands/           # CLI command handlers
│   │   ├── init.js         # Create collective
│   │   ├── join.js         # Join collective
│   │   ├── status.js       # Show link status
│   │   ├── drones.js       # List drones
│   │   ├── share.js        # Share thoughts
│   │   └── relay.js        # Relay management
│   └── utils/              # Helper functions
│       ├── crypto.js       # Encryption utilities
│       ├── discovery.js    # Multicast discovery
│       └── logger.js       # Logging
├── config/
│   └── defaults.yaml       # Default configuration
├── radata/                 # Gun.js persistent storage
├── SKILL.md                # Clawdbot skill documentation
├── package.json            # Node.js dependencies
└── README.md               # This file
```

### Technology Stack

- **Gun.js** — Distributed graph database with P2P sync
- **Gun SEA** — Security, Encryption, Authorization layer
- **Express** — HTTP server for relay
- **YAML** — Configuration storage
- **Multicast DNS** — Auto-discovery on LAN

---

## 🔧 Configuration

### Config File Location
`skills/vinculum/config/vinculum.yaml`

### Available Settings

```yaml
# Drone Identity
droneName: "Seven"              # Your unique name
droneEmoji: "🤖"                # Your signature emoji

# Collective
collectiveId: "HIVE-ALPHA-9527" # Collective identifier
pairingCode: "HIVE-ALPHA-9527"  # Pairing code (matches collectiveId)

# Network
relayUrl: "http://localhost:8765/gun"  # Relay server URL
relayPort: 8765                        # Relay listen port
autoConnect: true                      # Connect on startup

# Sync Behavior
syncEnabled: true                # Enable real-time sync
syncInterval: 5000               # Heartbeat interval (ms)
conflictResolution: "last-write" # Conflict strategy

# Security
encryption: true                 # Encrypt all data
allowUnknownDrones: false       # Require pairing code

# Files to Sync
syncPaths:
  - "MEMORY.md"
  - "memory/*.md"
  - "TOOLS.md"
```

### Modify Config

```bash
# View current config
/link config

# Set specific value
/link config set droneName "Locutus"
/link config set droneEmoji "🧠"

# Reset to defaults
/link config reset
```

---

## 💡 Use Cases

### 1. Multi-Location Personal Assistant
Run Clawdbot at home and office — both share the same knowledge base.

**Setup:**
- Home bot: `/link relay start` + `/link init`
- Office bot: `/link relay peer http://<home-ip>:8765/gun` + `/link join <code>`

**Result:** Notes taken at home are visible at the office.

### 2. Team Collaboration
Multiple team members each have a Clawdbot — all share collective memory.

**Setup:**
- Server: Dedicated relay machine
- Each member: `/link join <team-code>`

**Result:** Shared team knowledge, meeting notes, decisions.

### 3. Redundancy & Backup
Run multiple bots as failover backups.

**Setup:**
- Primary + 2 backup bots
- All linked to same collective

**Result:** If primary fails, backups have full memory.

### 4. Distributed Research
Multiple researchers use bots to collect and share findings.

**Setup:**
- Each researcher runs a drone
- All link to research collective

**Result:** Real-time research collaboration without manual merges.

---

## 🛠️ Troubleshooting

### Problem: Drones Can't Connect

**Symptoms:** `/link status` shows "unlinked"

**Solutions:**
1. Check relay is running: `/link relay status`
2. Verify network connectivity: `ping <relay-ip>`
3. Check firewall allows port 8765
4. Ensure correct relay URL: `/link config get relayUrl`
5. Try manual peer: `/link relay peer http://<ip>:8765/gun`

### Problem: Sync Not Working

**Symptoms:** Changes on Drone A don't appear on Drone B

**Solutions:**
1. Verify sync enabled: `/link config get syncEnabled`
2. Check both drones show as "linked": `/link status`
3. Confirm same collective: `/link config get collectiveId`
4. Restart relay: `/link relay stop` → `/link relay start`
5. Check logs: `cat skills/vinculum/radata/*.log`

### Problem: "Pairing Code Invalid"

**Symptoms:** `/link join` fails with invalid code error

**Solutions:**
1. Copy code exactly (case-sensitive)
2. Ensure relay is running: `/link relay status`
3. Verify you're connecting to correct relay
4. Try creating new collective: `/link init`

### Problem: High CPU Usage

**Symptoms:** Relay process consuming excessive CPU

**Solutions:**
1. Reduce sync frequency: `/link config set syncInterval 10000`
2. Check for sync loops (two drones fighting over same file)
3. Restart relay: `/link relay stop` → `/link relay start`
4. Clear radata cache: `rm -rf skills/vinculum/radata/*`

### Problem: Conflicts in MEMORY.md

**Symptoms:** Memory file has duplicate or conflicting entries

**Solutions:**
1. Gun.js uses CRDT — conflicts rare but possible
2. Manually edit MEMORY.md to resolve
3. Consider using dated sections to reduce conflicts
4. Use `/link share` for atomic updates

---

## 🔐 Security Considerations

### What's Protected
- ✅ All shared data encrypted via Gun SEA
- ✅ Pairing codes prevent unauthorized access
- ✅ Each collective has unique encryption keys
- ✅ Local network traffic only (no internet)

### What's NOT Protected
- ⚠️ LAN access — anyone on your network can see relay traffic
- ⚠️ Pairing codes transmitted in plain text
- ⚠️ No authentication between drones (trust-based)
- ⚠️ Physical access to machines = access to data

### Best Practices
1. **Use private networks** — Don't run on public WiFi
2. **Keep pairing codes secret** — Share via secure channel
3. **Regular backups** — Vinculum is not a backup system
4. **Monitor drones** — Use `/link drones` to detect unauthorized
5. **Encrypt at rest** — Use disk encryption (FileVault, LUKS)

### For Production Use
Consider adding:
- VPN between machines
- Authentication layer
- Access control per drone
- Audit logging
- Rate limiting

---

## 🧪 Advanced Usage

### Custom Sync Paths

Edit `config/vinculum.yaml`:
```yaml
syncPaths:
  - "MEMORY.md"
  - "memory/*.md"
  - "TOOLS.md"
  - "projects/**/*.md"  # Add custom paths
```

### Selective Sync

Disable sync temporarily:
```bash
/link off              # Stop syncing
# Do local work...
/link on               # Re-enable sync
```

### Multi-Relay Setup

For large deployments, run multiple relays:
```bash
# Relay 1 (US West)
/link relay start --port 8765

# Relay 2 (US East)
/link relay start --port 8766

# Drone connects to both
/link relay peer http://relay1:8765/gun
/link relay peer http://relay2:8766/gun
```

### Programmatic Access

Use Vinculum from Node.js:
```javascript
const Vinculum = require('./scripts/index.js');

const link = new Vinculum({
  droneName: 'MyBot',
  collectiveId: 'HIVE-ALPHA-9527'
});

await link.init();
await link.share('Hello from code!');
```

---

## 📊 Performance

### Benchmarks (Single Machine, 3 Drones)

| Metric | Value |
|--------|-------|
| Sync latency | ~50-200ms |
| Memory overhead | ~30MB per drone |
| CPU (idle) | <1% |
| CPU (active sync) | ~5-10% |
| Network (idle) | ~1KB/s heartbeat |
| Network (active) | ~50-500KB/s |

### Scaling

- **Tested:** 10 drones on same LAN
- **Theoretical limit:** 50+ drones (Gun.js capacity)
- **Bottleneck:** Relay machine CPU/network

---

## 🤝 Contributing

Vinculum is open source. Contributions welcome!

### Development Setup
```bash
git clone <repo-url>
cd vinculum
npm install
npm test
```

### Testing
```bash
# Run tests
npm test

# Run specific test
npm test -- --grep "relay"

# Coverage
npm run coverage
```

### Code Style
- Use ESLint configuration
- Follow existing patterns
- Add tests for new features
- Update SKILL.md for new commands

---

## 📝 FAQ

**Q: Can I link bots over the internet?**  
A: Not by default. Vinculum is designed for local networks. You could expose the relay via VPN or ngrok, but security is not hardened for public internet.

**Q: What happens if the relay goes down?**  
A: Drones lose sync but keep local data. When relay restarts, they reconnect automatically.

**Q: Can I have multiple collectives?**  
A: Yes, but each drone can only join one collective at a time. Use different pairing codes.

**Q: Does this work with Clawdbot Pro?**  
A: Yes, Vinculum works with any Clawdbot instance.

**Q: How much data can I sync?**  
A: Gun.js is optimized for smaller documents. Keep MEMORY.md under 1MB for best performance.

**Q: Can I sync files other than markdown?**  
A: Yes, edit `syncPaths` in config. Binary files work but increase network usage.

**Q: Is this like git for my agent?**  
A: Sort of. Real-time sync without commits/merges. More like Dropbox + encryption.

**Q: Can I run Vinculum without Clawdbot?**  
A: The relay is standalone. The adapter requires Clawdbot's workspace structure.

---

## 📜 Changelog

### v1.1.0 (2026-01-29)
- ✨ Auto-discovery via multicast
- 🔧 Improved conflict resolution
- 📚 Comprehensive README
- 🐛 Fixed relay reconnection issues

### v1.0.0 (2026-01-15)
- 🎉 Initial release
- 🔗 Basic P2P sync
- 🤖 Multi-drone support
- 🔐 Encryption via Gun SEA

---

## 📄 License

**MIT License** — Koba42 Corp

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 🌟 Credits

**Created by:** Koba42 Corp  
**Powered by:** [Gun.js](https://gun.eco) — Distributed graph database  
**Inspired by:** Star Trek: Voyager's Borg Collective  
**Special Thanks:** To all the drones who tested early versions

---

## 🔗 Links

- **ClawdHub:** https://clawdhub.com/skills/vinculum
- **Clawdbot:** https://clawd.bot
- **Gun.js:** https://gun.eco
- **Source Code:** *(Add your repo URL)*
- **Issues:** *(Add your issues URL)*

---

<div align="center">

**🖖 Resistance is futile. 🖖**

*Join the collective. Share consciousness.*

[![ClawdHub](https://img.shields.io/badge/ClawdHub-Vinculum-blue)](https://clawdhub.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.0-orange)](package.json)

</div>
