"""
Document providers for fetching content from various URI schemes.
"""

from pathlib import Path
from urllib.parse import urlparse

from .base import Document, DocumentProvider, get_registry


class FileDocumentProvider:
    """
    Fetches documents from the local filesystem.

    Supports file:// URIs and attempts to detect content type from extension.
    Performs text extraction for PDF and HTML files.
    """

    EXTENSION_TYPES = {
        ".md": "text/markdown",
        ".markdown": "text/markdown",
        ".txt": "text/plain",
        ".py": "text/x-python",
        ".js": "text/javascript",
        ".ts": "text/typescript",
        ".json": "application/json",
        ".yaml": "text/yaml",
        ".yml": "text/yaml",
        ".html": "text/html",
        ".htm": "text/html",
        ".css": "text/css",
        ".xml": "application/xml",
        ".rst": "text/x-rst",
        ".pdf": "application/pdf",
    }
    
    def supports(self, uri: str) -> bool:
        """Check if this is a file:// URI or bare path."""
        return uri.startswith("file://") or uri.startswith("/")
    
    def fetch(self, uri: str) -> Document:
        """Read file content from the filesystem with text extraction for PDF/HTML."""
        # Normalize to path
        if uri.startswith("file://"):
            path_str = uri.removeprefix("file://")
        else:
            path_str = uri

        path = Path(path_str)

        if not path.exists():
            raise IOError(f"File not found: {path}")

        if not path.is_file():
            raise IOError(f"Not a file: {path}")

        # Detect content type
        suffix = path.suffix.lower()
        content_type = self.EXTENSION_TYPES.get(suffix, "text/plain")

        # Extract text based on file type
        if suffix == ".pdf":
            content = self._extract_pdf_text(path)
        elif suffix in (".html", ".htm"):
            content = self._extract_html_text(path)
        else:
            # Read as plain text
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                raise IOError(f"Cannot read file as text: {path}")

        # Gather metadata
        stat = path.stat()
        metadata = {
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "name": path.name,
        }

        return Document(
            uri=f"file://{path.resolve()}",  # Normalize to absolute
            content=content,
            content_type=content_type,
            metadata=metadata,
        )

    def _extract_pdf_text(self, path: Path) -> str:
        """Extract text from PDF file."""
        try:
            from pypdf import PdfReader
        except ImportError:
            raise IOError(
                f"PDF support requires 'pypdf' library. "
                f"Install with: pip install pypdf\n"
                f"Cannot read PDF: {path}"
            )

        try:
            reader = PdfReader(path)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            if not text_parts:
                raise IOError(f"No text extracted from PDF: {path}")

            return "\n\n".join(text_parts)
        except Exception as e:
            raise IOError(f"Failed to extract text from PDF {path}: {e}")

    def _extract_html_text(self, path: Path) -> str:
        """Extract text from HTML file."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise IOError(
                f"HTML text extraction requires 'beautifulsoup4' library. "
                f"Install with: pip install beautifulsoup4\n"
                f"Cannot extract text from HTML: {path}"
            )

        try:
            html_content = path.read_text(encoding="utf-8")
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text
        except Exception as e:
            raise IOError(f"Failed to extract text from HTML {path}: {e}")


class HttpDocumentProvider:
    """
    Fetches documents from HTTP/HTTPS URLs.
    
    Requires the `requests` library (optional dependency).
    """
    
    def __init__(self, timeout: int = 30, max_size: int = 10_000_000):
        """
        Args:
            timeout: Request timeout in seconds
            max_size: Maximum content size in bytes
        """
        self.timeout = timeout
        self.max_size = max_size
    
    def supports(self, uri: str) -> bool:
        """Check if this is an HTTP(S) URL."""
        return uri.startswith("http://") or uri.startswith("https://")
    
    def fetch(self, uri: str) -> Document:
        """Fetch content from HTTP URL."""
        try:
            import requests
        except ImportError:
            raise RuntimeError("HTTP document fetching requires 'requests' library")

        try:
            # Use context manager to ensure connection is closed
            with requests.get(
                uri,
                timeout=self.timeout,
                headers={"User-Agent": "keep/0.1"},
                stream=True,
            ) as response:
                response.raise_for_status()

                # Check size
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > self.max_size:
                    raise IOError(f"Content too large: {content_length} bytes")

                # Read content with size limit
                content = response.text[:self.max_size]

                # Get content type
                content_type = response.headers.get("content-type", "text/plain")
                if ";" in content_type:
                    content_type = content_type.split(";")[0].strip()

                return Document(
                    uri=uri,
                    content=content,
                    content_type=content_type,
                    metadata={
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                    },
                )
        except requests.RequestException as e:
            raise IOError(f"Failed to fetch {uri}: {e}")


class CompositeDocumentProvider:
    """
    Combines multiple document providers, delegating to the appropriate one.
    
    This is the default provider used by Keeper.
    """
    
    def __init__(self, providers: list[DocumentProvider] | None = None):
        """
        Args:
            providers: List of providers to try. If None, uses defaults.
        """
        if providers is None:
            self._providers = [
                FileDocumentProvider(),
                HttpDocumentProvider(),
            ]
        else:
            self._providers = list(providers)
    
    def supports(self, uri: str) -> bool:
        """Check if any provider supports this URI."""
        return any(p.supports(uri) for p in self._providers)
    
    def fetch(self, uri: str) -> Document:
        """Fetch using the first provider that supports this URI."""
        for provider in self._providers:
            if provider.supports(uri):
                return provider.fetch(uri)
        
        raise ValueError(f"No provider supports URI: {uri}")
    
    def add_provider(self, provider: DocumentProvider) -> None:
        """Add a provider to the list (checked first)."""
        self._providers.insert(0, provider)


# Register providers
_registry = get_registry()
_registry.register_document("file", FileDocumentProvider)
_registry.register_document("http", HttpDocumentProvider)
_registry.register_document("composite", CompositeDocumentProvider)
