//! MCP (Model Context Protocol) server implementation for browser automation
//!
//! This module provides rmcp-compatible tools by wrapping the existing tool implementations.

pub mod handler;
pub use handler::BrowserServer;

use crate::tools::{self, Tool, ToolContext, ToolResult as InternalToolResult};
use rmcp::{ErrorData as McpError,
           handler::server::wrapper::Parameters,
           model::{CallToolResult, Content},
           tool, tool_router};

/// Convert internal ToolResult to MCP CallToolResult
fn convert_result(result: InternalToolResult) -> Result<CallToolResult, McpError> {
    if result.success {
        let text = if let Some(data) = result.data {
            serde_json::to_string_pretty(&data).unwrap_or_else(|_| data.to_string())
        } else {
            "Success".to_string()
        };
        Ok(CallToolResult::success(vec![Content::text(text)]))
    } else {
        let error_msg = result.error.unwrap_or_else(|| "Unknown error".to_string());
        Err(McpError::internal_error(error_msg, None))
    }
}

/// Macro to register MCP tools by automatically generating wrapper functions
macro_rules! register_mcp_tools {
    ($($mcp_name:ident => $tool_type:ty, $description:expr);* $(;)?) => {
        #[tool_router]
        impl BrowserServer {
            $(
                #[tool(description = $description)]
                fn $mcp_name(
                    &self,
                    params: Parameters<<$tool_type as Tool>::Params>,
                ) -> Result<CallToolResult, McpError> {
                    let session = self.session();
                    let mut context = ToolContext::new(&*session);
                    let tool = <$tool_type>::default();
                    let result = tool.execute_typed(params.0, &mut context)
                        .map_err(|e| McpError::internal_error(e.to_string(), None))?;
                    convert_result(result)
                }
            )*
        }
    };
}

// Register all MCP tools using the macro
register_mcp_tools! {
    // ---- Navigation and Browser Flow ----
    browser_navigate => tools::navigate::NavigateTool, "Navigate to a specified URL in the browser";
    browser_go_back => tools::go_back::GoBackTool, "Navigate back in browser history";
    browser_go_forward => tools::go_forward::GoForwardTool, "Navigate forward in browser history";
    browser_close => tools::close::CloseTool, "Close the browser when the task is complete";

    // ---- Page Content and Extraction ----
    browser_get_markdown => tools::markdown::GetMarkdownTool, "Get the markdown content of the current page (use this tool only for information extraction; for interaction use the snapshot tool instead)";
    browser_snapshot => tools::snapshot::SnapshotTool, "Get a snapshot of the current page with indexed interactive elements for interaction";
    browser_screenshot => tools::screenshot::ScreenshotTool, "Capture a screenshot of the current page";
    // browser_get_text => tools::extract::ExtractContentTool, "Extract text or HTML content from the page or an element";
    browser_evaluate => tools::evaluate::EvaluateTool, "Execute JavaScript code in the browser context";

    // ---- Interaction ----
    browser_click => tools::click::ClickTool, "Click on an element specified by CSS selector or index (index obtained from browser_snapshot tool)";
    browser_hover => tools::hover::HoverTool, "Hover over an element specified by CSS selector or index (index obtained from browser_snapshot tool)";
    browser_select => tools::select::SelectTool, "Select an option in a dropdown element by CSS selector or index (index obtained from browser_snapshot tool)";
    browser_input_fill => tools::input::InputTool, "Type text into an input element specified by CSS selector or index (index obtained from browser_snapshot tool)";
    browser_press_key => tools::press_key::PressKeyTool, "Press a key on the keyboard";
    browser_scroll => tools::scroll::ScrollTool, "Scroll the page by a specified amount or to the bottom";
    browser_wait => tools::wait::WaitTool, "Wait for an element to appear on the page";

    // ---- Tab Management ----
    browser_new_tab => tools::new_tab::NewTabTool, "Open a new tab and navigate to the specified URL";
    browser_tab_list => tools::tab_list::TabListTool, "Get the list of all browser tabs with their titles and URLs";
    browser_switch_tab => tools::switch_tab::SwitchTabTool, "Switch to a specific tab by index";
    browser_close_tab => tools::close_tab::CloseTabTool, "Close the current active tab";
}
