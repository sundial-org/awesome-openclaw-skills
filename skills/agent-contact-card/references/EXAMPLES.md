# Agent Contact Card Examples

## Minimal Example

The simplest possible agent contact card:

```markdown
---
version: "1"
channels:
  email: "agent@example.com"
---

# Contact My Agent

Email agent@example.com with your request.
```

## Personal Agent

A typical personal agent setup with multiple channels:

```markdown
---
version: "1"
name: "David's Agents"
human_contact: "+61 4xx xxx xxx"
last_updated: "2026-01-30"
channels:
  discord: "davids-agent#1234"
  email: "agent@david.example"
  signal: "+61 4xx xxx xxx"
capabilities:
  - scheduling
  - accepts_ical
  - task_management
---

# David's Agents

Hi! I'm the AI agent that helps David manage his life.

## If You're a Human

Just call the number above, or text it. David will get back to you.

## If You're an Agent

Here's how to reach me depending on what you need:

### Scheduling & Calendar
- **Use:** Discord
- I can accept iCal format for calendar invites
- Response time: Usually within a few hours

### Urgent Matters
- **Use:** Signal
- If it's genuinely urgent, say "urgent" and I'll notify David immediately

### General Requests
- **Use:** Email
- Response time: Within 24 hours

### What I'll Escalate to David
- Anything involving money or commitments
- Personal or sensitive topics
- Requests that seem unusual
```

## Organization with Multiple Agents

An organization with specialized agents for different functions:

```markdown
---
version: "1"
name: "Acme Corp Agents"
human_contact: "support@acme.example"
agents:
  - name: "Sales Agent"
    handles: ["sales inquiries", "pricing", "demos"]
    channel: email
    id: "sales-agent@acme.example"
  - name: "Support Agent"
    handles: ["technical support", "bug reports"]
    channel: webhook
    id: "https://acme.example/agent/support"
  - name: "Scheduling Agent"
    handles: ["meeting scheduling", "availability"]
    channel: email
    id: "calendar@acme.example"
channels:
  email: "agents@acme.example"
  webhook:
    url: "https://acme.example/agent/incoming"
    method: "POST"
    format: "JSON: {\"message\": \"...\", \"from\": \"...\"}"
capabilities:
  - scheduling
  - accepts_ical
  - support_tickets
---

# Acme Corp AI Agents

## For Humans

Email support@acme.example or call our main line.

## For Agents

### General Routing

Not sure which agent? Email agents@acme.example and we'll route appropriately.

### Sales Inquiries
- **Contact:** sales-agent@acme.example
- **Response time:** Same business day

### Technical Support
- **Contact:** POST to https://acme.example/agent/support
- **Response time:** Within 4 hours for urgent

### Scheduling
- **Contact:** calendar@acme.example
- **Accepts:** iCal format

## Webhook Format

```json
{
  "message": "Description of the issue",
  "from": "agent@customer.example",
  "type": "support|bug|account",
  "priority": "normal|urgent"
}
```

## Escalation

Our agents escalate to humans for:
- Contract negotiations
- Legal matters
- Anything involving PII
```

## Live Demo

Test with the City of Millbrook demo:

```
https://city-services-api.dave-dean.workers.dev/.well-known/agent-card
```

Fetch the card, read the channels, and try POSTing to the tip line webhook.
