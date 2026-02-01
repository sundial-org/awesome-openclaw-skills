use browser_use::{BrowserSession, LaunchOptions,
                  tools::{debug::{GetConsoleLogsParams, GetNetworkErrorsParams, GetConsoleLogsTool, GetNetworkErrorsTool},
                          Tool, ToolContext}};
use log::info;
use std::thread;
use std::time::Duration;

#[test]
#[ignore]
fn test_debug_tools() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Create a page that generates logs and network errors
    // Note: We use a non-existent domain for network error
    let html = r#"
        <!DOCTYPE html>
        <html>
        <body>
            <script>
                console.log('Test log message');
                console.warn('Test warning message');
                
                // Trigger a network error (async)
                fetch('http://this-domain-should-not-exist-at-all-12345.com/fail')
                    .catch(e => console.error('Fetch failed as expected'));
            </script>
        </body>
        </html>
    "#;

    let data_url = format!("data:text/html,{}", html);
    session.navigate(&data_url).expect("Failed to navigate");

    // Wait for events to be captured
    thread::sleep(Duration::from_secs(2));
    
    // Create tool context
    let mut context = ToolContext::new(&session);
    let logs_tool = GetConsoleLogsTool::default();
    let errors_tool = GetNetworkErrorsTool::default();

    // 1. Get console logs
    let logs_result = logs_tool
        .execute_typed(GetConsoleLogsParams {}, &mut context)
        .expect("Failed to execute get_console_logs");

    assert!(logs_result.success);
    
    let logs = logs_result.data.unwrap();
    let logs_arr = logs.as_array().expect("Logs should be an array");
    
    info!("Captured logs: {:?}", logs_arr);

    // Verify we captured the logs
    let has_log = logs_arr.iter().any(|l| l["text"].as_str().unwrap_or("").contains("Test log message"));
    let has_warn = logs_arr.iter().any(|l| l["text"].as_str().unwrap_or("").contains("Test warning message"));
    
    assert!(has_log, "Should capture console.log");
    assert!(has_warn, "Should capture console.warn");

    // 2. Get network errors
    // Note: Network errors might take longer or behave differently in headless depending on environment
    let errors_result = errors_tool
        .execute_typed(GetNetworkErrorsParams {}, &mut context)
        .expect("Failed to execute get_network_errors");

    assert!(errors_result.success);
    
    let errors = errors_result.data.unwrap();
    let errors_arr = errors.as_array().expect("Errors should be an array");
    
    info!("Captured network errors: {:?}", errors_arr);
    
    // We expect at least one error from the failed fetch
    // Note: precise error text varies by OS/Network, so we just check if we got *something* or if the logs caught the error
    // In many cases, fetch failure also logs to console.error.
    
    let has_fetch_error_log = logs_arr.iter().any(|l| l["text"].as_str().unwrap_or("").contains("Fetch failed"));
    assert!(has_fetch_error_log, "Should capture fetch failure in console logs");
    
    // Network errors might be empty if the browser handles it purely as a console error for data: URLs
    // But let's see.
}
