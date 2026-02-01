"""
ClawBack - Broker Adapter Interface
Abstract base class defining the common interface for all broker adapters
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BrokerAdapter(ABC):
    """
    Abstract base class for broker adapters.

    All broker implementations must inherit from this class and implement
    all abstract methods to ensure consistent behavior across different brokers.
    """

    # Class-level metadata that each adapter should define
    BROKER_NAME: str = "Unknown"

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the broker adapter.

        Args:
            config: Configuration dictionary containing:
                - broker.credentials.apiKey: API key/consumer key
                - broker.credentials.apiSecret: API secret/consumer secret
                - trading.accountId: Account ID for trading
        """
        self.config = config
        self._authenticated = False
        self._error_callback = None  # Callback for error notifications

    def set_error_callback(self, callback):
        """
        Set a callback function for error notifications.

        Args:
            callback: Function that accepts (operation: str, error: str, details: dict)
        """
        self._error_callback = callback

    def _notify_error(self, operation: str, error: str, details: dict = None):
        """
        Notify about an error via the registered callback.

        Args:
            operation: Name of the operation that failed
            error: Error message
            details: Additional error details
        """
        logger.error(f"Broker error in {operation}: {error}")
        if self._error_callback:
            try:
                self._error_callback(operation, error, details or {})
            except Exception as e:
                logger.error(f"Error in error callback: {e}")

    @property
    def is_authenticated(self) -> bool:
        """Check if the adapter is authenticated with the broker."""
        return self._authenticated

    @abstractmethod
    def get_auth_url(self) -> Optional[str]:
        """
        Get the authorization URL for OAuth flow.

        Returns:
            Authorization URL string, or None if OAuth is not required/failed
        """
        pass

    @abstractmethod
    def authenticate(self, verifier_code: str) -> bool:
        """
        Complete authentication using the verifier code from OAuth flow.

        Args:
            verifier_code: The verification code from the OAuth callback

        Returns:
            True if authentication succeeded, False otherwise
        """
        pass

    def renew_access_token(self) -> bool:
        """
        Renew/refresh the access token to extend its validity.

        Not all brokers support token renewal. Default implementation
        returns False. Override in broker-specific adapters if supported.

        Returns:
            True if renewal successful, False otherwise
        """
        return False

    def revoke_access_token(self) -> bool:
        """
        Revoke the current access token (logout).

        Returns:
            True if revocation successful, False otherwise
        """
        return False

    def set_tokens(self, access_token: str, access_secret: str = None):
        """
        Set access tokens directly (e.g., loaded from database).

        Args:
            access_token: The OAuth access token
            access_secret: The OAuth access secret (for OAuth1)
        """
        self.access_token = access_token
        self.access_secret = access_secret
        self._authenticated = True

    def get_tokens(self) -> Dict[str, str]:
        """
        Get current access tokens.

        Returns:
            Dict with access_token and access_secret
        """
        return {
            'access_token': getattr(self, 'access_token', None),
            'access_secret': getattr(self, 'access_secret', None)
        }

    @abstractmethod
    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        Get list of accounts available for trading.

        Returns:
            List of account dictionaries with at least:
                - accountId: Unique account identifier
                - accountType: Type of account (e.g., 'BROKERAGE', 'IRA')
                - accountName: Display name (optional)
        """
        pass

    @abstractmethod
    def get_account_balance(self, account_id: Optional[str] = None) -> Optional[Dict[str, float]]:
        """
        Get account balance information.

        Args:
            account_id: Optional account ID (uses default if not provided)

        Returns:
            Dictionary with:
                - cash_available: Cash available for trading
                - total_value: Total account value
                - raw_data: Full balance response from broker
            Returns None on error
        """
        pass

    @abstractmethod
    def get_positions(self, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current positions in account.

        Args:
            account_id: Optional account ID (uses default if not provided)

        Returns:
            List of position dictionaries with:
                - symbol: Stock symbol
                - quantity: Number of shares
                - cost_basis: Total cost basis
                - market_value: Current market value
                - current_price: Current price per share
        """
        pass

    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current quote for a symbol.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Dictionary with:
                - symbol: Stock symbol
                - last_price: Last trade price
                - bid: Current bid price
                - ask: Current ask price
                - volume: Trading volume
                - timestamp: Quote timestamp
            Returns None on error
        """
        pass

    @abstractmethod
    def place_order(self, account_id: str, order_details: Dict[str, Any]) -> bool:
        """
        Place a trade order.

        Args:
            account_id: Account ID to place order in
            order_details: Dictionary with:
                - symbol: Stock symbol
                - quantity: Number of shares
                - action: 'BUY' or 'SELL'
                - price_type: 'MARKET' or 'LIMIT'
                - limit_price: Required for LIMIT orders

        Returns:
            True if order placed successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_order_status(self, account_id: str, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of an order.

        Args:
            account_id: Account ID the order was placed in
            order_id: Order ID to check

        Returns:
            Order status dictionary, or None on error
        """
        pass

    def validate_order(self, order_details: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate order details before placement.

        Args:
            order_details: Order details dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['symbol', 'quantity', 'action']

        for field in required_fields:
            if field not in order_details:
                return False, f"Missing required field: {field}"

        if order_details.get('quantity', 0) <= 0:
            return False, "Quantity must be greater than 0"

        if order_details.get('action') not in ['BUY', 'SELL']:
            return False, "Action must be 'BUY' or 'SELL'"

        if order_details.get('price_type') == 'LIMIT' and 'limit_price' not in order_details:
            return False, "Limit price required for LIMIT orders"

        return True, ""


def get_broker_adapter(config: Dict[str, Any]) -> BrokerAdapter:
    """
    Factory function to create the appropriate broker adapter.

    Args:
        config: Configuration dictionary with broker.adapter specifying which adapter to use

    Returns:
        Initialized broker adapter instance

    Raises:
        ValueError: If the specified adapter is not supported
    """
    adapter_name = config.get('broker', {}).get('adapter', 'etrade').lower()

    if adapter_name == 'etrade':
        from .etrade_adapter import ETradeAdapter
        return ETradeAdapter(config)
    # Add more adapters here as they are implemented:
    # elif adapter_name == 'schwab':
    #     from schwab_adapter import SchwabAdapter
    #     return SchwabAdapter(config)
    # elif adapter_name == 'fidelity':
    #     from fidelity_adapter import FidelityAdapter
    #     return FidelityAdapter(config)
    else:
        raise ValueError(f"Unsupported broker adapter: {adapter_name}. Supported adapters: etrade")
