---
name: factory-ai
description: Use Factory AI's droid CLI for software engineering tasks. Supports interactive mode, exec mode, MCP servers, and plugins.
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":["droid"]}}
---

# Factory AI Droid CLI

Use `droid` to build features, debug, refactor, and deploy code.

## Installation

Already installed at: `/Users/mitchellbernstein/.local/bin/droid`

## Authentication

```bash
droid login
# or set FACTORY_API_KEY env var
export FACTORY_API_KEY=your-api-key
```

## Commands

### Interactive Mode
```bash
droid                           # Start fresh session
droid "fix the login bug"       # Start with prompt
droid -r                        # Resume last session
droid -r session-id             # Resume specific session
```

### Non-Interactive (Exec Mode)
```bash
droid exec "analyze this file"
droid exec "commit my changes with a good message"
droid exec "deploy to fly.io"
droid exec --help               # Show exec options
```

### Options for Exec
```bash
droid exec --force "fix lint errors"    # Auto-apply without confirmation
droid exec --json "analyze code"        # JSON output
droid exec --model claude "task"        # Specify model
```

### MCP Servers
```bash
droid mcp list                    # List installed MCP servers
droid mcp add server-name         # Add MCP server
droid mcp remove server-name      # Remove MCP server
```

### Plugins
```bash
droid plugin list                 # List plugins
droid plugin add name             # Add plugin
```

## Usage Patterns

### Feature Development
```bash
droid exec "add a user settings page with dark mode toggle"
```

### Debugging
```bash
droid exec "fix this error: [paste error]"
```

### Code Review
```bash
droid exec "review the PR for security issues"
```

### Git Operations
```bash
droid exec "create a PR for my changes"
droid exec "write a good commit message for the staged changes"
```

### Deployment
```bash
droid exec "deploy to fly.io"
```

### Multi-file Changes
```bash
droid
# Then in interactive mode:
@src/components/
@src/api/
Implement authentication flow
```

## Notes

- Droid has deep codebase understanding across your org
- Supports model flexibility (OpenAI, Anthropic, xAI, etc.)
- MCP servers for extended capabilities
- Session-based memory for context continuity
