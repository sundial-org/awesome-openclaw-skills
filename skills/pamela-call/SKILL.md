---
name: pamela-call
description: Make AI-powered phone calls with Pamela's voice API. Create outbound calls, register custom tools for mid-call actions, handle webhooks, and build React UIs. Use when the user wants to make phone calls, integrate voice AI, build IVR systems, navigate phone menus, or automate phone tasks.
---

# Pamela Voice API Skill

Make AI-powered phone calls with native phone tree navigation. **[ThisIsPamela](https://thisispamela.com)** is an enterprise voice AI platform that handles outbound calls, navigates phone trees, and integrates with your apps via SDKs, webhooks, and MCP.

**Jump to:** [Installation](#installation) · [Quick Start](#quick-start) · [Use Cases](#use-cases) · [SDK Reference](#sdk-reference)

## Prerequisites

- Enterprise subscription (required for API access)
- API key from your Enterprise account
- Node.js 18+ (for JS/React) or Python 3.8+ (for Python)

## Installation

**JavaScript/TypeScript:**
```bash
npm install @thisispamela/sdk
```

**Python:**
```bash
pip install thisispamela
```

**React:**
```bash
npm install @thisispamela/react @thisispamela/sdk
```

**CLI:**
```bash
npm install -g @thisispamela/cli
```

**MCP (for MCP-based agents):**
```bash
npm install @thisispamela/mcp
```

**Widget (embeddable, no framework):**
```bash
npm install @thisispamela/widget
```

Latest versions: SDK / CLI / Widget / MCP / Python `1.1.2`, React `1.1.3`.

## Getting Your API Key

1. Sign up for an Enterprise subscription at [app.thisispamela.com](https://app.thisispamela.com)
2. Navigate to Settings → Enterprise Access
3. Set up billing through Stripe
4. Click "Create API Key"
5. Save immediately - the full key (starts with `pk_live_`) is only shown once

## Quick Start

**Note:** Phone numbers must be in E.164 format (e.g., `+1234567890`).

### JavaScript

```typescript
import { PamelaClient } from '@thisispamela/sdk';

const client = new PamelaClient({ apiKey: 'pk_live_...' });

const call = await client.createCall({
  to: '+1234567890',
  task: 'Call the pharmacy and check if my prescription is ready',
  voice: 'female',
  agent_name: 'Pamela',
});

const status = await client.getCall(call.id);
console.log(status.transcript);
```

### Python

```python
from pamela import PamelaClient

client = PamelaClient(api_key="pk_live_...")

call = client.create_call(
    to="+1234567890",
    task="Call the pharmacy and check if my prescription is ready",
    voice="female",
    agent_name="Pamela",
)

status = client.get_call(call["id"])
print(status["transcript"])
```

### CLI

```bash
export PAMELA_API_KEY="pk_live_..."

thisispamela create-call \
  --to "+1234567890" \
  --task "Call the pharmacy and check if my prescription is ready"
```

## Use Cases

| Use Case | Example Task |
|----------|--------------|
| Appointment Scheduling | "Call the dentist and schedule a cleaning for next week" |
| Order Status | "Call the pharmacy and check if my prescription is ready" |
| Customer Support | "Navigate the IVR menu to reach billing department" |
| Information Gathering | "Call the restaurant and ask about vegetarian options" |
| Follow-ups | "Call to confirm the appointment for tomorrow at 2pm" |
| IVR Navigation | "Navigate the phone menu to reach a human representative" |

## Key Features

- **Phone tree navigation** - Automatically navigates IVR menus, handles holds and transfers
- **Custom tools** - Register tools the AI can call mid-conversation
- **Real-time transcripts** - Webhook updates as the call progresses
- **React components** - Pre-built UI for call status and transcripts

## SDK Reference

For detailed SDK documentation:

- **[JavaScript SDK](https://docs.thisispamela.com/sdk/javascript)** - Full JS/TS reference
- **[Python SDK](https://docs.thisispamela.com/sdk/python)** - Full Python reference
- **[React Components](https://docs.thisispamela.com/sdk/react)** - Component library (v1.1.3)
- **[Widget](https://docs.thisispamela.com/sdk/widget)** - Embeddable widget for any website
- **[MCP Server](https://docs.thisispamela.com/sdk/mcp)** - MCP tools for AI assistants
- **[CLI](https://docs.thisispamela.com/sdk/cli)** - Command-line reference

## Webhooks

Pamela sends webhooks for call lifecycle events:

- `call.queued` - Call created and queued
- `call.started` - Call connected
- `call.completed` - Call finished successfully
- `call.failed` - Call failed
- `call.transcript_update` - New transcript entries

Verify webhook signatures with the `X-Pamela-Signature` header.

## Billing

- **$0.10/minute** for API usage
- **Minimum 1 minute** per call
- **Only connected calls** are billed
- Enterprise subscription required

## Troubleshooting

**"Invalid API key"**
- Verify key starts with `pk_live_`
- Check key is active in Enterprise panel

**"403 Forbidden"**
- Enterprise subscription required
- Check subscription status at app.thisispamela.com

**"Invalid phone number"**
- Use E.164 format with country code: `+1234567890`

## Resources

- **Website:** https://thisispamela.com
- **Docs:** https://docs.thisispamela.com
- **Demo:** https://demo.thisispamela.com
- **API:** https://api.thisispamela.com
- **Discord (live support):** https://discord.gg/cJj5CK8V
- **Email:** support@thisispamela.com
