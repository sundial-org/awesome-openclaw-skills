---
name: npm-search
description: Search npm packages. Use for finding Node.js/JavaScript packages, libraries, and tools.
metadata: {"clawdbot":{"emoji":"📦","requires":{"bins":["jq","npm-search-mcp-server"]}}}
---

# NPM Search

CLI wrapper for npm-search-mcp-server.

> **Note:** Examples show command syntax. Replace queries with the user's actual request.

## Search Packages

```bash
bash scripts/npmsearch "<query>"
```

## Command Reference

| Command | Description |
|---------|-------------|
| `npmsearch "<query>"` | Search npm packages |

## Notes

- Requires `npm-search-mcp-server` installed
- Requires `jq`
