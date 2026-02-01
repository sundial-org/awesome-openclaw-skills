"""Configuration settings for AI Trader."""

import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class UnifAIConfig(BaseModel):
    """UnifAI SDK configuration."""
    agent_api_key: str = Field(default_factory=lambda: os.getenv("UNIFAI_AGENT_API_KEY", ""))
    toolkit_api_key: str = Field(default_factory=lambda: os.getenv("UNIFAI_TOOLKIT_API_KEY", ""))


class LLMConfig(BaseModel):
    """LLM configuration."""
    google_api_key: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    openrouter_api_key: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    default_model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gemini/gemini-3-flash-preview"))


class MarketConfig(BaseModel):
    """Prediction market configuration."""
    polymarket_api_key: str = Field(default_factory=lambda: os.getenv("POLYMARKET_API_KEY", ""))
    manifold_api_key: str = Field(default_factory=lambda: os.getenv("MANIFOLD_API_KEY", ""))


class OnChainConfig(BaseModel):
    """On-chain analysis configuration."""
    alchemy_api_key: str = Field(default_factory=lambda: os.getenv("ALCHEMY_API_KEY", ""))


class Settings(BaseModel):
    """Application settings."""
    unifai: UnifAIConfig = Field(default_factory=UnifAIConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    market: MarketConfig = Field(default_factory=MarketConfig)
    onchain: OnChainConfig = Field(default_factory=OnChainConfig)


settings = Settings()
