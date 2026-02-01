---
name: airfoil
description: Control AirPlay speakers via Airfoil from the command line. Connect, disconnect, set volume, and manage multi-room audio with simple CLI commands.
metadata: {"clawdbot":{"emoji":"🔊","os":["darwin"],"requires":{"bins":["osascript"]}}}
---

# 🔊 Airfoil Skill

```
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🎵  A I R F O I L   S P E A K E R   C O N T R O L  🎵  ║
    ║                                                           ║
    ║        Stream audio to any AirPlay speaker                ║
    ║              from your Mac via CLI                        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
```

> *"Why hop to your Mac when you can croak at it?"* 🐸

---

## 📖 What Does This Skill Do?

The **Airfoil Skill** gives you full control over your AirPlay speakers directly from the terminal – or through Clawd! Connect speakers, control volume, check status – all without touching the mouse.

**Features:**
- 📡 **List** — Show all available speakers
- 🔗 **Connect** — Connect to a speaker
- 🔌 **Disconnect** — Disconnect from a speaker
- 🔊 **Volume** — Control volume (0-100%)
- 📊 **Status** — Show connected speakers with volume levels

---

## ⚙️ Requirements

| What | Details |
|------|---------|
| **OS** | macOS (uses AppleScript) |
| **App** | [Airfoil](https://rogueamoeba.com/airfoil/mac/) by Rogue Amoeba |
| **Price** | $35 (free trial available) |

### Installation

1. **Install Airfoil:**
   ```bash
   # Via Homebrew
   brew install --cask airfoil
   
   # Or download from rogueamoeba.com/airfoil/mac/
   ```

2. **Launch Airfoil** and grant Accessibility permissions (System Settings → Privacy & Security → Accessibility)

3. **Skill is ready!** 🚀

---

## 🛠️ Commands

### `list` — Show All Speakers

```bash
./airfoil.sh list
```

**Output:**
```
Computer, Andy's M5 Macbook, Sonos Move, Living Room TV
```

---

### `connect <speaker>` — Connect to Speaker

```bash
./airfoil.sh connect "Sonos Move"
```

**Output:**
```
Connected: Sonos Move
```

> 💡 Speaker name must match exactly (case-sensitive!)

---

### `disconnect <speaker>` — Disconnect Speaker

```bash
./airfoil.sh disconnect "Sonos Move"
```

**Output:**
```
Disconnected: Sonos Move
```

---

### `volume <speaker> <0-100>` — Set Volume

```bash
# Set to 40%
./airfoil.sh volume "Sonos Move" 40

# Set to maximum
./airfoil.sh volume "Living Room TV" 100

# Quiet mode for night time
./airfoil.sh volume "Sonos Move" 15
```

**Output:**
```
Volume Sonos Move: 40%
```

---

### `status` — Show Connected Speakers

```bash
./airfoil.sh status
```

**Output:**
```
Sonos Move: 40%
Living Room TV: 65%
```

Or if nothing is connected:
```
No speakers connected
```

---

## 🎯 Example Workflows

### 🏠 "Music in the Living Room"
```bash
./airfoil.sh connect "Sonos Move"
./airfoil.sh volume "Sonos Move" 50
# → Now fire up Spotify/Apple Music and enjoy!
```

### 🎬 "Movie Night Setup"
```bash
./airfoil.sh connect "Living Room TV"
./airfoil.sh volume "Living Room TV" 70
./airfoil.sh disconnect "Sonos Move"  # If still connected
```

### 🌙 "All Off"
```bash
for speaker in "Sonos Move" "Living Room TV"; do
    ./airfoil.sh disconnect "$speaker" 2>/dev/null
done
echo "All speakers disconnected 🌙"
```

---

## 🔧 Troubleshooting

### ❌ "Speaker Not Found"

**Problem:** `execution error: Airfoil got an error: Can't get speaker...`

**Solutions:**
1. Check exact spelling: `./airfoil.sh list`
2. Speaker name is **case-sensitive** ("sonos move" ≠ "Sonos Move")
3. Speaker must be on the same network
4. Speaker must be powered on and reachable

---

### ❌ "Airfoil Won't Start / No Permission"

**Problem:** AppleScript can't control Airfoil

**Solutions:**
1. **System Settings → Privacy & Security → Accessibility**
2. Add Terminal (or iTerm)
3. Add Airfoil
4. Restart macOS (sometimes necessary 🙄)

---

### ❌ "Volume Doesn't Work"

**Problem:** Volume command has no effect

**Solutions:**
1. Speaker must be **connected** before volume can be set
2. First `connect`, then `volume`
3. Some speakers have hardware-side limits

---

### ❌ "Airfoil Not Installed"

**Problem:** `execution error: Application isn't running`

**Solution:**
```bash
# Start Airfoil
open -a Airfoil

# Or install it
brew install --cask airfoil
```

---

### ❌ "bc: command not found"

**Problem:** Volume calculation fails

**Solution:**
```bash
# Install bc (should be standard on macOS)
brew install bc
```

---

## 📋 Known Speakers

These speakers have been tested:

| Speaker | Type | Notes |
|---------|------|-------|
| `Computer` | Local | Always available |
| `Andy's M5 Macbook` | Mac | When on the network |
| `Sonos Move` | Sonos | Bluetooth or WiFi |
| `Living Room TV` | Apple TV | Via AirPlay |

> 💡 Use `./airfoil.sh list` to discover your own speakers!

---

## 🔗 Integration with Clawd

This skill works perfectly with Clawd! Examples:

```
"Hey Clawd, connect the Sonos Move"
→ ./airfoil.sh connect "Sonos Move"

"Turn the music down"
→ ./airfoil.sh volume "Sonos Move" 30

"Which speakers are on?"
→ ./airfoil.sh status
```

---

## 📜 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-25 | Initial release |
| 1.1.0 | 2025-06-10 | Documentation polished 🐸 |
| 1.2.0 | 2025-06-26 | Translated to English, ClawdHub-ready! |

---

## 🐸 Credits

```
  @..@
 (----)
( >__< )   "This skill was crafted with love
 ^^  ^^     by a frog and his human!"
```

**Author:** Andy Steinberger (with help from his Clawdbot Owen the Frog 🐸)  
**Powered by:** [Airfoil](https://rogueamoeba.com/airfoil/mac/) by Rogue Amoeba  
**Part of:** [Clawdbot](https://clawdhub.com) Skills Collection

---

<div align="center">

**Made with 💚 for the Clawdbot Community**

*Ribbit!* 🐸

</div>
