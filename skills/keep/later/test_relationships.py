"""
Tests for relationship extraction.
"""

import pytest

from keep.relationships import (
    extract_urls,
    extract_file_paths,
    extract_markdown_links,
    extract_imports,
    extract_all_references,
    parse_reference_tag,
    RelationshipExtractor,
)


# -----------------------------------------------------------------------------
# URL Extraction Tests
# -----------------------------------------------------------------------------

class TestUrlExtraction:
    """Tests for HTTP URL extraction."""
    
    def test_extracts_https_url(self):
        """Extracts HTTPS URLs."""
        content = "Check out https://example.com/page for more info."
        urls = extract_urls(content)
        assert "https://example.com/page" in urls
    
    def test_extracts_http_url(self):
        """Extracts HTTP URLs."""
        content = "See http://docs.example.org/guide"
        urls = extract_urls(content)
        assert "http://docs.example.org/guide" in urls
    
    def test_extracts_multiple_urls(self):
        """Extracts multiple URLs from content."""
        content = """
        Visit https://example.com and https://docs.example.com
        Also check http://api.example.com/v1
        """
        urls = extract_urls(content)
        assert len(urls) == 3
    
    def test_removes_trailing_punctuation(self):
        """Removes trailing punctuation from URLs."""
        content = "Go to https://example.com/path."
        urls = extract_urls(content)
        assert urls[0] == "https://example.com/path"
    
    def test_handles_urls_in_parentheses(self):
        """Handles URLs wrapped in parentheses."""
        content = "See the docs (https://docs.example.com) for details."
        urls = extract_urls(content)
        assert "https://docs.example.com" in urls
    
    def test_deduplicates_urls(self):
        """Same URL appearing twice is only returned once."""
        content = "Visit https://example.com and later https://example.com again."
        urls = extract_urls(content)
        assert urls.count("https://example.com") == 1


# -----------------------------------------------------------------------------
# File Path Extraction Tests
# -----------------------------------------------------------------------------

class TestFilePathExtraction:
    """Tests for file path extraction."""
    
    def test_extracts_absolute_unix_path(self):
        """Extracts absolute Unix paths."""
        content = "Edit the file at /etc/config/app.yaml"
        paths = extract_file_paths(content)
        assert "/etc/config/app.yaml" in paths
    
    def test_extracts_file_uri(self):
        """Extracts file:// URIs."""
        content = "Open file:///Users/me/doc.md"
        paths = extract_file_paths(content)
        assert "file:///Users/me/doc.md" in paths
    
    def test_extracts_relative_path(self):
        """Extracts relative paths."""
        content = "Import from ./lib/utils.py or ../config.yaml"
        paths = extract_file_paths(content)
        assert "./lib/utils.py" in paths
        assert "../config.yaml" in paths
    
    def test_requires_extension(self):
        """Paths must have file extensions to be extracted."""
        content = "The /var/log directory contains logs."
        paths = extract_file_paths(content)
        # No extension, should not be extracted
        assert "/var/log" not in paths


# -----------------------------------------------------------------------------
# Markdown Link Extraction Tests
# -----------------------------------------------------------------------------

class TestMarkdownLinkExtraction:
    """Tests for markdown link extraction."""
    
    def test_extracts_markdown_link(self):
        """Extracts [text](url) links."""
        content = "See the [documentation](https://docs.example.com) for details."
        links = extract_markdown_links(content)
        assert ("documentation", "https://docs.example.com") in links
    
    def test_extracts_multiple_links(self):
        """Extracts multiple markdown links."""
        content = """
        - [Home](index.md)
        - [API Reference](api.md)
        - [Examples](https://github.com/example/repo)
        """
        links = extract_markdown_links(content)
        assert len(links) == 3
    
    def test_extracts_relative_links(self):
        """Extracts relative path links."""
        content = "See [related doc](./other.md) for more."
        links = extract_markdown_links(content)
        assert ("related doc", "./other.md") in links


# -----------------------------------------------------------------------------
# Import Extraction Tests
# -----------------------------------------------------------------------------

