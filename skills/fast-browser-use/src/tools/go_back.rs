use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the go_back tool (no parameters needed)
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct GoBackParams {}

/// Tool for navigating back in browser history
#[derive(Default)]
pub struct GoBackTool;

impl Tool for GoBackTool {
    type Params = GoBackParams;

    fn name(&self) -> &str {
        "go_back"
    }

    fn execute_typed(&self, _params: GoBackParams, context: &mut ToolContext) -> Result<ToolResult> {
        context
            .session
            .go_back()
            .map_err(|e| BrowserError::ToolExecutionFailed { tool: "go_back".to_string(), reason: e.to_string() })?;

        // Get current URL after going back
        let current_url = context.session.tab()?.get_url();

        Ok(ToolResult::success_with(serde_json::json!({
            "message": "Navigated back in history",
            "url": current_url
        })))
    }
}
