---
name: inkjet
description: "Print text, images, and QR codes to a Bluetooth thermal printer. Use `inkjet print` for output, `inkjet scan` to discover printers."
homepage: https://github.com/AaronChartier/inkjet
metadata:
  openclaw:
    emoji: "🖨️"
    requires: { bins: ["inkjet"], bluetooth: true }
    install:
      - { id: "pip", kind: "pip", package: "inkjet", label: "Install (pip)" }
      - { id: "brew", kind: "brew", package: "aaronchartier/tap/inkjet", label: "Install (Homebrew)" }
---

# Thermal Printer Skill

Print text, images, and QR codes to a Bluetooth thermal printer using the `inkjet` CLI. Thermal paper is extremely low-cost, enabling high-frequency physical output.

## Installation

### via pip (Universal)
```bash
pip install inkjet
```

### via Homebrew (macOS)
```bash
brew install aaronchartier/tap/inkjet
```

## Setup

**Preparation:** Ensure your printer is turned **ON**. The printer does **NOT** need to be paired to the host computer's Bluetooth settings; `inkjet` connects directly via BLE.

Scan for printers and set default:
```bash
inkjet scan
```

Check current configuration:
```bash
inkjet whoami
```

## Print Text

Print strings directly. Supports standard escape sequences like `\n` for multiline output.

```bash
inkjet print text "Hello, World!"
inkjet print text "Line 1\nLine 2\nLine 3"
inkjet print text "Big Text" --size 72
```

## Print Markdown

Render high-fidelity formatted content using Markdown syntax. This is the recommended way for agents to output complex receipts or logs without saving temporary files.

```bash
inkjet print text "# Order 104\n- 1x Coffee\n- 1x Donut" --markdown
```

## Print Files

Output the contents of a local file. Supports plain text (`.txt`) and Markdown (`.md`).

```bash
inkjet print file ./receipt.txt
inkjet print file ./README.md
```

## Print Images

```bash
inkjet print image ./photo.png
inkjet print image ./logo.jpg --dither
```

## Print QR Codes

Generates and prints QR codes. Smartphone scanners (iPhone/Android) can reliably read codes down to `--size 75`.

```bash
inkjet print qr "https://github.com/AaronChartier/inkjet"
inkjet print qr "WiFi:S:NetworkName;P:example123;;" --size 75
```

## Paper Control

```bash
inkjet feed 100      # Feed paper forward (steps)
```

## Configuration

Manage settings globally or locally per project. If a `.inkjet/` folder exists in the current workspace, it will be prioritized (config setting with --local to create).

```bash
inkjet config show                    # Show all settings
inkjet config set printer <UUID>      # Set the default device
inkjet config set energy 12000        # Set local project darkness
inkjet config alias kitchen <UUID>    # Save a friendly name
```

## Multi-Printer Orchestration

If the environment (e.g., `TOOLS.md`) contains multiple printer UUIDs or **aliases**, target specific hardware using the `--address` / `-a` flag. Use `-a default` to explicitly target the primary configured device.

### Orchestration Strategies:
1. **Role-Based Routing**: Route content based on hardware role (e.g., Stickers vs Receipts).
   `inkjet print text "Label" -a stickers`
2. **High-Throughput (Load Balancing)**: Distribute jobs across a farm of printers (Round-Robin) to maximize prints-per-minute.

```bash
# Orchestrated Print Examples
inkjet print text "Main Status" -a office
inkjet print text "Order #104" -a kitchen
inkjet print qr "https://github.com/AaronChartier/inkjet" -a default
inkjet print file ./log.txt -a "UUID_EXT_1"
```

## Configuration Tweaking (Filesystem Access)

You can bypass the CLI and modify your behavior by writing directly to the configuration JSON. `inkjet` prioritizes `./.inkjet/config.json` over the global home directory (which is default).

### JSON Schema
```json
{
  "default_printer": "UUID",
  "printers": { "alias": "UUID" },
  "energy": 12000,
  "print_speed": 10,
  "quality": 3,
  "padding_left": 0,
  "padding_top": 10,
  "line_spacing": 8,
  "align": "left",
  "font_size": 18
}
```

Use this to adjust default margins (`padding`), alignment, or font sizes (size) for different document types without changing your command strings.

## JSON Output (for scripting)

Commands support `--json` for machine-readable output:

```bash
inkjet scan --json
inkjet whoami --json
```

## Piping Content (Dynamic Output)

Stream data from another command's output without creating a file. Use `-` as an argument to read from standard input (stdin).

```bash
# Text Piping
echo "Receipt line 1" | inkjet print text -

# Image Piping
curl -s "https://raw.githubusercontent.com/AaronChartier/inkjet/main/assets/logo.jpg" | inkjet print image -
```

## Troubleshooting

If printer not found:
```bash
inkjet doctor