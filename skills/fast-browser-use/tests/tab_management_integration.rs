use browser_use::{BrowserSession, LaunchOptions,
                  tools::{CloseTabParams, NewTabParams, SwitchTabParams, TabListParams, Tool, ToolContext,
                          close_tab::CloseTabTool, new_tab::NewTabTool, switch_tab::SwitchTabTool,
                          tab_list::TabListTool}};
use log::info;

#[test]
#[ignore]
fn test_new_tab() {
    use browser_use::tools::{NewTabParams, Tool, ToolContext, new_tab::NewTabTool};

    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to initial page
    session.navigate("data:text/html,<html><body><h1>First Tab</h1></body></html>").expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Get initial tab count
    let initial_tabs = session.get_tabs().expect("Failed to get tabs");
    let initial_count = initial_tabs.len();
    info!("Initial tab count: {}", initial_count);

    // Create tool and context
    let tool = NewTabTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool to create a new tab
    let result = tool
        .execute_typed(
            NewTabParams { url: "data:text/html,<html><body><h1>Second Tab</h1></body></html>".to_string() },
            &mut context,
        )
        .expect("Failed to execute new_tab tool");

    // Verify the result
    assert!(result.success, "Tool execution should succeed");
    assert!(result.data.is_some());

    let data = result.data.unwrap();
    assert!(data["url"].as_str().is_some(), "Result should contain url field");
    assert!(data["message"].as_str().is_some(), "Result should contain message field");

    info!("New tab result: {}", serde_json::to_string_pretty(&data).unwrap());

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify tab count increased
    let final_tabs = session.get_tabs().expect("Failed to get tabs");
    let final_count = final_tabs.len();
    info!("Final tab count: {}", final_count);

    assert_eq!(final_count, initial_count + 1, "Tab count should increase by 1");
}

#[test]
#[ignore] // Requires Chrome to be installed
fn test_tab_list() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to a simple page
    session.navigate("data:text/html,<html><body><h1>First Tab</h1></body></html>").expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Create tool and context
    let tool = TabListTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool
    let result = tool.execute_typed(TabListParams {}, &mut context).expect("Failed to execute tab_list tool");

    // Verify the result
    assert!(result.success, "Tool execution should succeed");
    assert!(result.data.is_some());

    let data = result.data.unwrap();
    let tab_list = data["tab_list"].as_array().expect("No tab_list field");
    let count = data["count"].as_u64().expect("No count field");

    info!("Tab list: {}", serde_json::to_string_pretty(&tab_list).unwrap());

    // Should have at least 1 tab
    assert!(count >= 1, "Expected at least 1 tab");
    assert_eq!(tab_list.len() as u64, count);

    // Check first tab structure
    let first_tab = &tab_list[0];
    assert!(first_tab["index"].is_number(), "Tab should have index");
    assert!(first_tab["active"].is_boolean(), "Tab should have active flag");
    assert!(first_tab["title"].is_string(), "Tab should have title");
    assert!(first_tab["url"].is_string(), "Tab should have url");
}

#[test]
#[ignore]
fn test_new_tab_and_switch() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to initial page
    session.navigate("data:text/html,<html><body><h1>First Tab</h1></body></html>").expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Create a new tab
    let new_tab_tool = NewTabTool::default();
    let mut context = ToolContext::new(&session);

    let result = new_tab_tool
        .execute_typed(
            NewTabParams { url: "data:text/html,<html><body><h1>Second Tab</h1></body></html>".to_string() },
            &mut context,
        )
        .expect("Failed to execute new_tab tool");

    assert!(result.success, "New tab creation should succeed");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // List tabs to verify count increased by 1
    let tab_list_tool = TabListTool::default();
    let mut context = ToolContext::new(&session);

    let result = tab_list_tool.execute_typed(TabListParams {}, &mut context).expect("Failed to execute tab_list tool");

    assert!(result.success);
    let data = result.data.unwrap();
    let count = data["count"].as_u64().expect("No count field");

    info!("Tab count after creating new tab: {}", count);
    assert!(count >= 2, "Should have at least 2 tabs, got {}", count);

    // Switch to first tab (index 0)
    let switch_tab_tool = SwitchTabTool::default();
    let mut context = ToolContext::new(&session);

    let result = switch_tab_tool
        .execute_typed(SwitchTabParams { index: 0 }, &mut context)
        .expect("Failed to execute switch_tab tool");

    assert!(result.success, "Switch tab should succeed");

    let data = result.data.unwrap();
    assert_eq!(data["index"].as_u64(), Some(0));
    info!("Switched to tab: {}", serde_json::to_string_pretty(&data).unwrap());
}

