use std::path::PathBuf;

/// Options for launching a new browser instance
#[derive(Debug, Clone)]
pub struct LaunchOptions {
    pub headless: bool,

    /// Custom Chrome/Chromium binary path
    pub chrome_path: Option<PathBuf>,

    pub window_width: u32,

    pub window_height: u32,

    /// User data directory for browser profile
    pub user_data_dir: Option<PathBuf>,

    pub sandbox: bool,

    pub launch_timeout: u64,
}

impl Default for LaunchOptions {
    fn default() -> Self {
        Self {
            headless: true,
            chrome_path: None,
            window_width: 1280,
            window_height: 720,
            user_data_dir: None,
            sandbox: true,
            launch_timeout: 30000,
        }
    }
}

impl LaunchOptions {
    /// Create new LaunchOptions with default values
    pub fn new() -> Self {
        Self::default()
    }

    /// Builder method: set headless mode
    pub fn headless(mut self, headless: bool) -> Self {
        self.headless = headless;
        self
    }

    /// Builder method: set Chrome binary path
    pub fn chrome_path(mut self, path: PathBuf) -> Self {
        self.chrome_path = Some(path);
        self
    }

    /// Builder method: set window dimensions
    pub fn window_size(mut self, width: u32, height: u32) -> Self {
        self.window_width = width;
        self.window_height = height;
        self
    }

    /// Builder method: set user data directory
    pub fn user_data_dir(mut self, dir: PathBuf) -> Self {
        self.user_data_dir = Some(dir);
        self
    }

    /// Builder method: enable/disable sandbox
    pub fn sandbox(mut self, sandbox: bool) -> Self {
        self.sandbox = sandbox;
        self
    }

    /// Builder method: set launch timeout
    pub fn launch_timeout(mut self, timeout_ms: u64) -> Self {
        self.launch_timeout = timeout_ms;
        self
    }
}

/// Options for connecting to an existing browser instance
#[derive(Debug, Clone)]
pub struct ConnectionOptions {
    /// WebSocket URL for Chrome DevTools Protocol
    pub ws_url: String,

    /// Connection timeout in milliseconds (default: 10000)
    pub timeout: u64,
}

impl ConnectionOptions {
    /// Create new ConnectionOptions with WebSocket URL
    pub fn new<S: Into<String>>(ws_url: S) -> Self {
        Self { ws_url: ws_url.into(), timeout: 10000 }
    }

    /// Builder method: set connection timeout
    pub fn timeout(mut self, timeout_ms: u64) -> Self {
        self.timeout = timeout_ms;
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_launch_options_default() {
        let opts = LaunchOptions::default();
        assert!(opts.headless);
        assert_eq!(opts.window_width, 1280);
        assert_eq!(opts.window_height, 720);
        assert!(opts.sandbox);
        assert_eq!(opts.launch_timeout, 30000);
    }

    #[test]
    fn test_launch_options_builder() {
        let opts = LaunchOptions::new().headless(false).window_size(1920, 1080).sandbox(false).launch_timeout(60000);

        assert!(!opts.headless);
        assert_eq!(opts.window_width, 1920);
        assert_eq!(opts.window_height, 1080);
        assert!(!opts.sandbox);
        assert_eq!(opts.launch_timeout, 60000);
    }

    #[test]
    fn test_connection_options() {
        let opts = ConnectionOptions::new("ws://localhost:9222").timeout(5000);

        assert_eq!(opts.ws_url, "ws://localhost:9222");
        assert_eq!(opts.timeout, 5000);
    }
}
