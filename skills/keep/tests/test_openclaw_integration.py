"""
Tests for OpenClaw integration - embedding provider config sharing.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from keep.config import (
    detect_default_providers,
    get_openclaw_memory_search_config,
    read_openclaw_config,
    ProviderConfig,
)


class TestReadOpenclawConfig:
    """Tests for reading OpenClaw config file."""

    def test_returns_none_when_no_config(self):
        """Should return None when no config file exists."""
        with patch.dict(os.environ, {"OPENCLAW_CONFIG": "/nonexistent/path.json"}, clear=False):
            result = read_openclaw_config()
            assert result is None

    def test_reads_config_from_env_path(self):
        """Should read config from OPENCLAW_CONFIG env var path."""
        config_data = {"agents": {"defaults": {"model": {"primary": "test-model"}}}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            with patch.dict(os.environ, {"OPENCLAW_CONFIG": temp_path}, clear=False):
                result = read_openclaw_config()
                assert result == config_data
        finally:
            os.unlink(temp_path)

    def test_returns_none_on_invalid_json(self):
        """Should return None for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json {{{")
            temp_path = f.name

        try:
            with patch.dict(os.environ, {"OPENCLAW_CONFIG": temp_path}, clear=False):
                result = read_openclaw_config()
                assert result is None
        finally:
            os.unlink(temp_path)


class TestGetOpenclawMemorySearchConfig:
    """Tests for extracting memorySearch config."""

    def test_returns_none_when_no_config(self):
        """Should return None when openclaw config is None."""
        result = get_openclaw_memory_search_config(None)
        assert result is None

    def test_returns_none_when_no_memory_search(self):
        """Should return None when memorySearch not configured."""
        config = {"agents": {"defaults": {}}}
        result = get_openclaw_memory_search_config(config)
        assert result is None

    def test_extracts_memory_search_config(self):
        """Should extract memorySearch config from nested structure."""
        memory_search = {
            "provider": "gemini",
            "model": "text-embedding-004",
            "remote": {"apiKey": "test-key"},
        }
        config = {"agents": {"defaults": {"memorySearch": memory_search}}}

        result = get_openclaw_memory_search_config(config)
        assert result == memory_search


class TestDetectDefaultProviders:
    """Tests for provider detection with OpenClaw integration."""

    def test_falls_back_to_sentence_transformers_without_config(self):
        """Should use sentence-transformers when no OpenClaw config."""
        with patch.dict(os.environ, {"OPENCLAW_CONFIG": "/nonexistent"}, clear=False):
            # Clear any API keys that might affect detection
            env = {
                "OPENCLAW_CONFIG": "/nonexistent",
                "OPENAI_API_KEY": "",
                "GEMINI_API_KEY": "",
                "GOOGLE_API_KEY": "",
            }
            with patch.dict(os.environ, env, clear=False):
                providers = detect_default_providers()
                assert providers["embedding"].name == "sentence-transformers"

    def test_uses_gemini_when_configured(self):
        """Should use Gemini embeddings when memorySearch.provider is gemini."""
        config_data = {
            "agents": {
                "defaults": {
                    "memorySearch": {
                        "provider": "gemini",
                        "model": "text-embedding-004",
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            env = {
                "OPENCLAW_CONFIG": temp_path,
                "GEMINI_API_KEY": "test-key",
            }
            with patch.dict(os.environ, env, clear=False):
                providers = detect_default_providers()
                assert providers["embedding"].name == "gemini"
                assert providers["embedding"].params.get("model") == "text-embedding-004"
        finally:
            os.unlink(temp_path)

    def test_uses_openai_when_configured(self):
        """Should use OpenAI embeddings when memorySearch.provider is openai."""
        config_data = {
            "agents": {
                "defaults": {
                    "memorySearch": {
                        "provider": "openai",
                        "model": "text-embedding-3-small",
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            env = {
                "OPENCLAW_CONFIG": temp_path,
                "OPENAI_API_KEY": "test-key",
            }
            with patch.dict(os.environ, env, clear=False):
                providers = detect_default_providers()
                assert providers["embedding"].name == "openai"
                assert providers["embedding"].params.get("model") == "text-embedding-3-small"
        finally:
            os.unlink(temp_path)

    def test_auto_prefers_openai_when_both_keys_present(self):
        """Should prefer OpenAI over Gemini when provider is auto and both keys present."""
        config_data = {
            "agents": {
                "defaults": {
                    "memorySearch": {
                        "provider": "auto",
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            env = {
                "OPENCLAW_CONFIG": temp_path,
                "OPENAI_API_KEY": "test-openai-key",
                "GEMINI_API_KEY": "test-gemini-key",
            }
            with patch.dict(os.environ, env, clear=False):
                providers = detect_default_providers()
                assert providers["embedding"].name == "openai"
        finally:
            os.unlink(temp_path)

    def test_auto_uses_gemini_when_only_gemini_key(self):
        """Should use Gemini when provider is auto and only Gemini key present."""
        config_data = {
            "agents": {
                "defaults": {
                    "memorySearch": {
                        "provider": "auto",
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            env = {
                "OPENCLAW_CONFIG": temp_path,
                "OPENAI_API_KEY": "",
                "GEMINI_API_KEY": "test-gemini-key",
            }
            with patch.dict(os.environ, env, clear=False):
                providers = detect_default_providers()
                assert providers["embedding"].name == "gemini"
        finally:
            os.unlink(temp_path)


class TestGeminiEmbeddingProvider:
    """Tests for the Gemini embedding provider."""

    @pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"),
        reason="Requires GEMINI_API_KEY or GOOGLE_API_KEY",
    )
    def test_gemini_embedding_basic(self):
        """Should generate embeddings using Gemini API."""
        from keep.providers.embeddings import GeminiEmbedding

        provider = GeminiEmbedding(model="text-embedding-004")

        embedding = provider.embed("Hello, world!")

        assert isinstance(embedding, list)
        assert len(embedding) == provider.dimension
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"),
        reason="Requires GEMINI_API_KEY or GOOGLE_API_KEY",
    )
    def test_gemini_embedding_batch(self):
        """Should generate batch embeddings using Gemini API."""
        from keep.providers.embeddings import GeminiEmbedding

        provider = GeminiEmbedding(model="text-embedding-004")

        texts = ["Hello", "World", "Test"]
        embeddings = provider.embed_batch(texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(len(e) == provider.dimension for e in embeddings)

    @pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"),
        reason="Requires GEMINI_API_KEY or GOOGLE_API_KEY",
    )
    def test_gemini_embedding_dimension(self):
        """Should report correct embedding dimension."""
        from keep.providers.embeddings import GeminiEmbedding

        provider = GeminiEmbedding(model="text-embedding-004")

        assert provider.dimension == 768

    def test_gemini_requires_api_key(self):
        """Should raise error when no API key available."""
        from keep.providers.embeddings import GeminiEmbedding

        # Need to clear the keys to test the error
        env_clear = {k: "" for k in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY"]}
        with patch.dict(os.environ, env_clear, clear=False):
            with pytest.raises(ValueError, match="Gemini API key required"):
                GeminiEmbedding()
