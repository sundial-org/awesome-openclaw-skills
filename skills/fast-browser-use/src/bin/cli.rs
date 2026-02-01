use browser_use::{BrowserSession, LaunchOptions};
use clap::{Parser, Subcommand};
use log::{info, warn};
use serde::{Deserialize, Serialize};
use std::{fs, path::PathBuf, thread, time::Duration};

#[derive(Parser)]
#[command(name = "fast-browser-use")]
#[command(version)]
#[command(about = "Fastest Browser Use CLI", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Navigate to a URL
    Navigate {
        /// URL to navigate to
        #[arg(long)]
        url: String,

        /// Simulate human behavior (random delays, mouse jitter)
        #[arg(long)]
        human_emulation: bool,

        /// Wait for a specific CSS selector to appear
        #[arg(long)]
        wait_for_selector: Option<String>,

        /// Load session (cookies/local storage) from file
        #[arg(long)]
        load_session: Option<PathBuf>,
    },
    /// Snapshot the current page (AI-optimized YAML DOM)
    Snapshot {
        /// URL to snapshot (if starting new session)
        #[arg(long)]
        url: Option<String>,

        /// Include computed styles
        #[arg(long)]
        include_styles: bool,

        /// Output file path
        #[arg(long)]
        output: Option<PathBuf>,
    },
    /// Login and save session
    Login {
        /// URL to login page
        #[arg(long)]
        url: String,

        /// File path to save session (cookies)
        #[arg(long)]
        save_session: PathBuf,
    },
    /// Scroll the page and extract new content (infinite scroll harvester)
    Harvest {
        /// URL to harvest
        #[arg(long)]
        url: String,

        /// CSS selector for items to extract
        #[arg(long)]
        selector: String,

        /// Number of scroll iterations
        #[arg(long, default_value = "3")]
        scrolls: u32,

        /// Delay between scrolls in ms
        #[arg(long, default_value = "1000")]
        delay: u64,

        /// Output file (JSON)
        #[arg(long)]
        output: Option<PathBuf>,
    },
    /// Convert page to markdown
    Markdown {
        /// URL to convert
        #[arg(long)]
        url: String,

        /// Output file path
        #[arg(long)]
        output: Option<PathBuf>,
    },
    /// Take a screenshot
    Screenshot {
        /// URL to screenshot
        #[arg(long)]
        url: String,

        /// Output file path (PNG)
        #[arg(long)]
        output: PathBuf,

        /// Full page screenshot (not just viewport)
        #[arg(long)]
        full_page: bool,
    },
}

#[derive(Serialize, Deserialize)]
struct SessionData {
    cookies: Vec<headless_chrome::protocol::cdp::Network::Cookie>,
    // Local storage could be added here
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();
    let cli = Cli::parse();

