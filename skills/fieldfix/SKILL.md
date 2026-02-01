---
name: fieldfix
description: Query and manage your heavy equipment fleet through FieldFix's API. Track machines, log maintenance, monitor expenses, and get AI diagnostics.
version: 1.0.0
author: FieldFix <support@fieldfix.ai>
homepage: https://www.fieldfix.ai/api
---

# FieldFix Skill

Query and manage your heavy equipment fleet through FieldFix's Agent API.

## Setup

1. **Get your API key** from [FieldFix Settings](https://app.fieldfix.ai/settings/api)
2. **Set environment variable:**
   ```bash
   export FIELDFIX_API_KEY=ff_sk_live_your_key_here
   ```

## Pricing

API access is included with all paid plans:
- **$10/machine/month** (1-25 machines)
- **$7/machine/month** (26-100 machines)  
- **$5/machine/month** (100+ machines)
- **2 months free trial** — no credit card required

## Capabilities

### Read Operations

**List all machines:**
```bash
node scripts/fieldfix.js machines
```

**Get machine details:**
```bash
node scripts/fieldfix.js machine <id>
```

**Get machine expenses:**
```bash
node scripts/fieldfix.js expenses <id>
```

**Get service history:**
```bash
node scripts/fieldfix.js service <id>
```

**Get fleet alerts:**
```bash
node scripts/fieldfix.js alerts
```

### Write Operations

**Log a service entry:**
```bash
node scripts/fieldfix.js log-service <id> "Oil Change" 120 "Changed oil and filter"
```

**Log an expense:**
```bash
node scripts/fieldfix.js log-expense <id> fuel 250 "Filled tank"
```

**Update hour meter:**
```bash
node scripts/fieldfix.js update-hours <id> 1250
```

## Example Prompts

Once configured, try asking your agent:

- "What machines do I have in FieldFix?"
- "When is my CAT 299 due for service?"
- "How much have I spent on fuel this month?"
- "Log an oil change on the excavator for $120"
- "What's the total cost per hour for my skid steer?"

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/machines` | GET | List all machines |
| `/machines/{id}` | GET | Get machine details |
| `/machines/{id}/expenses` | GET | Get expense history |
| `/machines/{id}/service` | GET | Get service history |
| `/alerts` | GET | Get fleet alerts |
| `/machines/{id}/service` | POST | Log service entry |
| `/machines/{id}/expenses` | POST | Log expense |
| `/machines/{id}/hours` | POST | Update hours |

## Links

- [FieldFix App](https://app.fieldfix.ai)
- [API Documentation](https://www.fieldfix.ai/api)
- [MCP Server (Claude Desktop)](https://www.npmjs.com/package/fieldfix-mcp-server)
