pub mod browser;
pub mod dom;
pub mod error;
pub mod tools;

#[cfg(feature = "mcp-handler")]
pub mod mcp;

pub use browser::{BrowserSession, ConnectionOptions, LaunchOptions};
pub use dom::{BoundingBox, DomTree, ElementNode};
pub use error::{BrowserError, Result};
pub use tools::{Tool, ToolContext, ToolRegistry, ToolResult};

#[cfg(feature = "mcp-handler")]
pub use mcp::BrowserServer;
#[cfg(feature = "mcp-handler")]
pub use rmcp::ServiceExt;
