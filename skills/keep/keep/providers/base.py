"""
Base provider protocols.

These define the interfaces that concrete providers must implement.
Using Protocol for structural subtyping - no explicit inheritance required.
"""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


# -----------------------------------------------------------------------------
# Document Fetching
# -----------------------------------------------------------------------------

@dataclass
class Document:
    """
    A fetched document ready for processing.
    
    Attributes:
        uri: Original URI that was fetched
        content: Text content of the document
        content_type: MIME type if known (e.g., "text/markdown", "text/plain")
        metadata: Additional metadata from the source (headers, file stats, etc.)
    """
    uri: str
    content: str
    content_type: str | None = None
    metadata: dict[str, Any] | None = None


@runtime_checkable
class DocumentProvider(Protocol):
    """
    Fetches document content from a URI.
    
    Implementations handle specific URI schemes (file://, https://, s3://, etc.)
    and convert the content to text.
    
    Example implementation:
        class FileDocumentProvider:
            def supports(self, uri: str) -> bool:
                return uri.startswith("file://")
            
            def fetch(self, uri: str) -> Document:
                path = uri.removeprefix("file://")
                content = Path(path).read_text()
                return Document(uri=uri, content=content, content_type="text/plain")
    """
    
    def supports(self, uri: str) -> bool:
        """
        Check if this provider can handle the given URI.
        
        Args:
            uri: The URI to check
            
        Returns:
            True if this provider can fetch the URI
        """
        ...
    
    def fetch(self, uri: str) -> Document:
        """
        Fetch and return the document content.
        
        Args:
            uri: The URI to fetch
            
        Returns:
            Document with text content
            
        Raises:
            ValueError: If URI is malformed
            IOError: If document cannot be fetched
        """
        ...


# -----------------------------------------------------------------------------
# Embedding Generation
# -----------------------------------------------------------------------------

@runtime_checkable
class EmbeddingProvider(Protocol):
    """
    Generates vector embeddings from text.
    
    Embeddings enable semantic similarity search. The same provider instance
    must be used for both indexing and querying to ensure consistent vectors.
    
    Example implementation:
        class SentenceTransformerEmbedding:
            def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(model_name)
            
            @property
            def dimension(self) -> int:
                return self.model.get_sentence_embedding_dimension()
            
            def embed(self, text: str) -> list[float]:
                return self.model.encode(text).tolist()
            
            def embed_batch(self, texts: list[str]) -> list[list[float]]:
                return self.model.encode(texts).tolist()
    """
    
    @property
    def dimension(self) -> int:
        """
        The dimensionality of the embedding vectors.
        
        This must be consistent across all calls. ChromaDb and other vector
        stores need this to configure the index.
        """
        ...
    
    def embed(self, text: str) -> list[float]:
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            A list of floats representing the embedding vector
        """
        ...
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        
        Batch processing is often more efficient than individual calls.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors, one per input text
        """
        ...


# -----------------------------------------------------------------------------
# Summarization
# -----------------------------------------------------------------------------

@runtime_checkable
class SummarizationProvider(Protocol):
    """
    Generates concise summaries of document content.
    
    Summaries are stored alongside items and enable quick recall without
    fetching the original document. They're also used for full-text search.
    
    Example implementation:
        class OpenAISummarization:
            def __init__(self, model: str = "gpt-4o-mini"):
                self.client = OpenAI()
                self.model = model
            
            def summarize(self, content: str, max_length: int = 500) -> str:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Summarize concisely."},
                        {"role": "user", "content": content}
                    ],
                    max_tokens=max_length
                )
                return response.choices[0].message.content
    """
    
    def summarize(self, content: str, *, max_length: int = 500) -> str:
        """
        Generate a summary of the content.
        
        Args:
            content: The full document content
            max_length: Approximate maximum length in characters
            
        Returns:
            A concise summary of the content
        """
        ...


# -----------------------------------------------------------------------------
# Tagging
# -----------------------------------------------------------------------------

@runtime_checkable
class TaggingProvider(Protocol):
    """
    Generates structured tags from document content.
    
    Tags enable traditional navigation and filtering. The provider analyzes
    content and returns relevant key-value pairs.
    
    Example implementation:
        class OpenAITagging:
            def __init__(self, model: str = "gpt-4o-mini"):
                self.client = OpenAI()
                self.model = model
            
            def tag(self, content: str) -> dict[str, str]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[...],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
    """
    
    def tag(self, content: str) -> dict[str, str]:
        """
        Generate tags for the content.
        
        Args:
            content: The full document content
            
        Returns:
            Dictionary of tag key-value pairs
            
        Note:
            Keys should be lowercase with underscores (e.g., "content_type").
            Values should be simple strings.
            System tags (keys starting with "_") should not be generated here.
        """
        ...


# -----------------------------------------------------------------------------
# Provider Registry
# -----------------------------------------------------------------------------

