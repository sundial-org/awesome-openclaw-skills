"""
MLX providers for Apple Silicon.

MLX is Apple's ML framework optimized for Apple Silicon. These providers
run entirely locally with no API keys required.

Requires: pip install mlx-lm mlx
"""

import os
from typing import Any

from .base import EmbeddingProvider, SummarizationProvider, get_registry


class MLXEmbedding:
    """
    Embedding provider using MLX on Apple Silicon.
    
    Uses sentence-transformer compatible models converted to MLX format.
    
    Requires: pip install mlx sentence-transformers
    """
    
    def __init__(self, model: str = "mlx-community/bge-small-en-v1.5"):
        """
        Args:
            model: Model name from mlx-community hub or local path.
                   Good options:
                   - mlx-community/bge-small-en-v1.5 (small, fast)
                   - mlx-community/bge-base-en-v1.5 (balanced)
                   - mlx-community/bge-large-en-v1.5 (best quality)
        """
        try:
            import mlx.core as mx
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise RuntimeError(
                "MLXEmbedding requires 'mlx' and 'sentence-transformers'. "
                "Install with: pip install mlx sentence-transformers"
            )
        
        self.model_name = model
        
        # sentence-transformers can use MLX backend on Apple Silicon
        # For MLX-specific models, we use the direct approach
        if model.startswith("mlx-community/"):
            # Use sentence-transformers which auto-detects MLX
            self._model = SentenceTransformer(model, device="mps")
        else:
            self._model = SentenceTransformer(model)
        
        self._dimension: int | None = None
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension from the model."""
        if self._dimension is None:
            self._dimension = self._model.get_sentence_embedding_dimension()
        return self._dimension
    
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class MLXSummarization:
    """
    Summarization provider using MLX-LM on Apple Silicon.
    
    Runs local LLMs optimized for Apple Silicon. No API key required.
    
    Requires: pip install mlx-lm
    """
    
    SYSTEM_PROMPT = """You are a precise summarization assistant. 
Create a concise summary of the provided document that captures:
- The main purpose or topic
- Key points or functionality
- Important details that would help someone decide if this document is relevant

Be factual and specific. Do not include phrases like "This document" - just state the content directly.
Keep the summary under 200 words."""
    
    def __init__(
        self,
        model: str = "mlx-community/Llama-3.2-3B-Instruct-4bit",
        max_tokens: int = 300,
    ):
        """
        Args:
            model: Model name from mlx-community hub or local path.
                   Good options for summarization:
                   - mlx-community/Llama-3.2-3B-Instruct-4bit (fast, small)
                   - mlx-community/Llama-3.2-8B-Instruct-4bit (better quality)
                   - mlx-community/Mistral-7B-Instruct-v0.3-4bit (good balance)
                   - mlx-community/Phi-3.5-mini-instruct-4bit (very fast)
            max_tokens: Maximum tokens in generated summary
        """
        try:
            from mlx_lm import load
        except ImportError:
            raise RuntimeError(
                "MLXSummarization requires 'mlx-lm'. "
                "Install with: pip install mlx-lm"
            )
        
        self.model_name = model
        self.max_tokens = max_tokens
        
        # Load model and tokenizer (downloads on first use)
        self._model, self._tokenizer = load(model)
    
    def summarize(self, content: str, *, max_length: int = 500) -> str:
        """Generate a summary using MLX-LM."""
        from mlx_lm import generate
        
        # Truncate very long content to fit context window
        # Most models have 4k-8k context, leave room for prompt and response
        max_content_chars = 12000
        truncated = content[:max_content_chars] if len(content) > max_content_chars else content
        
        # Format as chat (works with instruction-tuned models)
        if hasattr(self._tokenizer, "apply_chat_template"):
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"Summarize the following:\n\n{truncated}"},
            ]
            prompt = self._tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
        else:
            # Fallback for models without chat template
            prompt = f"{self.SYSTEM_PROMPT}\n\nDocument:\n{truncated}\n\nSummary:"
        
        # Generate
        response = generate(
            self._model,
            self._tokenizer,
            prompt=prompt,
            max_tokens=self.max_tokens,
            verbose=False,
        )
        
        return response.strip()


class MLXTagging:
    """
    Tagging provider using MLX-LM on Apple Silicon.
    
    Uses local LLMs to generate structured tags. No API key required.
    
    Requires: pip install mlx-lm
    """
    
    SYSTEM_PROMPT = """Analyze the document and generate relevant tags as a JSON object.

Generate tags for these categories when applicable:
- content_type: The type of content (e.g., "documentation", "code", "article", "config")
- language: Programming language if code (e.g., "python", "javascript")
- domain: Subject domain (e.g., "authentication", "database", "api", "testing")
- framework: Framework or library if relevant (e.g., "react", "django", "fastapi")

Only include tags that clearly apply. Values should be lowercase.
Respond with ONLY a JSON object, no explanation or other text."""
    
    def __init__(
        self,
        model: str = "mlx-community/Llama-3.2-3B-Instruct-4bit",
        max_tokens: int = 150,
    ):
        """
        Args:
            model: Model name from mlx-community hub
            max_tokens: Maximum tokens in generated response
        """
        try:
            from mlx_lm import load
        except ImportError:
            raise RuntimeError(
                "MLXTagging requires 'mlx-lm'. "
                "Install with: pip install mlx-lm"
            )
        
        self.model_name = model
        self.max_tokens = max_tokens
        self._model, self._tokenizer = load(model)
    
    def tag(self, content: str) -> dict[str, str]:
        """Generate tags using MLX-LM."""
        import json
        from mlx_lm import generate
        
        # Truncate content
        max_content_chars = 8000
        truncated = content[:max_content_chars] if len(content) > max_content_chars else content
        
        # Format prompt
        if hasattr(self._tokenizer, "apply_chat_template"):
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": truncated},
            ]
            prompt = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = f"{self.SYSTEM_PROMPT}\n\nDocument:\n{truncated}\n\nJSON:"
        
        response = generate(
            self._model,
            self._tokenizer,
            prompt=prompt,
            max_tokens=self.max_tokens,
            verbose=False,
        )
        
        # Parse JSON from response
        try:
            # Try to extract JSON from response
            response = response.strip()
            # Handle case where model includes markdown code fence
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            tags = json.loads(response)
            return {str(k): str(v) for k, v in tags.items()}
        except (json.JSONDecodeError, IndexError):
            return {}


def is_apple_silicon() -> bool:
    """Check if running on Apple Silicon."""
    import platform
    return platform.system() == "Darwin" and platform.machine() == "arm64"


# Register providers (only on Apple Silicon)
if is_apple_silicon():
    _registry = get_registry()
    _registry.register_embedding("mlx", MLXEmbedding)
    _registry.register_summarization("mlx", MLXSummarization)
    _registry.register_tagging("mlx", MLXTagging)
