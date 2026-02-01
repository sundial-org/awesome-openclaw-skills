---
name: snowflake-mcp
description: Connect to the Snowflake Managed MCP server with Clawdbot or other MCP clients. Use when wiring Snowflake MCP endpoints, validating connectivity, or configuring Cortex AI services.
---

# Snowflake MCP Connection

Use this skill to integrate the Snowflake Managed MCP server with Clawdbot. It covers endpoint creation, authentication, and tool validation so Snowflake data can be accessed through MCP.

## Quick Start

### Prerequisites

- Snowflake account with ACCOUNTADMIN role
- Programmatic Access Token (PAT) from Snowflake
- Clawdbot or any MCP-compatible client

### Step 1: Create Programmatic Access Token (PAT)

1. In Snowsight, go to your user menu → **My Profile**
2. Select **Programmatic Access Tokens**
3. Click **Create Token** for your role
4. Copy and save the token securely

### Step 2: Create MCP Server in Snowflake

Run this SQL in a Snowsight worksheet to create your MCP server:

```sql
CREATE OR REPLACE MCP SERVER my_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries against the Snowflake database."
    title: "SQL Execution Tool"
$$;
```

### Step 3: Test the Connection

Verify with curl (replace placeholders):

```bash
curl -X POST "https://YOUR-ORG-YOUR-ACCOUNT.snowflakecomputing.com/api/v2/databases/YOUR_DB/schemas/YOUR_SCHEMA/mcp-servers/my_mcp_server" \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/json' \
  --header "Authorization: Bearer YOUR-PAT-TOKEN" \
  --data '{
    "jsonrpc": "2.0",
    "id": 12345,
    "method": "tools/list",
    "params": {}
  }'
```

### Step 4: Configure Clawdbot

Create `mcp.json` at your project root (this is the MCP configuration Clawdbot can load for a session):

```json
{
  "mcpServers": {
    "Snowflake MCP Server": {
      "url": "https://YOUR-ORG-YOUR-ACCOUNT.snowflakecomputing.com/api/v2/databases/YOUR_DB/schemas/YOUR_SCHEMA/mcp-servers/my_mcp_server",
      "headers": {
        "Authorization": "Bearer YOUR-PAT-TOKEN"
      }
    }
  }
}
```

Start a new Clawdbot session and load `mcp.json` so the MCP connection is active. The Snowflake tools should appear in your session.

### Step 5: Verify in Clawdbot

1. Start a new Clawdbot session
2. Load `mcp.json` for the session
3. Ask a question that triggers Snowflake tools (for example, a SQL query)

## MCP Server Examples

### Basic SQL Execution Only

```sql
CREATE OR REPLACE MCP SERVER sql_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries against Snowflake."
    title: "SQL Execution"
$$;
```

### With Cortex Search (RAG)

First create a Cortex Search service in Snowsight (AI & ML → Cortex Search), then:

```sql
CREATE OR REPLACE MCP SERVER search_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "Document Search"
    identifier: "MY_DB.MY_SCHEMA.MY_SEARCH_SERVICE"
    type: "CORTEX_SEARCH_SERVICE_QUERY"
    description: "Search and retrieve information from documents using vector search."
    title: "Document Search"
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries."
    title: "SQL Execution"
$$;
```

### With Cortex Analyst (Semantic Views)

First upload a semantic YAML or create a Semantic View, then:

```sql
CREATE OR REPLACE MCP SERVER analyst_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "Sales Analytics"
    identifier: "MY_DB.MY_SCHEMA.SALES_SEMANTIC_VIEW"
    type: "CORTEX_ANALYST_MESSAGE"
    description: "Query sales metrics and KPIs using natural language."
    title: "Sales Analytics"
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries."
    title: "SQL Execution"
$$;
```

### With Cortex Agent

```sql
CREATE OR REPLACE MCP SERVER agent_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "Documentation Agent"
    identifier: "MY_DB.MY_SCHEMA.MY_AGENT"
    type: "CORTEX_AGENT_RUN"
    description: "An agent that answers questions using documentation."
    title: "Documentation Agent"
$$;
```

### Full Featured Server

```sql
CREATE OR REPLACE MCP SERVER full_mcp_server FROM SPECIFICATION
$$
tools:
  - name: "Analytics Semantic View"
    identifier: "ANALYTICS_DB.DATA.FINANCIAL_ANALYTICS"
    type: "CORTEX_ANALYST_MESSAGE"
    description: "Query financial metrics, customer data, and business KPIs."
    title: "Financial Analytics"
  - name: "Support Tickets Search"
    identifier: "SUPPORT_DB.DATA.TICKETS_SEARCH"
    type: "CORTEX_SEARCH_SERVICE_QUERY"
    description: "Search support tickets and customer interactions."
    title: "Support Search"
  - name: "SQL Execution Tool"
    type: "SYSTEM_EXECUTE_SQL"
    description: "Execute SQL queries against Snowflake."
    title: "SQL Execution"
  - name: "Send_Email"
    identifier: "MY_DB.DATA.SEND_EMAIL"
    type: "GENERIC"
    description: "Send emails to verified addresses."
    title: "Send Email"
    config:
      type: "procedure"
      warehouse: "COMPUTE_WH"
      input_schema:
        type: "object"
        properties:
          body:
            description: "Email body in HTML format."
            type: "string"
          recipient_email:
            description: "Recipient email address."
            type: "string"
          subject:
            description: "Email subject line."
            type: "string"
$$;
```

## Tool Types Reference

| Type | Purpose |
|------|---------|
| `SYSTEM_EXECUTE_SQL` | Execute arbitrary SQL queries |
| `CORTEX_SEARCH_SERVICE_QUERY` | RAG over unstructured data |
| `CORTEX_ANALYST_MESSAGE` | Natural language queries on semantic models |
| `CORTEX_AGENT_RUN` | Invoke Cortex Agents |
| `GENERIC` | Custom tools (procedures/functions) |

## Benefits

- **Governed by Design**: Same RBAC policies apply as your data
- **No Infrastructure**: No local server deployment needed
- **Reduced Integration**: Connect any MCP-compatible client
- **Extensible**: Add custom tools via procedures/functions

## Troubleshooting

### Connection Issues

- **SSL Error**: Use hyphens instead of underscores in account name
- **401 Unauthorized**: Verify PAT token is valid and not expired
- **404 Not Found**: Check database, schema, and MCP server names

### Testing Tools

List available tools:

```bash
curl -X POST "https://YOUR-ACCOUNT.snowflakecomputing.com/api/v2/databases/DB/schemas/SCHEMA/mcp-servers/SERVER" \
  -H "Authorization: Bearer PAT" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### PAT Token Notes

- PATs don't evaluate secondary roles
- Select a single role with all required permissions when creating
- Create new PAT to change role

## Alternative: Local MCP Server

For local deployment using the `snowflake-labs-mcp` package, see [mcp-client-setup.md](mcp-client-setup.md).

## Resources

- [Snowflake MCP Server Guide](https://www.snowflake.com/en/developers/guides/getting-started-with-snowflake-mcp-server/)
- [Snowflake MCP Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp)
- [GitHub: sfguide-getting-started-with-snowflake-mcp-server](https://github.com/Snowflake-Labs/sfguide-getting-started-with-snowflake-mcp-server)
- [MCP Protocol](https://modelcontextprotocol.io)
