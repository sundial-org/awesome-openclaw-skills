# Setup & Configuration

This document explains how to configure Preloop as an MCP server for your agent.

## MCP Server Endpoint

Preloop's MCP server is available at:
- **Production**: `https://preloop.ai/mcp/v1`
- **Self-hosted**: `https://your-preloop-instance.com/mcp/v1`
- **Local development**: `http://localhost:8000/mcp/v1`

## Configuration by Agent

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "preloop": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-everything"],
      "env": {
        "PRELOOP_URL": "https://preloop.ai/mcp/v1"
      }
    }
  }
}
```

Or if using HTTP transport directly:

```json
{
  "mcpServers": {
    "preloop": {
      "url": "https://preloop.ai/mcp/v1",
      "transport": "sse"
    }
  }
}
```

**File locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### Cline (VSCode Extension)

Add to your Cline settings:

```json
{
  "mcpServers": {
    "preloop": {
      "url": "https://preloop.ai/mcp/v1",
      "transport": "sse"
    }
  }
}
```

### Other Agents

For agents that support MCP servers, configure:
- **URL**: `https://preloop.ai/mcp/v1` (or your instance URL)
- **Transport**: SSE (Server-Sent Events) or HTTP
- **Authentication**: Include your Preloop API token in headers if required

## Verifying Connection

Once configured, restart your agent and verify:
1. The `request_approval` tool appears in the available tools list
2. Test with a simple approval request
3. Check that notifications are being sent (Slack, email, etc.)

## Approval Policy Setup

Before using the skill, you need an approval policy configured in Preloop:

1. Log in to your Preloop instance
2. Navigate to **Settings** → **Approval Policies**
3. Create a new policy:
   - **Name**: e.g., "Default Agent Approval"
   - **Notification Method**: Slack, email, mobile app, or webhook
   - **Approvers**: Select users or teams who can approve
   - **Timeout**: Default is 5 minutes
   - **Set as Default**: Enable this for automatic use
4. Save the policy

Without an approval policy, the `request_approval` tool will return an error.

## Authentication

If your Preloop instance requires authentication:

1. Generate an API token in Preloop (Settings → API Tokens)
2. Add to your MCP server configuration:
   ```json
   {
     "mcpServers": {
       "preloop": {
         "url": "https://your-instance.com/mcp/v1",
         "transport": "sse",
         "headers": {
           "Authorization": "Bearer YOUR_API_TOKEN"
         }
       }
     }
   }
   ```

## Troubleshooting

### Connection Issues

**Problem**: "Tool not found" or "MCP server not responding"

**Solutions**:
- Verify the URL is correct (check for typos)
- Ensure the Preloop instance is running and accessible
- Check network/firewall settings
- Restart your agent after configuration changes

### Authentication Issues

**Problem**: "Unauthorized" or "403 Forbidden"

**Solutions**:
- Verify your API token is valid and not expired
- Check that the token has the correct permissions
- Ensure the token is included in the headers correctly

### No Approval Policy

**Problem**: "No default approval policy found"

**Solution**: Create and configure an approval policy as described above.

## Advanced Configuration

### Multiple Preloop Instances

You can configure multiple Preloop instances:

```json
{
  "mcpServers": {
    "preloop-prod": {
      "url": "https://prod.preloop.ai/mcp/v1",
      "transport": "sse"
    },
    "preloop-dev": {
      "url": "https://dev.preloop.ai/mcp/v1",
      "transport": "sse"
    }
  }
}
```

### Custom Timeout

To override the default timeout:

```json
{
  "mcpServers": {
    "preloop": {
      "url": "https://preloop.ai/mcp/v1",
      "transport": "sse",
      "timeout": 600000
    }
  }
}
```

(Timeout in milliseconds; 600000 = 10 minutes)

## Support

For setup assistance:
- Documentation: https://docs.preloop.ai
- Community: https://community.preloop.ai
- Issues: https://github.com/preloop/preloop/issues