class ProviderRegistry:
    """
    Registry for discovering and instantiating providers.

    Providers are registered by name and can be instantiated from configuration.
    This allows the store configuration (TOML) to specify providers by name
    rather than requiring code changes.

    Example:
        registry = ProviderRegistry()
        registry.register_embedding("sentence-transformers", SentenceTransformerEmbedding)
        registry.register_embedding("openai", OpenAIEmbedding)

        # Later, from config:
        provider = registry.create_embedding("sentence-transformers", {"model": "all-MiniLM-L6-v2"})
    """

    def __init__(self):
        self._embedding_providers: dict[str, type] = {}
        self._summarization_providers: dict[str, type] = {}
        self._tagging_providers: dict[str, type] = {}
        self._document_providers: dict[str, type] = {}
        self._lazy_loaded = False
    
    def _ensure_providers_loaded(self) -> None:
        """Lazily load all provider modules."""
        if self._lazy_loaded:
            return

        self._lazy_loaded = True

        # Import provider modules to trigger registration
        # These imports are safe - they only register classes, don't instantiate
        try:
            from . import documents
        except ImportError:
            pass  # Document provider might not be available

        try:
            from . import embeddings
        except ImportError:
            pass  # Embedding providers might not be available

        try:
            from . import summarization
        except ImportError:
            pass  # Summarization providers might not be available

        try:
            from . import llm
        except ImportError:
            pass  # LLM providers might not be available

        try:
            from . import mlx
        except ImportError:
            pass  # MLX providers might not be available

    # Registration methods

    def register_embedding(self, name: str, provider_class: type) -> None:
        """Register an embedding provider class."""
        self._embedding_providers[name] = provider_class
    
    def register_summarization(self, name: str, provider_class: type) -> None:
        """Register a summarization provider class."""
        self._summarization_providers[name] = provider_class
    
    def register_tagging(self, name: str, provider_class: type) -> None:
        """Register a tagging provider class."""
        self._tagging_providers[name] = provider_class
    
    def register_document(self, name: str, provider_class: type) -> None:
        """Register a document provider class."""
        self._document_providers[name] = provider_class
    
    # Factory methods

    def create_embedding(self, name: str, params: dict | None = None) -> EmbeddingProvider:
        """Create an embedding provider instance."""
        self._ensure_providers_loaded()
        if name not in self._embedding_providers:
            available = ", ".join(self._embedding_providers.keys()) or "none"
            raise ValueError(
                f"Unknown embedding provider: '{name}'. "
                f"Available providers: {available}. "
                f"Install missing dependencies or check provider name."
            )
        try:
            return self._embedding_providers[name](**(params or {}))
        except Exception as e:
            raise RuntimeError(
                f"Failed to create embedding provider '{name}': {e}\n"
                f"Make sure required dependencies are installed."
            ) from e
    
    def create_summarization(self, name: str, params: dict | None = None) -> SummarizationProvider:
        """Create a summarization provider instance."""
        self._ensure_providers_loaded()
        if name not in self._summarization_providers:
            available = ", ".join(self._summarization_providers.keys()) or "none"
            raise ValueError(
                f"Unknown summarization provider: '{name}'. "
                f"Available providers: {available}. "
                f"Install missing dependencies or check provider name."
            )
        try:
            return self._summarization_providers[name](**(params or {}))
        except Exception as e:
            raise RuntimeError(
                f"Failed to create summarization provider '{name}': {e}\n"
                f"Make sure required dependencies are installed."
            ) from e
    
    def create_tagging(self, name: str, params: dict | None = None) -> TaggingProvider:
        """Create a tagging provider instance."""
        self._ensure_providers_loaded()
        if name not in self._tagging_providers:
            available = ", ".join(self._tagging_providers.keys()) or "none"
            raise ValueError(
                f"Unknown tagging provider: '{name}'. "
                f"Available providers: {available}. "
                f"Install missing dependencies or check provider name."
            )
        try:
            return self._tagging_providers[name](**(params or {}))
        except Exception as e:
            raise RuntimeError(
                f"Failed to create tagging provider '{name}': {e}\n"
                f"Make sure required dependencies are installed."
            ) from e
    
    def create_document(self, name: str, params: dict | None = None) -> DocumentProvider:
        """Create a document provider instance."""
        self._ensure_providers_loaded()
        if name not in self._document_providers:
            available = ", ".join(self._document_providers.keys()) or "none"
            raise ValueError(
                f"Unknown document provider: '{name}'. "
                f"Available providers: {available}. "
                f"Install missing dependencies or check provider name."
            )
        try:
            return self._document_providers[name](**(params or {}))
        except Exception as e:
            raise RuntimeError(
                f"Failed to create document provider '{name}': {e}\n"
                f"Make sure required dependencies are installed."
            ) from e
    
    # Introspection
    
    def list_embedding_providers(self) -> list[str]:
        """List registered embedding provider names."""
        return list(self._embedding_providers.keys())
    
    def list_summarization_providers(self) -> list[str]:
        """List registered summarization provider names."""
        return list(self._summarization_providers.keys())
    
    def list_tagging_providers(self) -> list[str]:
        """List registered tagging provider names."""
        return list(self._tagging_providers.keys())
    
    def list_document_providers(self) -> list[str]:
        """List registered document provider names."""
        return list(self._document_providers.keys())


# Global registry instance
# Concrete providers register themselves on import
_registry = ProviderRegistry()


def get_registry() -> ProviderRegistry:
    """Get the global provider registry."""
    return _registry
