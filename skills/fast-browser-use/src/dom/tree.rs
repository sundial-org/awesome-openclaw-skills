use crate::{dom::element::{AriaChild, AriaNode},
            error::{BrowserError, Result}};
use headless_chrome::Tab;
use std::sync::Arc;

/// Represents the ARIA snapshot of a web page
/// Based on Playwright's AriaSnapshot structure
#[derive(Debug, Clone)]
pub struct DomTree {
    /// Root AriaNode (usually a fragment)
    pub root: AriaNode,

    /// Array of CSS selectors indexed by element index
    pub selectors: Vec<String>,

    /// List of iframe indices (for multi-frame snapshots)
    pub iframe_indices: Vec<usize>,
}

/// Snapshot extraction response from JavaScript
#[derive(Debug, serde::Deserialize)]
struct SnapshotResponse {
    root: AriaNode,
    selectors: Vec<String>,
    #[serde(rename = "iframeIndices")]
    iframe_indices: Vec<usize>,
}

impl DomTree {
    /// Create a new DomTree from an AriaNode
    pub fn new(root: AriaNode) -> Self {
        let mut tree = Self { root, selectors: Vec::new(), iframe_indices: Vec::new() };
        tree.rebuild_maps();
        tree
    }

    /// Build DOM tree from a browser tab
    pub fn from_tab(tab: &Arc<Tab>) -> Result<Self> {
        Self::from_tab_with_prefix(tab, "")
    }

    /// Build DOM tree from a browser tab with a ref prefix (for iframe handling)
    pub fn from_tab_with_prefix(tab: &Arc<Tab>, _ref_prefix: &str) -> Result<Self> {
        // Note: ref_prefix is deprecated but kept for API compatibility
        // JavaScript code to extract ARIA snapshot
        let js_code = include_str!("extract_dom.js");

        // Execute JavaScript to extract DOM
        let result = tab
            .evaluate(js_code, false)
            .map_err(|e| BrowserError::DomParseFailed(format!("Failed to execute DOM extraction script: {}", e)))?;

        // Get the JSON string value
        let json_value = result
            .value
            .ok_or_else(|| BrowserError::DomParseFailed("No value returned from DOM extraction".to_string()))?;

        // The JavaScript returns a JSON string, so we need to parse it as a string first
        let json_str: String = serde_json::from_value(json_value)
            .map_err(|e| BrowserError::DomParseFailed(format!("Failed to get JSON string: {}", e)))?;

        // Then parse the JSON string into SnapshotResponse
        let response: SnapshotResponse = serde_json::from_str(&json_str)
            .map_err(|e| BrowserError::DomParseFailed(format!("Failed to parse snapshot JSON: {}", e)))?;

        Ok(Self { root: response.root, selectors: response.selectors, iframe_indices: response.iframe_indices })
    }

    /// Rebuild the selectors array by traversing the tree
    /// Note: This only resizes the array based on indices found.
    /// Actual selectors are populated from JavaScript extraction.
    fn rebuild_maps(&mut self) {
        self.iframe_indices.clear();

        // Find the maximum index in the tree
        let max_index = self.find_max_index(&self.root.clone());

        // Resize selectors array if needed
        if let Some(max_idx) = max_index {
            if self.selectors.len() <= max_idx {
                self.selectors.resize(max_idx + 1, String::new());
            }
        }

        // Collect iframe indices
        let root = self.root.clone();
        self.collect_iframe_indices(&root);
    }

    fn find_max_index(&self, node: &AriaNode) -> Option<usize> {
        let mut max = node.index;

        for child in &node.children {
            if let AriaChild::Node(child_node) = child {
                if let Some(child_max) = self.find_max_index(child_node) {
                    max = match max {
                        Some(current) => Some(current.max(child_max)),
                        None => Some(child_max),
                    };
                }
            }
        }

        max
    }

    fn collect_iframe_indices(&mut self, node: &AriaNode) {
        if let Some(index) = node.index {
            if node.role == "iframe" {
                self.iframe_indices.push(index);
            }
        }

        for child in &node.children {
            if let AriaChild::Node(child_node) = child {
                self.collect_iframe_indices(child_node);
            }
        }
    }

    /// Get CSS selector for a given index
    pub fn get_selector(&self, index: usize) -> Option<&String> {
        self.selectors.get(index).filter(|s| !s.is_empty())
    }

    /// Get all interactive element indices
    pub fn interactive_indices(&self) -> Vec<usize> {
        let mut indices = Vec::new();
        self.collect_indices(&self.root, &mut indices);
        indices.sort();
        indices
    }

    fn collect_indices(&self, node: &AriaNode, indices: &mut Vec<usize>) {
        if let Some(index) = node.index {
            indices.push(index);
        }
        for child in &node.children {
            if let AriaChild::Node(child_node) = child {
                self.collect_indices(child_node, indices);
            }
        }
    }

