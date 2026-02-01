use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ReadLinksParams {}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct Link {
    /// The visible text content of the link
    pub text: String,
    /// The href attribute of the link
    pub href: String,
}

#[derive(Default)]
pub struct ReadLinksTool;

impl Tool for ReadLinksTool {
    type Params = ReadLinksParams;

    fn name(&self) -> &str {
        "read_links"
    }

    fn execute_typed(&self, _params: ReadLinksParams, context: &mut ToolContext) -> Result<ToolResult> {
        // JavaScript code to extract all links on the page
        // We use JSON.stringify to ensure the result is returned properly
        let js_code = r#"
            JSON.stringify(
                Array.from(document.querySelectorAll('a[href]'))
                    .map(el => ({
                        text: el.innerText || '',
                        href: el.getAttribute('href') || ''
                    }))
                    .filter(link => link.href !== '')
            )
        "#;

        let result = context
            .session
            .tab()?
            .evaluate(js_code, false)
            .map_err(|e| BrowserError::EvaluationFailed(e.to_string()))?;

        // Parse the JSON string result into Link structs
        let links: Vec<Link> = result
            .value
            .and_then(|v| v.as_str().map(String::from))
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default();

        Ok(ToolResult::success_with(serde_json::json!({
            "links": links,
            "count": links.len()
        })))
    }
}
