# CODEBUDDY.md This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

`browser-use` is a Rust library for browser automation via Chrome DevTools Protocol (CDP). It provides:

- A browser session manager wrapping `headless_chrome`
- A tool system for common browser operations (navigate, click, input, extract, etc.)
- DOM extraction with indexed interactive elements
- An MCP (Model Context Protocol) server for AI-driven browser automation

## Common Commands

### Building

```bash
cargo build                    # Build library
cargo build --bin mcp-server  # Build MCP server binary
cargo build --release         # Production build
```

### Testing

```bash
cargo test                     # Run unit tests only
cargo test -- --ignored        # Run integration tests (requires Chrome installed)
cargo test dom_integration     # Run specific test file
```

### Running

```bash
cargo run --bin mcp-server              # Run MCP server (headless)
cargo run --bin mcp-server -- --headed  # Run with visible browser
```

### Development

```bash
cargo check        # Fast compile check
cargo clippy       # Linting
cargo fmt          # Format code
```

## Architecture

### Module Structure

The codebase is organized into five main modules:

**1. `browser/` - Browser Management**

- `session.rs`: `BrowserSession` wraps `headless_chrome::Browser` and manages tabs
- `config.rs`: `LaunchOptions` and `ConnectionOptions` for browser initialization
- Key APIs: `launch()`, `connect()`, `navigate()`, `extract_dom()`

**2. `dom/` - DOM Extraction & Indexing**

- `tree.rs`: `DomTree` represents page structure with indexed interactive elements
- `element.rs`: `ElementNode` is a serializable DOM node with visibility/interactivity metadata
- `extract_dom.js`: JavaScript injected into pages to extract DOM as JSON
- Flow: JS extraction → JSON → `ElementNode` tree → index interactive elements → `DomTree.selectors`

**3. `tools/` - Browser Automation Tools**

- Each tool is in its own file: `navigate.rs`, `click.rs`, `input.rs`, `extract.rs`, `screenshot.rs`, `evaluate.rs`, `wait.rs`
- All tools implement the `Tool` trait with type-safe parameter structs (e.g., `ClickParams`, `NavigateParams`)
- `ToolRegistry` manages tools and executes them with `ToolContext` (contains `BrowserSession` + optional cached `DomTree`)
- Element selection: tools accept either CSS selectors OR numeric indices (from `DomTree`)
- **⚠️ IMPORTANT: When adding a new tool, remember to register it in `src/mcp/mod.rs` using the `register_mcp_tools!` macro**

**4. `mcp/` - Model Context Protocol Server**

- `handler.rs`: `BrowserServer` wraps `BrowserSession` in `Arc<Mutex<>>` for thread-safe MCP access
- `mod.rs`: Uses `register_mcp_tools!` macro to auto-generate MCP tool wrappers from internal tools
- Runs as stdio-based MCP server via `rmcp` crate

**5. `error.rs` - Error Handling**

- `BrowserError` enum with variants for launch/connection/navigation/DOM/tool failures
- Converts `anyhow::Error` from `headless_chrome` and `serde_json::Error`

### Key Design Patterns

**Tool System**: The `Tool` trait uses associated types for compile-time parameter validation:

```rust
trait Tool {
    type Params: Serialize + Deserialize + JsonSchema;
    fn execute_typed(&self, params: Self::Params, context: &mut ToolContext) -> Result<ToolResult>;
}
```

**DOM Indexing**: Interactive elements get numeric indices for easier LLM targeting:

- Extract DOM → Traverse tree → Detect interactive elements (buttons, links, inputs)
- Assign indices only to visible + interactive elements
- Tools can use `{"index": 5}` instead of complex CSS selectors

**Dual Element Selection**: Tools accept both:

- CSS selector: `{"selector": "#submit-btn"}`
- Numeric index: `{"index": 5}` (requires DOM extraction first)

**MCP Integration**: The `register_mcp_tools!` macro automatically wraps internal tools:

- Takes tool type + MCP name + description
- Generates async function that locks session, calls tool, converts result
- All registered in `tool_router` for `rmcp` dispatcher

### Testing Approach

- Unit tests in each module for struct/enum behavior
- Integration tests in `tests/` require Chrome (`#[ignore]` attribute)
- Run ignored tests with: `cargo test -- --ignored`
- Tests use `data:` URLs to avoid network dependencies

## Important Implementation Notes

- The MCP server runs in a single-threaded Tokio runtime (`#[tokio::main(flavor = "current_thread")]`)
- `BrowserSession` holds a `headless_chrome::Browser` and manages one active tab at a time
- DOM extraction executes JavaScript in the browser and parses the returned JSON
- All tools work on the active tab; use `switch_tab()` to change context
- Element indices are only valid for the specific DOM extraction they came from
- Re-extracting the DOM rebuilds the selector list on `DomTree` and reassigns all indices
- **When writing JavaScript to be executed in the browser, always use `JSON.stringify()` to ensure the result is returned properly** - this prevents issues with complex objects and ensures consistent serialization

## Crate Dependencies

- `headless_chrome`: CDP client for Chrome/Chromium automation
- `rmcp`: Model Context Protocol (MCP) server framework
- `serde`/`serde_json`: JSON serialization for params and DOM
- `schemars`: JSON Schema generation for tool parameters
- `thiserror`: Ergonomic error definitions
- `tokio` (optional): Async runtime for MCP server
- `clap` (optional): CLI arg parsing for MCP server binary

## File Locations

- MCP server binary: `src/bin/mcp_server.rs`
- DOM extraction script: `src/dom/extract_dom.js` (embedded via `include_str!`)
- Integration tests: `tests/dom_integration.rs`
