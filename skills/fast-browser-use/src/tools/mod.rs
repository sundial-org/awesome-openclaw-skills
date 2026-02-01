//! Browser automation tools module
//!
//! This module provides a framework for browser automation tools and
//! includes implementations of common browser operations.

pub mod click;
pub mod close;
pub mod close_tab;
pub mod cookies;
pub mod debug;
pub mod evaluate;
pub mod extract;
pub mod go_back;
pub mod go_forward;
pub mod hover;
pub mod html_to_markdown;
pub mod input;
pub mod local_storage;
pub mod markdown;
pub mod navigate;
pub mod new_tab;
pub mod press_key;
pub mod read_links;
pub mod readability_script;
pub mod screenshot;
pub mod scroll;
pub mod select;
pub mod snapshot;
pub mod switch_tab;
pub mod tab_list;
pub mod annotate;
mod utils;
pub mod wait;

// Re-export Params types for use by MCP layer
pub use click::ClickParams;
pub use close::CloseParams;
pub use close_tab::CloseTabParams;
pub use cookies::{GetCookiesParams, SetCookiesParams};
pub use debug::{GetConsoleLogsParams, GetNetworkErrorsParams};
pub use evaluate::EvaluateParams;
pub use extract::ExtractParams;
pub use go_back::GoBackParams;
pub use go_forward::GoForwardParams;
pub use hover::HoverParams;
pub use input::InputParams;
pub use local_storage::{
    ClearLocalStorageParams, GetLocalStorageParams, RemoveLocalStorageParams, SetLocalStorageParams,
};
pub use markdown::GetMarkdownParams;
pub use navigate::NavigateParams;
pub use new_tab::NewTabParams;
pub use press_key::PressKeyParams;
pub use read_links::ReadLinksParams;
pub use screenshot::ScreenshotParams;
pub use scroll::ScrollParams;
pub use select::SelectParams;
pub use snapshot::SnapshotParams;
pub use switch_tab::SwitchTabParams;
pub use tab_list::TabListParams;
pub use annotate::AnnotateParams;
pub use wait::WaitParams;

use crate::{browser::BrowserSession, dom::DomTree, error::Result};
use serde_json::Value;
use std::{collections::HashMap, sync::Arc};

/// Tool execution context
pub struct ToolContext<'a> {
    /// Browser session
    pub session: &'a BrowserSession,

    /// Optional DOM tree (extracted on demand)
    pub dom_tree: Option<DomTree>,
}

impl<'a> ToolContext<'a> {
    /// Create a new tool context
    pub fn new(session: &'a BrowserSession) -> Self {
        Self { session, dom_tree: None }
    }

    /// Create a context with a pre-extracted DOM tree
    pub fn with_dom(session: &'a BrowserSession, dom_tree: DomTree) -> Self {
        Self { session, dom_tree: Some(dom_tree) }
    }

    /// Get or extract the DOM tree
    pub fn get_dom(&mut self) -> Result<&DomTree> {
        if self.dom_tree.is_none() {
            self.dom_tree = Some(self.session.extract_dom()?);
        }
        Ok(self.dom_tree.as_ref().unwrap())
    }
}

/// Result of tool execution
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct ToolResult {
    /// Whether the tool execution was successful
    pub success: bool,

    /// Result data (JSON value)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<Value>,

    /// Error message if execution failed
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,

    /// Additional metadata
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub metadata: HashMap<String, Value>,
}

impl ToolResult {
    /// Create a successful result
    pub fn success(data: Option<Value>) -> Self {
        Self { success: true, data, error: None, metadata: HashMap::new() }
    }

    /// Create a successful result with data
    pub fn success_with<T: serde::Serialize>(data: T) -> Self {
        Self { success: true, data: serde_json::to_value(data).ok(), error: None, metadata: HashMap::new() }
    }

    /// Create a failure result
    pub fn failure(error: impl Into<String>) -> Self {
        Self { success: false, data: None, error: Some(error.into()), metadata: HashMap::new() }
    }

    /// Add metadata to the result
    pub fn with_metadata(mut self, key: impl Into<String>, value: Value) -> Self {
        self.metadata.insert(key.into(), value);
        self
    }
}

/// Trait for browser automation tools with associated parameter types
pub trait Tool: Send + Sync + Default {
    /// Associated parameter type for this tool
    type Params: serde::Serialize + for<'de> serde::Deserialize<'de> + schemars::JsonSchema;

    /// Get tool name
    fn name(&self) -> &str;

    /// Get tool parameter schema (JSON Schema)
    fn parameters_schema(&self) -> Value {
        serde_json::to_value(schemars::schema_for!(Self::Params)).unwrap_or_default()
    }

    /// Execute the tool with strongly-typed parameters
    fn execute_typed(&self, params: Self::Params, context: &mut ToolContext) -> Result<ToolResult>;

