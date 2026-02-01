# Fulcra Context — Personal Data for AI Agents

Give your AI agent situational awareness. With your consent, access your biometrics, sleep, activity, location, and calendar data from the [Fulcra Life API](https://fulcradynamics.github.io/developer-docs/).

## What Is This?

An [OpenClaw](https://openclaw.ai) skill that connects AI agents to the [Fulcra](https://fulcradynamics.com) personal data platform. Your agent can:

- **Know how you slept** → adjust morning briefing tone and intensity
- **See heart rate / HRV trends** → detect stress, suggest breaks
- **Check your location** → context-aware suggestions (home vs. office vs. traveling)
- **Read your calendar** → proactive meeting prep, schedule awareness
- **Track workouts** → recovery-aware task scheduling

## Why Fulcra?

Most AI agents meet their user for the first time — **every time**. They have no memory of your health, no awareness of your schedule, no sense of how you're actually doing.

Fulcra fixes that. It aggregates data from Apple Health, wearables, calendars, and manual annotations into a single, normalized API. Your agent gets clean, consistent data regardless of what devices you use.

### Privacy-First by Design

- **OAuth2 per-user** — you control exactly what your agent sees
- **Consent is revocable** — disconnect anytime
- **No data monetization** — Fulcra is a paid service, not an ad platform. Your data is never sold.
- **Encryption at rest** — GDPR/CCPA compliant

This matters. When you give an AI agent access to your heart rate, sleep patterns, and calendar, you need to trust the platform holding that data. Fulcra's business model is structurally aligned with your privacy — they make money by serving you, not by selling your information.

## Quick Start

### Option 1: MCP Server (Any AI client)

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

Works with Claude Desktop, Goose, Windsurf, VS Code, and more.

### Option 2: OpenClaw Skill

```bash
clawdhub install fulcra-context
```

Or manually: copy `SKILL.md` to your OpenClaw workspace's `skills/fulcra-context/` directory.

### Option 3: Direct API

```bash
pip install fulcra-api
```

```python
from fulcra_api.core import FulcraAPI
api = FulcraAPI()
api.authorize()  # Opens browser for OAuth2 consent

# Get last night's sleep
import datetime
end = datetime.datetime.now(datetime.timezone.utc)
start = end - datetime.timedelta(hours=24)
sleep = api.time_series_grouped(
    start_time=start, end_time=end,
    metrics=["SleepStage"], sample_rate=300
)
```

## Available Data

| Data Type | Examples | Use Cases |
|-----------|----------|-----------|
| **Sleep** | Stages (REM, Deep, Light), duration, quality | Morning briefings, energy-aware scheduling |
| **Heart Rate** | BPM, resting rate, trends | Stress detection, workout recovery |
| **HRV** | Heart rate variability | Autonomic nervous system state, recovery |
| **Activity** | Steps, calories, exercise time | Activity-aware recommendations |
| **Calendar** | Events, times, locations | Proactive scheduling, meeting prep |
| **Location** | GPS coordinates, visits | Context-aware suggestions, travel detection |
| **Workouts** | Type, duration, intensity | Recovery scheduling |
| **Custom** | Manual annotations, moods, symptoms | Personalized context |

## Integration Patterns

### 🌅 Context-Aware Morning Briefing
Check sleep quality + today's calendar + weather → compose a briefing calibrated to actual energy level. Poor sleep? Lighter tone, fewer tasks. Great sleep? Full agenda.

### 💆 Stress-Aware Communication
Monitor HRV + heart rate → if stress indicators are elevated, keep messages brief and avoid adding non-urgent tasks.

### 🏃 Recovery-Aware Scheduling
After intense workout or poor sleep → suggest lighter schedule, remind about hydration, reschedule demanding work.

### ✈️ Travel Awareness
Detect location changes → adjust timezone handling, suggest local info, modify schedule expectations.

## Security

**Read [SECURITY.md](SECURITY.md) before deploying.** This skill accesses sensitive personal data. Key risks include token exposure, calendar/location leakage, and prompt injection attacks. The security guide covers mitigations for each.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | OpenClaw skill definition (API reference, quick commands) |
| `SECURITY.md` | Security & privacy guide (risks, mitigations, best practices) |
| `README.md` | This file |

## Links

- [Fulcra Platform](https://fulcradynamics.com)
- [Developer Docs](https://fulcradynamics.github.io/developer-docs/)
- [Life API Reference](https://fulcradynamics.github.io/developer-docs/api-reference/)
- [Python Client](https://github.com/fulcradynamics/fulcra-api-python)
- [MCP Server (open source)](https://github.com/fulcradynamics/fulcra-context-mcp)
- [Demo Notebooks](https://github.com/fulcradynamics/demos)
- [Fulcra Discord](https://discord.com/invite/aunahVEnPU)
- [OpenClaw](https://openclaw.ai) · [ClawdHub](https://www.clawhub.ai)

## License

MIT
