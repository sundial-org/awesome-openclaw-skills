# 🖨️ inkjet — Thermal Printer CLI

**The physical terminal for agents. Zero ink. Pennies per print.**

`inkjet` is a CLI control plane for inexpensive X6H-style Bluetooth thermal printers. Its designed for humans and agentic workflows that require high-frequency physical output without the overhead of proprietary ink, drivers, or "Low Cyan" warnings.

[Install](#install) • [Quickstart](#quickstart) • [Why inkjet?](#why-inkjet) • [Claude Skill](#claude-skill)

---

## Why inkjet?

### 1. The Name is Ironic
Traditional inkjet printers are a nightmare of DRM-locked cartridges, clogged heads, and expensive maintenance. **inkjet** has zero ink. It uses heat, cheap thermal paper, and code.

### 2. Agentic Economics
If your AI agent prints 50 status updates, debug logs, or "receipts of thought" per day, a standard printer would bankrupt you. Thermal paper costs practically nothing. `inkjet` enables a high-bandwidth, ultra-low-cost physical signaling channel for local AI.

### 3. Machine First
While most thermal printer apps are locked behind buggy mobile UIs, `inkjet` provides a clean, scriptable interface.

---

## Install

### via pip
```bash
pip install inkjet
```

### via Homebrew (macOS)
```bash
brew install aaronchartier/tap/inkjet
```

### Note for macOS Users
On the first run, macOS will display a system dialog asking for **Bluetooth Access**. 
1. Click **Allow**.
2. If the first command failed with an error, simply run it again—it will succeed now that permissions are granted.
3. Ensure Bluetooth is toggled **ON** in System Settings.

---

## Quickstart

**Preparation:** Ensure your printer is **ON**. Note that the printer does **NOT** need to be paired to your computer's Bluetooth settings; `inkjet` connects directly via BLE.

```bash
# 1. Discover and auto-configure your printer
inkjet scan

# 2. Print something immediately
inkjet print text "Ship it." --size 48

# 3. Verify configuration
inkjet whoami
```

---

## Usage

### General
- **About**: `inkjet about` (Show project credits and version)
- **Status**: `inkjet whoami` (Show current configuration)
- **Doctor**: `inkjet doctor` (Diagnose connection issues)

### Printing
- **Text**: `inkjet print text "Hello"` (supports `--size`, `--font`, and stdin via `-`)
- **Images**: `inkjet print image ./photo.png` (auto-dithering for thermal media)
- **QR Codes**: `inkjet print qr "https://github.com/AaronChartier/inkjet"`
- **Stdin**: `echo "Agent log..." | inkjet print text -`

### Configuration
- **Scan**: `inkjet scan` (discovers printers and identifies aliases)
- **Settings**: `inkjet config set energy 12000` (adjust darkness)
- **Layout**: `inkjet config set padding_top 20` (manage margins/spacing)
- **Aliases**: `inkjet config alias den "15F8CC20-..."` (save friendly names)
- **Default**: `inkjet config set printer <UUID>` (shortcut for setting the default device)

### Configuration Schema (JSON)
Agents can modify behavior by writing directly to `~/.inkjet/config.json` or `./.inkjet/config.json`:

```json
{
  "default_printer": "UUID",
  "printers": { "alias": "UUID" },
  "energy": 9500,
  "print_speed": 10,
  "quality": 3,
  "padding_left": 0,
  "padding_top": 10,
  "line_spacing": 8,
  "align": "left",
  "font_size": 18
}
```

### Smart Configuration (Local-First)
By default, `inkjet` saves settings to `~/.inkjet/config.json`. However, it supports a **Local-First** workflow ideal for specific projects or agents:
- **Prioritization**: If a `./.inkjet/config.json` exists in your current folder, `inkjet` will use it instead of the global one.
- **Portability**: Force a local config using the `--local` flag:
  - `inkjet config set energy 5000 --local`
  - `inkjet scan --local`
- **Verification**: Use `inkjet doctor` to see exactly which config file is currently active.

### Paper Control
- **Feed**: `inkjet feed 100` (manual advance)

---

## Claude Skill

`inkjet` is built to be a "Claude Skill." By adding the `inkjet` binary to your environment, you give your AI agents the ability to:
- Print physical status receipts for long-running tasks.
- Output QR codes for mobile handoffs (e.g., "Scan this to see the URL I just generated"). QR codes are ligible down to size 75.
- Create physical "ticketing" systems for Jira or GitHub issues.

See `SKILL.md` for the full agentic instruction set.

---

## Supported Hardware

`inkjet` is built for those **$5 'Got-It-Online' thermal printers** (Cat Printers, Mini Pocket Printers, etc). 

Specifically, any printer using the **X6H**, **GT01**, or **MX06** Bluetooth protocols. These are the gold standard for budget agentic output: they are small, battery-powered, and use standard 58mm thermal rolls that cost next to nothing. Personally tested working with **X6H**.

---

## Technical Protocol (for tinkerers)

`inkjet` communicates via Bluetooth Low Energy (BLE) using the industry-standard GATT write-point for this hardware family:

- **Service UUID**: `0000AE01-0000-1000-8000-00805F9B34FB`
- **Characteristic UUID**: `0000AE01-0000-1000-8000-00805F9B34FB`

If you encounter a new "mystery" printer that doesn't work out of the box, use a mobile BLE scanner like **nRF Connect** to check if your device exposes the `AE01` service. If it uses a different characteristic, please open an issue!

---

## License
MIT
