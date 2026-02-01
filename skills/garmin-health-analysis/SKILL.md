---
name: garmin-health-analysis
description: Talk to your Garmin data naturally - "what was my fastest speed snowboarding?", "how did I sleep last night?", "what was my heart rate at 3pm?". Access 20+ metrics (sleep stages, Body Battery, HRV, VO2 max, training readiness, body composition, SPO2), download FIT/GPX files for route analysis, query elevation/pace at any point, and generate interactive health dashboards. From casual "show me this week's workouts" to deep "analyze my recovery vs training load".
version: 1.2.2
author: EversonL & Claude
homepage: https://github.com/eversonl/ClawdBot-garmin-health-analysis
metadata: {"clawdbot":{"emoji":"⌚","requires":{"env":["GARMIN_EMAIL","GARMIN_PASSWORD"]},"install":[{"id":"garminconnect","kind":"python","package":"garminconnect","label":"Install garminconnect (pip)"},{"id":"fitparse","kind":"python","package":"fitparse","label":"Install fitparse (pip)"},{"id":"gpxpy","kind":"python","package":"gpxpy","label":"Install gpxpy (pip)"}]}}
---

# Garmin Health Analysis

Query health metrics from Garmin Connect and generate interactive HTML charts.

## Two Installation Paths

This skill supports **two different setups**:

1. **Clawdbot Skill** (this guide) - Use with Clawdbot for automation and proactive health monitoring
2. **MCP Server** ([see MCP setup guide](references/mcp_setup.md)) - Use with standard Claude Desktop as an MCP server

Choose the path that matches your use case. You can also use both simultaneously!

---

## Clawdbot Skill Setup (first time only)

### 1. Install Dependencies

```bash
pip3 install garminconnect
```

### 2. Configure Credentials

You have three options to provide your Garmin Connect credentials:

#### Option A: Clawdbot Config (Recommended - UI configurable)

Add credentials to `~/.clawdbot/clawdbot.json`:

```json
{
  "skills": {
    "entries": {
      "garmin-health-analysis": {
        "enabled": true,
        "env": {
          "GARMIN_EMAIL": "your-email@example.com",
          "GARMIN_PASSWORD": "your-password"
        }
      }
    }
  }
}
```

**Tip**: You can also set these through the Clawdbot UI in the Skills settings panel.

#### Option B: Local Config File

Create a config file in the skill directory:

```bash
cd ~/.clawdbot/skills/garmin-health-analysis
# or: cd <workspace>/skills/garmin-health-analysis
cp config.example.json config.json
# Edit config.json and add your email and password
```

**config.json:**
```json
{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

**Note**: `config.json` is gitignored to keep your credentials secure.

#### Option C: Command Line

Pass credentials directly when authenticating:
```bash
python3 scripts/garmin_auth.py login \
  --email YOUR_EMAIL@example.com \
  --password YOUR_PASSWORD
```

### 3. Authenticate

Login to Garmin Connect and save session tokens:

```bash
python3 scripts/garmin_auth.py login
```

This uses credentials from (in priority order):
1. Command line arguments (`--email`, `--password`)
2. Local config file (`config.json`)
3. Environment variables (`GARMIN_EMAIL`, `GARMIN_PASSWORD`)
4. Clawdbot config (`skills.entries.garmin-health-analysis.env`)

Session tokens are stored in `~/.clawdbot/garmin-tokens.json` and auto-refresh.

Check authentication status:
```bash
python3 scripts/garmin_auth.py status
```

## Fetching Data

Use `scripts/garmin_data.py` to get JSON data:

```bash
# Sleep (last 7 days default)
python3 scripts/garmin_data.py sleep --days 14

# Body Battery (Garmin's recovery metric)
python3 scripts/garmin_data.py body_battery --days 30

# HRV data
python3 scripts/garmin_data.py hrv --days 30

# Heart rate (resting, max, min)
python3 scripts/garmin_data.py heart_rate --days 7

# Activities/workouts
python3 scripts/garmin_data.py activities --days 30

# Stress levels
python3 scripts/garmin_data.py stress --days 7

# Combined summary with averages
python3 scripts/garmin_data.py summary --days 7

# Custom date range
python3 scripts/garmin_data.py sleep --start 2026-01-01 --end 2026-01-15

# User profile
python3 scripts/garmin_data.py profile
```

Output is JSON to stdout. Parse it to answer user questions.

## Generating Charts

Use `scripts/garmin_chart.py` for interactive HTML visualizations:

```bash
# Sleep analysis (hours + scores)
python3 scripts/garmin_chart.py sleep --days 30

# Body Battery recovery chart (color-coded)
python3 scripts/garmin_chart.py body_battery --days 30

# HRV & resting heart rate trends
python3 scripts/garmin_chart.py hrv --days 90

# Activities summary (by type, calories)
python3 scripts/garmin_chart.py activities --days 30

# Full dashboard (all 4 charts)
python3 scripts/garmin_chart.py dashboard --days 30

