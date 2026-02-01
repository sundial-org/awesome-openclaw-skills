"""DataForSEO API client initialization."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataforseo_client import configuration as dfs_config
from dataforseo_client import api_client as dfs_api_provider
from dataforseo_client.api.serp_api import SerpApi
from dataforseo_client.api.keywords_data_api import KeywordsDataApi
from dataforseo_client.api.dataforseo_labs_api import DataforseoLabsApi

from config.settings import settings


class DataForSEOClient:
    """Singleton client manager for DataForSEO APIs."""

    _instance = None
    _api_client = None
    _configuration = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the API client with credentials."""
        settings.validate()
        self._configuration = dfs_config.Configuration(
            username=settings.DATAFORSEO_LOGIN,
            password=settings.DATAFORSEO_PASSWORD
        )
        self._api_client = dfs_api_provider.ApiClient(self._configuration)

    @property
    def serp(self) -> SerpApi:
        """Get SERP API instance."""
        return SerpApi(self._api_client)

    @property
    def keywords_data(self) -> KeywordsDataApi:
        """Get Keywords Data API instance."""
        return KeywordsDataApi(self._api_client)

    @property
    def labs(self) -> DataforseoLabsApi:
        """Get DataForSEO Labs API instance."""
        return DataforseoLabsApi(self._api_client)

    @property
    def api_client(self):
        """Get raw API client for custom requests."""
        return self._api_client

    def close(self):
        """Close the API client connection."""
        if self._api_client:
            self._api_client.close()


def get_client() -> DataForSEOClient:
    """Get or create the DataForSEO client instance."""
    return DataForSEOClient()
