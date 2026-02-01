use crate::{error::Result,
            tools::{Tool, ToolContext, ToolResult,
                    snapshot::{RenderMode, render_aria_tree},
                    utils::normalize_url}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the new_tab tool
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct NewTabParams {
    /// URL to open in the new tab
    pub url: String,
}

/// Tool for opening a new tab
#[derive(Default)]
pub struct NewTabTool;

impl Tool for NewTabTool {
    type Params = NewTabParams;

    fn name(&self) -> &str {
        "new_tab"
    }

    fn execute_typed(&self, params: NewTabParams, context: &mut ToolContext) -> Result<ToolResult> {
        let normalized_url = normalize_url(&params.url);
        let tab = context
            .session
            .browser()
            .new_tab()
            .map_err(|e| crate::error::BrowserError::TabOperationFailed(format!("Failed to create tab: {}", e)))?;

        // Navigate to the normalized URL
        tab.navigate_to(&normalized_url).map_err(|e| {
            crate::error::BrowserError::NavigationFailed(format!("Failed to navigate to {}: {}", normalized_url, e))
        })?;

        // Wait for navigation to complete
        tab.wait_until_navigated().map_err(|e| {
            crate::error::BrowserError::NavigationFailed(format!(
                "Navigation to {} did not complete: {}",
                normalized_url, e
            ))
        })?;

        // Bring the new tab to front
        tab.activate()
            .map_err(|e| crate::error::BrowserError::TabOperationFailed(format!("Failed to activate tab: {}", e)))?;

        let snapshot = {
            let dom = context.get_dom()?;
            render_aria_tree(&dom.root, RenderMode::Ai, None)
        };

        Ok(ToolResult::success_with(serde_json::json!({
            "snapshot": snapshot
        })))
    }
}
