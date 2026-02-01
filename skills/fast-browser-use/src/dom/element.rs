use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Represents an ARIA node in the accessibility tree
/// Based on Playwright's AriaNode structure
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct AriaNode {
    /// ARIA role (e.g., "button", "link", "textbox", "generic", "iframe", "fragment")
    pub role: String,

    /// Accessible name of the element
    pub name: String,

    /// Index of the element in the interactive elements array
    #[serde(skip_serializing_if = "Option::is_none")]
    pub index: Option<usize>,

    /// Child nodes (can be AriaNode or text strings)
    #[serde(default)]
    pub children: Vec<AriaChild>,

    /// ARIA properties specific to this element (e.g., url, placeholder)
    #[serde(default)]
    pub props: HashMap<String, String>,

    /// Box information (visibility, cursor)
    #[serde(default)]
    pub box_info: BoxInfo,

    // ARIA states
    /// Whether element is checked (for checkboxes, radios, etc.)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub checked: Option<AriaChecked>,

    /// Whether element is disabled
    #[serde(skip_serializing_if = "Option::is_none")]
    pub disabled: Option<bool>,

    /// Whether element is expanded (for expandable elements)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expanded: Option<bool>,

    /// Heading/list level
    #[serde(skip_serializing_if = "Option::is_none")]
    pub level: Option<u32>,

    /// Whether button is pressed
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pressed: Option<AriaPressed>,

    /// Whether element is selected
    #[serde(skip_serializing_if = "Option::is_none")]
    pub selected: Option<bool>,

    /// Whether element is currently active/focused
    #[serde(skip_serializing_if = "Option::is_none")]
    pub active: Option<bool>,
}

/// Child of an AriaNode - either another AriaNode or a text string
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(untagged)]
pub enum AriaChild {
    Text(String),
    Node(Box<AriaNode>),
}

/// ARIA checked state (true, false, or mixed)
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(untagged)]
pub enum AriaChecked {
    Bool(bool),
    Mixed(String), // "mixed"
}

/// ARIA pressed state (true, false, or mixed)
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(untagged)]
pub enum AriaPressed {
    Bool(bool),
    Mixed(String), // "mixed"
}

/// Box/visibility information for an element
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct BoxInfo {
    /// Whether the element is visible (non-zero bounding box)
    #[serde(default)]
    pub visible: bool,

    /// CSS cursor value (e.g., "pointer", "default")
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cursor: Option<String>,

    /// Bounding box rectangle (x, y, width, height)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rect: Option<Rect>,
}

/// Rectangle for bounding box
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Rect {
    pub x: f64,
    pub y: f64,
    pub width: f64,
    pub height: f64,
}

impl Default for BoxInfo {
    fn default() -> Self {
        Self { visible: false, cursor: None, rect: None }
    }
}

impl AriaNode {
    /// Create a new AriaNode with minimal fields
    pub fn new(role: impl Into<String>, name: impl Into<String>) -> Self {
        Self {
            role: role.into(),
            name: name.into(),
            index: None,
            children: Vec::new(),
            props: HashMap::new(),
            box_info: BoxInfo::default(),
            checked: None,
            disabled: None,
            expanded: None,
            level: None,
            pressed: None,
            selected: None,
            active: None,
        }
    }

    /// Create a fragment node (root container)
    pub fn fragment() -> Self {
        Self::new("fragment", "")
    }

    /// Builder: set index
    pub fn with_index(mut self, index: usize) -> Self {
        self.index = Some(index);
        self
    }

    /// Builder: add a child node
    pub fn with_child(mut self, child: AriaChild) -> Self {
        self.children.push(child);
        self
    }

    /// Builder: add multiple children
    pub fn with_children(mut self, children: Vec<AriaChild>) -> Self {
        self.children = children;
        self
    }

    /// Builder: add a property
    pub fn with_prop(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.props.insert(key.into(), value.into());
        self
    }

