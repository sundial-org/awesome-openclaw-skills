use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct WaitParams {
    /// CSS selector to wait for
    pub selector: String,

    /// Timeout in milliseconds (default: 30000)
    #[serde(default = "default_timeout")]
    pub timeout_ms: u64,
}

fn default_timeout() -> u64 {
    30000
}

#[derive(Default)]
pub struct WaitTool;

impl Tool for WaitTool {
    type Params = WaitParams;

    fn name(&self) -> &str {
        "wait"
    }

    fn execute_typed(&self, params: WaitParams, context: &mut ToolContext) -> Result<ToolResult> {
        let start = std::time::Instant::now();

        context
            .session
            .tab()?
            .wait_for_element_with_custom_timeout(&params.selector, Duration::from_millis(params.timeout_ms))
            .map_err(|e| {
                BrowserError::Timeout(format!(
                    "Element '{}' not found within {} ms: {}",
                    params.selector, params.timeout_ms, e
                ))
            })?;

        let elapsed = start.elapsed().as_millis() as u64;

        Ok(ToolResult::success_with(serde_json::json!({
            "selector": params.selector,
            "found": true,
            "elapsed_ms": elapsed
        })))
    }
}
