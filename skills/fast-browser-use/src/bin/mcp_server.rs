use browser_use::{browser::LaunchOptions, mcp::BrowserServer};
use clap::{Parser, ValueEnum};
use log::{debug, info};
use rmcp::{ServiceExt, transport::stdio};
use std::io::{stdin, stdout};

#[cfg(feature = "mcp-server")]
use rmcp::transport::{sse_server::{SseServer, SseServerConfig},
                      streamable_http_server::{StreamableHttpService, session::local::LocalSessionManager}};

#[cfg(feature = "mcp-server")]
use tokio_util::sync::CancellationToken;

#[derive(Debug, Clone, Copy, ValueEnum)]
enum Transport {
    Stdio,
    Sse,
    Http,
}

#[derive(Parser)]
#[command(name = "browser-use")]
#[command(version)]
#[command(about = "Browser automation MCP server", long_about = None)]
struct Cli {
    /// Launch browser in headed mode (default: headless)
    #[arg(long, short = 'H')]
    headed: bool,

    /// Path to custom browser executable
    #[arg(long, value_name = "PATH")]
    executable_path: Option<String>,

    /// CDP endpoint URL for remote browser connection
    #[arg(long, value_name = "URL")]
    cdp_endpoint: Option<String>,

    /// WebSocket endpoint URL for remote browser connection
    #[arg(long, value_name = "URL")]
    ws_endpoint: Option<String>,

    /// Persistent browser profile directory
    #[arg(long, value_name = "DIR")]
    user_data_dir: Option<String>,

    /// Transport type to use
    #[arg(long, short = 't', value_enum, default_value = "stdio")]
    transport: Transport,

    /// Port for SSE or HTTP transport (default: 3000)
    #[arg(long, short = 'p', default_value = "3000")]
    port: u16,

    /// SSE endpoint path (default: /sse)
    #[arg(long, default_value = "/sse")]
    sse_path: String,

    /// SSE POST path for messages (default: /message)
    #[arg(long, default_value = "/message")]
    sse_post_path: String,

    /// HTTP streamable endpoint path (default: /mcp)
    #[arg(long, default_value = "/mcp")]
    http_path: String,

    /// Log file path for stdio mode (default: browser-use-mcp.log)
    #[arg(long, default_value = "browser-use-mcp.log")]
    log_file: String,
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    let options = LaunchOptions { headless: !cli.headed, ..Default::default() };

    info!("Browser-use MCP Server v{}", env!("CARGO_PKG_VERSION"));
    info!("Browser mode: {}", if options.headless { "headless" } else { "headed" });

    if let Some(ref path) = cli.executable_path {
        info!("Browser executable: {}", path);
    }

    if let Some(ref endpoint) = cli.cdp_endpoint {
        info!("CDP endpoint: {}", endpoint);
    }

    if let Some(ref endpoint) = cli.ws_endpoint {
        info!("WebSocket endpoint: {}", endpoint);
    }

    if let Some(ref dir) = cli.user_data_dir {
        info!("User data directory: {}", dir);
    }

    match cli.transport {
        Transport::Stdio => {
            info!("Transport: stdio");
            info!("Ready to accept MCP connections via stdio");
            let (_read, _write) = (stdin(), stdout());
            let service = BrowserServer::with_options(options.clone())
                .map_err(|e| format!("Failed to create browser server: {}", e))?;
            let server = service.serve(stdio()).await?;

            // Set up signal handler for graceful shutdown
            #[cfg(unix)]
            {
                let mut sigterm = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())?;
                let mut sigint = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::interrupt())?;

                tokio::select! {
                    quit_reason = server.waiting() => {
                        debug!("Server quit with reason: {:?}", quit_reason);
                    }
                    _ = sigterm.recv() => {
                        info!("Received SIGTERM, shutting down gracefully...");
                    }
                    _ = sigint.recv() => {
                        info!("Received SIGINT (Ctrl+C), shutting down gracefully...");
                    }
                }
            }

            #[cfg(windows)]
            {
                let mut ctrl_c = tokio::signal::windows::ctrl_c()?;
                let mut ctrl_break = tokio::signal::windows::ctrl_break()?;

                tokio::select! {
                    quit_reason = server.waiting() => {
                        debug!("Server quit with reason: {:?}", quit_reason);
                    }
                    _ = ctrl_c.recv() => {
                        info!("Received Ctrl+C, shutting down gracefully...");
                    }
                    _ = ctrl_break.recv() => {
                        info!("Received Ctrl+Break, shutting down gracefully...");
                    }
                }
            }

            #[cfg(not(any(unix, windows)))]
            {
                let quit_reason = server.waiting().await;
                debug!("Server quit with reason: {:?}", quit_reason);
            }
        }
        Transport::Sse => {
            info!("Transport: SSE");
            info!("Port: {}", cli.port);
            info!("SSE path: {}", cli.sse_path);
            info!("SSE POST path: {}", cli.sse_post_path);

            let bind_addr = format!("127.0.0.1:{}", cli.port);

            let config = SseServerConfig {
                bind: bind_addr.parse()?,
                sse_path: cli.sse_path.clone(),
                post_path: cli.sse_post_path.clone(),
                ct: CancellationToken::new(),
                sse_keep_alive: None,
            };

            let (sse_server, router) = SseServer::new(config);

            info!("Ready to accept MCP connections at http://{}{}", bind_addr, cli.sse_path);

            // Register service factory for each connection
            let _cancellation_token = sse_server.with_service(move || {
                BrowserServer::with_options(options.clone()).expect("Failed to create browser server")
            });

            // Start HTTP server with SSE router
            let listener = tokio::net::TcpListener::bind(&bind_addr).await?;
            axum::serve(listener, router.into_make_service()).await?;
        }
        Transport::Http => {
            info!("Transport: HTTP streamable");
            info!("Port: {}", cli.port);
            info!("HTTP path: {}", cli.http_path);

            let bind_addr = format!("127.0.0.1:{}", cli.port);

            let service_factory = move || {
                BrowserServer::with_options(options.clone())
                    .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))
            };

            let http_service =
                StreamableHttpService::new(service_factory, LocalSessionManager::default().into(), Default::default());

            let router = axum::Router::new().nest_service(&cli.http_path, http_service);

            info!("Ready to accept MCP connections at http://{}{}", bind_addr, cli.http_path);

            let listener = tokio::net::TcpListener::bind(bind_addr).await?;
            axum::serve(listener, router).await?;
        }
    }

    Ok(())
}