    /// Builder: set box info
    pub fn with_box(mut self, visible: bool, cursor: Option<String>) -> Self {
        self.box_info = BoxInfo { visible, cursor, rect: None };
        self
    }

    /// Builder: set checked state
    pub fn with_checked(mut self, checked: bool) -> Self {
        self.checked = Some(AriaChecked::Bool(checked));
        self
    }

    /// Builder: set disabled state
    pub fn with_disabled(mut self, disabled: bool) -> Self {
        self.disabled = Some(disabled);
        self
    }

    /// Builder: set expanded state
    pub fn with_expanded(mut self, expanded: bool) -> Self {
        self.expanded = Some(expanded);
        self
    }

    /// Builder: set level
    pub fn with_level(mut self, level: u32) -> Self {
        self.level = Some(level);
        self
    }

    /// Check if this node is interactive (has an index and is visible)
    pub fn is_interactive(&self) -> bool {
        self.index.is_some() && self.box_info.visible
    }

    /// Check if this node has pointer cursor
    pub fn has_pointer_cursor(&self) -> bool {
        self.box_info.cursor.as_ref().map_or(false, |c| c == "pointer")
    }

    /// Check if this is a fragment or iframe
    pub fn is_container(&self) -> bool {
        self.role == "fragment" || self.role == "iframe"
    }

    /// Get all text content (concatenate all text children recursively)
    pub fn get_text_content(&self) -> String {
        let mut result = String::new();
        self.collect_text(&mut result);
        result.trim().to_string()
    }

    fn collect_text(&self, buffer: &mut String) {
        for child in &self.children {
            match child {
                AriaChild::Text(text) => {
                    buffer.push_str(text);
                    buffer.push(' ');
                }
                AriaChild::Node(node) => {
                    node.collect_text(buffer);
                }
            }
        }
    }

    /// Count total nodes in subtree
    pub fn count_nodes(&self) -> usize {
        1 + self
            .children
            .iter()
            .map(|c| match c {
                AriaChild::Text(_) => 0,
                AriaChild::Node(n) => n.count_nodes(),
            })
            .sum::<usize>()
    }

    /// Find node by index (depth-first search)
    pub fn find_by_index(&self, index: usize) -> Option<&AriaNode> {
        if self.index == Some(index) {
            return Some(self);
        }

        for child in &self.children {
            if let AriaChild::Node(node) = child {
                if let Some(found) = node.find_by_index(index) {
                    return Some(found);
                }
            }
        }

        None
    }

    /// Find node by index (mutable)
    pub fn find_by_index_mut(&mut self, index: usize) -> Option<&mut AriaNode> {
        if self.index == Some(index) {
            return Some(self);
        }

        for child in &mut self.children {
            if let AriaChild::Node(node) = child {
                if let Some(found) = node.find_by_index_mut(index) {
                    return Some(found);
                }
            }
        }

        None
    }

    /// Count interactive elements in subtree (elements with indices)
    pub fn count_interactive(&self) -> usize {
        let mut count = 0;
        self.count_interactive_recursive(&mut count);
        count
    }

    fn count_interactive_recursive(&self, count: &mut usize) {
        if self.index.is_some() {
            *count += 1;
        }

        for child in &self.children {
            if let AriaChild::Node(node) = child {
                node.count_interactive_recursive(count);
            }
        }
    }

    /// Check if two nodes are equal (for diffing)
    /// Based on Playwright's ariaNodesEqual
    pub fn aria_equals(&self, other: &AriaNode) -> bool {
        if self.role != other.role || self.name != other.name {
            return false;
        }

        if self.checked != other.checked
            || self.disabled != other.disabled
            || self.expanded != other.expanded
            || self.level != other.level
            || self.pressed != other.pressed
            || self.selected != other.selected
        {
            return false;
        }

        if self.has_pointer_cursor() != other.has_pointer_cursor() {
            return false;
        }

        if self.props.len() != other.props.len() {
            return false;
        }

        for (k, v) in &self.props {
            if other.props.get(k) != Some(v) {
                return false;
            }
        }

        true
    }
}

