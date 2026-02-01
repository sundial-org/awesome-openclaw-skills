use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the scroll tool
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ScrollParams {
    /// Amount to scroll in pixels (positive for down, negative for up).
    /// If not provided, scrolls to the bottom of the page.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub amount: Option<i32>,
}

/// Tool for scrolling the page
#[derive(Default)]
pub struct ScrollTool;

const SCROLL_JS: &str = include_str!("scroll.js");

impl Tool for ScrollTool {
    type Params = ScrollParams;

    fn name(&self) -> &str {
        "scroll"
    }

    fn execute_typed(&self, params: ScrollParams, context: &mut ToolContext) -> Result<ToolResult> {
        let config = serde_json::json!({
            "amount": params.amount
        });
        let scroll_js = SCROLL_JS.replace("__SCROLL_CONFIG__", &config.to_string());

        let result = context
            .session
            .tab()?
            .evaluate(&scroll_js, true)
            .map_err(|e| BrowserError::ToolExecutionFailed { tool: "scroll".to_string(), reason: e.to_string() })?;

        // Parse the JSON string returned by JavaScript
        let result_json: serde_json::Value = if let Some(serde_json::Value::String(json_str)) = result.value {
            serde_json::from_str(&json_str).unwrap_or(serde_json::json!({"actualScroll": 0, "isAtBottom": false}))
        } else {
            result.value.unwrap_or(serde_json::json!({"actualScroll": 0, "isAtBottom": false}))
        };

        let actual_scroll = result_json["actualScroll"].as_i64().unwrap_or(0);
        let is_at_bottom = result_json["isAtBottom"].as_bool().unwrap_or(false);

        let message = if is_at_bottom {
            format!("Scrolled {} pixels. Reached the bottom of the page.", actual_scroll)
        } else {
            format!("Scrolled {} pixels. Did not reach the bottom of the page.", actual_scroll)
        };

        Ok(ToolResult::success_with(serde_json::json!({
            "scrolled": actual_scroll,
            "isAtBottom": is_at_bottom,
            "message": message
        })))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_scroll_params_with_amount() {
        let json = serde_json::json!({
            "amount": 500
        });

        let params: ScrollParams = serde_json::from_value(json).unwrap();
        assert_eq!(params.amount, Some(500));
    }

    #[test]
    fn test_scroll_params_negative_amount() {
        let json = serde_json::json!({
            "amount": -300
        });

        let params: ScrollParams = serde_json::from_value(json).unwrap();
        assert_eq!(params.amount, Some(-300));
    }

    #[test]
    fn test_scroll_params_no_amount() {
        let json = serde_json::json!({});

        let params: ScrollParams = serde_json::from_value(json).unwrap();
        assert_eq!(params.amount, None);
    }
}
