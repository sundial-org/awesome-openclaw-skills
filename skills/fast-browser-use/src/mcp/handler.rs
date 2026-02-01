//! ServerHandler implementation for BrowserSession

use crate::browser::BrowserSession;
use log::debug;
use rmcp::{ServerHandler,
           handler::server::tool::ToolRouter,
           model::{ServerCapabilities, ServerInfo},
           tool_handler};
use std::sync::{Arc, Mutex};

/// MCP Server wrapper for BrowserSession
///
/// This struct holds a browser session and provides thread-safe access
/// for MCP tool execution.
#[derive(Clone)]
pub struct BrowserServer {
    session: Arc<Mutex<BrowserSession>>,
    tool_router: ToolRouter<Self>,
}

impl BrowserServer {
    /// Create a new browser server with default launch options
    pub fn new() -> Result<Self, String> {
        let session = BrowserSession::new().map_err(|e| format!("Failed to launch browser: {}", e))?;

        Ok(Self { session: Arc::new(Mutex::new(session)), tool_router: Self::tool_router() })
    }

    /// Create a new browser server with custom launch options
    pub fn with_options(options: crate::browser::LaunchOptions) -> Result<Self, String> {
        let session = BrowserSession::launch(options).map_err(|e| format!("Failed to launch browser: {}", e))?;

        Ok(Self { session: Arc::new(Mutex::new(session)), tool_router: Self::tool_router() })
    }

    /// Get a reference to the browser session (blocking lock)
    pub(crate) fn session(&self) -> std::sync::MutexGuard<'_, BrowserSession> {
        self.session.lock().expect("Failed to lock browser session")
    }
}

impl Default for BrowserServer {
    fn default() -> Self {
        Self::new().expect("Failed to create default browser server")
    }
}

impl Drop for BrowserServer {
    fn drop(&mut self) {
        debug!("BrowserServer dropped");
    }
}

#[tool_handler]
impl ServerHandler for BrowserServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            instructions: Some("Browser-use MCP Server".into()),
            capabilities: ServerCapabilities::builder().enable_tools().build(),
            ..Default::default()
        }
    }
}
