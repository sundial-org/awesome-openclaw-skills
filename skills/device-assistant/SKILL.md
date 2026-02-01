---
name: device-assistant
version: 1.0.0
description: "Personal device and appliance manager with error code lookup and troubleshooting. Tracks all your devices (appliances, electronics, software) with model numbers, manuals, and warranty info. When something breaks, tell it the error code and get instant solutions. Use when: device shows error, need manual, warranty check, adding new device, maintenance reminder. Triggers: /device, /geräte, 'mein Geschirrspüler', 'Fehler E24', 'Fehlermeldung', device problems, appliance issues."
author: clawdbot
license: MIT
metadata:
  clawdbot:
    emoji: "🔧"
    triggers: ["/device", "/geräte"]
    requires:
      bins: ["jq", "curl"]
  tags: ["devices", "appliances", "troubleshooting", "maintenance", "home", "warranty"]
---

# Device Assistant 🔧

Personal device manager with error code lookup, troubleshooting, and maintenance tracking.

## Features

- **Device Registry**: Track all devices with model, serial, purchase info
- **Error Lookup**: Instant error code explanations
- **Troubleshooting**: Step-by-step solutions
- **Manual Links**: Quick access to documentation
- **Warranty Tracking**: Know when warranties expire
- **Maintenance Reminders**: Filter changes, updates, etc.

## Commands

| Command | Action |
|---------|--------|
| `/device` | List all devices or show status |
| `/device add` | Add a new device (interactive) |
| `/device list [category]` | List devices by category |
| `/device info <name>` | Show device details |
| `/device error <name> <code>` | Lookup error code |
| `/device help <name> <problem>` | Troubleshoot a problem |
| `/device manual <name>` | Get manual/documentation |
| `/device warranty` | Show warranty status |
| `/device maintenance` | Show maintenance schedule |
| `/device remove <name>` | Remove a device |

## Natural Language

The skill understands natural queries:

- *"Mein Geschirrspüler zeigt E24"*
- *"Waschmaschine macht komische Geräusche"*
- *"Wo ist die Anleitung für den Thermomix?"*
- *"Wann läuft die Garantie vom TV aus?"*

## Device Categories

| Category | Examples |
|----------|----------|
| `kitchen` | Geschirrspüler, Kühlschrank, Backofen, Thermomix |
| `laundry` | Waschmaschine, Trockner |
| `electronics` | TV, Router, NAS, Computer |
| `climate` | Heizung, Klimaanlage, Luftreiniger |
| `smart-home` | Hue, Homematic, Sensoren |
| `software` | Apps, Betriebssysteme, Lizenzen |
| `other` | Alles andere |

## Handler Commands

```bash
handler.sh status $WORKSPACE                     # Overview
handler.sh list [category] $WORKSPACE            # List devices
handler.sh add <json> $WORKSPACE                 # Add device
handler.sh info <device-id> $WORKSPACE           # Device details
handler.sh error <device-id> <code> $WORKSPACE   # Error lookup
handler.sh troubleshoot <device-id> <problem> $WS # Get help
handler.sh manual <device-id> $WORKSPACE         # Manual link
handler.sh warranty $WORKSPACE                   # Warranty overview
handler.sh maintenance $WORKSPACE                # Maintenance due
handler.sh update <device-id> <json> $WORKSPACE  # Update device
handler.sh remove <device-id> $WORKSPACE         # Remove device
handler.sh search <query> $WORKSPACE             # Search devices
handler.sh log <device-id> <note> $WORKSPACE     # Add maintenance log
```

## Data Structure

### Device Entry

```json
{
  "id": "dishwasher-1",
  "name": "Geschirrspüler",
  "nickname": "Spüli",
  "category": "kitchen",
  "manufacturer": "Siemens",
  "model": "SN658X06TE",
  "serialNumber": "ABC123456",
  "purchaseDate": "2022-03-15",
  "purchasePrice": 899,
  "warranty": {
    "expires": "2025-03-15",
    "type": "manufacturer",
    "notes": "3 Jahre Siemens"
  },
  "manualUrl": "https://...",
  "supportUrl": "https://...",
  "location": "Küche",
  "notes": "Salz alle 2 Monate nachfüllen",
  "maintenance": [
    {"task": "Filter reinigen", "interval": "monthly", "lastDone": "2026-01-01"}
  ],
  "errorHistory": [],
  "addedAt": "2024-01-01"
}
```

## Error Code Lookup

The skill searches for error codes using:

1. **Built-in database** for common manufacturers
2. **Web search** for specific model + error code
3. **Manual extraction** if manual URL is stored

### Common Error Code Patterns

| Manufacturer | Pattern | Example |
|--------------|---------|---------|
| Siemens/Bosch | E + number | E24, E15 |
| Miele | F + number | F11, F53 |
| AEG | E + number | E10, E20 |
| Samsung | Letters + numbers | UE, OE, LE |
| LG | Letters | OE, IE, PE |

## Example Session

```
User: Ich habe einen neuen Geschirrspüler

Bot: 🔧 Neues Gerät hinzufügen:
     
     Welche Infos hast du?
     • Hersteller?
     • Modell?
     • Seriennummer? (optional)
     • Kaufdatum?

User: Siemens SN658X06TE, gekauft am 15.3.2022

Bot: ✅ Gespeichert!
     
     📦 Geschirrspüler (Siemens SN658X06TE)
     📅 Gekauft: 15.03.2022
     🛡️ Garantie: bis 15.03.2025 (ABGELAUFEN)
     📄 Anleitung: [Link gefunden]
     
     Spitzname vergeben? (z.B. "Spüli")
```

```
User: Mein Geschirrspüler zeigt E24

Bot: 🔧 Siemens SN658X06TE — Fehler E24
     
     ⚠️ Bedeutung: Abpumpproblem
     Das Wasser wird nicht richtig abgepumpt.
     
     🔨 Lösung:
     1. Gerät ausschalten
     2. Sieb am Boden prüfen und reinigen
     3. Abflussschlauch auf Knicke prüfen
     4. Siphon-Anschluss kontrollieren
     5. Gerät neu starten
     
     📄 Details: Anleitung S. 45
     
     [Problem gelöst] [Weitere Hilfe]
```

## Data Files

Stored in `$WORKSPACE/memory/device-assistant/`:

| File | Purpose |
|------|---------|
| `devices.json` | All registered devices |
| `error-history.json` | Past errors and solutions |
| `maintenance-log.json` | Maintenance history |
| `error-codes/` | Cached error code info |

## Warranty Alerts

The skill can remind you before warranties expire:

```
⚠️ Garantie-Warnung:

Diese Geräte laufen bald ab:
• TV Samsung (noch 30 Tage)
• Waschmaschine (noch 45 Tage)

Tipp: Jetzt prüfen ob alles funktioniert!
```

## Requirements

- `jq` (JSON processing)
- `curl` (web lookups)
- Internet for error code search
