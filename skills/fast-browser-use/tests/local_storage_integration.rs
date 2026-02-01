use browser_use::{BrowserSession, LaunchOptions,
                  tools::{local_storage::{ClearLocalStorageParams, GetLocalStorageParams, RemoveLocalStorageParams, SetLocalStorageParams},
                          Tool, ToolContext, local_storage::{ClearLocalStorageTool, GetLocalStorageTool, RemoveLocalStorageTool, SetLocalStorageTool}}};
use log::info;

#[test]
#[ignore]
fn test_local_storage_workflow() {
    let session = BrowserSession::launch(LaunchOptions::new().headless(true)).expect("Failed to launch browser");

    // Navigate to a domain to have a context for localStorage
    session.navigate("https://example.com").expect("Failed to navigate");

    let mut context = ToolContext::new(&session);
    let get_tool = GetLocalStorageTool::default();
    let set_tool = SetLocalStorageTool::default();
    let remove_tool = RemoveLocalStorageTool::default();
    let clear_tool = ClearLocalStorageTool::default();

    // 1. Set a value
    let set_result = set_tool
        .execute_typed(SetLocalStorageParams { key: "test_key".to_string(), value: "test_value".to_string() }, &mut context)
        .expect("Failed to set localStorage");
    assert!(set_result.success);

    // 2. Get the value
    let get_result = get_tool
        .execute_typed(GetLocalStorageParams { key: Some("test_key".to_string()) }, &mut context)
        .expect("Failed to get localStorage");
    assert!(get_result.success);
    assert_eq!(get_result.data.unwrap().as_str(), Some("test_value"));

    // 3. Set another value
    set_tool
        .execute_typed(SetLocalStorageParams { key: "key2".to_string(), value: "value2".to_string() }, &mut context)
        .expect("Failed to set localStorage key2");

    // 4. Get all values
    let get_all_result = get_tool
        .execute_typed(GetLocalStorageParams { key: None }, &mut context)
        .expect("Failed to get all localStorage");
    let all_data = get_all_result.data.unwrap();
    println!("All data: {:?}", all_data);
    assert_eq!(all_data["test_key"].as_str(), Some("test_value"));
    assert_eq!(all_data["key2"].as_str(), Some("value2"));

    // 5. Remove one value
    let remove_result = remove_tool
        .execute_typed(RemoveLocalStorageParams { key: "test_key".to_string() }, &mut context)
        .expect("Failed to remove localStorage item");
    assert!(remove_result.success);

    // Verify removal
    let get_removed = get_tool
        .execute_typed(GetLocalStorageParams { key: Some("test_key".to_string()) }, &mut context)
        .expect("Failed to get localStorage");
    assert!(get_removed.data.unwrap().is_null());

    // 6. Clear all
    let clear_result = clear_tool
        .execute_typed(ClearLocalStorageParams, &mut context)
        .expect("Failed to clear localStorage");
    assert!(clear_result.success);

    // Verify clear
    let get_all_cleared = get_tool
        .execute_typed(GetLocalStorageParams { key: None }, &mut context)
        .expect("Failed to get all localStorage after clear");
    
    // The implementation returns an empty object {}
    let cleared_obj = get_all_cleared.data.unwrap();
    assert!(cleared_obj.as_object().unwrap().is_empty());

    info!("LocalStorage workflow passed!");
}