#[test]
#[ignore]
fn test_switch_tab_invalid_index() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    session.navigate("data:text/html,<html><body><h1>Tab</h1></body></html>").expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Try to switch to invalid index
    let switch_tab_tool = SwitchTabTool::default();
    let mut context = ToolContext::new(&session);

    let result = switch_tab_tool
        .execute_typed(SwitchTabParams { index: 999 }, &mut context)
        .expect("Failed to execute switch_tab tool");

    // Should fail gracefully
    assert!(!result.success, "Should fail for invalid index");
    assert!(result.error.is_some());
    info!("Expected error: {}", result.error.unwrap());
}

#[test]
#[ignore]
fn test_close_tab() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Create two tabs
    session.navigate("data:text/html,<html><body><h1>First Tab</h1></body></html>").expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    let new_tab_tool = NewTabTool::default();
    let mut context = ToolContext::new(&session);

    new_tab_tool
        .execute_typed(
            NewTabParams { url: "data:text/html,<html><body><h1>Second Tab</h1></body></html>".to_string() },
            &mut context,
        )
        .expect("Failed to create new tab");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify we have at least 2 tabs
    let tab_list_tool = TabListTool::default();
    let mut context = ToolContext::new(&session);

    let result = tab_list_tool.execute_typed(TabListParams {}, &mut context).expect("Failed to execute tab_list tool");

    let count_before = result.data.unwrap()["count"].as_u64().unwrap();
    info!("Tab count before closing: {}", count_before);
    assert!(count_before >= 2, "Should have at least 2 tabs before closing, got {}", count_before);

    // Close the active tab (second tab)
    let close_tab_tool = CloseTabTool::default();
    let mut context = ToolContext::new(&session);

    let result =
        close_tab_tool.execute_typed(CloseTabParams {}, &mut context).expect("Failed to execute close_tab tool");

    assert!(result.success, "Close tab should succeed");
    info!("Closed tab: {}", serde_json::to_string_pretty(&result.data.unwrap()).unwrap());

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Verify we now have one less tab
    let mut context = ToolContext::new(&session);
    let result = tab_list_tool.execute_typed(TabListParams {}, &mut context).expect("Failed to execute tab_list tool");

    let count_after = result.data.unwrap()["count"].as_u64().unwrap();
    info!("Tab count after closing: {}", count_after);
    assert_eq!(count_after, count_before - 1, "Should have one less tab after closing");
}

#[test]
#[ignore]
fn test_tab_workflow() {
    // Test a complete workflow: create multiple tabs, switch between them, list them, and close one
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Start with first tab
    session.navigate("data:text/html,<html><body><h1>Tab 1</h1></body></html>").expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(300));

    // Create second tab
    let new_tab_tool = NewTabTool::default();
    let mut context = ToolContext::new(&session);

    new_tab_tool
        .execute_typed(
            NewTabParams { url: "data:text/html,<html><body><h1>Tab 2</h1></body></html>".to_string() },
            &mut context,
        )
        .expect("Failed to create tab 2");

    std::thread::sleep(std::time::Duration::from_millis(300));

    // Create third tab
    let mut context = ToolContext::new(&session);
    new_tab_tool
        .execute_typed(
            NewTabParams { url: "data:text/html,<html><body><h1>Tab 3</h1></body></html>".to_string() },
            &mut context,
        )
        .expect("Failed to create tab 3");

    std::thread::sleep(std::time::Duration::from_millis(300));

    // List all tabs
    let tab_list_tool = TabListTool::default();
    let mut context = ToolContext::new(&session);

    let result = tab_list_tool.execute_typed(TabListParams {}, &mut context).expect("Failed to list tabs");

    let count = result.data.as_ref().unwrap()["count"].as_u64().unwrap();
    info!("Total tabs: {}", count);
    assert!(count >= 3, "Should have at least 3 tabs, got {}", count);
    info!("All tabs: {}", result.data.unwrap()["summary"].as_str().unwrap());

    // Switch to second tab (index 1)
    let switch_tab_tool = SwitchTabTool::default();
    let mut context = ToolContext::new(&session);

    let result =
        switch_tab_tool.execute_typed(SwitchTabParams { index: 1 }, &mut context).expect("Failed to switch to tab 1");

    assert!(result.success);
    assert_eq!(result.data.unwrap()["index"].as_u64(), Some(1));

    std::thread::sleep(std::time::Duration::from_millis(300));

    // Close the current tab (tab 2, index 1)
    let close_tab_tool = CloseTabTool::default();
    let mut context = ToolContext::new(&session);

    let result = close_tab_tool.execute_typed(CloseTabParams {}, &mut context).expect("Failed to close tab");

    assert!(result.success);
    info!("Closed: {}", result.data.unwrap()["message"].as_str().unwrap());

    std::thread::sleep(std::time::Duration::from_millis(300));

    // List tabs again to verify we have 2 tabs left
    let mut context = ToolContext::new(&session);
    let result = tab_list_tool.execute_typed(TabListParams {}, &mut context).expect("Failed to list tabs");

    let final_count = result.data.unwrap()["count"].as_u64().unwrap();
    info!("Final tab count: {}", final_count);
    assert_eq!(final_count, count - 1, "Should have one less tab after closing");
}
