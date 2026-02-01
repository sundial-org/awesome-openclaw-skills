use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the go_forward tool (no parameters needed)
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct GoForwardParams {}

/// Tool for navigating forward in browser history
#[derive(Default)]
pub struct GoForwardTool;

impl Tool for GoForwardTool {
    type Params = GoForwardParams;

    fn name(&self) -> &str {
        "go_forward"
    }

    fn execute_typed(&self, _params: GoForwardParams, context: &mut ToolContext) -> Result<ToolResult> {
        context
            .session
            .go_forward()
            .map_err(|e| BrowserError::ToolExecutionFailed { tool: "go_forward".to_string(), reason: e.to_string() })?;

        // Get current URL after going forward
        let current_url = context.session.tab()?.get_url();

        Ok(ToolResult::success_with(serde_json::json!({
            "message": "Navigated forward in history",
            "url": current_url
        })))
    }
}