    /// Count total nodes in the tree
    pub fn count_nodes(&self) -> usize {
        self.root.count_nodes()
    }

    /// Count interactive elements (elements with indices)
    pub fn count_interactive(&self) -> usize {
        self.root.count_interactive()
    }

    /// Find node by index
    pub fn find_node_by_index(&self, index: usize) -> Option<&AriaNode> {
        self.root.find_by_index(index)
    }

    /// Find node by index (mutable)
    pub fn find_node_by_index_mut(&mut self, index: usize) -> Option<&mut AriaNode> {
        self.root.find_by_index_mut(index)
    }

    /// Get all iframe indices for multi-frame snapshot handling
    pub fn get_iframe_indices(&self) -> &[usize] {
        &self.iframe_indices
    }

    /// Convert the DOM tree to JSON
    pub fn to_json(&self) -> Result<String> {
        serde_json::to_string_pretty(&self.root)
            .map_err(|e| BrowserError::DomParseFailed(format!("Failed to serialize DOM to JSON: {}", e)))
    }

    /// Replace an iframe node's children with content from another snapshot
    /// Used for multi-frame snapshot assembly
    pub fn inject_iframe_content(&mut self, iframe_index: usize, iframe_snapshot: DomTree) {
        if let Some(iframe_node) = self.find_node_by_index_mut(iframe_index) {
            // Replace iframe's children with the snapshot's root children
            iframe_node.children = iframe_snapshot.root.children;

            // Merge selectors (offset by current length)
            let offset = self.selectors.len();
            for selector in iframe_snapshot.selectors {
                if !selector.is_empty() {
                    self.selectors.push(selector);
                }
            }

            // Update iframe indices with offset
            for idx in iframe_snapshot.iframe_indices {
                self.iframe_indices.push(idx + offset);
            }
        }
    }

    /// Create a snapshot with multiple frames assembled
    /// Takes a function that can retrieve snapshots for iframe elements
    pub fn assemble_with_iframes<F>(mut self, mut get_iframe_snapshot: F) -> Self
    where
        F: FnMut(usize) -> Option<DomTree>,
    {
        let iframe_indices = self.iframe_indices.clone();

        for iframe_index in iframe_indices {
            if let Some(iframe_snapshot) = get_iframe_snapshot(iframe_index) {
                self.inject_iframe_content(iframe_index, iframe_snapshot);
            }
        }

        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_tree() -> AriaNode {
        let mut root = AriaNode::fragment();

        root.children.push(AriaChild::Node(Box::new(
            AriaNode::new("button", "Click me").with_index(0).with_box(true, Some("pointer".to_string())),
        )));

        root.children
            .push(AriaChild::Node(Box::new(AriaNode::new("link", "Go to page").with_index(1).with_box(true, None))));

        root.children.push(AriaChild::Node(Box::new(
            AriaNode::new("paragraph", "").with_child(AriaChild::Text("Some text".to_string())),
        )));

        root
    }

    #[test]
    fn test_find_node_by_index() {
        let root = create_test_tree();
        let tree = DomTree::new(root);

        let button = tree.find_node_by_index(0);
        assert!(button.is_some());
        assert_eq!(button.unwrap().role, "button");
        assert_eq!(button.unwrap().name, "Click me");

        let not_found = tree.find_node_by_index(999);
        assert!(not_found.is_none());
    }

    #[test]
    fn test_count_nodes() {
        let root = create_test_tree();
        let tree = DomTree::new(root);

        // fragment + button + link + paragraph = 4
        assert_eq!(tree.count_nodes(), 4);
    }

    #[test]
    fn test_interactive_indices() {
        let root = create_test_tree();
        let tree = DomTree::new(root);

        let indices = tree.interactive_indices();
        assert_eq!(indices.len(), 2);
        assert!(indices.contains(&0));
        assert!(indices.contains(&1));
    }

    #[test]
    fn test_inject_iframe_content() {
        let mut main_tree = AriaNode::fragment();
        main_tree.children.push(AriaChild::Node(Box::new(AriaNode::new("iframe", "").with_index(0))));

        let mut iframe_tree = AriaNode::fragment();
        iframe_tree.children.push(AriaChild::Node(Box::new(AriaNode::new("button", "Inside iframe").with_index(0))));

        let mut main = DomTree::new(main_tree);
        let iframe = DomTree::new(iframe_tree);

        main.inject_iframe_content(0, iframe);

        // Check that iframe now has the button as a child
        let iframe_node = main.find_node_by_index(0).unwrap();
        assert_eq!(iframe_node.children.len(), 1);

        match &iframe_node.children[0] {
            AriaChild::Node(n) => {
                assert_eq!(n.role, "button");
                assert_eq!(n.name, "Inside iframe");
            }
            _ => panic!("Expected node child"),
        }
    }
}
