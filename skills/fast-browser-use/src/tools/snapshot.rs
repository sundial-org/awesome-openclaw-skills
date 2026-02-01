use crate::{dom::{AriaChild, AriaNode, yaml_escape_key_if_needed, yaml_escape_value_if_needed},
            error::Result,
            tools::{Tool, ToolContext, ToolResult}};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Parameters for the snapshot tool
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, Default)]
pub struct SnapshotParams {
    /// Whether to include full snapshot or incremental
    #[serde(default)]
    pub incremental: bool,
}

/// Tool for getting an ARIA snapshot of the page in YAML format
#[derive(Default)]
pub struct SnapshotTool;

impl Tool for SnapshotTool {
    type Params = SnapshotParams;

    fn name(&self) -> &str {
        "snapshot"
    }

    fn execute_typed(&self, params: SnapshotParams, context: &mut ToolContext) -> Result<ToolResult> {
        // Get or extract the DOM tree
        let dom = context.get_dom()?;

        // Generate YAML snapshot
        let yaml_snapshot = render_aria_tree(&dom.root, RenderMode::Ai, None);

        // Count interactive elements
        let interactive_count = dom.count_interactive();

        let result = if params.incremental {
            // TODO: Implement incremental snapshots
            serde_json::json!({
                "full": yaml_snapshot,
                "interactive_count": interactive_count,
            })
        } else {
            serde_json::json!({
                "snapshot": yaml_snapshot,
                "interactive_count": interactive_count,
            })
        };

        Ok(ToolResult::success_with(result))
    }
}

/// Rendering mode for ARIA tree
#[derive(Debug, Clone, Copy)]
pub enum RenderMode {
    /// AI consumption mode (includes refs, cursor, active markers)
    Ai,
    /// Expect mode (for testing)
    Expect,
}

/// Render an ARIA tree to YAML format
/// Based on Playwright's renderAriaTree function
pub fn render_aria_tree(root: &AriaNode, mode: RenderMode, previous: Option<&AriaNode>) -> String {
    let mut lines = Vec::new();

    let render_cursor_pointer = matches!(mode, RenderMode::Ai);
    let render_active = matches!(mode, RenderMode::Ai);

    // Do not render the root fragment, just its children
    let nodes_to_render = if root.role == "fragment" {
        &root.children
    } else {
        // Single root node case - wrap it
        return render_single_node(root, mode, previous);
    };

    for node in nodes_to_render {
        match node {
            AriaChild::Text(text) => {
                visit_text(text, "", &mut lines);
            }
            AriaChild::Node(node) => {
                visit(node, "", render_cursor_pointer, render_active, &mut lines, previous);
            }
        }
    }

    lines.join("\n")
}

fn render_single_node(root: &AriaNode, mode: RenderMode, previous: Option<&AriaNode>) -> String {
    let mut lines = Vec::new();
    let render_cursor_pointer = matches!(mode, RenderMode::Ai);
    let render_active = matches!(mode, RenderMode::Ai);

    visit(root, "", render_cursor_pointer, render_active, &mut lines, previous);

    lines.join("\n")
}

fn visit_text(text: &str, indent: &str, lines: &mut Vec<String>) {
    let escaped = yaml_escape_value_if_needed(text);
    if !escaped.is_empty() {
        lines.push(format!("{}- text: {}", indent, escaped));
    }
}

fn visit(
    aria_node: &AriaNode,
    indent: &str,
    render_cursor_pointer: bool,
    render_active: bool,
    lines: &mut Vec<String>,
    _previous: Option<&AriaNode>,
) {
    // Create the key (role + name + attributes)
    let key = create_key(aria_node, render_cursor_pointer, render_active);
    let escaped_key = format!("{}- {}", indent, yaml_escape_key_if_needed(&key));

    // Get single inlined text child if applicable
    let single_text_child = get_single_inlined_text_child(aria_node);

    if aria_node.children.is_empty() && aria_node.props.is_empty() {
        // Leaf node without children or props
        lines.push(escaped_key);
    } else if let Some(text) = single_text_child {
        // Leaf node with just text inside
        lines.push(format!("{}: {}", escaped_key, yaml_escape_value_if_needed(&text)));
    } else {
        // Node with props and/or children
        lines.push(format!("{}:", escaped_key));

        // Render props
        for (name, value) in &aria_node.props {
            lines.push(format!("{}  - /{}: {}", indent, name, yaml_escape_value_if_needed(value)));
        }

        // Render children
        let child_indent = format!("{}  ", indent);
        let in_cursor_pointer = aria_node.index.is_some() && render_cursor_pointer && aria_node.has_pointer_cursor();

        for child in &aria_node.children {
            match child {
                AriaChild::Text(text) => {
                    visit_text(text, &child_indent, lines);
                }
                AriaChild::Node(child_node) => {
                    visit(
                        child_node,
                        &child_indent,
                        render_cursor_pointer && !in_cursor_pointer,
                        render_active,
                        lines,
                        None,
                    );
                }
            }
        }
    }
}

