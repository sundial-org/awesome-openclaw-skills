use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ExtractParams {
    /// CSS selector (optional, defaults to body)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub selector: Option<String>,

    /// Format: "text" or "html"
    #[serde(default = "default_format")]
    pub format: String,
}

fn default_format() -> String {
    "text".to_string()
}

#[derive(Default)]
pub struct ExtractContentTool;

impl Tool for ExtractContentTool {
    type Params = ExtractParams;

    fn name(&self) -> &str {
        "extract"
    }

    fn execute_typed(&self, params: ExtractParams, context: &mut ToolContext) -> Result<ToolResult> {
        let content = if let Some(selector) = &params.selector {
            let tab = context.session.tab()?;
            let element = context.session.find_element(&tab, selector)?;

            if params.format == "html" {
                element.get_content().map_err(|e| BrowserError::ToolExecutionFailed {
                    tool: "extract".to_string(),
                    reason: e.to_string(),
                })?
            } else {
                element.get_inner_text().map_err(|e| BrowserError::ToolExecutionFailed {
                    tool: "extract".to_string(),
                    reason: e.to_string(),
                })?
            }
        } else {
            // Extract from body
            let js_code = if params.format == "html" { "document.body.innerHTML" } else { "document.body.innerText" };

            let result = context
                .session
                .tab()?
                .evaluate(js_code, false)
                .map_err(|e| BrowserError::EvaluationFailed(e.to_string()))?;

            result.value.and_then(|v| v.as_str().map(String::from)).unwrap_or_default()
        };

        Ok(ToolResult::success_with(serde_json::json!({
            "content": content,
            "format": params.format,
            "length": content.len()
        })))
    }
}
