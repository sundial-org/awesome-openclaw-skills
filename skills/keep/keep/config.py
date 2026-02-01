"""
Configuration management for associative memory stores.

The configuration is stored as a TOML file in the store directory.
It specifies which providers to use and their parameters.
"""

import os
import platform
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# tomli_w for writing TOML (tomllib is read-only)
try:
    import tomli_w
except ImportError:
    tomli_w = None  # type: ignore


CONFIG_FILENAME = "keep.toml"
CONFIG_VERSION = 1


@dataclass
class ProviderConfig:
    """Configuration for a single provider."""
    name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class StoreConfig:
    """Complete store configuration."""
    path: Path
    version: int = CONFIG_VERSION
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Provider configurations
    embedding: ProviderConfig = field(default_factory=lambda: ProviderConfig("sentence-transformers"))
    summarization: ProviderConfig = field(default_factory=lambda: ProviderConfig("truncate"))
    document: ProviderConfig = field(default_factory=lambda: ProviderConfig("composite"))
    
    @property
    def config_path(self) -> Path:
        """Path to the TOML config file."""
        return self.path / CONFIG_FILENAME
    
    def exists(self) -> bool:
        """Check if config file exists."""
        return self.config_path.exists()


def read_openclaw_config() -> dict | None:
    """
    Read OpenClaw configuration if available.

    Checks:
    1. OPENCLAW_CONFIG environment variable
    2. ~/.openclaw/openclaw.json (default location)

    Returns None if not found or invalid.
    """
    import json

    # Try environment variable first
    config_path_str = os.environ.get("OPENCLAW_CONFIG")
    if config_path_str:
        config_file = Path(config_path_str)
    else:
        # Default location
        config_file = Path.home() / ".openclaw" / "openclaw.json"

    if not config_file.exists():
        return None

    try:
        with open(config_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def get_openclaw_memory_search_config(openclaw_config: dict | None) -> dict | None:
    """
    Extract memorySearch config from OpenClaw config.

    Returns the memorySearch settings or None if not configured.

    Example structure:
        {
            "provider": "openai" | "gemini" | "local" | "auto",
            "model": "text-embedding-3-small",
            "remote": {
                "apiKey": "sk-...",
                "baseUrl": "https://..."
            }
        }
    """
    if not openclaw_config:
        return None

    return (openclaw_config
            .get("agents", {})
            .get("defaults", {})
            .get("memorySearch", None))


def detect_default_providers() -> dict[str, ProviderConfig]:
    """
    Detect the best default providers for the current environment.

    Priority for embeddings:
    1. OpenClaw memorySearch config (if configured with provider + API key)
    2. sentence-transformers (local fallback)

    Priority for summarization:
    1. OpenClaw model config + Anthropic (if configured and ANTHROPIC_API_KEY available)
    2. MLX (Apple Silicon local-first)
    3. OpenAI (if API key available)
    4. Fallback: truncate

    Returns provider configs for: embedding, summarization, document
    """
    providers = {}

    # Check for Apple Silicon
    is_apple_silicon = (
        platform.system() == "Darwin" and
        platform.machine() == "arm64"
    )

    # Check for API keys
    has_anthropic_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_openai_key = bool(
        os.environ.get("KEEP_OPENAI_API_KEY") or
        os.environ.get("OPENAI_API_KEY")
    )
    has_gemini_key = bool(
        os.environ.get("GEMINI_API_KEY") or
        os.environ.get("GOOGLE_API_KEY")
    )

    # Check for OpenClaw config
    openclaw_config = read_openclaw_config()
    openclaw_model = None
    if openclaw_config:
        model_str = (openclaw_config.get("agents", {})
                     .get("defaults", {})
                     .get("model", {})
                     .get("primary", ""))
        if model_str:
            openclaw_model = model_str

    # Get OpenClaw memorySearch config for embeddings
    memory_search = get_openclaw_memory_search_config(openclaw_config)

    # Embedding: check OpenClaw memorySearch config first, then fall back to local
    embedding_provider = None
    if memory_search:
        ms_provider = memory_search.get("provider", "auto")
        ms_model = memory_search.get("model")
        ms_api_key = memory_search.get("remote", {}).get("apiKey")

        if ms_provider == "openai" or (ms_provider == "auto" and has_openai_key):
            # Use OpenAI embeddings if configured or auto with key available
            api_key = ms_api_key or os.environ.get("OPENAI_API_KEY")
            if api_key:
                params = {}
                if ms_model:
                    params["model"] = ms_model
                embedding_provider = ProviderConfig("openai", params)

        elif ms_provider == "gemini" or (ms_provider == "auto" and has_gemini_key and not has_openai_key):
            # Use Gemini embeddings if configured or auto with key available
            api_key = ms_api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if api_key:
                params = {}
                if ms_model:
                    params["model"] = ms_model
                embedding_provider = ProviderConfig("gemini", params)

    # Fall back to sentence-transformers (local, always works)
    if embedding_provider is None:
        embedding_provider = ProviderConfig("sentence-transformers")

    providers["embedding"] = embedding_provider
    
    # Summarization: priority order based on availability
    # 1. OpenClaw + Anthropic (if configured and key available)
    if openclaw_model and openclaw_model.startswith("anthropic/") and has_anthropic_key:
        # Extract model name from "anthropic/claude-sonnet-4-5" format
        model_name = openclaw_model.split("/", 1)[1] if "/" in openclaw_model else "claude-3-5-haiku-20241022"
        # Map OpenClaw model names to actual Anthropic model names
        model_mapping = {
            "claude-sonnet-4": "claude-sonnet-4-20250514",
            "claude-sonnet-4-5": "claude-sonnet-4-20250514",
            "claude-sonnet-3-5": "claude-3-5-sonnet-20241022",
            "claude-haiku-3-5": "claude-3-5-haiku-20241022",
        }
        actual_model = model_mapping.get(model_name, "claude-3-5-haiku-20241022")
        providers["summarization"] = ProviderConfig("anthropic", {"model": actual_model})
    # 2. MLX on Apple Silicon (local-first)
    elif is_apple_silicon:
        try:
            import mlx_lm  # noqa
            providers["summarization"] = ProviderConfig("mlx", {"model": "mlx-community/Llama-3.2-3B-Instruct-4bit"})
        except ImportError:
            if has_openai_key:
                providers["summarization"] = ProviderConfig("openai")
            else:
                providers["summarization"] = ProviderConfig("passthrough")
    # 3. OpenAI (if key available)
    elif has_openai_key:
        providers["summarization"] = ProviderConfig("openai")
    # 4. Fallback: truncate
    else:
        providers["summarization"] = ProviderConfig("truncate")
    
    # Document provider is always composite
    providers["document"] = ProviderConfig("composite")
    
    return providers


def create_default_config(store_path: Path) -> StoreConfig:
    """Create a new config with auto-detected defaults."""
    providers = detect_default_providers()
    
    return StoreConfig(
        path=store_path,
        embedding=providers["embedding"],
        summarization=providers["summarization"],
        document=providers["document"],
    )


def load_config(store_path: Path) -> StoreConfig:
    """
    Load configuration from a store directory.
    
    Raises:
        FileNotFoundError: If config doesn't exist
        ValueError: If config is invalid
    """
    config_path = store_path / CONFIG_FILENAME
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
    
    # Validate version
    version = data.get("store", {}).get("version", 1)
    if version > CONFIG_VERSION:
        raise ValueError(f"Config version {version} is newer than supported ({CONFIG_VERSION})")
    
    # Parse provider configs
    def parse_provider(section: dict) -> ProviderConfig:
        return ProviderConfig(
            name=section.get("name", ""),
            params={k: v for k, v in section.items() if k != "name"},
        )
    
    return StoreConfig(
        path=store_path,
        version=version,
        created=data.get("store", {}).get("created", ""),
        embedding=parse_provider(data.get("embedding", {"name": "sentence-transformers"})),
        summarization=parse_provider(data.get("summarization", {"name": "truncate"})),
        document=parse_provider(data.get("document", {"name": "composite"})),
    )


def save_config(config: StoreConfig) -> None:
    """
    Save configuration to the store directory.
    
    Creates the directory if it doesn't exist.
    """
    if tomli_w is None:
        raise RuntimeError("tomli_w is required to save config. Install with: pip install tomli-w")
    
    # Ensure directory exists
    config.path.mkdir(parents=True, exist_ok=True)
    
    # Build TOML structure
    def provider_to_dict(p: ProviderConfig) -> dict:
        d = {"name": p.name}
        d.update(p.params)
        return d
    
    data = {
        "store": {
            "version": config.version,
            "created": config.created,
        },
        "embedding": provider_to_dict(config.embedding),
        "summarization": provider_to_dict(config.summarization),
        "document": provider_to_dict(config.document),
    }
    
    with open(config.config_path, "wb") as f:
        tomli_w.dump(data, f)


def load_or_create_config(store_path: Path) -> StoreConfig:
    """
    Load existing config or create a new one with defaults.
    
    This is the main entry point for config management.
    """
    config_path = store_path / CONFIG_FILENAME
    
    if config_path.exists():
        return load_config(store_path)
    else:
        config = create_default_config(store_path)
        save_config(config)
        return config
