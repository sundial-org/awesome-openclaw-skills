use crate::{error::Result,
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the close_tab tool (no parameters needed)
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct CloseTabParams {}

/// Tool for closing the current active tab
#[derive(Default)]
pub struct CloseTabTool;

impl Tool for CloseTabTool {
    type Params = CloseTabParams;

    fn name(&self) -> &str {
        "close_tab"
    }

    fn execute_typed(&self, _params: CloseTabParams, context: &mut ToolContext) -> Result<ToolResult> {
        // Get the current tab info before closing
        let active_tab = context.session.tab()?;
        let tab_title = active_tab.get_title().unwrap_or_default();
        let tab_url = active_tab.get_url();

        // Get the current tab index
        let tabs = context.session.get_tabs()?;
        let current_index = tabs.iter().position(|tab| std::sync::Arc::ptr_eq(tab, &active_tab)).unwrap_or(0);

        // Close the active tab
        active_tab
            .close(true)
            .map_err(|e| crate::error::BrowserError::TabOperationFailed(format!("Failed to close tab: {}", e)))?;

        let message = format!("Closed tab [{}]: {} ({})", current_index, tab_title, tab_url);

        Ok(ToolResult::success_with(serde_json::json!({
            "index": current_index,
            "title": tab_title,
            "url": tab_url,
            "message": message
        })))
    }
}