class TestImportExtraction:
    """Tests for code import extraction."""
    
    def test_python_import(self):
        """Extracts Python import statements."""
        content = """
        import os
        import sys
        from pathlib import Path
        from collections.abc import Mapping
        """
        imports = extract_imports(content, "python")
        assert "os" in imports
        assert "sys" in imports
        assert "pathlib" in imports
        assert "collections" in imports
    
    def test_javascript_import(self):
        """Extracts JavaScript imports."""
        content = """
        import React from 'react';
        import { useState } from 'react';
        const fs = require('fs');
        """
        imports = extract_imports(content, "javascript")
        assert "react" in imports
        assert "fs" in imports
    
    def test_rust_use(self):
        """Extracts Rust use statements."""
        content = """
        use std::collections::HashMap;
        use tokio::runtime::Runtime;
        extern crate serde;
        """
        imports = extract_imports(content, "rust")
        # Extracts full paths or crate names
        assert any("std" in imp for imp in imports)
        assert any("tokio" in imp for imp in imports)
        assert "serde" in imports
    
    def test_auto_detect_language(self):
        """Auto-detects language when not specified."""
        python_code = """
        def main():
            import json
            data = json.load(f)
        """
        imports = extract_imports(python_code)
        assert "json" in imports


# -----------------------------------------------------------------------------
# RelationshipExtractor Tests
# -----------------------------------------------------------------------------

class TestRelationshipExtractor:
    """Tests for the main RelationshipExtractor class."""
    
    @pytest.fixture
    def extractor(self):
        return RelationshipExtractor()
    
    def test_extracts_references_tag(self, extractor):
        """URLs become _references tag."""
        content = "See https://example.com for more."
        tags = extractor.extract(content)
        assert "_references" in tags
        assert "https://example.com" in tags["_references"]
    
    def test_extracts_local_references_tag(self, extractor):
        """File paths become _references_local tag."""
        content = "Edit /etc/config.yaml to configure."
        tags = extractor.extract(content)
        assert "_references_local" in tags
        assert "/etc/config.yaml" in tags["_references_local"]
    
    def test_extracts_imports_tag(self, extractor):
        """Code imports become _imports tag."""
        content = """
        import os
        from pathlib import Path
        """
        tags = extractor.extract(content, content_type="code")
        assert "_imports" in tags
        assert "os" in tags["_imports"]
        assert "pathlib" in tags["_imports"]
    
    def test_extracts_links_tag(self, extractor):
        """Markdown links become _links tag."""
        content = "See [docs](./docs.md) and [api](api.md)."
        tags = extractor.extract(content)
        assert "_links" in tags
        assert "./docs.md" in tags["_links"]
    
    def test_respects_max_refs(self):
        """Limits number of references stored."""
        extractor = RelationshipExtractor(max_refs=2)
        content = "Visit https://a.com https://b.com https://c.com https://d.com"
        tags = extractor.extract(content)
        refs = tags["_references"].split(",")
        assert len(refs) == 2
    
    def test_comma_separated_values(self, extractor):
        """Multiple refs are comma-separated."""
        content = "See https://a.com and https://b.com"
        tags = extractor.extract(content)
        assert "," in tags["_references"]
    
    def test_filters_anchor_only_links(self, extractor):
        """Anchor-only links (#section) are filtered out."""
        content = "Jump to [section](#introduction)."
        tags = extractor.extract(content)
        assert "_links" not in tags  # Only anchor links, filtered out


# -----------------------------------------------------------------------------
# Utility Function Tests
# -----------------------------------------------------------------------------

class TestUtilityFunctions:
    """Tests for convenience functions."""
    
    def test_extract_all_references(self):
        """extract_all_references combines all reference types."""
        content = """
        Visit https://example.com
        Edit /etc/config.yaml
        See [docs](./docs.md)
        """
        refs = extract_all_references(content)
        assert "https://example.com" in refs
        assert "/etc/config.yaml" in refs
        assert "./docs.md" in refs
    
    def test_parse_reference_tag(self):
        """parse_reference_tag splits comma-separated values."""
        tag = "https://a.com,https://b.com,https://c.com"
        refs = parse_reference_tag(tag)
        assert refs == ["https://a.com", "https://b.com", "https://c.com"]
    
    def test_parse_reference_tag_empty(self):
        """parse_reference_tag handles empty input."""
        assert parse_reference_tag("") == []
        assert parse_reference_tag(None) == []
