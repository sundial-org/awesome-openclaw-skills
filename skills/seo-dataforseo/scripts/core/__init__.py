"""Core module with client and storage utilities."""
from .client import get_client
from .storage import save_result, load_result, list_results

__all__ = ["get_client", "save_result", "load_result", "list_results"]
