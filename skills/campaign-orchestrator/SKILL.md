---
name: campaign-orchestrator
description: Multi-channel follow-up campaign orchestrator for ShapeScale sales. Schedules and executes SMS + Email sequences with CRM logging and auto-termination on replies. Use when following up with demo leads or managing outreach campaigns.
homepage: https://github.com/kesslerio/shapescale-moltbot-skills
metadata: {"moltbot":{"emoji":"📋","requires":{"env":["DIALPAD_API_KEY","ATTIO_API_KEY","GOG_KEYRING_PASSWORD"]},"primaryEnv":"DIALPAD_API_KEY"}}
---

# Campaign Orchestrator Skill

Multi-channel follow-up campaign orchestrator for ShapeScale sales. Executes scheduled SMS + Email sequences with CRM integration and auto-termination on replies.

## Overview

A **Campaign** is a defined sequence of steps (SMS/Email) that executes over time. When a lead replies to any message, the campaign automatically terminates.

### Key Features

- **Multi-channel**: SMS (Dialpad) + Email (Gmail)
- **Scheduled**: Cron-based execution with configurable delays
- **Personalized**: Templates filled from Attio CRM data
- **Auto-terminating**: Replies stop all future scheduled steps
- **Logged**: All activities recorded in Attio

## Setup

**Environment variables required:**
```bash
DIALPAD_API_KEY=your_dialpad_api_key
ATTIO_API_KEY=your_attio_api_key
GOG_KEYRING_PASSWORD=your_google_password  # For Gmail access
```

**Also ensure:**
- Dialpad webhook is configured to hit this server
- Attio has company/contact records for leads
- Gmail API access enabled for sales email

## Usage

### Start a Campaign

```bash
# Start primary follow-up campaign for a lead
python3 campaign.py start "primary" --lead "Apex Fitness"

# Start with custom delay override (hours)
python3 campaign.py start "primary" --lead "Apex Fitness" --delay 2

# Start with Attio deal/company ID
python3 campaign.py start "post-demo" --lead "Apex Fitness" --attio-id "deal-uuid"
```

### Pre-Campaign Checklist (MANDATORY)

Before starting ANY campaign, verify:

1. **Customer Status Check**
   - Search memory/CRM for "already a customer" or "purchased" flags
   - Check exclusion list in campaigns.json
   - Verify email domain not in customer database

2. **Email Formatting Check** (for email steps)
   - Preview template renders as proper paragraphs
   - 2-4 sentences per paragraph, blank line between
   - No single-sentence orphan paragraphs
   - No hard line breaks mid-paragraph

3. **Tone Check**
   - No apologetic language ("no worries", "sorry to bother")
   - No easy outs ("if not relevant, no problem")
   - Professional, not needy

**NEVER campaign to existing customers unless explicitly requested for upsell.**

### Check Campaign Status

```bash
# Status for specific lead
python3 campaign.py status "Apex Fitness"

# All active campaigns
python3 campaign.py list
```

### Stop a Campaign

```bash
# Manual termination (lead replied, not interested, etc.)
python3 campaign.py stop "Apex Fitness" --reason "replied_interested"
```

### Remove a Lead

```bash
# Remove lead from campaigns (opted out, not interested)
python3 campaign.py remove "Apex Fitness"
```

### Check for Responses

```bash
# Check if lead has responded to any prior messages
python3 campaign.py check "Apex Fitness"
# Shows response status for each completed step
# Warns if responses detected (safe to proceed or terminate)
```

### View Pending Steps

```bash
# Show all pending campaign steps sorted by time
python3 campaign.py pending
# Useful for seeing what's due soon across all campaigns
```

### Template Management

```bash
# List available templates
python3 campaign.py templates

# Preview a template
python3 campaign.py preview "primary"
```

## Campaign Templates

| Template | Timing | Channel | Purpose |
|----------|--------|---------|---------|
| `primary` | +4 hours | SMS | Recap demo, share recording |
| `secondary` | +1 day | Email | Pricing, detailed ROI |
| `tertiary` | +4 days | SMS | Quick check-in |
| `quaternary` | +7 days | Email | Final follow-up, case study |
| `post-demo` | +0 hours | SMS | Immediate thank you |

### Template Variables

Templates support variable substitution:

```
{name}      - Lead first name
{company}   - Company name
{deal_value} - Deal value from Attio
{owner}     - Sales owner name
{demo_notes} - Notes from demo conversation
{checkout_link} - Personalized checkout URL
```

## Architecture

```
campaign-orchestrator/
├── SKILL.md              # This file
├── campaign.py           # Main CLI (start, stop, status, list)
├── webhook_handler.py    # Processes reply → termination
├── primary.md            # SMS follow-up template
├── secondary.md          # Email template
├── post-demo.md          # Immediate follow-up template
└── state/
    └── campaigns.json    # Campaign state persistence
```

## State Management

Campaign state is stored in `<workspace>/state/campaigns.json`:

```json
{
  "campaigns": {
    "Apex Fitness": {
      "template": "primary",
      "attio_id": "deal-uuid",
      "started": "2026-01-27T13:00:00Z",
      "steps_completed": ["sms_primary"],
      "next_step": "email_secondary",
      "next_scheduled": "2026-01-28T13:00:00Z",
      "status": "active"
    }
  },
  "templates": {
    "primary": {...},
    "secondary": {...}
  }
}
```

## Cron Integration

Campaign steps are executed via Clawdbot's cron system:

- **Executor job**: Runs every 5 minutes to check for due steps
- **Per-campaign jobs**: Created for each scheduled step

The scheduler script creates and manages these jobs automatically.

## Webhook Handling

When Dialpad receives a reply to a campaign message:

1. Dialpad sends webhook to server
2. `webhook_handler.py` parses the reply
3. Looks up which campaign the original message belonged to
4. Marks campaign as terminated
5. Logs the reply to Attio

## Integration Points

### Dialpad SMS
```bash
python3 /home/art/niemand/skills/dialpad/send_sms.py --to "+14155551234" --message "..."
```

### Gmail (via gog)
```bash
gog-shapescale --account martin@shapescale.com send-email --to "lead@company.com" --subject "..." --body "..."
```

### Attio CRM
```bash
attio note companies "company-uuid" "Campaign message sent: {message}"
```

## Examples

### Full Campaign Workflow

```bash
# 1. After demo, start campaign
/campaign start "post-demo" --lead "Dr. Smith's Clinic"

# 2. Check status next day
/campaign status "Dr. Smith's Clinic"
# Output: Step 1 sent, Step 2 scheduled for tomorrow

# 3. Lead replies "interested"
# Webhook automatically terminates campaign
# Logs reply to Attio

# 4. Manual follow-up if needed
/campaign start "secondary" --lead "Dr. Smith's Clinic" --delay 0
```

### Monitoring Active Campaigns

```bash
# List all active
/campaign list

# Output:
# Active Campaigns:
# - Apex Fitness (primary) - Step 2/4, next: email
# - Dr. Smith's Clinic (post-demo) - Complete
# - Wellness Center (tertiary) - Step 1/3, next: sms
```

## Troubleshooting

**Campaign not sending:**
- Check `cron` is running: `crontab -l`
- Check logs: `journalctl -u moltbot` or campaign logs
- Verify API keys: `echo $DIALPAD_API_KEY`

**Webhook not terminating:**
- Verify Dialpad webhook URL is configured
- Check webhook handler is running
- Check `campaigns.json` for matching lead

**Template variables not filling:**
- Verify lead exists in Attio with required fields
- Check template syntax: `{variable}` not `{ variable }`

## License

Part of shapescale-moltbot-skills. See parent repository.
