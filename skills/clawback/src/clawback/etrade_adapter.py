"""
ClawBack - E*TRADE Broker Adapter
Implementation of BrokerAdapter for E*TRADE API
"""
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import quote, unquote
import requests
from requests_oauthlib import OAuth1

from .broker_adapter import BrokerAdapter

logger = logging.getLogger(__name__)


class ETradeAdapter(BrokerAdapter):
    """
    E*TRADE API adapter implementing the BrokerAdapter interface.

    All E*TRADE-specific URLs and configuration are contained within this class.
    The config only needs to provide credentials.
    """

    BROKER_NAME = "E*TRADE"

    # E*TRADE API URLs - configurable for sandbox vs production
    URLS = {
        "sandbox": {
            "base": "https://apisb.etrade.com",
            "request_token": "https://apisb.etrade.com/oauth/request_token",
            "access_token": "https://apisb.etrade.com/oauth/access_token",
            "authorize": "https://us.etrade.com/e/t/etws/authorize"
        },
        "production": {
            "base": "https://api.etrade.com",
            "request_token": "https://api.etrade.com/oauth/request_token",
            "access_token": "https://api.etrade.com/oauth/access_token",
            "authorize": "https://us.etrade.com/e/t/etws/authorize"
        }
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize E*TRADE adapter.

        Args:
            config: Configuration dictionary with:
                - broker.credentials.apiKey: E*TRADE consumer key
                - broker.credentials.apiSecret: E*TRADE consumer secret
                - trading.accountId: E*TRADE account ID
        """
        super().__init__(config)

        broker_config = config.get('broker', {})
        credentials = broker_config.get('credentials', {})

        # Get environment (sandbox or production)
        self.environment = broker_config.get('environment', 'production').lower()
        if self.environment not in ['sandbox', 'production']:
            self.environment = 'production'

        # Set URLs based on environment
        env_urls = self.URLS[self.environment]
        self.BASE_URL = env_urls['base']
        self.OAUTH_URLS = {
            "request_token": env_urls['request_token'],
            "access_token": env_urls['access_token'],
            "authorize": env_urls['authorize']
        }

        # Get credentials
        self.api_key = credentials.get('apiKey', '')
        self.api_secret = credentials.get('apiSecret', '')

        # OAuth tokens (set during authentication)
        self.request_token = None
        self.request_secret = None
        self.access_token = None
        self.access_secret = None

        # Account information
        self.account_id = config.get('trading', {}).get('accountId', '')
        self.account_id_key = None
        self.accounts_map = {}  # accountId -> accountIdKey mapping

        logger.info(f"Initialized E*TRADE adapter ({self.environment} environment)")

    def _get_oauth(self) -> OAuth1:
        """Get OAuth1 session for API calls."""
        if not self.access_token or not self.access_secret:
            raise ValueError("Not authenticated. Call authenticate() first.")

        return OAuth1(
            self.api_key,
            client_secret=self.api_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_secret,
            signature_method='HMAC-SHA1'
        )

    def get_auth_url(self) -> Optional[str]:
        """Get the authorization URL for OAuth flow."""
        try:
            oauth = OAuth1(self.api_key, client_secret=self.api_secret, callback_uri='oob')
            response = requests.post(self.OAUTH_URLS['request_token'], auth=oauth)

            if response.status_code == 200:
                credentials = dict(pair.split('=') for pair in response.text.split('&'))
                self.request_token = unquote(credentials.get('oauth_token', ''))
                self.request_secret = unquote(credentials.get('oauth_token_secret', ''))
                logger.info(f"Got request token: {self.request_token[:20]}...")

                # Generate authorization URL
                auth_url = f"{self.OAUTH_URLS['authorize']}?key={self.api_key}&token={quote(self.request_token, safe='')}"
                return auth_url
            else:
                logger.error(f"Failed to get request token: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error getting request token: {e}")
            return None

    def authenticate(self, verifier_code: str) -> bool:
        """Complete authentication using the verifier code from OAuth flow."""
        try:
            oauth = OAuth1(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.request_token,
                resource_owner_secret=self.request_secret,
                verifier=verifier_code
            )

            response = requests.post(self.OAUTH_URLS['access_token'], auth=oauth)

            if response.status_code == 200:
                credentials = dict(pair.split('=') for pair in response.text.split('&'))
                self.access_token = unquote(credentials.get('oauth_token', ''))
                self.access_secret = unquote(credentials.get('oauth_token_secret', ''))
                self._authenticated = True
                logger.info("Successfully authenticated with E*TRADE")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return False

    def renew_access_token(self) -> bool:
        """
        Renew the access token to extend its validity.

        E*TRADE access tokens expire after 2 hours of inactivity.
        Calling this endpoint extends the token's validity.
        Tokens expire completely at midnight ET regardless of renewal.

        Returns:
            True if renewal successful, False otherwise
        """
        if not self.access_token or not self.access_secret:
            logger.warning("Cannot renew: no access token available")
            return False

        try:
            oauth = self._get_oauth()
            renew_url = f"{self.BASE_URL}/oauth/renew_access_token"

            response = requests.get(renew_url, auth=oauth)

            if response.status_code == 200:
                logger.info("Successfully renewed E*TRADE access token")
                return True
            else:
                logger.warning(f"Token renewal failed: {response.status_code} - {response.text}")
                self._notify_error("Token Renewal", f"HTTP {response.status_code}",
                                   {"response": response.text[:200]})
                return False

        except Exception as e:
            logger.error(f"Error renewing access token: {e}")
            self._notify_error("Token Renewal", str(e))
            return False

    def revoke_access_token(self) -> bool:
        """
        Revoke the current access token.

        Returns:
            True if revocation successful, False otherwise
        """
        if not self.access_token or not self.access_secret:
            return True  # Already revoked

        try:
            oauth = self._get_oauth()
            revoke_url = f"{self.BASE_URL}/oauth/revoke_access_token"

            response = requests.get(revoke_url, auth=oauth)

            if response.status_code == 200:
                logger.info("Successfully revoked E*TRADE access token")
                self.access_token = None
                self.access_secret = None
                self._authenticated = False
                return True
            else:
                logger.warning(f"Token revocation failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error revoking access token: {e}")
            return False

    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get list of accounts available for trading."""
        try:
            oauth = self._get_oauth()
            url = f"{self.BASE_URL}/v1/accounts/list.json"

            response = requests.get(url, auth=oauth)

            if response.status_code == 200:
                data = response.json()
                accounts = data.get('AccountListResponse', {}).get('Accounts', {}).get('Account', [])

                # Ensure accounts is a list
                if isinstance(accounts, dict):
                    accounts = [accounts]

                # Build accountId -> accountIdKey mapping
                result = []
                for acc in accounts:
                    account_id = acc.get('accountId', '')
                    account_id_key = acc.get('accountIdKey', '')
                    self.accounts_map[account_id] = account_id_key

                    result.append({
                        'accountId': account_id,
                        'accountIdKey': account_id_key,
                        'accountType': acc.get('accountType', ''),
                        'accountName': acc.get('accountName', ''),
                        'accountDesc': acc.get('accountDesc', ''),
                        'raw_data': acc
                    })

                # Set default account if not specified
                if not self.account_id and result:
                    self.account_id = result[0]['accountId']
                    logger.info(f"Using account ID: {self.account_id}")

                # Set the account_id_key for the configured account
                if self.account_id and self.account_id in self.accounts_map:
                    self.account_id_key = self.accounts_map[self.account_id]
                    logger.info(f"Account ID Key: {self.account_id_key}")

                return result
            else:
                error_msg = f"HTTP {response.status_code}"
                self._notify_error("Get Accounts", error_msg, {
                    "status_code": response.status_code,
                    "response": response.text[:200]
                })
                return []

        except Exception as e:
            self._notify_error("Get Accounts", str(e))
            return []

    def get_account_balance(self, account_id: Optional[str] = None) -> Optional[Dict[str, float]]:
        """Get account balance information."""
        try:
            account_id = account_id or self.account_id
            if not account_id:
                raise ValueError("No account ID specified")

            # Use accountIdKey for API calls
            account_key = self.accounts_map.get(account_id, self.account_id_key or account_id)

            oauth = self._get_oauth()
            url = f"{self.BASE_URL}/v1/accounts/{account_key}/balance.json?instType=BROKERAGE&realTimeNAV=true"

            response = requests.get(url, auth=oauth)

            if response.status_code == 200:
                data = response.json()
                balance_info = data.get('BalanceResponse', {}).get('Computed', {})

                cash_available = float(balance_info.get('cashAvailableForInvestment', 0))
                total_account_value = float(balance_info.get('RealTimeValues', {}).get('totalAccountValue', 0))

                # Fallback to non-realtime if realtime not available
                if total_account_value == 0:
                    total_account_value = float(balance_info.get('totalAccountValue', 0))

                logger.info(f"Account balance - Cash: ${cash_available:,.2f}, Total: ${total_account_value:,.2f}")
                return {
                    'cash_available': cash_available,
                    'total_value': total_account_value,
                    'raw_data': balance_info
                }
            else:
                error_msg = f"HTTP {response.status_code}"
                self._notify_error("Get Account Balance", error_msg, {
                    "status_code": response.status_code,
                    "account_id": account_id,
                    "response": response.text[:200]
                })
                return None

        except Exception as e:
            self._notify_error("Get Account Balance", str(e), {"account_id": account_id})
            return None

    def get_positions(self, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get current positions in account."""
        try:
            account_id = account_id or self.account_id
            if not account_id:
                raise ValueError("No account ID specified")

            account_key = self.accounts_map.get(account_id, self.account_id_key or account_id)

            oauth = self._get_oauth()
            url = f"{self.BASE_URL}/v1/accounts/{account_key}/portfolio.json"

            response = requests.get(url, auth=oauth)

            if response.status_code == 200:
                data = response.json()
                portfolio = data.get('PortfolioResponse', {}).get('AccountPortfolio', [])

                # Handle single portfolio as dict
                if isinstance(portfolio, dict):
                    portfolio = [portfolio]

                position_list = []
                for account_portfolio in portfolio:
                    positions = account_portfolio.get('Position', [])
                    if isinstance(positions, dict):
                        positions = [positions]

                    for pos in positions:
                        product = pos.get('Product', {})
                        position_list.append({
                            'symbol': product.get('symbol', ''),
                            'quantity': float(pos.get('quantity', 0)),
                            'cost_basis': float(pos.get('totalCost', 0)),
                            'market_value': float(pos.get('marketValue', 0)),
                            'current_price': float(pos.get('Quick', {}).get('lastTrade', 0)),
                            'gain_loss': float(pos.get('totalGain', 0)),
                            'gain_loss_pct': float(pos.get('totalGainPct', 0)),
                            'raw_data': pos
                        })

                logger.info(f"Found {len(position_list)} positions")
                return position_list
            elif response.status_code == 204:
                # No positions
                logger.info("No positions in account")
                return []
            else:
                error_msg = f"HTTP {response.status_code}"
                self._notify_error("Get Positions", error_msg, {
                    "status_code": response.status_code,
                    "account_id": account_id,
                    "response": response.text[:200]
                })
                return []

        except Exception as e:
            self._notify_error("Get Positions", str(e), {"account_id": account_id})
            return []

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current quote for a symbol."""
        try:
            oauth = self._get_oauth()
            url = f"{self.BASE_URL}/v1/market/quote/{symbol.upper()}.json"

            response = requests.get(url, auth=oauth)

            if response.status_code == 200:
                data = response.json()
                quote_data = data.get('QuoteResponse', {}).get('QuoteData', [])

                if isinstance(quote_data, list) and quote_data:
                    quote_data = quote_data[0]
                elif not quote_data:
                    logger.error(f"No quote data for {symbol}")
                    return None

                all_data = quote_data.get('All', {})

                quote = {
                    'symbol': symbol.upper(),
                    'last_price': float(all_data.get('lastTrade', 0)),
                    'bid': float(all_data.get('bid', 0)),
                    'ask': float(all_data.get('ask', 0)),
                    'volume': int(all_data.get('totalVolume', 0)),
                    'timestamp': quote_data.get('dateTimeUTC', ''),
                    'change': float(all_data.get('changeClose', 0)),
                    'change_pct': float(all_data.get('changeClosePercentage', 0)),
                    'raw_data': quote_data
                }

                logger.debug(f"Quote for {symbol}: ${quote['last_price']:.2f}")
                return quote
            else:
                error_msg = f"HTTP {response.status_code}"
                self._notify_error("Get Quote", error_msg, {
                    "symbol": symbol,
                    "status_code": response.status_code
                })
                return None

        except Exception as e:
            self._notify_error("Get Quote", str(e), {"symbol": symbol})
            return None

    def place_order(self, account_id: str, order_details: Dict[str, Any]) -> bool:
        """Place a trade order."""
        try:
            # Validate order first
            is_valid, error_msg = self.validate_order(order_details)
            if not is_valid:
                logger.error(f"Order validation failed: {error_msg}")
                return False

            # Use accountIdKey for API calls
            account_key = self.accounts_map.get(account_id, self.account_id_key or account_id)

            oauth = self._get_oauth()
            preview_url = f"{self.BASE_URL}/v1/accounts/{account_key}/orders/preview.json"

            # Build order request
            client_order_id = str(int(time.time() * 1000))
            order_request = {
                "PreviewOrderRequest": {
                    "orderType": "EQ",
                    "clientOrderId": client_order_id,
                    "Order": [
                        {
                            "allOrNone": False,
                            "priceType": order_details.get('price_type', 'MARKET'),
                            "orderTerm": "GOOD_FOR_DAY",
                            "marketSession": "REGULAR",
                            "Instrument": [
                                {
                                    "Product": {
                                        "securityType": "EQ",
                                        "symbol": order_details['symbol'].upper()
                                    },
                                    "orderAction": order_details['action'],
                                    "quantityType": "QUANTITY",
                                    "quantity": int(order_details['quantity'])
                                }
                            ]
                        }
                    ]
                }
            }

            # Add limit price if specified
            if order_details.get('price_type') == 'LIMIT' and 'limit_price' in order_details:
                order_request['PreviewOrderRequest']['Order'][0]['limitPrice'] = float(order_details['limit_price'])

            # Preview the order
            response = requests.post(preview_url, auth=oauth, json=order_request)

            if response.status_code == 200:
                data = response.json()
                preview_ids = data.get('PreviewOrderResponse', {}).get('PreviewIds', [])

                if preview_ids:
                    preview_id = preview_ids[0].get('previewId')

                    # Place the order
                    place_url = f"{self.BASE_URL}/v1/accounts/{account_key}/orders/place.json"
                    place_request = {
                        "PlaceOrderRequest": {
                            "orderType": "EQ",
                            "clientOrderId": client_order_id,
                            "PreviewIds": preview_ids,
                            "Order": order_request['PreviewOrderRequest']['Order']
                        }
                    }

                    place_response = requests.post(place_url, auth=oauth, json=place_request)

                    if place_response.status_code == 200:
                        order_response = place_response.json()
                        order_ids = order_response.get('PlaceOrderResponse', {}).get('OrderIds', [])
                        if order_ids:
                            order_id = order_ids[0].get('orderId')
                            logger.info(f"Order placed: {order_details['action']} {order_details['quantity']} {order_details['symbol']} (Order ID: {order_id})")
                        else:
                            logger.info(f"Order placed: {order_details['action']} {order_details['quantity']} {order_details['symbol']}")
                        return True
                    else:
                        error_msg = f"HTTP {place_response.status_code}"
                        self._notify_error("Place Order", error_msg, {
                            "symbol": order_details['symbol'],
                            "action": order_details['action'],
                            "quantity": order_details['quantity'],
                            "status_code": place_response.status_code,
                            "response": place_response.text[:200]
                        })
                        return False
                else:
                    self._notify_error("Place Order", "No preview ID in response", {
                        "symbol": order_details['symbol'],
                        "action": order_details['action']
                    })
                    return False
            else:
                error_msg = f"Order preview failed: HTTP {response.status_code}"
                self._notify_error("Place Order (Preview)", error_msg, {
                    "symbol": order_details['symbol'],
                    "action": order_details['action'],
                    "quantity": order_details['quantity'],
                    "response": response.text[:200]
                })
                return False

        except Exception as e:
            self._notify_error("Place Order", str(e), {
                "symbol": order_details.get('symbol'),
                "action": order_details.get('action')
            })
            return False

    def get_order_status(self, account_id: str, order_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an order."""
        try:
            account_key = self.accounts_map.get(account_id, self.account_id_key or account_id)

            oauth = self._get_oauth()
            url = f"{self.BASE_URL}/v1/accounts/{account_key}/orders/{order_id}.json"

            response = requests.get(url, auth=oauth)

            if response.status_code == 200:
                data = response.json()
                order = data.get('OrdersResponse', {}).get('Order', [])
                if isinstance(order, list) and order:
                    return order[0]
                return order
            else:
                logger.error(f"Failed to get order status: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return None

    def get_orders(self, account_id: Optional[str] = None, status: str = 'OPEN') -> List[Dict[str, Any]]:
        """
        Get orders for the account.

        Args:
            account_id: Optional account ID
            status: Order status filter ('OPEN', 'EXECUTED', 'CANCELLED', etc.)

        Returns:
            List of order dictionaries
        """
        try:
            account_id = account_id or self.account_id
            account_key = self.accounts_map.get(account_id, self.account_id_key or account_id)

            oauth = self._get_oauth()
            url = f"{self.BASE_URL}/v1/accounts/{account_key}/orders.json?status={status}"

            response = requests.get(url, auth=oauth)

            if response.status_code == 200:
                data = response.json()
                orders = data.get('OrdersResponse', {}).get('Order', [])
                if isinstance(orders, dict):
                    orders = [orders]
                return orders
            elif response.status_code == 204:
                return []
            else:
                logger.error(f"Failed to get orders: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []

    def cancel_order(self, account_id: str, order_id: str) -> bool:
        """
        Cancel an order.

        Args:
            account_id: Account ID
            order_id: Order ID to cancel

        Returns:
            True if cancelled successfully
        """
        try:
            account_key = self.accounts_map.get(account_id, self.account_id_key or account_id)

            oauth = self._get_oauth()
            url = f"{self.BASE_URL}/v1/accounts/{account_key}/orders/cancel.json"

            cancel_request = {
                "CancelOrderRequest": {
                    "orderId": order_id
                }
            }

            response = requests.put(url, auth=oauth, json=cancel_request)

            if response.status_code == 200:
                logger.info(f"Order {order_id} cancelled successfully")
                return True
            else:
                logger.error(f"Failed to cancel order: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
