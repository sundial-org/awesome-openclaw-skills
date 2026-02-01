//! DOM extraction and manipulation module
//!
//! This module provides functionality for extracting and working with the DOM structure
//! of web pages. It includes:
//! - ElementNode: Representation of DOM elements
//! - DomTree: Complete DOM tree with indexing for interactive elements

pub mod element;
pub mod tree;
pub mod yaml;

pub use element::{AriaChild, AriaNode, BoundingBox, ElementNode};
pub use tree::DomTree;
pub use yaml::{yaml_escape_key_if_needed, yaml_escape_value_if_needed};
