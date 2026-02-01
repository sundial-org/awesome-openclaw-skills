use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the press_key tool
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct PressKeyParams {
    /// Name of the key to press (e.g., "Enter", "Tab", "Escape", "ArrowDown", "F1", etc.)
    pub key: String,
}

/// Tool for pressing keyboard keys
#[derive(Default)]
pub struct PressKeyTool;

impl Tool for PressKeyTool {
    type Params = PressKeyParams;

    fn name(&self) -> &str {
        "press_key"
    }

    fn execute_typed(&self, params: PressKeyParams, context: &mut ToolContext) -> Result<ToolResult> {
        context
            .session
            .tab()?
            .press_key(&params.key)
            .map_err(|e| BrowserError::ToolExecutionFailed { tool: "press_key".to_string(), reason: e.to_string() })?;

        Ok(ToolResult::success_with(serde_json::json!({
            "key": params.key
        })))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_press_key_tool_metadata() {
        let tool = PressKeyTool;
        assert_eq!(tool.name(), "press_key");
        let schema = tool.parameters_schema();
        assert!(schema.is_object());
    }

    #[test]
    fn test_press_key_params_various_keys() {
        let test_keys = vec![
            "Enter",
            "Tab",
            "Escape",
            "Backspace",
            "Delete",
            "ArrowLeft",
            "ArrowRight",
            "ArrowUp",
            "ArrowDown",
            "Home",
            "End",
            "PageUp",
            "PageDown",
            "F1",
            "F12",
            "ShiftLeft",
            "MetaLeft",
            "Space",
        ];

        for key in test_keys {
            let json = serde_json::json!({ "key": key });
            let params: PressKeyParams = serde_json::from_value(json).unwrap();
            assert_eq!(params.key, key);
        }
    }
}
