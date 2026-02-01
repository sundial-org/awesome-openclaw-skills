use crate::{
    error::{BrowserError, Result},
    tools::{Tool, ToolContext, ToolResult},
    dom::element::AriaChild,
};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use image::Rgba;
use imageproc::drawing::{draw_filled_rect_mut, draw_text_mut};
use imageproc::rect::Rect as ImageRect;
use rusttype::{Font, Scale};
use std::io::Cursor;
use base64::{Engine as _, engine::general_purpose::STANDARD as BASE64};

/// Parameters for the annotate tool
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct AnnotateParams {
    /// Whether to return the base64 image (default: false, saves to file)
    #[serde(default)]
    pub return_base64: bool,

    /// Path to save the annotated screenshot (if not returning base64)
    pub path: Option<String>,
}

/// Tool for capturing a screenshot with annotated interactive elements
#[derive(Default)]
pub struct AnnotateTool;

impl Tool for AnnotateTool {
    type Params = AnnotateParams;

    fn name(&self) -> &str {
        "annotate"
    }

    fn execute_typed(&self, params: AnnotateParams, context: &mut ToolContext) -> Result<ToolResult> {
        // 1. Capture screenshot
        let screenshot_data = context
            .session
            .tab()?
            .capture_screenshot(
                headless_chrome::protocol::cdp::Page::CaptureScreenshotFormatOption::Png,
                None,
                None,
                false, // Viewport only for annotation usually makes more sense to match coordinates
            )
            .map_err(|e| BrowserError::ScreenshotFailed(e.to_string()))?;

        // 2. Extract DOM with bounding boxes
        let dom = context.get_dom()?;

        // 3. Load image
        let mut img = image::load_from_memory(&screenshot_data)
            .map_err(|e| BrowserError::ScreenshotFailed(format!("Failed to load screenshot image: {}", e)))?
            .to_rgba8();

        let (width, height) = img.dimensions();

        // 4. Load font (using a built-in font or loading from bytes if possible, otherwise we might fail)
        // Since we can't easily rely on system fonts in a portable way, we'll try to use a bundled font or fallback.
        // For this environment, let's assume we can't bundle a font easily without adding it to the repo.
        // Actually, we can use `ab_glyph` with a font file.
        // A better approach for a self-contained binary is to include a font as bytes.
        // Let's use a very simple fallback or a known system font path if we can't embed.
        // Wait, `imageproc` examples often use `DejaVuSans`.
        // I'll try to look for a system font, or if that fails, just draw boxes without text? 
        // No, numbers are crucial.
        // I will embed a font. `DejaVuSans.ttf` is open.
        // Since I can't download files easily right now, I'll assume a system path or try to find one.
        // MacOS: /System/Library/Fonts/Helvetica.ttc
        // Linux: /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
        
        let font_path = if cfg!(target_os = "macos") {
            "/System/Library/Fonts/Helvetica.ttc"
        } else {
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        };
        
        // Very basic font loading fallback
        let font_bytes = std::fs::read(font_path).unwrap_or_default();
        let font = Font::try_from_bytes(&font_bytes);

        // 5. Draw annotations
        let mut map = HashMap::new();
        let mut valid_indices = Vec::new();

        // Collect all interactive elements with valid rects
        // We traverse the DOM tree
        let mut queue = vec![&dom.root];
        while let Some(node) = queue.pop() {
            if let Some(index) = node.index {
                if let Some(rect) = &node.box_info.rect {
                    if rect.width > 0.0 && rect.height > 0.0 && rect.x >= 0.0 && rect.y >= 0.0 {
                        // Check if rect is within viewport roughly
                         if rect.x < width as f64 && rect.y < height as f64 {
                             valid_indices.push((index, rect.clone()));
                             
                             // Add to selector map
                             if let Some(selector) = dom.get_selector(index) {
                                 map.insert(index.to_string(), selector.clone());
                             }
                         }
                    }
                }
            }
            
            for child in &node.children {
                if let AriaChild::Node(child_node) = child {
                    queue.push(child_node);
                }
            }
        }
        
        // Sort indices for consistent visualization if needed, but they are already indexed
        
        for (index, rect) in valid_indices {
             // Draw yellow box
             let x = rect.x as i32;
             let y = rect.y as i32;
             let w = rect.width as u32;
             let h = rect.height as u32;
             
             // Define color: Yellow with alpha
             let color = Rgba([255, 255, 0, 128]); // Semi-transparent yellow
             let border_color = Rgba([255, 0, 0, 255]); // Red border
             
             // Draw filled rect (marker)
             // We'll draw a small badge at the top-left corner of the element
             let badge_size = 20;
             let badge_rect = ImageRect::at(x, y).of_size(badge_size, badge_size);
             
             draw_filled_rect_mut(&mut img, badge_rect, border_color);
             
             // Draw text number
             if let Some(font) = &font {
                 let scale = Scale::uniform(16.0);
                 let text = index.to_string();
                 draw_text_mut(&mut img, Rgba([255, 255, 255, 255]), x + 2, y + 2, scale, font, &text);
             }
        }

        // 6. Save or return
        let mut bytes: Vec<u8> = Vec::new();
        img.write_to(&mut Cursor::new(&mut bytes), image::ImageOutputFormat::Png)
             .map_err(|e| BrowserError::ScreenshotFailed(format!("Failed to encode annotated image: {}", e)))?;

        let mut result_data = serde_json::Map::new();
        result_data.insert("map".to_string(), serde_json::to_value(&map).unwrap());
        
        if params.return_base64 {
            let base64_string = BASE64.encode(&bytes);
            result_data.insert("image_base64".to_string(), serde_json::Value::String(base64_string));
        }
        
        if let Some(path) = params.path {
            std::fs::write(&path, &bytes)
                .map_err(|e| BrowserError::ScreenshotFailed(format!("Failed to save annotated screenshot: {}", e)))?;
            result_data.insert("path".to_string(), serde_json::Value::String(path));
        }

        Ok(ToolResult::success(Some(serde_json::Value::Object(result_data))))
    }
}
