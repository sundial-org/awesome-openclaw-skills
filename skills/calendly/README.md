# Calendly Moltbot Skill

Moltbot skill for Calendly integration. List events, check availability, manage meetings via the Calendly API.

## Features

- **User Info**: Get authenticated user details
- **Event Management**: List, view, and cancel scheduled events
- **Invitee Management**: View event invitees
- **Organization**: List organization memberships

> **Note:** Scheduling API features (list-event-types, get-event-type-availability, schedule-event) are available in calendly-mcp-server v2.0.0, which is currently unreleased. This skill uses v1.0.0 from npm for portability. See [Upgrade to v2.0](#upgrade-to-v20) for instructions once published.

## Installation

```bash
# Clone the repo
git clone https://github.com/kesslerio/calendly-moltbot-skill.git
cd calendly-moltbot-skill

# The CLI is self-contained (generated via mcporter from MCP server)
chmod +x calendly
```

## Configuration

Add your Calendly Personal Access Token to your environment:

```bash
export CALENDLY_API_KEY="your-pat-token"
```

Get your token from: https://calendly.com/integrations/api_webhooks

## Usage

### Get Your Profile

```bash
./calendly get-current-user
```

### List Events

```bash
./calendly list-events --user-uri "<YOUR_USER_URI>"
```

### Get Event Details

```bash
./calendly get-event --event-uuid "<EVENT_UUID>"
```

### Cancel Event

```bash
./calendly cancel-event --event-uuid "<EVENT_UUID>" --reason "Rescheduling needed"
```

## Available Commands

### Event Management
- `get-current-user` - Get authenticated user details
- `list-events` - List scheduled events
- `get-event` - Get event details
- `cancel-event` - Cancel an event
- `list-event-invitees` - List invitees for an event
- `list-organization-memberships` - List organization memberships

### OAuth
- `get-oauth-url` - Generate OAuth authorization URL
- `exchange-code-for-tokens` - Exchange authorization code for tokens
- `refresh-access-token` - Refresh access token

## Integration with Moltbot

Add to your Moltbot skills configuration:

```bash
# Copy or symlink to your Moltbot skills directory
ln -s $(pwd) /path/to/your/moltbot/skills/calendly

# Or add to your moltbot.json config:
{
  "skills": [
    {
      "name": "calendly",
      "path": "/path/to/calendly-moltbot-skill"
    }
  ]
}
```

Then use in conversations:
- "What meetings do I have?"
- "Cancel my 2pm meeting"
- "Who's attending my next call?"

## Upgrade to v2.0

Once calendly-mcp-server v2.0.0 is published to npm (adds Scheduling API with event types, availability, and programmatic scheduling), regenerate the CLI:

```bash
# Update to v2.0+
MCPORTER_CONFIG=./mcporter.json npx mcporter@latest generate-cli --server calendly --output calendly

# Verify new commands appear
./calendly --help | grep -E "list-event-types|get-event-type-availability|schedule-event"
```

The v2.0 Scheduling API will add:
- `list-event-types` - List available event types for scheduling
- `get-event-type-availability` - Get available time slots
- `schedule-event` - Schedule meetings programmatically

**Requires:** Paid Calendly plan (Standard or higher)

## Development

This skill wraps the [calendly-mcp-server](https://github.com/meAmitPatil/calendly-mcp-server) MCP server via [mcporter](https://github.com/steipete/mcporter).

To regenerate the CLI (if the upstream MCP server updates):

```bash
# Uses mcporter.json config (not tracked in git)
cat > mcporter.json <<EOF
{
  "mcpServers": {
    "calendly": {
      "command": "npx",
      "args": ["-y", "calendly-mcp-server"],
      "env": {
        "CALENDLY_API_KEY": "\${CALENDLY_API_KEY}"
      }
    }
  }
}
EOF

# Generate CLI
MCPORTER_CONFIG=./mcporter.json npx mcporter@latest generate-cli --server calendly --output calendly
```

## License

MIT

## Credits

- MCP Server: [meAmitPatil/calendly-mcp-server](https://github.com/meAmitPatil/calendly-mcp-server)
- CLI Generator: [mcporter](https://github.com/steipete/mcporter)
- Moltbot: [moltbot.io](https://moltbot.io)
