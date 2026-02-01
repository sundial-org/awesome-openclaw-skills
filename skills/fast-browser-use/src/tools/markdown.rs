use crate::{error::{BrowserError, Result},
            tools::{Tool, ToolContext, ToolResult, html_to_markdown::convert_html_to_markdown,
                    readability_script::READABILITY_SCRIPT}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for getting markdown content with pagination support
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct GetMarkdownParams {
    /// Page number to extract (1-based index, default: 1)
    #[serde(default = "default_page")]
    pub page: usize,

    /// Maximum characters per page (default: 100000)
    #[serde(default = "default_page_size")]
    pub page_size: usize,
}

fn default_page() -> usize {
    1
}

fn default_page_size() -> usize {
    100_000
}

impl Default for GetMarkdownParams {
    fn default() -> Self {
        Self { page: default_page(), page_size: default_page_size() }
    }
}

#[derive(Default)]
pub struct GetMarkdownTool;

impl Tool for GetMarkdownTool {
    type Params = GetMarkdownParams;

    fn name(&self) -> &str {
        "get_markdown"
    }

    fn execute_typed(&self, params: GetMarkdownParams, context: &mut ToolContext) -> Result<ToolResult> {
        // Wait for network idle with a timeout
        // Since headless_chrome doesn't have a direct network idle wait,
        // we add a small delay to let dynamic content load
        std::thread::sleep(std::time::Duration::from_millis(1000));

        // Inject Readability.js script and the conversion script
        // Use 'var' instead of 'const' to allow redeclaration on subsequent calls
        // This prevents "identifier already declared" errors when calling get_markdown multiple times
        let js_code = format!(
            "var READABILITY_SCRIPT = {};\n{}",
            serde_json::to_string(READABILITY_SCRIPT).unwrap(),
            include_str!("convert_to_markdown.js")
        );

        // Execute the JavaScript to extract and convert content
        let result = context
            .session
            .tab()?
            .evaluate(&js_code, false)
            .map_err(|e| BrowserError::EvaluationFailed(e.to_string()))?;

        // Parse the result
        let result_value = result.value.ok_or_else(|| {
            // Capture description if available
            let description = result
                .description
                .map(|d| format!("Description: {}", d))
                .unwrap_or_else(|| format!("Type: {:?}", result.Type));

            BrowserError::ToolExecutionFailed {
                tool: "get_markdown".to_string(),
                reason: format!("No value returned from JavaScript. {}", description),
            }
        })?;

        // The JavaScript returns a JSON string, so we need to parse it
        let extraction_result: ExtractionResult = if let Some(json_str) = result_value.as_str() {
            serde_json::from_str(json_str).map_err(|e| BrowserError::ToolExecutionFailed {
                tool: "get_markdown".to_string(),
                reason: format!("Failed to parse extraction result: {}", e),
            })?
        } else {
            // If it's already an object, try to deserialize directly
            serde_json::from_value(result_value).map_err(|e| BrowserError::ToolExecutionFailed {
                tool: "get_markdown".to_string(),
                reason: format!("Failed to deserialize extraction result: {}", e),
            })?
        };

        // Check if Readability failed
        if extraction_result.readability_failed {
            return Err(BrowserError::ToolExecutionFailed {
                tool: "get_markdown".to_string(),
                reason: extraction_result.error.unwrap_or_else(|| "Readability extraction failed".to_string()),
            });
        }

        // Convert the extracted HTML content to Markdown
        let full_markdown = convert_html_to_markdown(&extraction_result.content);

        // Calculate pagination information
        let total_pages =
            if full_markdown.is_empty() { 1 } else { (full_markdown.len() + params.page_size - 1) / params.page_size };

        // Clamp page number to valid range
        let current_page = params.page.clamp(1, total_pages.max(1));

        // Calculate start and end indices for the requested page
        let start_idx = (current_page - 1) * params.page_size;
        let end_idx = (start_idx + params.page_size).min(full_markdown.len());

        // Extract the content for the current page
        let mut page_content =
            if start_idx < full_markdown.len() { full_markdown[start_idx..end_idx].to_string() } else { String::new() };

        // Add title to the first page only
        if current_page == 1 && !extraction_result.title.is_empty() {
            page_content = format!("# {}\n\n{}", extraction_result.title, page_content);
        }

        // Add pagination information if there are multiple pages
        if total_pages > 1 {
            let pagination_info = if current_page < total_pages {
                format!(
                    "\n\n---\n\n*Page {} of {}. There are {} more page(s) with additional content.*\n",
                    current_page,
                    total_pages,
                    total_pages - current_page
                )
            } else {
                format!("\n\n---\n\n*Page {} of {}. This is the last page.*\n", current_page, total_pages)
            };
            page_content.push_str(&pagination_info);
        }

        // Return the result with pagination metadata
        Ok(ToolResult::success_with(serde_json::json!({
            "markdown": page_content,
            "title": extraction_result.title,
            "url": extraction_result.url,
            "currentPage": current_page,
            "totalPages": total_pages,
            "hasMorePages": current_page < total_pages,
            "length": page_content.len(),
            "byline": extraction_result.byline,
            "excerpt": extraction_result.excerpt,
            "siteName": extraction_result.site_name,
        })))
    }
}

/// Structure for extraction result returned from JavaScript
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ExtractionResult {
    title: String,
    content: String,
    text_content: String,
    url: String,
    #[serde(default)]
    excerpt: String,
    #[serde(default)]
    byline: String,
    #[serde(default)]
    site_name: String,
    #[serde(default)]
    length: usize,
    #[serde(default)]
    lang: String,
    #[serde(default)]
    dir: String,
    #[serde(default)]
    published_time: String,
    #[serde(default)]
    readability_failed: bool,
    #[serde(default)]
    error: Option<String>,
}
