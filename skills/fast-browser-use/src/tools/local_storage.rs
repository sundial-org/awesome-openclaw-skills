use crate::{error::{BrowserError, Result}, tools::{Tool, ToolContext, ToolResult}};
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct GetLocalStorageParams {
    /// The key to retrieve. If omitted, returns all key-value pairs.
    pub key: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct SetLocalStorageParams {
    pub key: String,
    pub value: String,
}

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct RemoveLocalStorageParams {
    /// The key to remove.
    pub key: String,
}

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct ClearLocalStorageParams;

#[derive(Default)]
pub struct GetLocalStorageTool;

impl Tool for GetLocalStorageTool {
    type Params = GetLocalStorageParams;

    fn name(&self) -> &str {
        "get_local_storage"
    }

        fn execute_typed(&self, params: Self::Params, context: &mut ToolContext) -> Result<ToolResult> {

            let (script, is_json) = if let Some(key) = &params.key {

                (format!(r#"window.localStorage.getItem("{}")"#, key.replace("\"", "\\\"")), false)

            } else {

                (r#"

                JSON.stringify((function() {

                    const items = {};

                    for (let i = 0; i < localStorage.length; i++) {

                        const key = localStorage.key(i);

                        items[key] = localStorage.getItem(key);

                    }

                    return items;

                })())

                "#.to_string(), true)

            };

    

            let remote_object = context.session.tab()?.evaluate(&script, false)

                .map_err(|e| BrowserError::EvaluationFailed(format!("Failed to get local storage: {}", e)))?;

    

            let value = remote_object.value.unwrap_or(Value::Null);

    

            if is_json {

                 if let Some(json_str) = value.as_str() {

                     let parsed: Value = serde_json::from_str(json_str)

                        .map_err(|e| BrowserError::EvaluationFailed(format!("Failed to parse local storage JSON: {}", e)))?;

                     return Ok(ToolResult::success_with(parsed));

                 }

            }

            

            Ok(ToolResult::success_with(value))

        }
}

#[derive(Default)]
pub struct SetLocalStorageTool;

impl Tool for SetLocalStorageTool {
    type Params = SetLocalStorageParams;

    fn name(&self) -> &str {
        "set_local_storage"
    }

    fn execute_typed(&self, params: Self::Params, context: &mut ToolContext) -> Result<ToolResult> {
        let script = format!(
            r#"window.localStorage.setItem("{}", "{}")"#,
            params.key.replace("\"", "\\\""),
            params.value.replace("\"", "\\\"")
        );

        context.session.tab()?.evaluate(&script, false)
            .map_err(|e| BrowserError::EvaluationFailed(format!("Failed to set local storage: {}", e)))?;

        Ok(ToolResult::success(None))
    }
}

#[derive(Default)]
pub struct RemoveLocalStorageTool;

impl Tool for RemoveLocalStorageTool {
    type Params = RemoveLocalStorageParams;

    fn name(&self) -> &str {
        "remove_local_storage"
    }

    fn execute_typed(&self, params: Self::Params, context: &mut ToolContext) -> Result<ToolResult> {
        let script = format!(r#"window.localStorage.removeItem("{}")"#, params.key.replace("\"", "\\\""));

        context.session.tab()?.evaluate(&script, false)
            .map_err(|e| BrowserError::EvaluationFailed(format!("Failed to remove local storage item: {}", e)))?;

        Ok(ToolResult::success(None))
    }
}

#[derive(Default)]
pub struct ClearLocalStorageTool;

impl Tool for ClearLocalStorageTool {
    type Params = ClearLocalStorageParams;

    fn name(&self) -> &str {
        "clear_local_storage"
    }

    fn execute_typed(&self, _params: Self::Params, context: &mut ToolContext) -> Result<ToolResult> {
        context.session.tab()?.evaluate("window.localStorage.clear()", false)
            .map_err(|e| BrowserError::EvaluationFailed(format!("Failed to clear local storage: {}", e)))?;

        Ok(ToolResult::success(None))
    }
}
