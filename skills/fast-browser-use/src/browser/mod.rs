//! Browser management module
//!
//! This module provides functionality for launching and managing Chrome/Chromium browser instances.
//! It includes configuration options, session management, and browser lifecycle control.

pub mod config;
pub mod debug;
pub mod session;

pub use config::{ConnectionOptions, LaunchOptions};
pub use session::BrowserSession;

use crate::error::Result;

/// Initialize a new browser session with default options
pub fn init() -> Result<BrowserSession> {
    BrowserSession::new()
}

/// Initialize a new browser session with custom launch options
pub fn init_with_options(options: LaunchOptions) -> Result<BrowserSession> {
    BrowserSession::launch(options)
}

/// Connect to an existing browser instance
pub fn connect(ws_url: &str) -> Result<BrowserSession> {
    BrowserSession::connect(ConnectionOptions::new(ws_url))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_launch_options_export() {
        let opts = LaunchOptions::new().headless(true);
        assert!(opts.headless);
    }

    #[test]
    fn test_connection_options_export() {
        let opts = ConnectionOptions::new("ws://localhost:9222");
        assert_eq!(opts.ws_url, "ws://localhost:9222");
    }

    #[test]
    #[ignore]
    fn test_init() {
        let result = init();
        assert!(result.is_ok());
    }

    #[test]
    #[ignore]
    fn test_init_with_options() {
        let opts = LaunchOptions::new().headless(true).window_size(1024, 768);

        let result = init_with_options(opts);
        assert!(result.is_ok());
    }
}
