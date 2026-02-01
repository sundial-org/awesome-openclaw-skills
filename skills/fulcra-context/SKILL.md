---
name: fulcra-context
description: Access your human's personal context data (biometrics, sleep, activity, calendar, location) via the Fulcra Life API and MCP server. Requires human's Fulcra account + OAuth2 consent.
homepage: https://fulcradynamics.com
metadata: {"openclaw":{"emoji":"🫀","requires":{"bins":["curl"]},"primaryEnv":"FULCRA_ACCESS_TOKEN"}}
---

# Fulcra Context — Personal Data for AI Partners

Give your agent situational awareness. With your human's consent, access their biometrics, sleep, activity, location, and calendar data from the Fulcra Life API.

## What This Enables

With Fulcra Context, you can:
- Know how your human slept → adjust morning briefing intensity
- See heart rate / HRV trends → detect stress, suggest breaks
- Check location → context-aware suggestions (home vs. office vs. traveling)
- Read calendar → proactive meeting prep, schedule awareness
- Track workouts → recovery-aware task scheduling

## Privacy Model

- **OAuth2 per-user** — your human controls exactly what data you see
- **Their data stays theirs** — Fulcra stores it, you get read access only
- **Consent is revocable** — they can disconnect anytime
- **NEVER share your human's Fulcra data publicly without explicit permission**

## Setup

### Option 1: MCP Server (Recommended)

Use Fulcra's hosted MCP server at `https://mcp.fulcradynamics.com/mcp` (Streamable HTTP transport, OAuth2 auth).

Your human needs a Fulcra account (free via the [Context iOS app](https://apps.apple.com/app/id1633037434) or [Portal](https://portal.fulcradynamics.com/)).

**Claude Desktop config** (claude_desktop_config.json):
```json
{
  "mcpServers": {
    "fulcra_context": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.fulcradynamics.com/mcp"]
    }
  }
}
```

**Or run locally via uvx:**
```json
{
  "mcpServers": {
    "fulcra_context": {
      "command": "uvx",
      "args": ["fulcra-context-mcp@latest"]
    }
  }
}
```

Also tested with: Goose, Windsurf, VS Code. Open source: [github.com/fulcradynamics/fulcra-context-mcp](https://github.com/fulcradynamics/fulcra-context-mcp)

### Option 2: Direct API Access

1. Your human creates a Fulcra account
2. They generate an access token via the [Python client](https://github.com/fulcradynamics/fulcra-api-python) or Portal
3. Store the token: `skills.entries.fulcra-context.apiKey` in openclaw.json

## Quick Commands

### Check sleep (last night)

```bash
# Get time series for sleep stages (last 24h)
curl -s "https://api.fulcradynamics.com/data/v0/time_series_grouped?metrics=SleepStage&start=$(date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)&end=$(date -u +%Y-%m-%dT%H:%M:%SZ)&samprate=300" \
  -H "Authorization: Bearer $FULCRA_ACCESS_TOKEN"
```

### Check heart rate (recent)

```bash
curl -s "https://api.fulcradynamics.com/data/v0/time_series_grouped?metrics=HeartRate&start=$(date -u -v-2H +%Y-%m-%dT%H:%M:%SZ)&end=$(date -u +%Y-%m-%dT%H:%M:%SZ)&samprate=60" \
  -H "Authorization: Bearer $FULCRA_ACCESS_TOKEN"
```

### Check today's calendar

```bash
curl -s "https://api.fulcradynamics.com/data/v0/{fulcra_userid}/calendar_events?start=$(date -u +%Y-%m-%dT00:00:00Z)&end=$(date -u +%Y-%m-%dT23:59:59Z)" \
  -H "Authorization: Bearer $FULCRA_ACCESS_TOKEN"
```

### Available metrics

```bash
curl -s "https://api.fulcradynamics.com/data/v0/metrics_catalog" \
  -H "Authorization: Bearer $FULCRA_ACCESS_TOKEN"
```

## Key Metrics

| Metric | What It Tells You |
|--------|-------------------|
| SleepStage | Sleep quality — REM, Deep, Light, Awake |
| HeartRate | Current stress/activity level |
| HRV | Recovery and autonomic nervous system state |
| StepCount | Activity level throughout the day |
| ActiveCaloriesBurned | Exercise intensity |
| RespiratoryRate | Baseline health indicator |
| BloodOxygen | Wellness check |

## Integration Patterns

### Morning Briefing
Check sleep + calendar + weather → compose a briefing calibrated to energy level.

### Stress-Aware Communication
Monitor HRV + heart rate → if elevated, keep messages brief and non-urgent.

### Proactive Recovery
After intense workout or poor sleep → suggest lighter schedule, remind about hydration.

### Travel Awareness
Location changes → adjust timezone handling, suggest local info, modify schedule expectations.

## Demo Mode vs Private Mode

When sharing publicly (Moltbook, X, etc.):
- ✅ OK to share: biometric trends, sleep quality, step counts, HRV (anonymized)
- ❌ NEVER share: real location, real calendar events, identifying data
- Use simulated location/calendar data for public demos

## Links

- [Fulcra Platform](https://fulcradynamics.com)
- [Developer Docs](https://fulcradynamics.github.io/developer-docs/)
- [Life API Reference](https://fulcradynamics.github.io/developer-docs/api-reference/)
- [Python Client](https://github.com/fulcradynamics/fulcra-api-python)
- [MCP Server](https://github.com/fulcradynamics/fulcra-context-mcp)
- [Demo Notebooks](https://github.com/fulcradynamics/demos)
- [Discord](https://discord.com/invite/aunahVEnPU)
