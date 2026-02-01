use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the click tool
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ClickParams {
    /// CSS selector (use either this or index, not both)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub selector: Option<String>,

    /// Element index from DOM tree (use either this or selector, not both)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub index: Option<usize>,
}

/// Tool for clicking elements
#[derive(Default)]
pub struct ClickTool;

impl Tool for ClickTool {
    type Params = ClickParams;

    fn name(&self) -> &str {
        "click"
    }

    fn execute_typed(&self, params: ClickParams, context: &mut ToolContext) -> Result<ToolResult> {
        // Validate that exactly one selector method is provided
        match (&params.selector, &params.index) {
            (Some(_), Some(_)) => {
                return Err(BrowserError::ToolExecutionFailed {
                    tool: "click".to_string(),
                    reason: "Cannot specify both 'selector' and 'index'. Use one or the other.".to_string(),
                });
            }
            (None, None) => {
                return Err(BrowserError::ToolExecutionFailed {
                    tool: "click".to_string(),
                    reason: "Must specify either 'selector' or 'index'.".to_string(),
                });
            }
            _ => {}
        }

        if let Some(selector) = params.selector {
            // CSS selector path
            let tab = context.session.tab()?;
            let element = context.session.find_element(&tab, &selector)?;
            element
                .click()
                .map_err(|e| BrowserError::ToolExecutionFailed { tool: "click".to_string(), reason: e.to_string() })?;

            Ok(ToolResult::success_with(serde_json::json!({
                "selector": selector,
                "method": "css"
            })))
        } else if let Some(index) = params.index {
            // Index path - convert index to CSS selector
            let css_selector = {
                let dom = context.get_dom()?;
                let selector = dom
                    .get_selector(index)
                    .ok_or_else(|| BrowserError::ElementNotFound(format!("No element with index {}", index)))?;
                selector.clone()
            };

            let tab = context.session.tab()?;
            let element = context.session.find_element(&tab, &css_selector)?;
            element
                .click()
                .map_err(|e| BrowserError::ToolExecutionFailed { tool: "click".to_string(), reason: e.to_string() })?;

            Ok(ToolResult::success_with(serde_json::json!({
                "index": index,
                "selector": css_selector,
                "method": "index"
            })))
        } else {
            unreachable!("Validation above ensures one field is Some")
        }
    }
}
