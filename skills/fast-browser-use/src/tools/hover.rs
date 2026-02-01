use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the hover tool
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct HoverParams {
    /// CSS selector (use either this or index, not both)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub selector: Option<String>,

    /// Element index from DOM tree (use either this or selector, not both)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub index: Option<usize>,
}

/// Tool for hovering over elements
#[derive(Default)]
pub struct HoverTool;

const HOVER_JS: &str = include_str!("hover.js");

impl Tool for HoverTool {
    type Params = HoverParams;

    fn name(&self) -> &str {
        "hover"
    }

    fn execute_typed(&self, params: HoverParams, context: &mut ToolContext) -> Result<ToolResult> {
        // Validate that exactly one selector method is provided
        match (&params.selector, &params.index) {
            (Some(_), Some(_)) => {
                return Err(BrowserError::ToolExecutionFailed {
                    tool: "hover".to_string(),
                    reason: "Cannot specify both 'selector' and 'index'. Use one or the other.".to_string(),
                });
            }
            (None, None) => {
                return Err(BrowserError::ToolExecutionFailed {
                    tool: "hover".to_string(),
                    reason: "Must specify either 'selector' or 'index'.".to_string(),
                });
            }
            _ => {}
        }

        let css_selector = if let Some(selector) = params.selector {
            selector
        } else if let Some(index) = params.index {
            let dom = context.get_dom()?;
            let selector = dom
                .get_selector(index)
                .ok_or_else(|| BrowserError::ElementNotFound(format!("No element with index {}", index)))?;
            selector.clone()
        } else {
            unreachable!("Validation above ensures one field is Some")
        };

        // Find the element (to verify it exists)

        // Scroll into view if needed, then hover
        let selector_json = serde_json::to_string(&css_selector).expect("serializing CSS selector never fails");
        let hover_js = HOVER_JS.replace("__SELECTOR__", &selector_json);

        let result = context
            .session
            .tab()?
            .evaluate(&hover_js, false)
            .map_err(|e| BrowserError::ToolExecutionFailed { tool: "hover".to_string(), reason: e.to_string() })?;

        // Parse the JSON string returned by JavaScript
        let result_json: serde_json::Value = if let Some(serde_json::Value::String(json_str)) = result.value {
            serde_json::from_str(&json_str)
                .unwrap_or(serde_json::json!({"success": false, "error": "Failed to parse result"}))
        } else {
            result.value.unwrap_or(serde_json::json!({"success": false, "error": "No result returned"}))
        };

        if result_json["success"].as_bool() == Some(true) {
            Ok(ToolResult::success_with(serde_json::json!({
                "selector": css_selector,
                "element": {
                    "tagName": result_json["tagName"],
                    "id": result_json["id"],
                    "className": result_json["className"]
                }
            })))
        } else {
            Err(BrowserError::ToolExecutionFailed {
                tool: "hover".to_string(),
                reason: result_json["error"].as_str().unwrap_or("Unknown error").to_string(),
            })
        }
    }
}
