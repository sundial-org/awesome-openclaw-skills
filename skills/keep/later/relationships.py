"""
Relationship extraction for associative memory.

Detects references, links, and relationships between items without
requiring ML models. These are "batteries-included" extractors that
work on content structure.

Relationships are returned as tags where the value is a comma-separated
list of target IDs (URIs). This keeps the model simple — relationships
are just tags pointing to other items.
"""

import re
from typing import Any
from urllib.parse import urlparse


# -----------------------------------------------------------------------------
# URL and Path Extraction
# -----------------------------------------------------------------------------

# URL pattern - matches http(s) URLs
URL_PATTERN = re.compile(
    r'https?://[^\s<>\[\]()"\',;]+[^\s<>\[\]()"\',;.!?]',
    re.IGNORECASE
)

# File path patterns
FILE_PATH_PATTERNS = [
    # Unix absolute paths
    re.compile(r'(?<![a-zA-Z0-9])/(?:[a-zA-Z0-9._-]+/)*[a-zA-Z0-9._-]+\.[a-zA-Z0-9]+'),
    # file:// URIs
    re.compile(r'file://[^\s<>\[\]()"\',;]+'),
    # Relative paths with extension (e.g., ./foo/bar.py, ../config.yaml)
    re.compile(r'\.{1,2}/(?:[a-zA-Z0-9._-]+/)*[a-zA-Z0-9._-]+\.[a-zA-Z0-9]+'),
]

# Markdown link pattern: [text](url)
MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

