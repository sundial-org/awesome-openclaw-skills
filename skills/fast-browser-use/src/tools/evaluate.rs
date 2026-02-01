use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct EvaluateParams {
    /// JavaScript code to execute
    pub code: String,

    /// Wait for promise resolution (default: false)
    #[serde(default)]
    pub await_promise: bool,
}

#[derive(Default)]
pub struct EvaluateTool;

impl Tool for EvaluateTool {
    type Params = EvaluateParams;

    fn name(&self) -> &str {
        "evaluate"
    }

    fn execute_typed(&self, params: EvaluateParams, context: &mut ToolContext) -> Result<ToolResult> {
        let result = context
            .session
            .tab()?
            .evaluate(&params.code, params.await_promise)
            .map_err(|e| BrowserError::EvaluationFailed(e.to_string()))?;

        let result_value = result.value.unwrap_or(Value::Null);

        Ok(ToolResult::success_with(serde_json::json!({
            "result": result_value
        })))
    }
}
