"""
Summarization and tagging providers using LLMs.
"""

import json
import os
from typing import Any

from .base import SummarizationProvider, TaggingProvider, get_registry


# -----------------------------------------------------------------------------
# Summarization Providers
# -----------------------------------------------------------------------------

class AnthropicSummarization:
    """
    Summarization provider using Anthropic's Claude API.
    
    Requires: ANTHROPIC_API_KEY environment variable.
    Optionally reads from OpenClaw config via OPENCLAW_CONFIG env var.
    """
    
    SYSTEM_PROMPT = """You are a precise summarization assistant. 
Create a concise summary of the provided document that captures:
- The main purpose or topic
- Key points or functionality
- Important details that would help someone decide if this document is relevant

Be factual and specific. Do not include phrases like "This document" - just state the content directly."""
    
    def __init__(
        self,
        model: str = "claude-3-5-haiku-20241022",
        api_key: str | None = None,
        max_tokens: int = 200,
    ):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise RuntimeError("AnthropicSummarization requires 'anthropic' library")
        
        self.model = model
        self.max_tokens = max_tokens
        
        # Try environment variable first, then OpenClaw config
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            # Try to read from OpenClaw config (OAuth tokens stored separately)
            # For now, just require explicit API key
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        
        self.client = Anthropic(api_key=key)
    
    def summarize(self, content: str) -> str:
        """Generate summary using Anthropic Claude."""
        # Truncate very long content
        truncated = content[:50000] if len(content) > 50000 else content
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": truncated}
                ],
            )
            
            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return truncated[:500]  # Fallback
        except Exception as e:
            # Fallback to truncation on error
            return truncated[:500]


class OpenAISummarization:
    """
    Summarization provider using OpenAI's chat API.
    
    Requires: KEEP_OPENAI_API_KEY or OPENAI_API_KEY environment variable.
    """
    
    SYSTEM_PROMPT = """You are a precise summarization assistant. 
Create a concise summary of the provided document that captures:
- The main purpose or topic
- Key points or functionality
- Important details that would help someone decide if this document is relevant

Be factual and specific. Do not include phrases like "This document" - just state the content directly."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        max_tokens: int = 200,
    ):
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("OpenAISummarization requires 'openai' library")
        
        self.model = model
        self.max_tokens = max_tokens
        
        key = api_key or os.environ.get("KEEP_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API key required")
        
        self._client = OpenAI(api_key=key)
    
    def summarize(self, content: str, *, max_length: int = 500) -> str:
        """Generate a summary using OpenAI."""
        # Truncate very long content to avoid token limits
        truncated = content[:50000] if len(content) > 50000 else content
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": truncated},
            ],
            max_tokens=self.max_tokens,
            temperature=0.3,
        )
        
        return response.choices[0].message.content.strip()


class OllamaSummarization:
    """
    Summarization provider using Ollama's local API.
    """
    
    SYSTEM_PROMPT = OpenAISummarization.SYSTEM_PROMPT
    
    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
    
    def summarize(self, content: str, *, max_length: int = 500) -> str:
        """Generate a summary using Ollama."""
        import requests
        
        truncated = content[:50000] if len(content) > 50000 else content
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": truncated},
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        
        return response.json()["message"]["content"].strip()


class PassthroughSummarization:
    """
    Summarization provider that returns the first N characters.
    
    Useful for testing or when LLM summarization is not needed.
    """
    
    def __init__(self, max_chars: int = 500):
        self.max_chars = max_chars
    
    def summarize(self, content: str, *, max_length: int = 500) -> str:
        """Return truncated content as summary."""
        limit = min(self.max_chars, max_length)
        if len(content) <= limit:
            return content
        return content[:limit].rsplit(" ", 1)[0] + "..."


# -----------------------------------------------------------------------------
# Tagging Providers
# -----------------------------------------------------------------------------

class AnthropicTagging:
    """
    Tagging provider using Anthropic's Claude API with JSON output.
    """
    
    SYSTEM_PROMPT = """Analyze the document and generate relevant tags as a JSON object.

