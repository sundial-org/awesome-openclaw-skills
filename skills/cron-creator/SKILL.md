---
name: cron-creator
description: "Create Clawdbot cron jobs from natural language. Use when: users want to schedule recurring messages, reminders, or check-ins without using terminal commands. Examples: 'Create a daily reminder at 8am', 'Set up a weekly check-in on Mondays', 'Remind me to drink water every 2 hours'."
---

# Cron Creator

Create Clawdbot cron jobs automatically from natural language requests.

## Quick Install (One Command)

Run this in your terminal:

```bash
bash -c "$(curl -sL https://raw.githubusercontent.com/digitaladaption/cron-creator/main/install.sh)"
```

Or manually:

```bash
# Install skill
mkdir -p ~/.clawdbot/skills
git clone https://github.com/digitaladaption/cron-creator.git ~/.clawdbot/skills/cron-creator

# Configure and restart
clawdbot gateway restart
```

That's it! Then just say things like:

- "Create a daily Ikigai reminder at 8:45am"
- "Remind me to drink water every 2 hours"
- "Set up a weekly check-in on Mondays at 9am"

## What It Does

1. **Hears** your request to create a cron job
2. **Parses** time, frequency, channel, and message
3. **Creates** the cron job automatically
4. **Confirms** it's done

## Trigger Patterns

Say things like:
- "Create a cron job for..."
- "Set up a reminder..."
- "Schedule a..."
- "Remind me to..."
- "Create a daily/weekly check-in..."
- "Add a recurring..."

## Examples

| You Say | What Happens |
|---------|-------------|
| "Create a daily Ikigai reminder at 8:45am" | Creates daily 8:45am Ikigai journal prompt |
| "Remind me to drink water every 2 hours" | Creates hourly water reminder |
| "Set up a weekly check-in on Mondays at 9am" | Creates Monday 9am weekly review |
| "Wake me at 7am every day" | Creates daily 7am alarm/reminder |
| "Send me a quote every morning at 6:30" | Creates daily quote at 6:30am |

## Supported Time Formats

| You Say | Cron |
|---------|------|
| "8am" | `0 8 * * *` |
| "8:45am" | `45 8 * * *` |
| "9pm" | `0 21 * * *` |
| "noon" | `0 12 * * *` |
| "midnight" | `0 0 * * *` |

## Supported Frequencies

| You Say | Cron |
|---------|------|
| "daily" / "every day" | Daily at specified time |
| "weekdays" | Mon-Fri at specified time |
| "mondays" / "every monday" | Weekly on Monday |
| "hourly" / "every hour" | Every hour at :00 |
| "every 2 hours" | `0 */2 * * *` |
| "weekly" | Weekly (defaults to Monday) |
| "monthly" | Monthly (1st of month) |

## Channels

Just mention the channel in your request:
- "on WhatsApp" → WhatsApp
- "on Telegram" → Telegram
- "on Slack" → Slack
- "on Discord" → Discord

Default: WhatsApp

## Default Messages

The skill auto-generates appropriate messages:

| Type | Default Message |
|------|-----------------|
| Ikigai | Morning journal with purpose, food, movement, connection, gratitude |
| Water | "💧 Time to drink water! Stay hydrated! 🚰" |
| Morning | "🌅 Good morning! Time for your daily check-in." |
| Evening | "🌙 Evening check-in! How was your day?" |
| Weekly | Weekly goals review |
| Default | "⏰ Your scheduled reminder is here!" |

## How It Works

1. **Install** the skill (see Quick Install above)
2. **Chat** naturally: "Create a daily reminder at 8am"
3. **Done!** The cron job is created automatically

## For Developers

### Files
- `SKILL.md` - This documentation
- `scripts/cron_creator.py` - Natural language parser
- `install.sh` - Automatic installer script

### The Parser
The `cron_creator.py` script:
- Extracts time, frequency, channel, destination from natural language
- Generates appropriate `clawdbot cron add` command
- Returns JSON with parsed fields and command

### Manual Testing
```bash
# Test the parser
python3 scripts/cron_creator.py "Create a daily reminder at 8:45am"

# Output includes:
# - parsed time, frequency, channel
# - generated cron expression
# - full clawdbot cron add command
```

### Configuration
The install script automatically configures:
- Clawdbot tools.exec.host=gateway (allows running clawdbot commands)
- Skill files in ~/.clawdbot/skills/cron-creator
- Gateway restart to apply changes

### Troubleshooting

**Skill not loading?**
```bash
clawdbot skills list | grep cron
```

**Cron not created?**
```bash
# Check clawdbot is running
clawdbot status

# Check cron jobs
clawdbot cron list
```

**Need to reinstall?**
```bash
# Run install again
bash -c "$(curl -sL https://raw.githubusercontent.com/digitaladaption/cron-creator/main/install.sh)"
```

## GitHub

https://github.com/digitaladaption/cron-creator

Report issues or contribute there!
