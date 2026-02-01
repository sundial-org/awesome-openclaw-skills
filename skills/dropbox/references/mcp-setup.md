# Dropbox MCP Setup Guide

The `dbx-mcp-server` enables AI agents to interact with your Dropbox account directly.

## Configuration

Add the following to your MCP configuration (e.g., `claude_desktop_config.json` or your agent's config):

```json
{
  "mcpServers": {
    "dropbox": {
      "command": "npx",
      "args": ["-y", "dbx-mcp-server"],
      "env": {
        "DROPBOX_APP_KEY": "YOUR_APP_KEY",
        "DROPBOX_APP_SECRET": "YOUR_APP_SECRET",
        "DROPBOX_REFRESH_TOKEN": "YOUR_REFRESH_TOKEN"
      }
    }
  }
}
```

## Permissions Needed

Ensure your Dropbox App has the following scopes:
- `files.metadata.read`
- `files.metadata.write`
- `files.content.read`
- `files.content.write`
- `files.browser.read`

## Troubleshooting

- **Token Expired**: Ensure you are using a *refresh* token, not a short-lived access token.
- **Permission Denied**: Check the scopes in the Dropbox App Console.
