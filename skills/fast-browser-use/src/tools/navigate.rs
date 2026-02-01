use crate::{error::Result,
            tools::{Tool, ToolContext, ToolResult,
                    snapshot::{RenderMode, render_aria_tree},
                    utils::normalize_url}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the navigate tool
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct NavigateParams {
    /// URL to navigate to
    pub url: String,

    /// Wait for navigation to complete (default: true)
    #[serde(default = "default_wait")]
    pub wait_for_load: bool,
}

fn default_wait() -> bool {
    true
}

/// Tool for navigating to a URL
#[derive(Default)]
pub struct NavigateTool;

impl Tool for NavigateTool {
    type Params = NavigateParams;

    fn name(&self) -> &str {
        "navigate"
    }

    fn execute_typed(&self, params: NavigateParams, context: &mut ToolContext) -> Result<ToolResult> {
        // Normalize the URL
        let normalized_url = normalize_url(&params.url);

        // Navigate to normalized URL
        context.session.navigate(&normalized_url)?;

        // Wait for navigation if requested
        if params.wait_for_load {
            context.session.wait_for_navigation()?;
        }

        let snapshot = {
            let dom = context.get_dom()?;
            render_aria_tree(&dom.root, RenderMode::Ai, None)
        };

        Ok(ToolResult::success_with(serde_json::json!({
            "snapshot": snapshot
        })))
    }
}