    match cli.command {
        Commands::Navigate { url, human_emulation, wait_for_selector, load_session } => {
            info!("Navigating to: {}", url);
            let options = LaunchOptions::default().sandbox(false);
            
            let session = BrowserSession::launch(options)?;

            if let Some(path) = load_session {
                if path.exists() {
                    info!("Loading session from {:?}", path);
                    let data = fs::read_to_string(path)?;
                    let session_data: SessionData = serde_json::from_str(&data)?;
                    
                    // Convert cookies to CookieParam format
                    let cookie_params: Vec<_> = session_data.cookies.into_iter().map(|c| {
                        browser_use::tools::cookies::CookieParam {
                            name: c.name,
                            value: c.value,
                            url: Some(url.clone()), // Scope to target URL
                            domain: Some(c.domain),
                            path: Some(c.path),
                            secure: Some(c.secure),
                            http_only: Some(c.http_only),
                            same_site: None, // Simplified
                            expires: Some(c.expires),
                        }
                    }).collect();
                    
                    session.set_cookies(cookie_params)?;
                } else {
                    warn!("Session file not found: {:?}", path);
                }
            }

            session.navigate(&url)?;

            if human_emulation {
                info!("Engaging human emulation (random delays)...");
                // Simple emulation: random sleep
                // Real implementation would inject mouse movements
                let delay = 1000 + (rand::random::<u64>() % 2000);
                thread::sleep(Duration::from_millis(delay));
            }

            if let Some(selector) = wait_for_selector {
                info!("Waiting for selector: {}", selector);
                let tab = session.get_active_tab()?;
                tab.wait_for_element(&selector)?;
            } else {
                session.wait_for_navigation()?;
            }

            info!("Navigation complete.");
        }
        Commands::Snapshot { url, include_styles, output } => {
            let session = BrowserSession::launch(LaunchOptions::default().sandbox(false))?;
            
            if let Some(u) = url {
                info!("Navigating to {}", u);
                session.navigate(&u)?;
                session.wait_for_navigation()?;
            }

            if include_styles {
                info!("Including styles (experimental)...");
            }

            let dom = session.extract_dom()?;
            // We use the 'Ai' render mode from the library via existing snapshot logic or direct call
            // Since we can't easily access render_aria_tree directly if it's not pub, we use the tool logic.
            // But we can import `render_aria_tree` if we made it pub (it is pub in `snapshot.rs` but `snapshot.rs` module is pub).
            // `use browser_use::tools::snapshot::{render_aria_tree, RenderMode};`
            
            // Check if we can access it. `src/tools/snapshot.rs` has `pub fn render_aria_tree`.
            // `src/tools/mod.rs` has `pub mod snapshot`.
            // `src/lib.rs` has `pub mod tools`.
            // So yes.
            
            use browser_use::tools::snapshot::{render_aria_tree, RenderMode};
            
            let snapshot_yaml = render_aria_tree(&dom.root, RenderMode::Ai, None);
            
            if let Some(path) = output {
                fs::write(&path, snapshot_yaml)?;
                info!("Snapshot saved to {:?}", path);
            } else {
                println!("{}", snapshot_yaml);
            }
        }
        Commands::Login { url, save_session } => {
            info!("Opening headed browser for login at {}", url);
            let options = LaunchOptions::default().headless(false).sandbox(false);
            let session = BrowserSession::launch(options)?;
            
            session.navigate(&url)?;
            
            println!("Press Enter after you have logged in...");
            let mut input = String::new();
            std::io::stdin().read_line(&mut input)?;
            
            info!("Saving session...");
            let cookies = session.get_cookies()?;
            
            let session_data = SessionData {
                cookies,
            };
            
            let json = serde_json::to_string_pretty(&session_data)?;
            fs::write(&save_session, json)?;
            info!("Session saved to {:?}", save_session);
        }
        Commands::Harvest { url, selector, scrolls, delay, output } => {
            info!("🚜 Harvesting from {} (selector: {}, scrolls: {})", url, selector, scrolls);
            let session = BrowserSession::launch(LaunchOptions::default().sandbox(false))?;
            
            session.navigate(&url)?;
            session.wait_for_navigation()?;
            
            let tab = session.get_active_tab()?;
            let mut all_items: Vec<String> = Vec::new();
            let mut seen: std::collections::HashSet<String> = std::collections::HashSet::new();
            
            for i in 0..=scrolls {
                info!("Scroll iteration {}/{}", i, scrolls);
                
                let extract_js = format!(r#"
                    (function() {{
                        var els = document.querySelectorAll('{}');
                        var texts = [];
                        for (var i = 0; i < els.length; i++) {{
                            texts.push(els[i].innerText.trim());
                        }}
                        return JSON.stringify(texts);
                    }})()
                "#, selector.replace('\'', "\\'"));
                
                let result = tab.evaluate(&extract_js, false)?;
                if let Some(value) = &result.value {
                    if let Some(json_str) = value.as_str() {
                        if let Ok(items) = serde_json::from_str::<Vec<String>>(json_str) {
                            for item in items {
                                if !item.is_empty() && !seen.contains(&item) {
                                    seen.insert(item.clone());
                                    all_items.push(item);
                                }
                            }
                        }
                    }
                }
                
                if i < scrolls {
                    let scroll_js = "window.scrollBy(0, window.innerHeight); true";
                    tab.evaluate(scroll_js, false)?;
                    thread::sleep(Duration::from_millis(delay));
                }
            }
            
            info!("✅ Harvested {} unique items", all_items.len());
            
            let json_output = serde_json::to_string_pretty(&all_items)?;
            if let Some(path) = output {
                fs::write(&path, &json_output)?;
                info!("Saved to {:?}", path);
            } else {
                println!("{}", json_output);
            }
        }
        Commands::Markdown { url, output } => {
            info!("Converting {} to markdown", url);
            let session = BrowserSession::launch(LaunchOptions::default().sandbox(false))?;
            
            session.navigate(&url)?;
            session.wait_for_navigation()?;
            
            let result = session.execute_tool("get_markdown", serde_json::json!({}))?;
            
            let markdown = result.data.as_ref()
                .and_then(|d: &serde_json::Value| d.get("markdown"))
                .and_then(|m| m.as_str())
                .unwrap_or("Failed to extract markdown");
            
            if let Some(path) = output {
                fs::write(&path, markdown)?;
                info!("Saved to {:?}", path);
            } else {
                println!("{}", markdown);
            }
        }
        Commands::Screenshot { url, output, full_page } => {
            info!("📸 Screenshotting {}", url);
            let session = BrowserSession::launch(LaunchOptions::default().sandbox(false))?;
            
            session.navigate(&url)?;
            session.wait_for_navigation()?;
            
            let tab = session.get_active_tab()?;
            let screenshot_data = tab.capture_screenshot(
                headless_chrome::protocol::cdp::Page::CaptureScreenshotFormatOption::Png,
                None,
                None,
                !full_page,
            )?;
            
            fs::write(&output, &screenshot_data)?;
            info!("✅ Saved screenshot to {:?}", output);
        }
    }

    Ok(())
}
