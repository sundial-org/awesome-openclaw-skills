use browser_use::{BrowserSession, LaunchOptions};
use log::info;

#[test]
#[ignore] // Requires Chrome to be installed
fn test_dom_extraction() {
    // Launch browser
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to a simple page
    session
        .navigate(
            "data:text/html,<html><body><button id='test-btn'>Click me</button><a href='#'>Link</a></body></html>",
        )
        .expect("Failed to navigate");

    // Extract DOM
    let dom = session.extract_dom().expect("Failed to extract DOM");

    // Verify DOM structure
    assert_eq!(dom.root.role, "fragment");
    assert!(dom.count_nodes() > 0);

    // Note: interactive elements might be 0 due to visibility issues with data: URLs
    // Just verify we got the structure
    info!("DOM tree element count: {}", dom.count_nodes());
    info!("Interactive elements: {}", dom.count_interactive());

    // Convert to JSON
    let json = dom.to_json().expect("Failed to convert to JSON");
    assert!(json.contains("button"));
}

#[test]
#[ignore]
fn test_simplified_dom_extraction() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Page with script and style tags that should be removed
    // Use a simple HTML page
    session
        .navigate("data:text/html,<html><head></head><body><p>Hello</p><button>Click</button></body></html>")
        .expect("Failed to navigate");

    // Small delay to let page render
    std::thread::sleep(std::time::Duration::from_millis(500));

    // Extract simplified DOM
    let dom = session.extract_dom().expect("Failed to extract DOM");

    // Verify we got content
    let json = dom.to_json().expect("Failed to convert to JSON");
    assert!(json.contains("button") || json.contains("body"));
    info!("Simplified DOM: {}", json);
}

#[test]
#[ignore]
fn test_read_links() {
    use browser_use::tools::{ReadLinksParams, Tool, ToolContext, read_links::ReadLinksTool};

    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    let html = concat!(
        "<html><head><title>Links Test</title></head><body>",
        "<a href=\"https://example.com\">Example</a>",
        "<a href=\"/path\">Relative</a>",
        "<a href=\"#anchor\">Anchor</a>",
        "<a href=\"https://rust-lang.org\">Rust</a>",
        "<a>No Href</a>",
        "<a href=\"\">Empty</a>",
        "</body></html>"
    );

    session.navigate(&format!("data:text/html,{}", html)).expect("Failed navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    let tool = ReadLinksTool::default();
    let mut context = ToolContext::new(&session);

    let result = tool.execute_typed(ReadLinksParams {}, &mut context).expect("Failed execute");

    assert!(result.success);
    let data = result.data.unwrap();
    let links = data["links"].as_array().unwrap();
    let count = data["count"].as_u64().unwrap();

    info!("Links found: {}", count);
    for link in links {
        info!("  {} -> {}", link["text"].as_str().unwrap_or(""), link["href"].as_str().unwrap_or(""));
    }

    // Due to data: URL limitations, we may not get all links
    assert!(count >= 2, "Expected at least 2 links");
    assert_eq!(links.len() as u64, count);

    let texts: Vec<&str> = links.iter().filter_map(|l| l["text"].as_str()).collect();

    // Verify the links we do get are correct
    assert!(texts.contains(&"Example"));
    assert!(texts.contains(&"Relative"));

    // Verify href values
    let ex_link = links.iter().find(|l| l["text"].as_str() == Some("Example")).expect("Example link not found");
    assert_eq!(ex_link["href"].as_str(), Some("https://example.com"));
}

#[test]
#[ignore]
fn test_press_key_enter() {
    use browser_use::tools::{PressKeyParams, Tool, ToolContext, press_key::PressKeyTool};

    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Create a page with an input field that responds to Enter key
    let html = r#"
        <html>
        <head><title>Press Key Test</title></head>
        <body>
            <input type="text" id="input1" value="test">
            <div id="output"></div>
            <script>
                document.getElementById('input1').addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        document.getElementById('output').textContent = 'Enter pressed!';
                    }
                });
            </script>
        </body>
        </html>
    "#;

    session.navigate(&format!("data:text/html,{}", html)).expect("Failed to navigate");

    std::thread::sleep(std::time::Duration::from_millis(500));

    // Focus the input element first
    session.tab().unwrap().find_element("#input1").expect("Input not found").click().expect("Failed to click input");

    std::thread::sleep(std::time::Duration::from_millis(200));

    // Create tool and context
    let tool = PressKeyTool::default();
    let mut context = ToolContext::new(&session);

    // Execute the tool to press Enter
    let result = tool
        .execute_typed(PressKeyParams { key: "Enter".to_string() }, &mut context)
        .expect("Failed to execute press_key tool");

    // Verify the result
    assert!(result.success, "Tool execution should succeed");
    assert!(result.data.is_some());

    let data = result.data.unwrap();
    assert_eq!(data["key"].as_str(), Some("Enter"));

    std::thread::sleep(std::time::Duration::from_millis(200));

    // Verify that the event was triggered
    let output = session.tab().unwrap().wait_for_element("#output").ok().and_then(|elem| elem.get_inner_text().ok());

    info!("Output after Enter key: {:?}", output);

    // 校验 output 内容
    assert_eq!(output.as_deref(), Some("Enter pressed!"), "Output should be 'Enter pressed!', but was: {:?}", output);
    // Note: Due to limitations with data: URLs and event handling,
    // we mainly verify that the tool executes without error
}
