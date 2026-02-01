"""
Embedding providers for generating vector representations of text.
"""

import os
from typing import Any

from .base import EmbeddingProvider, get_registry


class SentenceTransformerEmbedding:
    """
    Embedding provider using sentence-transformers library.
    
    Runs locally, no API key required. Good default for getting started.
    
    Requires: pip install sentence-transformers
    """
    
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        """
        Args:
            model: Model name from sentence-transformers hub
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise RuntimeError(
                "SentenceTransformerEmbedding requires 'sentence-transformers' library. "
                "Install with: pip install sentence-transformers"
            )
        
        self.model_name = model
        self._model = SentenceTransformer(model)
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension from the model."""
        return self._model.get_sentence_embedding_dimension()
    
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class OpenAIEmbedding:
    """
    Embedding provider using OpenAI's API.
    
    Requires: KEEP_OPENAI_API_KEY or OPENAI_API_KEY environment variable.
    Requires: pip install openai
    """
    
    # Model dimensions (as of 2024)
    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }
    
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
    ):
        """
        Args:
            model: OpenAI embedding model name
            api_key: API key (defaults to environment variable)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError(
                "OpenAIEmbedding requires 'openai' library. "
                "Install with: pip install openai"
            )
        
        self.model_name = model
        self._dimension = self.MODEL_DIMENSIONS.get(model, 1536)
        
        # Resolve API key
        key = api_key or os.environ.get("KEEP_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "OpenAI API key required. Set KEEP_OPENAI_API_KEY or OPENAI_API_KEY"
            )
        
        self._client = OpenAI(api_key=key)
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension for the model."""
        return self._dimension
    
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        response = self._client.embeddings.create(
            model=self.model_name,
            input=text,
        )
        return response.data[0].embedding
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        response = self._client.embeddings.create(
            model=self.model_name,
            input=texts,
        )
        # Sort by index to ensure order matches input
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [d.embedding for d in sorted_data]


class GeminiEmbedding:
    """
    Embedding provider using Google's Gemini API.

    Requires: GEMINI_API_KEY or GOOGLE_API_KEY environment variable.
    Requires: pip install google-genai
    """

    # Model dimensions (as of 2025)
    MODEL_DIMENSIONS = {
        "text-embedding-004": 768,
        "embedding-001": 768,
        "gemini-embedding-001": 768,
    }

    def __init__(
        self,
        model: str = "text-embedding-004",
        api_key: str | None = None,
    ):
        """
        Args:
            model: Gemini embedding model name
            api_key: API key (defaults to environment variable)
        """
        try:
            from google import genai
        except ImportError:
            raise RuntimeError(
                "GeminiEmbedding requires 'google-genai' library. "
                "Install with: pip install google-genai"
            )

        self.model_name = model
        self._dimension = self.MODEL_DIMENSIONS.get(model, 768)

        # Resolve API key
        key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY or GOOGLE_API_KEY"
            )

        self._client = genai.Client(api_key=key)

    @property
    def dimension(self) -> int:
        """Get embedding dimension for the model."""
        return self._dimension

    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        result = self._client.models.embed_content(
            model=self.model_name,
            contents=text,
        )
        return list(result.embeddings[0].values)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        result = self._client.models.embed_content(
            model=self.model_name,
            contents=texts,
        )
        return [list(e.values) for e in result.embeddings]


class OllamaEmbedding:
    """
    Embedding provider using Ollama's local API.

    Requires: Ollama running locally (default: http://localhost:11434)
    """
    
    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
    ):
        """
        Args:
            model: Ollama model name
            base_url: Ollama API base URL
        """
        self.model_name = model
        self.base_url = base_url.rstrip("/")
        self._dimension: int | None = None
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension (determined on first embed call)."""
        if self._dimension is None:
            # Generate a test embedding to determine dimension
            test_embedding = self.embed("test")
            self._dimension = len(test_embedding)
        return self._dimension
    
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        import requests
        
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model_name, "prompt": text},
        )
        response.raise_for_status()
        
        embedding = response.json()["embedding"]
        
        if self._dimension is None:
            self._dimension = len(embedding)
        
        return embedding
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts (sequential for Ollama)."""
        return [self.embed(text) for text in texts]


# Register providers
_registry = get_registry()
_registry.register_embedding("sentence-transformers", SentenceTransformerEmbedding)
_registry.register_embedding("openai", OpenAIEmbedding)
_registry.register_embedding("gemini", GeminiEmbedding)
_registry.register_embedding("ollama", OllamaEmbedding)
