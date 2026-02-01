# Garmin Health Analysis - Clawdbot Skill

> **Talk to your Garmin data naturally** - "what was my fastest speed snowboarding?", "how did I sleep last night?", "what was my heart rate at 3pm?"

Access 20+ metrics from your Garmin device: sleep stages, Body Battery, HRV, VO2 max, training readiness, body composition, SPO2, and more. Download FIT/GPX files, query elevation/pace at any point, and generate interactive health dashboards.

## 🔵 Looking for Claude Desktop? 

**This is the Clawdbot skill repo.** For standard Claude Desktop, use the dedicated MCP server:

👉 **[garmin-health-mcp-server](https://github.com/eversonl/garmin-health-mcp-server)** - Node.js MCP server for Claude Desktop

---

## 🚀 Clawdbot Installation

**Best for**: Automated health monitoring, scheduled reports, proactive check-ins

```bash
# Install via clawdhub
clawdhub install garmin-health-analysis

# Or manually
cd ~/.clawdbot/skills
git clone https://github.com/eversonl/ClawdBot-garmin-health-analysis.git garmin-health-analysis

# Install dependencies
pip3 install garminconnect fitparse gpxpy

# Configure credentials and authenticate
python3 scripts/garmin_auth.py login
```

**[📖 Full Setup Guide](SKILL.md)**

## ⚡ Features

- **Natural language queries**: "How's my recovery this week?" → instant Body Battery analysis
- **Sleep analysis**: Hours, stages (light/deep/REM), quality scores, trends
- **Recovery tracking**: Body Battery, HRV, training readiness, stress levels
- **Workout data**: Activities by type, calories, duration, pace, elevation
- **Health metrics**: Resting heart rate, VO2 max, body composition, SPO2
- **Activity files**: Download FIT/GPX for detailed route and performance analysis
- **Interactive charts**: Beautiful HTML dashboards with Chart.js visualizations
- **Science-backed insights**: Interpret trends with expert analysis framework

## 📊 Example Queries

**Clawdbot or Claude Desktop:**

> "How did I sleep last night?"
> 
> "Show me my health dashboard for the last month"
> 
> "Is my HRV improving?"
> 
> "What was my fastest speed during yesterday's bike ride?"
> 
> "How's my recovery vs. training load balance?"
> 
> "Download the GPX file for my Sunday run"

## 🛠️ Key Metrics

| Metric | Range | What It Means |
|--------|-------|---------------|
| **Body Battery** | 0-100 | Garmin's recovery score (higher = more energy) |
| **Sleep Score** | 0-100 | Overall sleep quality (90+ = excellent) |
| **HRV** | 20-200+ ms | Heart rate variability (higher = better recovery) |
| **Resting HR** | 40-80 bpm | Lower is generally better (athletes: 40-60) |
| **Stress** | Low/Med/High | Based on HRV throughout the day |

## 📦 What's Included

```
garmin-health-analysis/
├── SKILL.md                       # Clawdbot setup & usage
├── README.md                      # This file
├── install.sh                     # Automated installation script
├── scripts/
│   ├── garmin_auth.py            # Authentication helper
│   ├── garmin_data.py            # Fetch health metrics (JSON)
│   ├── garmin_chart.py           # Generate HTML charts
│   ├── garmin_data_extended.py   # Extended metrics (VO2, readiness, etc.)
│   ├── garmin_activity_files.py  # Download FIT/GPX files
│   └── garmin_query.py           # Time-based queries
├── references/
│   ├── health_analysis.md        # Metric interpretation guide
│   ├── api.md                    # Garmin Connect API docs
│   └── extended_capabilities.md  # Advanced features
└── config.example.json           # Credentials template
```

## 🔒 Privacy & Security

- Credentials stored locally (never sent to third parties)
- Session tokens auto-refresh (no repeated logins)
- Connects only to Garmin's official API
- No cloud storage or external data sharing
- Open source - audit the code yourself

## 📚 Documentation

- **[SKILL.md](SKILL.md)** - Complete Clawdbot setup, commands, troubleshooting
- **[references/health_analysis.md](references/health_analysis.md)** - Science-backed metric interpretation
- **[references/api.md](references/api.md)** - Garmin Connect API details
- **[references/extended_capabilities.md](references/extended_capabilities.md)** - Advanced features

### Looking for Claude Desktop?
See **[garmin-health-mcp-server](https://github.com/eversonl/garmin-health-mcp-server)** for the dedicated MCP server (you can use both!)

## 🐛 Troubleshooting

**Authentication issues?**
- Run `python3 scripts/garmin_auth.py login` to refresh tokens
- Check credentials in config.json or environment variables
- Try logging into Garmin Connect web to verify account

**Missing data?**
- Some metrics require specific devices (Body Battery needs HRV-capable watches)
- Check device was worn during the time period
- New accounts may have limited history

**Rate limits?**
- Garmin limits API requests - wait a few minutes and try again
- Batch queries when possible (use `summary` instead of individual calls)

## 🙏 Credits

- **Author**: EversonL & Claude
- **Version**: 1.2.0
- **License**: MIT
- **Dependencies**: [python-garminconnect](https://github.com/cyberjunky/python-garminconnect), fitparse, gpxpy

## 🔗 Links

- **Clawdbot**: [clawdbot.com](https://clawdbot.com)
- **ClawdHub**: [clawdhub.com](https://clawdhub.com)
- **Garmin Connect**: [connect.garmin.com](https://connect.garmin.com)

---

**Questions?** Open an issue on GitHub or ask in the Clawdbot Discord!
