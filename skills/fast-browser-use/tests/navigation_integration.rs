use browser_use::{BrowserSession, LaunchOptions,
                  tools::{CloseParams, GoBackParams, GoForwardParams, Tool, ToolContext, close::CloseTool,
                          go_back::GoBackTool, go_forward::GoForwardTool}};
use log::info;

#[test]
#[ignore] // Requires Chrome to be installed
fn test_go_back_tool() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to first page
    session.navigate("data:text/html,<html><body><h1>Page 1</h1></body></html>").expect("Failed to navigate to page 1");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Navigate to second page
    session.navigate("data:text/html,<html><body><h1>Page 2</h1></body></html>").expect("Failed to navigate to page 2");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify we're on page 2
    let current_url = session.tab().unwrap().get_url();
    assert!(current_url.contains("Page 2"));

    // Create tool and context
    let tool = GoBackTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool to go back
    let result = tool.execute_typed(GoBackParams {}, &mut context).expect("Failed to execute go_back tool");

    // Verify the result
    assert!(result.success, "Tool execution should succeed");
    assert!(result.data.is_some());

    let data = result.data.unwrap();
    info!("Go back result: {}", serde_json::to_string_pretty(&data).unwrap());

    assert_eq!(data["message"].as_str(), Some("Navigated back in history"));

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify we went back to page 1
    let new_url = session.tab().unwrap().get_url();
    assert!(new_url.contains("Page 1"));
}

#[test]
#[ignore]
fn test_go_forward_tool() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to first page
    session.navigate("data:text/html,<html><body><h1>Page 1</h1></body></html>").expect("Failed to navigate to page 1");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Navigate to second page
    session.navigate("data:text/html,<html><body><h1>Page 2</h1></body></html>").expect("Failed to navigate to page 2");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Go back to page 1
    session.go_back().expect("Failed to go back");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify we're on page 1
    let current_url = session.tab().unwrap().get_url();
    assert!(current_url.contains("Page 1"));

    // Create tool and context
    let tool = GoForwardTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool to go forward
    let result = tool.execute_typed(GoForwardParams {}, &mut context).expect("Failed to execute go_forward tool");

    // Verify the result
    assert!(result.success, "Tool execution should succeed");
    assert!(result.data.is_some());

    let data = result.data.unwrap();
    info!("Go forward result: {}", serde_json::to_string_pretty(&data).unwrap());

    assert_eq!(data["message"].as_str(), Some("Navigated forward in history"));

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify we went forward to page 2
    let new_url = session.tab().unwrap().get_url();
    assert!(new_url.contains("Page 2"));
}

#[test]
#[ignore]
fn test_navigation_workflow() {
    // Test a complete workflow: navigate to multiple pages, go back, go forward
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to page 1
    session
        .navigate("data:text/html,<html><body><h1>Page 1</h1><a id='link' href='data:text/html,<html><body><h1>Page 2</h1></body></html>'>Next</a></body></html>")
        .expect("Failed to navigate to page 1");

    std::thread::sleep(std::time::Duration::from_millis(500));

    info!("On page 1");

    // Navigate to page 2
    session.navigate("data:text/html,<html><body><h1>Page 2</h1></body></html>").expect("Failed to navigate to page 2");

    std::thread::sleep(std::time::Duration::from_millis(500));

    info!("On page 2");

    // Navigate to page 3
    session.navigate("data:text/html,<html><body><h1>Page 3</h1></body></html>").expect("Failed to navigate to page 3");

    std::thread::sleep(std::time::Duration::from_millis(500));

    info!("On page 3");

    // Create tools
    let go_back_tool = GoBackTool::default();
    let go_forward_tool = GoForwardTool::default();

    // Go back to page 2
    let mut context = ToolContext::new(&session);
    let result = go_back_tool.execute_typed(GoBackParams {}, &mut context).expect("Failed to go back");

    assert!(result.success);
    info!("Went back to page 2");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Go back to page 1
    let mut context = ToolContext::new(&session);
    let result = go_back_tool.execute_typed(GoBackParams {}, &mut context).expect("Failed to go back");

    assert!(result.success);
    info!("Went back to page 1");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify we're on page 1
    let current_url = session.tab().unwrap().get_url();
    assert!(current_url.contains("Page 1"));

    // Go forward to page 2
    let mut context = ToolContext::new(&session);
    let result = go_forward_tool.execute_typed(GoForwardParams {}, &mut context).expect("Failed to go forward");

    assert!(result.success);
    info!("Went forward to page 2");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify we're on page 2
    let current_url = session.tab().unwrap().get_url();
    assert!(current_url.contains("Page 2"));
}

#[test]
#[ignore]
fn test_close_tool() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to a page
    session.navigate("data:text/html,<html><body><h1>Test Page</h1></body></html>").expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify browser is working
    let tabs = session.get_tabs().expect("Failed to get tabs");
    assert!(!tabs.is_empty(), "Should have at least one tab");

    // Create tool and context
    let tool = CloseTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool to close the browser
    let result = tool.execute_typed(CloseParams {}, &mut context).expect("Failed to execute close tool");

    // Verify the result
    assert!(result.success, "Tool execution should succeed");
    assert!(result.data.is_some());

    let data = result.data.unwrap();
    info!("Close result: {}", serde_json::to_string_pretty(&data).unwrap());

    assert_eq!(data["message"].as_str(), Some("Browser closed successfully"));

    // Note: After closing, subsequent operations may fail
    // The browser tabs should be closed
    std::thread::sleep(std::time::Duration::from_millis(500));
}

#[test]
#[ignore]
fn test_go_back_on_first_page() {
    // Test that going back on the first page doesn't crash
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to only one page
    session.navigate("data:text/html,<html><body><h1>First Page</h1></body></html>").expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Create tool and context
    let tool = GoBackTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool - should succeed but do nothing
    let result = tool.execute_typed(GoBackParams {}, &mut context).expect("Failed to execute go_back tool");

    assert!(result.success, "Tool execution should succeed even if no previous page");
    info!("Go back on first page result: {}", serde_json::to_string_pretty(&result.data.unwrap()).unwrap());
}

#[test]
#[ignore]
fn test_go_forward_on_last_page() {
    // Test that going forward when there's no forward history doesn't crash
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to a page
    session.navigate("data:text/html,<html><body><h1>Page</h1></body></html>").expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Create tool and context
    let tool = GoForwardTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool - should succeed but do nothing
    let result = tool.execute_typed(GoForwardParams {}, &mut context).expect("Failed to execute go_forward tool");

    assert!(result.success, "Tool execution should succeed even if no forward history");
    info!("Go forward on last page result: {}", serde_json::to_string_pretty(&result.data.unwrap()).unwrap());
}
