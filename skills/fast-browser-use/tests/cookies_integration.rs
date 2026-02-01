use browser_use::{BrowserSession, LaunchOptions,
                  tools::{cookies::{CookieParam, GetCookiesParams, SetCookiesParams},
                          Tool, ToolContext, cookies::{GetCookiesTool, SetCookiesTool}}};
use log::info;

#[test]
#[ignore]
fn test_cookies_workflow() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to a domain first
    session.navigate("https://example.com").expect("Failed to navigate");
    
    // Create tool context
    let mut context = ToolContext::new(&session);
    let set_cookies_tool = SetCookiesTool::default();
    let get_cookies_tool = GetCookiesTool::default();

    // 1. Set a cookie
    let cookie = CookieParam {
        name: "test_cookie".to_string(),
        value: "test_value".to_string(),
        domain: Some("example.com".to_string()),
        path: Some("/".to_string()),
        secure: Some(false),
        http_only: Some(false),
        same_site: None,
        expires: None,
        url: Some("https://example.com".to_string()),
    };

    let set_result = set_cookies_tool
        .execute_typed(SetCookiesParams { cookies: vec![cookie] }, &mut context)
        .expect("Failed to execute set_cookies");

    assert!(set_result.success, "set_cookies should succeed");

    // 2. Get cookies
    let get_result = get_cookies_tool
        .execute_typed(GetCookiesParams { urls: None }, &mut context)
        .expect("Failed to execute get_cookies");

    assert!(get_result.success, "get_cookies should succeed");
    
    let cookies_json = get_result.data.unwrap();
    let cookies = cookies_json.as_array().expect("Data should be an array");
    
    // Verify the cookie was set
    let found = cookies.iter().any(|c| {
        c["name"].as_str() == Some("test_cookie") && c["value"].as_str() == Some("test_value")
    });

    assert!(found, "Should find the set cookie");
    
    info!("Successfully set and retrieved cookies!");
}