fn create_key(aria_node: &AriaNode, render_cursor_pointer: bool, render_active: bool) -> String {
    let mut key = aria_node.role.clone();

    // Add name if present and not too long
    if !aria_node.name.is_empty() && aria_node.name.len() <= 900 {
        // YAML has a limit of 1024 characters per key
        let name = &aria_node.name;
        // Simple stringification (no regex handling for now)
        key.push(' ');
        key.push_str(&format!("{:?}", name)); // JSON-style quoting
    }

    // Add ARIA state attributes
    if let Some(checked) = &aria_node.checked {
        match checked {
            crate::dom::element::AriaChecked::Bool(true) => key.push_str(" [checked]"),
            crate::dom::element::AriaChecked::Bool(false) => {}
            crate::dom::element::AriaChecked::Mixed(_) => key.push_str(" [checked=mixed]"),
        }
    }

    if aria_node.disabled == Some(true) {
        key.push_str(" [disabled]");
    }

    if aria_node.expanded == Some(true) {
        key.push_str(" [expanded]");
    }

    if render_active && aria_node.active == Some(true) {
        key.push_str(" [active]");
    }

    if let Some(level) = aria_node.level {
        key.push_str(&format!(" [level={}]", level));
    }

    if let Some(pressed) = &aria_node.pressed {
        match pressed {
            crate::dom::element::AriaPressed::Bool(true) => key.push_str(" [pressed]"),
            crate::dom::element::AriaPressed::Bool(false) => {}
            crate::dom::element::AriaPressed::Mixed(_) => key.push_str(" [pressed=mixed]"),
        }
    }

    if aria_node.selected == Some(true) {
        key.push_str(" [selected]");
    }

    // Add index attribute
    if let Some(index) = aria_node.index {
        key.push_str(&format!(" [index={}]", index));

        if render_cursor_pointer && aria_node.has_pointer_cursor() {
            key.push_str(" [cursor=pointer]");
        }
    }

    key
}

fn get_single_inlined_text_child(aria_node: &AriaNode) -> Option<String> {
    if aria_node.children.len() == 1 && aria_node.props.is_empty() {
        if let AriaChild::Text(text) = &aria_node.children[0] {
            return Some(text.clone());
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_render_simple_tree() {
        let mut root = AriaNode::fragment();
        root.children.push(AriaChild::Node(Box::new(
            AriaNode::new("button", "Click me").with_index(0).with_box(true, Some("pointer".to_string())),
        )));

        let yaml = render_aria_tree(&root, RenderMode::Ai, None);
        assert!(yaml.contains("button"));
        assert!(yaml.contains("Click me"));
        assert!(yaml.contains("[index=0]"));
        assert!(yaml.contains("[cursor=pointer]"));
    }

    #[test]
    fn test_render_tree_with_text() {
        let mut root = AriaNode::fragment();
        root.children.push(AriaChild::Text("Hello world".to_string()));

        let yaml = render_aria_tree(&root, RenderMode::Ai, None);
        eprintln!("YAML output:\n{}", yaml);
        assert!(yaml.contains("text:"));
        assert!(yaml.contains("Hello world"));
    }

    #[test]
    fn test_render_nested_tree() {
        let mut root = AriaNode::fragment();
        let mut div = AriaNode::new("generic", "");
        div.children.push(AriaChild::Text("Parent text".to_string()));
        div.children.push(AriaChild::Node(Box::new(AriaNode::new("button", "Child button").with_index(0))));

        root.children.push(AriaChild::Node(Box::new(div)));

        let yaml = render_aria_tree(&root, RenderMode::Ai, None);
        assert!(yaml.contains("generic"));
        assert!(yaml.contains("Parent text"));
        assert!(yaml.contains("button"));
        assert!(yaml.contains("Child button"));
    }

    #[test]
    fn test_render_with_props() {
        let mut root = AriaNode::fragment();
        root.children.push(AriaChild::Node(Box::new(
            AriaNode::new("link", "Go to page").with_index(0).with_prop("url", "https://example.com"),
        )));

        let yaml = render_aria_tree(&root, RenderMode::Ai, None);
        eprintln!("YAML output:\n{}", yaml);
        assert!(yaml.contains("link"));
        assert!(yaml.contains("[index=0]"));
        assert!(yaml.contains("/url:"));
        assert!(yaml.contains("https://example.com"));
    }

    #[test]
    fn test_render_with_aria_states() {
        let mut root = AriaNode::fragment();
        root.children.push(AriaChild::Node(Box::new(
            AriaNode::new("checkbox", "Accept terms").with_index(0).with_checked(true).with_disabled(false),
        )));

        let yaml = render_aria_tree(&root, RenderMode::Ai, None);
        assert!(yaml.contains("checkbox"));
        assert!(yaml.contains("[checked]"));
        // disabled=false should not appear
        assert!(!yaml.contains("[disabled]"));
    }

    #[test]
    fn test_render_heading_with_level() {
        let mut root = AriaNode::fragment();
        root.children.push(AriaChild::Node(Box::new(AriaNode::new("heading", "Page Title").with_level(1))));

        let yaml = render_aria_tree(&root, RenderMode::Ai, None);
        assert!(yaml.contains("heading"));
        assert!(yaml.contains("Page Title"));
        assert!(yaml.contains("[level=1]"));
    }

    #[test]
    fn test_empty_snapshot() {
        let root = AriaNode::fragment();
        let yaml = render_aria_tree(&root, RenderMode::Ai, None);
        assert_eq!(yaml.trim(), "");
    }
}