Generate tags for these categories when applicable:
- content_type: The type of content (e.g., "documentation", "code", "article", "config")
- language: Programming language if code (e.g., "python", "javascript")
- domain: Subject domain (e.g., "authentication", "database", "api", "testing")
- framework: Framework or library if relevant (e.g., "react", "django", "fastapi")

Only include tags that clearly apply. Values should be lowercase.

Respond with a JSON object only, no explanation."""
    
    def __init__(
        self,
        model: str = "claude-3-5-haiku-20241022",
        api_key: str | None = None,
    ):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise RuntimeError("AnthropicTagging requires 'anthropic' library")
        
        self.model = model
        
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        
        self._client = Anthropic(api_key=key)
    
    def tag(self, content: str) -> dict[str, str]:
        """Generate tags using Anthropic Claude."""
        truncated = content[:20000] if len(content) > 20000 else content
        
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.2,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": truncated}
                ],
            )
            
            # Parse JSON from response
            if response.content and len(response.content) > 0:
                tags = json.loads(response.content[0].text)
                return {str(k): str(v) for k, v in tags.items()}
            return {}
        except (json.JSONDecodeError, Exception):
            return {}


class OpenAITagging:
    """
    Tagging provider using OpenAI's chat API with JSON output.
    """
    
    SYSTEM_PROMPT = """Analyze the document and generate relevant tags as a JSON object.

Generate tags for these categories when applicable:
- content_type: The type of content (e.g., "documentation", "code", "article", "config")
- language: Programming language if code (e.g., "python", "javascript")
- domain: Subject domain (e.g., "authentication", "database", "api", "testing")
- framework: Framework or library if relevant (e.g., "react", "django", "fastapi")

Only include tags that clearly apply. Values should be lowercase.

Respond with a JSON object only, no explanation."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
    ):
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("OpenAITagging requires 'openai' library")
        
        self.model = model
        
        key = api_key or os.environ.get("KEEP_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API key required")
        
        self._client = OpenAI(api_key=key)
    
    def tag(self, content: str) -> dict[str, str]:
        """Generate tags using OpenAI."""
        truncated = content[:20000] if len(content) > 20000 else content
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": truncated},
            ],
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0.2,
        )
        
        try:
            tags = json.loads(response.choices[0].message.content)
            # Ensure all values are strings
            return {str(k): str(v) for k, v in tags.items()}
        except json.JSONDecodeError:
            return {}


class OllamaTagging:
    """
    Tagging provider using Ollama's local API.
    """
    
    SYSTEM_PROMPT = OpenAITagging.SYSTEM_PROMPT
    
    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
    
    def tag(self, content: str) -> dict[str, str]:
        """Generate tags using Ollama."""
        import requests
        
        truncated = content[:20000] if len(content) > 20000 else content
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": truncated},
                ],
                "format": "json",
                "stream": False,
            },
        )
        response.raise_for_status()
        
        try:
            tags = json.loads(response.json()["message"]["content"])
            return {str(k): str(v) for k, v in tags.items()}
        except (json.JSONDecodeError, KeyError):
            return {}


class NoopTagging:
    """
    Tagging provider that returns empty tags.
    
    Useful when tagging is disabled or for testing.
    """
    
    def tag(self, content: str) -> dict[str, str]:
        """Return empty tags."""
        return {}


# Register providers
_registry = get_registry()
_registry.register_summarization("anthropic", AnthropicSummarization)
_registry.register_summarization("openai", OpenAISummarization)
_registry.register_summarization("ollama", OllamaSummarization)
_registry.register_summarization("passthrough", PassthroughSummarization)
_registry.register_tagging("anthropic", AnthropicTagging)
_registry.register_tagging("openai", OpenAITagging)
_registry.register_tagging("ollama", OllamaTagging)
_registry.register_tagging("noop", NoopTagging)