    /// Execute the tool with JSON parameters (default implementation)
    fn execute(&self, params: Value, context: &mut ToolContext) -> Result<ToolResult> {
        let typed_params: Self::Params = serde_json::from_value(params)
            .map_err(|e| crate::error::BrowserError::InvalidArgument(format!("Invalid parameters: {}", e)))?;
        self.execute_typed(typed_params, context)
    }
}

/// Type-erased tool trait for dynamic dispatch
pub trait DynTool: Send + Sync {
    fn name(&self) -> &str;
    fn parameters_schema(&self) -> Value;
    fn execute(&self, params: Value, context: &mut ToolContext) -> Result<ToolResult>;
}

/// Blanket implementation to convert any Tool into DynTool
impl<T: Tool> DynTool for T {
    fn name(&self) -> &str {
        Tool::name(self)
    }

    fn parameters_schema(&self) -> Value {
        Tool::parameters_schema(self)
    }

    fn execute(&self, params: Value, context: &mut ToolContext) -> Result<ToolResult> {
        Tool::execute(self, params, context)
    }
}

/// Tool registry for managing and accessing tools
pub struct ToolRegistry {
    tools: HashMap<String, Arc<dyn DynTool>>,
}

impl ToolRegistry {
    /// Create a new empty tool registry
    pub fn new() -> Self {
        Self { tools: HashMap::new() }
    }

    /// Create a registry with default tools
    pub fn with_defaults() -> Self {
        let mut registry = Self::new();

        // Register navigation tools
        registry.register(navigate::NavigateTool);
        registry.register(go_back::GoBackTool);
        registry.register(go_forward::GoForwardTool);
        registry.register(wait::WaitTool);

        // Register interaction tools
        registry.register(click::ClickTool);
        registry.register(input::InputTool);
        registry.register(select::SelectTool);
        registry.register(hover::HoverTool);
        registry.register(press_key::PressKeyTool);
        registry.register(scroll::ScrollTool);

        // Register tab management tools
        registry.register(new_tab::NewTabTool);
        registry.register(tab_list::TabListTool);
        registry.register(switch_tab::SwitchTabTool);
        registry.register(close_tab::CloseTabTool);

        // Register reading and extraction tools
        registry.register(extract::ExtractContentTool);
        registry.register(markdown::GetMarkdownTool);
        registry.register(read_links::ReadLinksTool);
        registry.register(snapshot::SnapshotTool);

        // Register utility tools
        registry.register(screenshot::ScreenshotTool);
        registry.register(annotate::AnnotateTool);
        registry.register(evaluate::EvaluateTool);
        registry.register(close::CloseTool);
        
        // Register cookie tools
        registry.register(cookies::GetCookiesTool);
        registry.register(cookies::SetCookiesTool);

        // Register debug tools
        registry.register(debug::GetConsoleLogsTool);
        registry.register(debug::GetNetworkErrorsTool);
        
        // Register local storage tools
        registry.register(local_storage::GetLocalStorageTool);
        registry.register(local_storage::SetLocalStorageTool);
        registry.register(local_storage::RemoveLocalStorageTool);
        registry.register(local_storage::ClearLocalStorageTool);

        registry
    }

    /// Register a tool
    pub fn register<T: Tool + 'static>(&mut self, tool: T) {
        let name = tool.name().to_string();
        self.tools.insert(name, Arc::new(tool));
    }

    /// Get a tool by name
    pub fn get(&self, name: &str) -> Option<&Arc<dyn DynTool>> {
        self.tools.get(name)
    }

    /// Check if a tool exists
    pub fn has(&self, name: &str) -> bool {
        self.tools.contains_key(name)
    }

    /// List all tool names
    pub fn list_names(&self) -> Vec<String> {
        self.tools.keys().cloned().collect()
    }

    /// Get all tools
    pub fn all_tools(&self) -> Vec<Arc<dyn DynTool>> {
        self.tools.values().cloned().collect()
    }

    /// Execute a tool by name
    pub fn execute(&self, name: &str, params: Value, context: &mut ToolContext) -> Result<ToolResult> {
        match self.get(name) {
            Some(tool) => tool.execute(params, context),
            None => Ok(ToolResult::failure(format!("Tool '{}' not found", name))),
        }
    }

    /// Get the number of registered tools
    pub fn count(&self) -> usize {
        self.tools.len()
    }
}

impl Default for ToolRegistry {
    fn default() -> Self {
        Self::with_defaults()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tool_result_success() {
        let result = ToolResult::success(Some(serde_json::json!({"url": "https://example.com"})));
        assert!(result.success);
        assert!(result.data.is_some());
        assert!(result.error.is_none());
    }

    #[test]
    fn test_tool_result_failure() {
        let result = ToolResult::failure("Test error");
        assert!(!result.success);
        assert!(result.data.is_none());
        assert_eq!(result.error, Some("Test error".to_string()));
    }

    #[test]
    fn test_tool_result_with_metadata() {
        let result = ToolResult::success(None).with_metadata("duration_ms", serde_json::json!(100));

        assert!(result.metadata.contains_key("duration_ms"));
    }
}
