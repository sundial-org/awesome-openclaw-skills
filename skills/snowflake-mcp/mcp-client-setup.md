# MCP Client Setup Reference

Use this guide to connect Clawdbot to the Snowflake MCP server.

## Method 1: Managed Snowflake MCP Server (Recommended)

Uses Snowflake's cloud-hosted MCP server. No local installation required.

### Clawdbot Configuration

Create `mcp.json` at your project root:

```json
{
  "mcpServers": {
    "Snowflake MCP Server": {
      "url": "https://YOUR-ORG-YOUR-ACCOUNT.snowflakecomputing.com/api/v2/databases/YOUR_DB/schemas/YOUR_SCHEMA/mcp-servers/YOUR_MCP_SERVER",
      "headers": {
        "Authorization": "Bearer YOUR-PAT-TOKEN"
      }
    }
  }
}
```

Start a new Clawdbot session and add `mcp.json` as context (or configure MCP servers in Clawdbot settings if available).

### URL Format

```
https://{org}-{account}.snowflakecomputing.com/api/v2/databases/{database}/schemas/{schema}/mcp-servers/{mcp_server_name}
```

### Getting Your Values

| Value | Where to Find |
|-------|---------------|
| `org-account` | Snowsight URL or `SELECT CURRENT_ACCOUNT()` |
| `database` | Database containing MCP server |
| `schema` | Schema containing MCP server |
| `mcp_server_name` | Name from `CREATE MCP SERVER` |
| `PAT` | Snowsight → Profile → Programmatic Access Tokens |

---

## Method 2: Local MCP Server (snowflake-labs-mcp)

Uses the Snowflake-Labs MCP package running locally.

### Prerequisites

```bash
# Install uv package manager
brew install uv
# or
pip install uv
```

### Clawdbot Configuration

```json
{
  "mcpServers": {
    "snowflake": {
      "command": "uvx",
      "args": [
        "snowflake-labs-mcp",
        "--service-config-file",
        "~/.mcp/snowflake_config.yaml",
        "--account", "your-account.region",
        "--user", "your_username",
        "--password", "your_password"
      ]
    }
  }
}
```

### Using Connection File

Create `~/.snowflake/connections.toml`:

```toml
[default]
account = "your-account.region"
user = "your_username"
password = "your_password"
warehouse = "COMPUTE_WH"
role = "ANALYST_ROLE"
```

Then in `mcp.json`:

```json
{
  "mcpServers": {
    "snowflake": {
      "command": "uvx",
      "args": [
        "snowflake-labs-mcp",
        "--service-config-file",
        "~/.mcp/snowflake_config.yaml",
        "--connection-name",
        "default"
      ]
    }
  }
}
```

### Key Pair Authentication

```json
{
  "mcpServers": {
    "snowflake": {
      "command": "uvx",
      "args": [
        "snowflake-labs-mcp",
        "--service-config-file",
        "~/.mcp/snowflake_config.yaml",
        "--account", "your-account",
        "--user", "your_user",
        "--private-key-file", "~/.snowflake/rsa_key.p8",
        "--private-key-file-pwd", "key_password"
      ]
    }
  }
}
```

---

## Comparison

| Feature | Managed MCP Server | Local MCP Server |
|---------|-------------------|------------------|
| Infrastructure | None (cloud-hosted) | Local process |
| Authentication | PAT token | Multiple options |
| Setup Complexity | Lower | Higher |
| Custom Tools | Via SQL | Via config file |
| Governance | Full RBAC | Role-based |
| Offline Access | No | Yes |

---

## Verification

1. In Clawdbot, add `mcp.json` to the session context
2. Ask a question that triggers Snowflake tools (for example, a SQL query)
