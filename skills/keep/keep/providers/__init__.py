"""
Provider interfaces for associative memory services.

Each provider type defines a protocol that concrete implementations must follow.
Providers are configured at store initialization and handle the heavy lifting of:
- Embedding generation (for semantic search)
- Summarization (for human-readable recall)
- Tagging (for structured navigation)
- Document fetching (for URI resolution)

Concrete providers are lazily loaded when first requested via the registry.
This avoids import-time failures when optional dependencies are missing.
"""

from .base import (
    Document,
    EmbeddingProvider,
    SummarizationProvider,
    TaggingProvider,
    DocumentProvider,
    ProviderRegistry,
    get_registry,
)

# Providers are now loaded lazily by ProviderRegistry._ensure_providers_loaded()
# This avoids import-time failures when optional dependencies are missing

__all__ = [
    # Protocols
    "EmbeddingProvider",
    "SummarizationProvider", 
    "TaggingProvider",
    "DocumentProvider",
    # Data types
    "Document",
    # Registry
    "ProviderRegistry",
    "get_registry",
]