# Save to specific file
python3 scripts/garmin_chart.py dashboard --days 90 --output ~/Desktop/garmin-health.html
```

Charts open automatically in the default browser. They use Chart.js with a modern gradient design, stat cards, and interactive tooltips.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "How did I sleep last night?" | `garmin_data.py summary --days 1`, report sleep hours + score |
| "How's my recovery this week?" | `garmin_data.py body_battery --days 7`, report average + trend |
| "Show me my health for the last month" | `garmin_chart.py dashboard --days 30` |
| "Is my HRV improving?" | `garmin_data.py hrv --days 30`, analyze trend |
| "What workouts did I do this week?" | `garmin_data.py activities --days 7`, list activities with details |
| "How's my resting heart rate?" | `garmin_data.py heart_rate --days 7`, report average + trend |

## Key Metrics

### Body Battery (0-100)
Garmin's proprietary recovery metric based on HRV, stress, sleep, and activity:
- **High (75-100)**: Fully recharged, ready for high intensity
- **Medium (50-74)**: Moderate energy, good for regular activity
- **Low (25-49)**: Limited energy, recovery needed
- **Very Low (0-24)**: Depleted, prioritize rest

### Sleep Scores (0-100)
Overall sleep quality based on duration, stages, and disturbances:
- **Excellent (90-100)**: Optimal restorative sleep
- **Good (80-89)**: Quality sleep with minor issues
- **Fair (60-79)**: Adequate but could improve
- **Poor (0-59)**: Significant sleep deficiencies

### HRV (Heart Rate Variability)
Measured in milliseconds, higher is generally better:
- Indicates nervous system balance and recovery capacity
- Track **trends** over time (increasing = improving recovery)
- Affected by sleep, stress, training load, illness
- Normal range varies by individual (20-200+ ms)

### Resting Heart Rate (bpm)
Lower generally indicates better cardiovascular fitness:
- **Athletes**: 40-60 bpm
- **Fit adults**: 60-70 bpm
- **Average adults**: 70-80 bpm
- Sudden increases may indicate stress, illness, or overtraining

### Stress Levels
Based on HRV analysis throughout the day:
- **Low stress**: Rest and recovery periods
- **Medium stress**: Normal daily activities
- **High stress**: Physical activity or mental pressure

## Health Analysis

When users ask for insights or want to understand their trends, use `references/health_analysis.md` for:
- Science-backed interpretation of all metrics
- Normal ranges by age and fitness level
- Pattern detection (weekly trends, recovery cycles, training load balance)
- Actionable recommendations based on data
- Warning signs that suggest rest or medical consultation

### Analysis workflow
1. Fetch data: `python3 scripts/garmin_data.py summary --days N`
2. Read `references/health_analysis.md` for interpretation framework
3. Apply the analysis framework: Status → Trends → Patterns → Insights → Recommendations
4. Always include disclaimer that this is informational, not medical advice

## Troubleshooting

### Authentication Issues
- **"Invalid credentials"**: Double-check email/password, try logging into Garmin Connect web
- **"Tokens expired"**: Run login again: `python3 scripts/garmin_auth.py login ...`
- **"Too many requests"**: Garmin rate-limits; wait a few minutes and try again

### Missing Data
- Some metrics require specific Garmin devices (Body Battery needs HRV-capable devices)
- Historical data may have gaps if device wasn't worn
- New accounts may have limited history

### Library Issues
- If `garminconnect` import fails: `pip3 install --upgrade garminconnect`
- Garmin occasionally changes their API; update the library if requests fail

## Privacy Note

- Credentials are stored locally in `~/.clawdbot/garmin-tokens.json`
- Session tokens refresh automatically
- No data is sent anywhere except to Garmin's official servers
- You can revoke access anytime by deleting the tokens file

## Comparison: Garmin vs Whoop

| Feature | Garmin | Whoop |
|---------|--------|-------|
| **Recovery metric** | Body Battery (0-100) | Recovery Score (0-100%) |
| **HRV tracking** | Yes (nightly average) | Yes (detailed) |
| **Sleep stages** | Light, Deep, REM, Awake | Light, SWS, REM, Awake |
| **Activity tracking** | Built-in GPS, many sport modes | Strain score (0-21) |
| **Stress** | All-day stress levels | Not directly tracked |
| **API** | Unofficial (garminconnect) | Official OAuth |
| **Device types** | Watches, fitness trackers | Wearable band only |

## References

- `references/api.md` — Garmin Connect API details (unofficial)
- `references/health_analysis.md` — Science-backed health data interpretation
- [garminconnect library](https://github.com/cyberjunky/python-garminconnect) — Python API wrapper
- [Garmin Connect](https://connect.garmin.com) — Official web interface

## Version Info

- **Created**: 2026-01-25
- **Author**: EversonL & Claude
- **Version**: 1.2.0
- **Dependencies**: garminconnect, fitparse, gpxpy (Python libraries)
- **License**: MIT
