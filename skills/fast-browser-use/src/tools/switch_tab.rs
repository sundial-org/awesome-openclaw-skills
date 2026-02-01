use crate::{error::Result,
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the switch_tab tool
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct SwitchTabParams {
    /// Tab index to switch to
    pub index: usize,
}

/// Tool for switching to a specific tab
#[derive(Default)]
pub struct SwitchTabTool;

impl Tool for SwitchTabTool {
    type Params = SwitchTabParams;

    fn name(&self) -> &str {
        "switch_tab"
    }

    fn execute_typed(&self, params: SwitchTabParams, context: &mut ToolContext) -> Result<ToolResult> {
        // Get all tabs to validate index
        let tabs = context.session.get_tabs()?;

        if params.index >= tabs.len() {
            return Ok(ToolResult::failure(format!(
                "Invalid tab index: {}. Valid range: 0-{}",
                params.index,
                tabs.len() - 1
            )));
        }

        // Note: We can't directly call session.switch_tab() because we only have &BrowserSession
        // Instead, we'll need to work with the browser directly
        // However, since this requires mutable access to the session, we need to handle this differently

        // Get the tab at the specified index
        let target_tab = tabs[params.index].clone();

        // Activate the tab
        target_tab.activate().map_err(|e| {
            crate::error::BrowserError::TabOperationFailed(format!("Failed to activate tab {}: {}", params.index, e))
        })?;

        // Get updated tab info
        let title = target_tab.get_title().unwrap_or_default();
        let url = target_tab.get_url();

        // Build tab list summary
        let mut tab_list_str = String::new();
        for (idx, tab) in tabs.iter().enumerate() {
            let tab_title = tab.get_title().unwrap_or_default();
            let tab_url = tab.get_url();
            tab_list_str.push_str(&format!("[{}] {} ({})\n", idx, tab_title, tab_url));
        }

        let summary = format!("Switched to tab {}\nAll Tabs:\n{}", params.index, tab_list_str);

        Ok(ToolResult::success_with(serde_json::json!({
            "index": params.index,
            "title": title,
            "url": url,
            "message": summary
        })))
    }
}
