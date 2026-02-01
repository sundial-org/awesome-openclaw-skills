# XcodeBuildMCP Setup (Prereqs + MCP Client Config)

## Requirements

XcodeBuildMCP requires:
- macOS 14.5 or newer
- Xcode 16.x
- Node.js 18.x or newer

These requirements come from the XcodeBuildMCP package info.

## MCP client configuration

Add the server to your MCP client config. The official docs show two common ways:

### Option A: Use npx (no global install)

```json
{
  "mcpServers": {
    "xcodebuildmcp": {
      "command": "npx",
      "args": ["-y", "xcodebuildmcp@latest"]
    }
  }
}
```

### Option B: Use a global install

```json
{
  "mcpServers": {
    "xcodebuildmcp": {
      "command": "xcodebuildmcp"
    }
  }
}
```

Source: XcodeBuildMCP documentation.

## Optional: Smithery install helper

Smithery provides a one-line install to add the server for MCP clients:

```
npx -y @smithery/cli install xcodebuildmcp --client <your-client>
```

Source: MCP Servers directory entry for XcodeBuildMCP.

## Optional: UI automation prerequisites

If you plan to use UI automation tools (tap/type/gesture), the MCP Servers listing notes the optional AXe (Accessibility eXtensions) helpers.

## OpenClaw note

Once the MCP server is configured, OpenClaw should expose tools prefixed with `mcp__xcodebuildmcp__*`. If you don’t see them, ensure the MCP server is running and the client config is loaded.
