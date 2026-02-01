use crate::{browser::debug::{ConsoleLog, NetworkError}, error::Result, tools::{Tool, ToolContext, ToolResult}};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct GetConsoleLogsParams {
    // No params needed, gets all logs since session start
}

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct GetNetworkErrorsParams {
    // No params needed
}

#[derive(Default)]
pub struct GetConsoleLogsTool;

impl Tool for GetConsoleLogsTool {
    type Params = GetConsoleLogsParams;

    fn name(&self) -> &str {
        "get_console_logs"
    }

    fn execute_typed(&self, _params: Self::Params, context: &mut ToolContext) -> Result<ToolResult> {
        let logs = context.session.get_console_logs()?;
        Ok(ToolResult::success_with(logs))
    }
}

#[derive(Default)]
pub struct GetNetworkErrorsTool;

impl Tool for GetNetworkErrorsTool {
    type Params = GetNetworkErrorsParams;

    fn name(&self) -> &str {
        "get_network_errors"
    }

    fn execute_typed(&self, _params: Self::Params, context: &mut ToolContext) -> Result<ToolResult> {
        let errors = context.session.get_network_errors()?;
        Ok(ToolResult::success_with(errors))
    }
}
