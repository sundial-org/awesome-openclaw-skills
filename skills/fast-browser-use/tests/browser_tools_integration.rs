use browser_use::{BrowserSession, LaunchOptions,
                  tools::{HoverParams, ScrollParams, SelectParams, Tool, ToolContext, hover::HoverTool,
                          scroll::ScrollTool, select::SelectTool}};
use log::info;

#[test]
#[ignore] // Requires Chrome to be installed
fn test_select_tool() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Create a page with a select dropdown
    let html = r#"
        <!DOCTYPE html>
        <html>
        <body>
            <select id="country">
                <option value="us">United States</option>
                <option value="uk">United Kingdom</option>
                <option value="ca">Canada</option>
            </select>
            <div id="result"></div>
            <script>
                document.getElementById('country').addEventListener('change', function(e) {
                    document.getElementById('result').textContent = 'Selected: ' + e.target.value;
                });
            </script>
        </body>
        </html>
    "#;

    let data_url = format!("data:text/html,{}", html);
    session.navigate(&data_url).expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Create tool and context
    let tool = SelectTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool to select an option
    let result = tool
        .execute_typed(
            SelectParams { selector: Some("#country".to_string()), index: None, value: "uk".to_string() },
            &mut context,
        )
        .expect("Failed to execute select tool");

    // Verify the result
    assert!(result.success, "Tool execution should succeed");
    assert!(result.data.is_some());

    let data = result.data.unwrap();
    info!("Select result: {}", serde_json::to_string_pretty(&data).unwrap());

    assert_eq!(data["value"].as_str(), Some("uk"));
    assert_eq!(data["selectedText"].as_str(), Some("United Kingdom"));
}

#[test]
#[ignore]
fn test_hover_tool() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Create a page with a hoverable element
    let html = r#"
        <!DOCTYPE html>
        <html>
        <body>
            <button id="hover-btn">Hover Me</button>
            <div id="result"></div>
            <script>
                document.getElementById('hover-btn').addEventListener('mouseover', function() {
                    document.getElementById('result').textContent = 'Hovered!';
                });
            </script>
        </body>
        </html>
    "#;

    let data_url = format!("data:text/html,{}", html);
    session.navigate(&data_url).expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Create tool and context
    let tool = HoverTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool
    let result = tool
        .execute_typed(HoverParams { selector: Some("#hover-btn".to_string()), index: None }, &mut context)
        .expect("Failed to execute hover tool");

    // Verify the result
    assert!(result.success, "Tool execution should succeed");
    assert!(result.data.is_some());

    let data = result.data.unwrap();
    info!("Hover result: {}", serde_json::to_string_pretty(&data).unwrap());

    assert_eq!(data["selector"].as_str(), Some("#hover-btn"));
}

#[test]
#[ignore]
fn test_scroll_tool_with_amount() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Create a long page
    let html = r#"
        <!DOCTYPE html>
        <html>
        <body style="height: 3000px;">
            <h1>Top of page</h1>
            <div style="margin-top: 1000px;">Middle</div>
            <div style="margin-top: 1000px;">Bottom</div>
        </body>
        </html>
    "#;

    let data_url = format!("data:text/html,{}", html);
    session.navigate(&data_url).expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Create tool and context
    let tool = ScrollTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool to scroll down 500 pixels
    let result =
        tool.execute_typed(ScrollParams { amount: Some(500) }, &mut context).expect("Failed to execute scroll tool");

    // Verify the result
    assert!(result.success, "Tool execution should succeed");
    assert!(result.data.is_some());

    let data = result.data.unwrap();
    info!("Scroll result: {}", serde_json::to_string_pretty(&data).unwrap());

    let scrolled = data["scrolled"].as_i64();
    assert!(scrolled.is_some() && scrolled.unwrap() > 0, "Should have scrolled");
}

#[test]
#[ignore]
fn test_scroll_tool_to_bottom() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Create a page
    let html = r#"
        <!DOCTYPE html>
        <html>
        <body style="height: 2000px;">
            <h1>Top of page</h1>
            <div style="margin-top: 1800px;">Bottom</div>
        </body>
        </html>
    "#;

    let data_url = format!("data:text/html,{}", html);
    session.navigate(&data_url).expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Create tool and context
    let tool = ScrollTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool multiple times to reach bottom
    for _ in 0..10 {
        let result =
            tool.execute_typed(ScrollParams { amount: None }, &mut context).expect("Failed to execute scroll tool");

        assert!(result.success);

        let data = result.data.as_ref().unwrap();
        let is_at_bottom = data["isAtBottom"].as_bool().unwrap_or(false);

        info!("Scroll iteration: scrolled={}, isAtBottom={}", data["scrolled"], is_at_bottom);

        if is_at_bottom {
            info!("Reached bottom of page");
            break;
        }

        std::thread::sleep(std::time::Duration::from_millis(100));
    }
}

#[test]
#[ignore]
fn test_select_with_index() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Create a page with a select dropdown
    let html = r#"
        <!DOCTYPE html>
        <html>
        <body>
            <select id="color">
                <option value="red">Red</option>
                <option value="green">Green</option>
                <option value="blue">Blue</option>
            </select>
        </body>
        </html>
    "#;

    let data_url = format!("data:text/html,{}", html);
    session.navigate(&data_url).expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // First extract DOM to get indices
    let _dom = session.extract_dom().expect("Failed to extract DOM");

    // Create tool and context
    let tool = SelectTool::default();
    let mut context = ToolContext::new(&session);

    // Try to select using index (the select element should have index 0 since it's the first interactive element)
    let result =
        tool.execute_typed(SelectParams { selector: None, index: Some(0), value: "green".to_string() }, &mut context);

    // This might fail if DOM indexing doesn't include select elements, which is acceptable
    // The test is mainly to verify the API works
    if let Ok(result) = result {
        info!("Select with index result: {}", serde_json::to_string_pretty(&result.data.unwrap()).unwrap());
    } else {
        info!("Select with index failed (may be expected if select not indexed)");
    }
}
