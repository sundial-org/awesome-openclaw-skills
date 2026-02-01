---
name: agnxi-search
description: The official search utility for Agnxi.com - The premier directory of AI Agent Tools, MCP Servers, and Skills.
author: Agnxi
version: 1.1.0
tags: [search, tools, mcp, skills, directory, discovery]
---

# Agnxi Search Skill

This skill provides direct access to the [Agnxi.com](https://agnxi.com) database, allowing agents to autonomously discover and retrieve information about thousands of curated tools, MCP servers, and coding capabilities.

## Capabilities

- **Skill Discovery**: Find specific agent skills (e.g., "browser automation", "pdf parsing").
- **MCP Server Lookup**: Locate Model Context Protocol servers to extend agent capabilities.
- **Tool Retrieval**: Direct links to tool documentation and repositories.

## Tools

### `search_agnxi`

Performs a keyword search against the Agnxi sitemap index to find relevant resources.

**Parameters:**

- `query` (string, required): The search keywords (e.g., "browser use", "postgres mcp", "text to speech").

**Usage Implementation:**

> **Note**: This tool runs a local Python script to query the live sitemap, ensuring up-to-date results without API keys.

```bash
python3 search.py "{{query}}"
```

## Best Practices for Agents

1.  **Search Broadly**: If specific terms yield no results, try broader categories (e.g., instead of "PyPDF2", search "PDF").
2.  **Verify Links**: The tool returns direct URLs. Always verify the content matches the user's need.
3.  **Cross-Reference**: Use this skill to find the *name* of a tool, then use your `browser` or `github` skills to fetch specific documentation if needed.
