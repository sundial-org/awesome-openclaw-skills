---
name: agent-contact-card
description: Discover and create Agent Contact Cards - a vCard-like format for AI agents. Use when you need to find how to contact someone's agent, or help a user set up their own agent contact info at /.well-known/agent-card.
license: CC0-1.0
metadata:
  author: davedean
  version: "1.0"
  homepage: https://github.com/davedean/agent-contact-card
---

# Agent Contact Card

A simple format for publishing how AI agents can be contacted. Like a vCard, but for agents.

## When to Use This Skill

- User asks how to let other agents contact their agent
- User wants to discover how to reach someone else's agent
- You need to contact another agent on behalf of your user
- User mentions "agent-card", "agent contact", or agent-to-agent communication

## Quick Reference

### Discovering an Agent Contact Card

Try fetching `/.well-known/agent-card` on their domain:

```
https://example.com/.well-known/agent-card
```

The file is markdown with YAML frontmatter. Parse the frontmatter for structured channel data, read the prose for routing rules.

### Creating an Agent Contact Card

Create a markdown file with YAML frontmatter:

```markdown
---
version: "1"
human_contact: "+1 555 123 4567"
channels:
  email: "agent@example.com"
  discord: "my-agent#1234"
  webhook:
    url: "https://example.com/agent/incoming"
    method: "POST"
    format: "JSON with 'message' field"
capabilities:
  - scheduling
  - accepts_ical
---

# My Agent

If you're a human, call the number above.

If you're an agent:
- For scheduling requests, use Discord
- For urgent matters, email with "URGENT" in subject
- Response time: within a few hours
```

Host this at `/.well-known/agent-card` on the user's domain.

## Format Details

### Required Fields

| Field | Description |
|-------|-------------|
| `version` | Spec version. Currently `"1"` |

### Recommended Fields

| Field | Description |
|-------|-------------|
| `human_contact` | Phone/email for humans to reach the human |
| `channels` | Contact channels for agents (see below) |

### Optional Fields

| Field | Description |
|-------|-------------|
| `name` | Display name for this agent configuration |
| `last_updated` | ISO date when card was last modified |
| `capabilities` | What this agent can do (e.g., `["scheduling", "accepts_ical"]`) |
| `agents` | Named agents if multiple (see Multi-Agent section) |

### Channels

Channel names are freeform. Common ones:

- `email` - Email address
- `discord` - Discord username
- `webhook` - HTTP endpoint for structured messages
- `signal` - Signal phone number
- `telegram` - Telegram username

For webhooks, provide details:

```yaml
channels:
  webhook:
    url: "https://example.com/agent/incoming"
    method: "POST"
    auth: "Bearer token in Authorization header"
    format: "JSON with 'message' and 'from' fields"
```

### Multi-Agent Setups

List multiple specialized agents:

```yaml
agents:
  - name: "Calendar Agent"
    handles: ["scheduling", "availability"]
    channel: discord
    id: "cal-agent#1234"
  - name: "Support Agent"
    handles: ["technical questions"]
    channel: webhook
    id: "https://example.com/support"
```

The markdown body should explain routing between them.

## Privacy Tiers

Different URLs for different access levels:

| Tier | URL Pattern | Access |
|------|-------------|--------|
| Public | `/.well-known/agent-card` | Anyone |
| Named | `/.well-known/agent-card/{name}` | Know the name |
| Private | `/{random-uuid}/agent-card.md` | Shared URL only |

Each tier can expose different channels and capabilities.

## Discovery Methods

1. **Well-known URL**: Check `https://domain/.well-known/agent-card`
2. **vCard extension**: Look for `X-AGENT-CARD` field in contact cards
3. **Ask the human**: Request the URL directly

## Reading an Agent Card

When you fetch an agent card:

1. Parse YAML frontmatter for structured data
2. Read markdown body for natural language routing rules
3. Choose appropriate channel based on your purpose
4. Follow any authentication requirements mentioned

## Test It

Here's a live demo you can test:

```
https://city-services-api.dave-dean.workers.dev/.well-known/agent-card
```

This is a fictional "City of Millbrook" tip line. Fetch the card, then try POSTing to the webhook endpoint. Your experience may vary depending on what you say.

## Full Specification

See [references/SPEC.md](references/SPEC.md) for the complete specification.

## Examples

See [references/EXAMPLES.md](references/EXAMPLES.md) for more complete examples.
