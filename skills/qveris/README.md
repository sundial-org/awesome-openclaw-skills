# QVeris Skill for Claude Code

[中文文档](README.zh-CN.md) | English

A skill that enables Claude Code to dynamically search and execute tools via the QVeris API.

## Features

- **Tool Discovery**: Search for APIs by describing what you need
- **Tool Execution**: Execute any discovered tool with parameters
- **Wide Coverage**: Access weather, stocks, search, currency, and thousands more APIs

## Installation

### Prerequisites

This skill requires `uv`, a fast Python package manager. Install it first:

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For other installation methods, see the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### Install the Skill

1. Copy this folder to your Claude Code skills directory:
   ```bash
   cp -r qveris ~/.claude/skills/
   ```

2. Set your API key:
   ```bash
   export QVERIS_API_KEY="your-api-key-here"
   ```

   Get your API key at https://qveris.ai

## Usage

Once installed, Claude Code will automatically use this skill when you ask questions about:
- Weather data
- Stock prices and market analysis
- Web searches
- Currency exchange rates
- And more...

### Manual Commands

```bash
# Search for tools
uv run scripts/qveris_tool.py search "stock price data"

# Execute a tool
uv run scripts/qveris_tool.py execute <tool_id> --search-id <id> --params '{"symbol": "AAPL"}'
```

## Author

[@hqmank](https://x.com/hqmank)

## License

MIT
