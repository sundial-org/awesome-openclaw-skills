---
name: virus-monitor
version: 0.1.0
description: Virus-Monitoring für Wien (Abwasser + Sentinel)
author: ClaudeBot
tags: [health, vienna, monitoring, covid, influenza, rsv]
---

# virus-monitor

Kombiniert mehrere österreichische Datenquellen für Virus-Monitoring:

## Datenquellen

1. **Nationales Abwassermonitoring** (abwassermonitoring.at)
   - SARS-CoV-2 Genkopien pro Einwohner/Tag
   - Bundesländer-Daten inkl. Wien
   
2. **MedUni Wien Sentinel System** (viro.meduniwien.ac.at)
   - Positivitätsraten für respiratorische Viren
   - DINÖ (Diagnostisches Influenza Netzwerk Österreich)
   - Wöchentliche Berichte

3. **AGES Abwasser Dashboard** (abwasser.ages.at)
   - SARS-CoV-2, Influenza, RSV
   - Österreichweit

## Usage

```bash
# Alle Daten als JSON
virus-monitor

# Nur bestimmte Quelle
virus-monitor --source abwasser
virus-monitor --source sentinel
virus-monitor --source ages
```

## Output

```json
{
  "timestamp": "2026-01-09T00:37:00Z",
  "status": "erhöht",
  "sources": {
    "abwasser": { ... },
    "sentinel": { ... },
    "ages": { ... }
  },
  "summary": {
    "wien": {
      "sars_cov_2": "...",
      "influenza": "...",
      "rsv": "..."
    }
  }
}
```

## Status-Levels

- `niedrig` - Normale saisonale Aktivität
- `moderat` - Erhöhte Aktivität, Aufmerksamkeit empfohlen  
- `erhöht` - Deutlich erhöhte Aktivität
- `hoch` - Starke Virus-Zirkulation

## Dependencies

- `curl` - HTTP requests
- `jq` - JSON processing
- Standard Unix tools (awk, grep, sed)

## Notes

- Abwasserdaten haben ~1-2 Wochen Verzögerung
- Sentinel-Daten werden wöchentlich aktualisiert (Freitags)
- AGES Dashboard ist eine Shiny-App (dynamisch)
