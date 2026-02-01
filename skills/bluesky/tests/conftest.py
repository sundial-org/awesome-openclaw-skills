"""
Pytest fixtures for bsky tests.
"""
import pytest
import sys
import os

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


@pytest.fixture
def mock_config(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".config" / "bsky"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def mock_session():
    """Mock session data for testing."""
    return {
        "handle": "test.bsky.social",
        "did": "did:plc:testuser123",
        "accessJwt": "fake-access-token",
        "refreshJwt": "fake-refresh-token"
    }
