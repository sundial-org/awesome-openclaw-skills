# Lobster Workflows

This directory contains [Lobster](https://github.com/openclaw/lobster) workflow definitions for the finance-news skill.

## Available Workflows

### `briefing.yaml` - Market Briefing with Approval

Generates a market briefing and sends to WhatsApp with an approval gate.

**Usage:**
```bash
# Run via Lobster CLI
lobster "workflows.run --file ~/projects/finance-news-openclaw-skill/workflows/briefing.yaml"

# With custom args
lobster "workflows.run --file workflows/briefing.yaml --args-json '{\"time\":\"evening\",\"lang\":\"en\"}'"
```

**Arguments:**
| Arg | Default | Description |
|-----|---------|-------------|
| `time` | `morning` | Briefing type: `morning` or `evening` |
| `lang` | `de` | Language: `en` or `de` |
| `channel` | `whatsapp` | Delivery channel: `whatsapp` or `telegram` |
| `target` | env var | Group name, JID, phone number, or Telegram chat ID |
| `fast` | `false` | Use fast mode (shorter timeouts) |

**Environment Variables:**
| Variable | Description |
|----------|-------------|
| `FINANCE_NEWS_CHANNEL` | Default channel: `whatsapp` or `telegram` |
| `FINANCE_NEWS_TARGET` | Default target (group name, phone, chat ID) |

**Examples:**
```bash
# WhatsApp group (default)
lobster "workflows.run --file workflows/briefing.yaml"

# Telegram group
lobster "workflows.run --file workflows/briefing.yaml --args-json '{\"channel\":\"telegram\",\"target\":\"-1001234567890\"}'"

# WhatsApp DM to phone number
lobster "workflows.run --file workflows/briefing.yaml --args-json '{\"target\":\"+15551234567\"}'"

# Telegram DM to user
lobster "workflows.run --file workflows/briefing.yaml --args-json '{\"channel\":\"telegram\",\"target\":\"@username\"}'"
```

**Flow:**
1. **Generate** - Runs Docker container to produce briefing JSON
2. **Approve** - Halts for human review (shows briefing preview)
3. **Send** - Delivers to channel (WhatsApp/Telegram) after approval

**Requirements:**
- Docker with `finance-news-briefing` image built
- `jq` for JSON parsing
- `openclaw` CLI for message delivery

## Adding to Lobster Registry

To make these workflows available as named workflows in Lobster:

```typescript
// In lobster/src/workflows/registry.ts
export const workflowRegistry = {
  // ... existing workflows
  'finance.briefing': {
    name: 'finance.briefing',
    description: 'Generate market briefing with approval gate for WhatsApp/Telegram',
    argsSchema: {
      type: 'object',
      properties: {
        time: { type: 'string', enum: ['morning', 'evening'], default: 'morning' },
        lang: { type: 'string', enum: ['en', 'de'], default: 'de' },
        channel: { type: 'string', enum: ['whatsapp', 'telegram'], default: 'whatsapp' },
        target: { type: 'string', description: 'Group name, JID, phone, or chat ID' },
        fast: { type: 'boolean', default: false },
      },
    },
    examples: [
      { args: { time: 'morning', lang: 'de' }, description: 'German morning briefing to WhatsApp' },
      { args: { channel: 'telegram', target: '-1001234567890' }, description: 'Send to Telegram group' },
    ],
    sideEffects: ['message.send'],
  },
};
```

## Why Lobster?

Using Lobster instead of direct cron execution provides:

- **Approval gates** - Review briefing before it's sent
- **Resumability** - If interrupted, continue from last step
- **Token efficiency** - One workflow call vs. multiple LLM tool calls
- **Determinism** - Same inputs = same outputs
