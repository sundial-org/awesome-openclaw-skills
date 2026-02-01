---
name: deepwiki
description: Query the DeepWiki MCP server for GitHub repository documentation, wiki structure, and AI-powered questions.
homepage: https://docs.devin.ai/work-with-devin/deepwiki-mcp
---

# DeepWiki

Use this skill to access documentation for public GitHub repositories via the DeepWiki MCP server. You can search repository wikis, get structure, and ask complex questions grounded in the repository's documentation.

## Commands

### Ask Question
Ask any question about a GitHub repository and get an AI-powered, context-grounded response.
```bash
node ./scripts/deepwiki.js ask <owner/repo> "your question"
```

### Read Wiki Structure
Get a list of documentation topics for a GitHub repository.
```bash
node ./scripts/deepwiki.js structure <owner/repo>
```

### Read Wiki Contents
View documentation about a specific path in a GitHub repository's wiki.
```bash
node ./scripts/deepwiki.js contents <owner/repo> <path>
```

## Examples

**Ask about Devin's MCP usage:**
```bash
node ./scripts/deepwiki.js ask cognitionlabs/devin "How do I use MCP?"
```

**Get the structure for the React docs:**
```bash
node ./scripts/deepwiki.js structure facebook/react
```

## Notes
- Base Server: `https://mcp.deepwiki.com/mcp`
- Works for public repositories only.
- No authentication required.