// Legacy compatibility: ElementNode type alias for old code
// This allows gradual migration from ElementNode to AriaNode
pub type ElementNode = AriaNode;

// Legacy: BoundingBox (now BoxInfo)
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct BoundingBox {
    pub x: f64,
    pub y: f64,
    pub width: f64,
    pub height: f64,
}

impl BoundingBox {
    pub fn new(x: f64, y: f64, width: f64, height: f64) -> Self {
        Self { x, y, width, height }
    }

    pub fn is_visible(&self) -> bool {
        self.width > 0.0 && self.height > 0.0
    }

    pub fn area(&self) -> f64 {
        self.width * self.height
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_interactive() {
        let interactive = AriaNode::new("button", "Click").with_index(0).with_box(true, None);
        assert!(interactive.is_interactive());

        let not_interactive = AriaNode::new("button", "Click").with_box(false, None);
        assert!(!not_interactive.is_interactive());

        let no_index = AriaNode::new("button", "Click").with_box(true, None);
        assert!(!no_index.is_interactive());
    }

    #[test]
    fn test_has_pointer_cursor() {
        let with_pointer = AriaNode::new("button", "").with_box(true, Some("pointer".to_string()));
        assert!(with_pointer.has_pointer_cursor());

        let without_pointer = AriaNode::new("button", "").with_box(true, Some("default".to_string()));
        assert!(!without_pointer.has_pointer_cursor());
    }

    #[test]
    fn test_get_text_content() {
        let mut node = AriaNode::new("div", "");
        node.children.push(AriaChild::Text("Hello ".to_string()));
        node.children.push(AriaChild::Node(Box::new(
            AriaNode::new("span", "").with_child(AriaChild::Text("World".to_string())),
        )));

        assert_eq!(node.get_text_content(), "Hello  World");
    }

    #[test]
    fn test_find_by_index() {
        let mut root = AriaNode::new("fragment", "");
        root.children.push(AriaChild::Node(Box::new(AriaNode::new("button", "First").with_index(0))));
        root.children.push(AriaChild::Node(Box::new(AriaNode::new("button", "Second").with_index(1))));

        let found = root.find_by_index(1);
        assert!(found.is_some());
        assert_eq!(found.unwrap().name, "Second");

        let not_found = root.find_by_index(999);
        assert!(not_found.is_none());
    }

    #[test]
    fn test_count_interactive() {
        let mut root = AriaNode::fragment().with_index(0);
        root.children.push(AriaChild::Node(Box::new(AriaNode::new("button", "").with_index(1))));
        root.children.push(AriaChild::Node(Box::new(AriaNode::new("link", "").with_index(2))));

        let count = root.count_interactive();
        assert_eq!(count, 3); // root + button + link
    }

    #[test]
    fn test_aria_equals() {
        let node1 = AriaNode::new("button", "Click").with_disabled(false).with_box(true, Some("pointer".to_string()));

        let node2 = AriaNode::new("button", "Click").with_disabled(false).with_box(true, Some("pointer".to_string()));

        assert!(node1.aria_equals(&node2));

        let node3 = AriaNode::new("button", "Click").with_disabled(true).with_box(true, Some("pointer".to_string()));

        assert!(!node1.aria_equals(&node3));
    }

    #[test]
    fn test_count_nodes() {
        let mut root = AriaNode::fragment();
        root.children.push(AriaChild::Text("text".to_string()));
        root.children.push(AriaChild::Node(Box::new(AriaNode::new("button", ""))));
        root.children.push(AriaChild::Node(Box::new(
            AriaNode::new("div", "").with_child(AriaChild::Node(Box::new(AriaNode::new("span", "")))),
        )));

        // root + button + div + span = 4
        assert_eq!(root.count_nodes(), 4);
    }
}