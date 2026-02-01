"""Configuration management for DataForSEO toolkit."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in current working directory
load_dotenv()


class Settings:
    """Application settings loaded from environment."""

    # Authentication
    DATAFORSEO_LOGIN: str = os.getenv("DATAFORSEO_LOGIN", "")
    DATAFORSEO_PASSWORD: str = os.getenv("DATAFORSEO_PASSWORD", "")

    # Default location/language settings
    DEFAULT_LOCATION_NAME: str = "United States"
    DEFAULT_LOCATION_CODE: int = 2840
    DEFAULT_LANGUAGE_NAME: str = "English"
    DEFAULT_LANGUAGE_CODE: str = "en"

    # Results storage (saves to current working directory)
    RESULTS_DIR: Path = Path.cwd() / "results"

    # API limits (for reference)
    MAX_KEYWORDS_SEARCH_VOLUME: int = 700
    MAX_KEYWORDS_OVERVIEW: int = 700
    MAX_KEYWORDS_DIFFICULTY: int = 1000
    MAX_KEYWORDS_IDEAS: int = 200
    MAX_TRENDS_KEYWORDS: int = 5

    @classmethod
    def validate(cls) -> bool:
        """Validate required settings are present."""
        if not cls.DATAFORSEO_LOGIN or not cls.DATAFORSEO_PASSWORD:
            raise ValueError(
                "DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD must be set in .env file. "
                "Get your credentials from https://app.dataforseo.com/api-access"
            )
        return True


settings = Settings()
