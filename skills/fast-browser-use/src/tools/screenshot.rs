use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ScreenshotParams {
    /// Path to save the screenshot
    pub path: String,

    /// Capture full page (default: false)
    #[serde(default)]
    pub full_page: bool,
}

#[derive(Default)]
pub struct ScreenshotTool;

impl Tool for ScreenshotTool {
    type Params = ScreenshotParams;

    fn name(&self) -> &str {
        "screenshot"
    }

    fn execute_typed(&self, params: ScreenshotParams, context: &mut ToolContext) -> Result<ToolResult> {
        let screenshot_data = context
            .session
            .tab()?
            .capture_screenshot(
                headless_chrome::protocol::cdp::Page::CaptureScreenshotFormatOption::Png,
                None,
                None,
                params.full_page,
            )
            .map_err(|e| BrowserError::ScreenshotFailed(e.to_string()))?;

        std::fs::write(&params.path, &screenshot_data)
            .map_err(|e| BrowserError::ScreenshotFailed(format!("Failed to save screenshot: {}", e)))?;

        Ok(ToolResult::success_with(serde_json::json!({
            "path": params.path,
            "size_bytes": screenshot_data.len(),
            "full_page": params.full_page
        })))
    }
}
