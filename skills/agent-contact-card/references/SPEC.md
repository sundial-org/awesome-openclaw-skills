# Agent Contact Card Specification

**Version:** 1.0-draft
**Status:** Draft

## Overview

An Agent Contact Card is a simple way to publish how AI agents acting on your behalf can be contacted. It uses a markdown file with YAML frontmatter, designed to be readable by both humans and machines - like a vCard, but for agents.

## File Format

An Agent Contact Card is a UTF-8 encoded markdown file with YAML frontmatter.

### Structure

```markdown
---
# YAML frontmatter (required)
version: "1"
# ... structured fields ...
---

# Markdown body (optional but recommended)
Human-readable description and routing rules.
```

### Frontmatter Fields

#### Required

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Spec version. Currently `"1"` |

#### Recommended

| Field | Type | Description |
|-------|------|-------------|
| `human_contact` | string | Phone/email for humans to reach the human (not the agent) |
| `channels` | object | Contact channels for agents (see below) |

#### Optional

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name for this agent configuration |
| `last_updated` | string | ISO date when this card was last modified (e.g., `"2026-01-30"`) |
| `agents` | array | Named agents if you have multiple (see Multi-Agent section) |
| `capabilities` | array | What this agent can do (e.g., `["scheduling", "accepts_ical"]`) |
| `public_key` | string | Public key for signed/encrypted communication |

### Channels Object

The `channels` field maps channel names to contact info:

```yaml
channels:
  discord: "username#1234"
  email: "agent@example.com"
  signal: "+1234567890"
  webhook: "https://example.com/agent/incoming"
```

Channel names are freeform. Common ones:
- `discord` - Discord username or bot ID
- `email` - Email address
- `signal` - Signal phone number
- `telegram` - Telegram username
- `slack` - Slack workspace/channel
- `webhook` - HTTP endpoint for structured messages
- `imessage` - iMessage-capable phone/email

For webhooks, you can provide more detail:

```yaml
channels:
  webhook:
    url: "https://example.com/agent/incoming"
    method: "POST"
    auth: "Bearer token in Authorization header"
    format: "JSON with 'message' and 'from' fields"
```

### Markdown Body

The body contains human-readable rules and context. Agents should read and interpret this as natural language instructions.

Good things to include:
- Which channel to use for what purpose
- Response time expectations
- What topics/requests are handled
- When to escalate to the human
- Any authentication or verification requirements

### Writing Effective Rules

Since agents interpret the prose as natural language, clarity matters. Write rules that are specific and actionable.

**Good - clear and actionable:**
```markdown
- For scheduling requests, use Discord. I can parse iCal attachments.
- For urgent matters, email with "URGENT" in the subject line.
- Response time: Discord within hours, email within 24h.
```

**Bad - ambiguous:**
```markdown
- Use whatever channel feels right.
- I prefer Discord but email is fine too I guess.
- I'll get back to you when I can.
```

## Discovery

### Well-Known URL

Agents SHOULD check for an Agent Contact Card at:

```
https://{domain}/.well-known/agent-card
```

For individual users within an organization:

```
https://{domain}/.well-known/agent-card/{username}
```

### vCard Extension

The `X-AGENT-CARD` field in a vCard points to an Agent Contact Card:

```
X-AGENT-CARD:https://example.com/.well-known/agent-card
```

### Discovery Priority

When trying to contact someone's agents:

1. Check for `X-AGENT-CARD` in their vCard (most specific)
2. Try `/.well-known/agent-card` on their domain
3. Ask the human for a URL

## Multi-Agent Configurations

If you have multiple specialized agents, list them:

```yaml
agents:
  - name: "Calendar Agent"
    handles: ["scheduling", "availability"]
    channel: discord
    id: "cal-agent#1234"
  - name: "General Agent"
    handles: ["everything else"]
    channel: email
    id: "agent@example.com"
```

The markdown body should explain routing between them.

## Security Considerations

### Authentication

For sensitive operations, agents may require verification. Document this in the markdown body:

```markdown
## Verification

For any request involving:
- Financial transactions
- Personal information
- Scheduling that affects others

I'll send a verification code to the human's phone before proceeding.
```

### Signed Messages

For webhook-based communication, you can specify a public key:

```yaml
public_key: |
  -----BEGIN PUBLIC KEY-----
  ...
  -----END PUBLIC KEY-----
```

And document the signature scheme in the body.

## Privacy Tiers

You can maintain multiple Agent Contact Cards at different URLs:

| Tier | URL Pattern | Discoverability |
|------|-------------|-----------------|
| Public | `/.well-known/agent-card` | Anyone can find it |
| Professional | `/.well-known/agent-card/{name}` | Discoverable if you know the name |
| Private | `/{random-uuid}/agent-card.md` | Only people you give the URL to |

Each tier can expose different channels, capabilities, and access levels.

## MIME Type

Agent Contact Cards SHOULD be served with:
- `text/markdown` (preferred)
- `text/plain` (acceptable)

## Example

See the [examples](examples/) directory for complete examples.

## Versioning

This spec uses semantic versioning. The `version` field in frontmatter indicates which spec version the file conforms to.

- `"1"` - Current version (this document)

Future versions will maintain backwards compatibility where possible.
