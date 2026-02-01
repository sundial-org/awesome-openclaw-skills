# browser-use

A lightweight Rust library for browser automation via Chrome DevTools Protocol (CDP).

## ✨ Highlights

- **Zero Node.js dependency** - Pure Rust implementation directly controlling browsers via CDP
- **Lightweight & Fast** - No heavy runtime, minimal overhead
- **MCP Integration** - Built-in Model Context Protocol server for AI-driven automation
- **Simple API** - Easy-to-use tools for common browser operations

## Installation

```bash
cargo add browser-use
```

## Styling

```bash
cargo +nightly fmt
```

## Quick Start

```rust
use browser_use::browser::BrowserSession;

// Launch browser and navigate
let session = BrowserSession::launch(Default::default())?;
session.navigate("https://example.com", None)?;

// Extract DOM with indexed interactive elements
let dom = session.extract_dom()?;
```

## MCP Server

Run the built-in MCP server for AI-driven automation:

```bash
# Headless mode
cargo run --bin mcp-server

# Visible browser
cargo run --bin mcp-server -- --headed
```

## Features

- Navigate, click, input, screenshot, extract content
- DOM extraction with indexed interactive elements
- CSS selector or numeric index-based element targeting
- Thread-safe browser session management

## Requirements

- Rust 1.70+
- Chrome or Chromium installed
