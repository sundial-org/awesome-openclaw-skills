# Changelog

## v1.2.2 (2026-01-26)

### 🧹 Repository Cleanup & Focus

**Removed old MCP server files** - Now using dedicated MCP server repo for Claude Desktop users:
- Removed `CLAUDE_DESKTOP.md` (old MCP setup docs)
- Removed `mcp_server.py` (old Python MCP server - 750+ lines)
- Removed `requirements.txt` (old MCP dependencies)

**Updated documentation for clarity:**
- README.md now clearly identifies this as the Clawdbot skill
- Added prominent callout directing Claude Desktop users to the dedicated MCP server repo
- Simplified `references/mcp_setup.md` to redirect to https://github.com/eversonl/garmin-health-mcp-server
- Updated file tree to reflect current structure

**New dedicated MCP server** for Claude Desktop users:
- Purpose-built Node.js MCP server at https://github.com/eversonl/garmin-health-mcp-server
- Uses modern @modelcontextprotocol/sdk
- Easy `npm install` + `npm run auth` setup
- Comprehensive installation guide and troubleshooting

**Both can coexist** - Shared authentication allows users to install both the Clawdbot skill and MCP server simultaneously.

**This repo is now focused exclusively on the Clawdbot skill** for automated health monitoring, scheduled reports, and proactive check-ins.

## v1.2.0 (2026-01-26)

### 🚀 Major Feature: MCP Server for Claude Desktop & Code

**NEW: Works with Claude Desktop, Claude Code, and any MCP client!**

- Added `mcp_server.py` - full MCP (Model Context Protocol) server implementation
- Exposes all Garmin tools to Claude Desktop, Claude Code, and other MCP-compatible clients
- New installation guide: `CLAUDE_DESKTOP.md` with step-by-step setup
- 14 MCP tools available:
  - Health metrics (sleep, Body Battery, HRV, activities, heart rate)
  - Time-based queries (HR/stress/BB at specific times)
  - Extended metrics (training readiness, body composition, SPO2)
  - Activity file downloads and analysis
- Updated README with Claude Desktop quick start
- Added `mcp` to requirements.txt

**Now you can use this skill with:**
- ✅ Clawdbot (original)
- ✅ Claude Desktop (new!)
- ✅ Claude Code / VS Code extension (new!)
- ✅ Any MCP-compatible client (new!)

## v1.1.5 (2026-01-25)

### Metadata
- Expanded ClawdHub description with conversational examples and "talk to your data" messaging
- Showcases real use cases: "what was my fastest speed?", activity analysis, recovery tracking

## v1.1.3 (2026-01-25)

### Documentation
- Updated Version Info section in SKILL.md with correct author and all dependencies

## v1.1.2 (2026-01-25)

### Metadata
- Updated description to highlight v1.1+ features (time queries, 20+ metrics, FIT/GPX analysis)
- Changed author to "EversonL & Claude"

## v1.1.1 (2026-01-25)

### Documentation
- Updated metadata with new dependencies (fitparse, gpxpy)

## v1.1.0 (2026-01-25)

### 🚀 Major Features

**Time-Based Queries**
- New `garmin_query.py` script for time-based questions
- Ask "what was my heart rate at 3pm?" and get instant answers
- Supports heart rate, stress, Body Battery, steps
- Flexible time parsing (12/24 hour formats)

**Extended Metrics** (`garmin_data_extended.py`)
- Training readiness & training status
- Body composition (weight, body fat %, muscle mass, BMI)
- Weight tracking over time
- SPO2 (blood oxygen saturation)
- Detailed respiration data
- Intraday steps, floors climbed
- Intensity minutes (vigorous/moderate activity)
- Hydration tracking
- Time-series stress data
- Max metrics (VO2 max, fitness age, endurance/hill scores)
- Intraday heart rate (all samples)

**Activity File Analysis** (`garmin_activity_files.py`)
- Download FIT/GPX/TCX files from activities
- Parse FIT files for GPS, elevation, HR, cadence, power
- Parse GPX files for route visualization
- Query data at specific distances ("what was my elevation at mile 2?")
- Query data at specific times during activities
- Comprehensive activity analysis & statistics
- Support for advanced use cases (route mapping, pace analysis, elevation profiles)

**Documentation**
- New `references/extended_capabilities.md` with comprehensive usage examples
- Updated dependencies (fitparse, gpxpy)

## v1.0.1 (2026-01-25)

### Bug Fixes
- Fixed sleep data extraction - properly parse nested `dailySleepDTO` object from Garmin API
- Sleep time and scores now display correctly in all charts and dashboards

## v1.0.0 (2026-01-25)

### Initial Release

**Features:**
- Fetch health data from Garmin Connect (sleep, Body Battery, HRV, heart rate, activities, stress)
- Generate interactive HTML charts with Chart.js
- Science-backed health analysis framework
- Support for multiple credential configuration methods
- Automatic token refresh

**Data Available:**
- Sleep: duration, stages (deep/light/REM), scores, HRV during sleep
- Body Battery: Garmin's recovery metric (0-100)
- HRV: nightly heart rate variability with baseline tracking
- Heart Rate: resting, max, min throughout the day
- Activities: workouts with calories, duration, heart rate, GPS data
- Stress: all-day stress levels based on HRV analysis

**Charts:**
- Sleep analysis (hours + scores)
- Body Battery recovery (color-coded by level)
- HRV & Resting Heart Rate trends
- Activities summary (by type with calories)
- Full dashboard combining all metrics

**Configuration:**
- UI-configurable via Clawdbot config (`skills.entries.garmin-health-analysis.env`)
- Local config.json support
- Command-line arguments
- Environment variables

**Requirements:**
- Python 3.7+
- garminconnect library (installed via pip)
- Garmin Connect account with wearable device

**Security:**
- Session tokens stored locally in `~/.clawdbot/garmin/`
- Tokens auto-refresh
- No data sent anywhere except Garmin's official servers
