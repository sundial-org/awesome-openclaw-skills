---
name: jb-docs
description: Query Juicebox V5 documentation via REST API or MCP server. Search docs, get contract addresses, and find implementation guides.
---

# Juicebox V5 Documentation Lookup

Query Juicebox documentation via the REST API or MCP server.

## MCP Server (Recommended)

Add to your Claude Code or MCP client configuration:

```json
{
  "mcpServers": {
    "juice-docs": {
      "type": "http",
      "url": "https://docs.juicebox.money/api/mcp-sse"
    }
  }
}
```

### MCP Tools Available
- `search_docs` - Search documentation by keyword
- `get_doc` - Get full document content by path
- `list_docs_by_category` - List docs in a category
- `get_doc_structure` - Get documentation structure

### Direct MCP Call Example
```bash
curl -X POST https://docs.juicebox.money/api/mcp-sse \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_docs","arguments":{"query":"pay hook"}}}'
```

## REST API Endpoints

### Search Documentation
```bash
POST https://docs.juicebox.money/api/mcp/search
Content-Type: application/json

{
  "query": "pay hook",
  "category": "all",    # all, developer, user, dao, ecosystem
  "version": "v5",      # v3, v4, v5, all
  "limit": 10
}
```

### Get Specific Document
```bash
POST https://docs.juicebox.money/api/mcp/get-doc
Content-Type: application/json

{
  "path": "dev/v5/learn/overview.md"
}
```

### List Documents by Category
```bash
GET https://docs.juicebox.money/api/mcp/list-docs?category=developer&version=v5
```

### Get Documentation Structure
```bash
GET https://docs.juicebox.money/api/mcp/structure
```

## Using WebFetch

Use WebFetch to query the API or fetch documentation pages directly:

### Search for documentation
```
WebFetch https://docs.juicebox.money/dev/v5/build/pay-hook/
"Extract how to implement a pay hook"
```

### Fetch specific pages
```
WebFetch https://docs.juicebox.money/dev/v5/learn/overview/
"Summarize the V5 protocol overview"
```

## Documentation Structure

```
/dev/                    # Developer documentation root
/dev/v5/learn/           # Conceptual documentation
/dev/v5/build/           # Implementation guides
/dev/v5/api/             # API reference
/dev/v5/api/core/        # Core contract docs
```

## Available Documentation

### Protocol Documentation
- **Learn**: Conceptual guides and protocol overview
- **Build**: Implementation guides and tutorials
- **API**: Technical specifications and contract interfaces

### Contract Addresses
- Deployed addresses for all networks (Ethereum, Optimism, Arbitrum, Base)
- Latest V5 contract addresses
- Hook deployer addresses

### Code References
- Interface definitions
- Struct documentation
- Event signatures

## Common Documentation Queries

### "What's the JBController address on mainnet?"
Use the /references folder for offline contract addresses, or fetch from docs.

### "How do I implement a pay hook?"
```
WebFetch https://docs.juicebox.money/dev/v5/build/pay-hook/
"Extract implementation steps for pay hooks"
```

### "What events does JBMultiTerminal emit?"
```
WebFetch https://docs.juicebox.money/dev/v5/api/core/jbmultiterminal/
"List all events emitted by JBMultiTerminal"
```

## Official Resources

- **Docs**: https://docs.juicebox.money
- **GitHub**: https://github.com/jbx-protocol
- **V5 Core**: https://github.com/Bananapus/nana-core-v5
- **Buyback Hook**: https://github.com/Bananapus/nana-buyback-hook-v5
- **721 Hook**: https://github.com/Bananapus/nana-721-hook-v5
- **Revnet**: https://github.com/rev-net/revnet-core-v5

## Generation Guidelines

1. **Use WebFetch** to query documentation pages directly
2. **Reference the /references folder** for offline interface/struct definitions
3. **Provide direct links** to relevant documentation
4. **Default to V5** unless user explicitly asks about older versions

## Example Prompts

- "What's the JBController address on Optimism?"
- "Show me the documentation for pay hooks"
- "What events does the terminal emit?"
- "Get the latest V5 contract addresses"