# Import patterns by language
IMPORT_PATTERNS = {
    "python": [
        re.compile(r'^\s*import\s+([\w.]+)', re.MULTILINE),
        re.compile(r'^\s*from\s+([\w.]+)\s+import', re.MULTILINE),
    ],
    "javascript": [
        re.compile(r'^\s*import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE),
        re.compile(r'require\([\'"]([^\'"]+)[\'"]\)', re.MULTILINE),
    ],
    "typescript": [
        re.compile(r'^\s*import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE),
    ],
    "go": [
        re.compile(r'^\s*import\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE),
        re.compile(r'^\s*"([^"]+)"', re.MULTILINE),  # Inside import block
    ],
    "rust": [
        re.compile(r'^\s*use\s+([\w:]+)', re.MULTILINE),
        re.compile(r'^\s*extern\s+crate\s+(\w+)', re.MULTILINE),
    ],
}


def extract_urls(content: str) -> list[str]:
    """
    Extract HTTP(S) URLs from content.
    
    Returns deduplicated list of URLs found.
    """
    urls = URL_PATTERN.findall(content)
    # Clean up trailing punctuation that might have been captured
    cleaned = []
    for url in urls:
        # Remove common trailing chars that aren't part of URLs
        while url and url[-1] in '.,;:!?)\'">':
            url = url[:-1]
        if url and url not in cleaned:
            cleaned.append(url)
    return cleaned


def extract_file_paths(content: str) -> list[str]:
    """
    Extract file paths and file:// URIs from content.
    
    Returns deduplicated list of paths found.
    """
    paths = []
    for pattern in FILE_PATH_PATTERNS:
        for match in pattern.findall(content):
            if match not in paths:
                paths.append(match)
    return paths


def extract_markdown_links(content: str) -> list[tuple[str, str]]:
    """
    Extract markdown links as (text, url) tuples.
    
    Returns list of (link_text, link_url) pairs.
    """
    return MARKDOWN_LINK_PATTERN.findall(content)


def extract_imports(content: str, language: str | None = None) -> list[str]:
    """
    Extract import/require statements from code.
    
    Args:
        content: Source code content
        language: Programming language (python, javascript, etc.)
                  If None, tries all known patterns.
    
    Returns:
        List of imported module/package names
    """
    imports = []
    
    languages = [language] if language else IMPORT_PATTERNS.keys()
    
    for lang in languages:
        if lang not in IMPORT_PATTERNS:
            continue
        for pattern in IMPORT_PATTERNS[lang]:
            for match in pattern.findall(content):
                # Normalize: take just the top-level package
                module = match.split('.')[0].split('/')[0]
                if module and module not in imports:
                    imports.append(module)
    
    return imports


# -----------------------------------------------------------------------------
# Relationship Extractor
# -----------------------------------------------------------------------------

class RelationshipExtractor:
    """
    Extracts relationships from content as tags.
    
    Detected relationships:
    - _references: URLs found in content
    - _references_local: File paths found in content  
    - _imports: Code imports/dependencies
    - _links: Markdown link targets
    
    All relationship tags use underscore prefix (system tags) since
    they're derived automatically, not provided by users.
    """
    
    def __init__(
        self,
        extract_urls: bool = True,
        extract_paths: bool = True,
        extract_imports: bool = True,
        extract_links: bool = True,
        max_refs: int = 20,
    ):
        """
        Args:
            extract_urls: Whether to extract HTTP URLs
            extract_paths: Whether to extract file paths
            extract_imports: Whether to extract code imports
            extract_links: Whether to extract markdown links
            max_refs: Maximum references to store per type (prevents huge tags)
        """
        self.extract_urls = extract_urls
        self.extract_paths = extract_paths
        self.extract_imports = extract_imports
        self.extract_links = extract_links
        self.max_refs = max_refs
    
    def extract(
        self,
        content: str,
        *,
        language: str | None = None,
        content_type: str | None = None,
    ) -> dict[str, str]:
        """
        Extract relationships from content.
        
        Args:
            content: Text content to analyze
            language: Programming language (for import extraction)
            content_type: Content type hint (e.g., "code", "documentation")
        
        Returns:
            Dict of relationship tags. Values are comma-separated lists
            of target URIs/identifiers.
        """
        tags = {}
        
        # Extract URLs
        if self.extract_urls:
            urls = extract_urls(content)[:self.max_refs]
            if urls:
                tags["_references"] = ",".join(urls)
        
        # Extract file paths
        if self.extract_paths:
            paths = extract_file_paths(content)[:self.max_refs]
            if paths:
                tags["_references_local"] = ",".join(paths)
        
        # Extract imports (only for code)
        if self.extract_imports:
            # Detect language from content if not provided
            if language is None and content_type == "code":
                language = self._detect_language(content)
            
            if language or content_type == "code":
                imports = extract_imports(content, language)[:self.max_refs]
                if imports:
                    tags["_imports"] = ",".join(imports)
        
        # Extract markdown links
        if self.extract_links:
            links = extract_markdown_links(content)
            link_urls = [url for _, url in links if url][:self.max_refs]
            if link_urls:
                # Filter out anchors-only links
                external_links = [u for u in link_urls if not u.startswith('#')]
                if external_links:
                    tags["_links"] = ",".join(external_links)
        
        return tags
    
    def _detect_language(self, content: str) -> str | None:
        """Simple language detection for import extraction."""
        # Check for distinctive patterns
        if re.search(r'^\s*(def|class)\s+\w+.*:', content, re.MULTILINE):
            return "python"
        if re.search(r'^\s*(const|let|var)\s+\w+\s*=', content, re.MULTILINE):
            return "javascript"
        if re.search(r'^\s*fn\s+\w+', content, re.MULTILINE):
            return "rust"
        if re.search(r'^\s*func\s+\w+', content, re.MULTILINE):
            return "go"
        return None


# -----------------------------------------------------------------------------
# Convenience functions
# -----------------------------------------------------------------------------

def extract_all_references(content: str) -> list[str]:
    """
    Extract all references (URLs + paths + links) from content.
    
    Convenience function for quick reference extraction.
    """
    refs = []
    refs.extend(extract_urls(content))
    refs.extend(extract_file_paths(content))
    refs.extend(url for _, url in extract_markdown_links(content))
    return list(dict.fromkeys(refs))  # Dedupe preserving order


def parse_reference_tag(tag_value: str) -> list[str]:
    """
    Parse a comma-separated reference tag back to a list.
    
    Useful for querying: given an item's _references tag,
    get the list of URIs it references.
    """
    if not tag_value:
        return []
    return [ref.strip() for ref in tag_value.split(",") if ref.strip()]
