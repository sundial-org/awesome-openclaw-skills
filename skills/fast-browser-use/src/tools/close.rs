use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the close tool (no parameters needed)
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct CloseParams {}

/// Tool for closing the browser
#[derive(Default)]
pub struct CloseTool;

impl Tool for CloseTool {
    type Params = CloseParams;

    fn name(&self) -> &str {
        "close"
    }

    fn execute_typed(&self, _params: CloseParams, context: &mut ToolContext) -> Result<ToolResult> {
        // Note: Closing the browser via BrowserSession is tricky because we hold a reference
        // In a real implementation, this would need to signal the session owner to close
        // For now, we'll close all tabs as a proxy for closing the browser

        context
            .session
            .close()
            .map_err(|e| BrowserError::ToolExecutionFailed { tool: "close".to_string(), reason: e.to_string() })?;

        Ok(ToolResult::success_with(serde_json::json!({
            "message": "Browser closed successfully"
        })))
    }
}
