"""
Tests for the broker adapter module
"""
import pytest
from unittest.mock import MagicMock, patch

from broker_adapter import BrokerAdapter, get_broker_adapter


class TestBrokerAdapterBase:
    """Tests for the BrokerAdapter abstract base class"""

    def test_broker_adapter_is_abstract(self):
        """Test that BrokerAdapter cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BrokerAdapter({})

    def test_broker_adapter_requires_abstract_methods(self):
        """Test that subclasses must implement abstract methods"""

        class IncompleteBroker(BrokerAdapter):
            pass

        with pytest.raises(TypeError):
            IncompleteBroker({})

    def test_broker_adapter_validate_order(self, sample_config):
        """Test the validate_order method"""

        # Create a minimal concrete implementation for testing
        class TestBroker(BrokerAdapter):
            BROKER_NAME = "TestBroker"

            def get_auth_url(self):
                return None

            def authenticate(self, verifier_code):
                return True

            def get_accounts(self):
                return []

            def get_account_balance(self, account_id=None):
                return None

            def get_positions(self, account_id=None):
                return []

            def get_quote(self, symbol):
                return None

            def place_order(self, account_id, order_details):
                return False

            def get_order_status(self, account_id, order_id):
                return None

        broker = TestBroker(sample_config)

        # Valid order
        valid_order = {
            'symbol': 'AAPL',
            'quantity': 10,
            'action': 'BUY',
            'price_type': 'MARKET'
        }
        is_valid, error = broker.validate_order(valid_order)
        assert is_valid is True
        assert error == ""

        # Missing symbol
        invalid_order = {'quantity': 10, 'action': 'BUY'}
        is_valid, error = broker.validate_order(invalid_order)
        assert is_valid is False
        assert 'symbol' in error.lower()

        # Invalid quantity
        invalid_order = {'symbol': 'AAPL', 'quantity': 0, 'action': 'BUY'}
        is_valid, error = broker.validate_order(invalid_order)
        assert is_valid is False
        assert 'quantity' in error.lower()

        # Invalid action
        invalid_order = {'symbol': 'AAPL', 'quantity': 10, 'action': 'HOLD'}
        is_valid, error = broker.validate_order(invalid_order)
        assert is_valid is False
        assert 'action' in error.lower()

        # LIMIT order without price
        invalid_order = {
            'symbol': 'AAPL',
            'quantity': 10,
            'action': 'BUY',
            'price_type': 'LIMIT'
        }
        is_valid, error = broker.validate_order(invalid_order)
        assert is_valid is False
        assert 'limit' in error.lower()

        # Valid LIMIT order
        valid_limit = {
            'symbol': 'AAPL',
            'quantity': 10,
            'action': 'BUY',
            'price_type': 'LIMIT',
            'limit_price': 150.0
        }
        is_valid, error = broker.validate_order(valid_limit)
        assert is_valid is True

    def test_is_authenticated_property(self, sample_config):
        """Test is_authenticated property"""

        class TestBroker(BrokerAdapter):
            BROKER_NAME = "TestBroker"

            def get_auth_url(self):
                return None

            def authenticate(self, verifier_code):
                self._authenticated = True
                return True

            def get_accounts(self):
                return []

            def get_account_balance(self, account_id=None):
                return None

            def get_positions(self, account_id=None):
                return []

            def get_quote(self, symbol):
                return None

            def place_order(self, account_id, order_details):
                return False

            def get_order_status(self, account_id, order_id):
                return None

        broker = TestBroker(sample_config)

        # Initially not authenticated
        assert broker.is_authenticated is False

        # After authentication
        broker.authenticate("test-code")
        assert broker.is_authenticated is True


class TestGetBrokerAdapter:
    """Tests for the get_broker_adapter factory function"""

    def test_get_etrade_adapter(self, sample_config):
        """Test that etrade adapter is returned for 'etrade' config"""
        adapter = get_broker_adapter(sample_config)

        assert adapter is not None
        assert adapter.BROKER_NAME == "E*TRADE"

    def test_get_adapter_case_insensitive(self, sample_config):
        """Test that adapter name is case insensitive"""
        sample_config['broker']['adapter'] = 'ETRADE'
        adapter = get_broker_adapter(sample_config)
        assert adapter.BROKER_NAME == "E*TRADE"

        sample_config['broker']['adapter'] = 'Etrade'
        adapter = get_broker_adapter(sample_config)
        assert adapter.BROKER_NAME == "E*TRADE"

    def test_get_adapter_invalid_type(self, sample_config):
        """Test that invalid adapter type raises ValueError"""
        sample_config['broker']['adapter'] = 'invalid_broker'

        with pytest.raises(ValueError) as exc_info:
            get_broker_adapter(sample_config)

        assert 'invalid_broker' in str(exc_info.value).lower()
        assert 'unsupported' in str(exc_info.value).lower()

    def test_default_adapter_is_etrade(self):
        """Test that default adapter is etrade when not specified"""
        config = {'broker': {'credentials': {'apiKey': 'key', 'apiSecret': 'secret'}}}
        adapter = get_broker_adapter(config)
        assert adapter.BROKER_NAME == "E*TRADE"


class TestETradeAdapter:
    """Tests for the E*TRADE adapter implementation"""

    def test_etrade_adapter_initialization(self, sample_config):
        """Test E*TRADE adapter initializes correctly"""
        from etrade_adapter import ETradeAdapter

        adapter = ETradeAdapter(sample_config)

        assert adapter.BROKER_NAME == "E*TRADE"
        assert adapter.api_key == "test-api-key"
        assert adapter.api_secret == "test-api-secret"
        assert adapter.account_id == "test-account-123"

    def test_etrade_adapter_urls(self, sample_config):
        """Test E*TRADE adapter has correct URLs"""
        from etrade_adapter import ETradeAdapter

        adapter = ETradeAdapter(sample_config)

        assert 'api.etrade.com' in adapter.BASE_URL
        assert 'request_token' in adapter.OAUTH_URLS
        assert 'access_token' in adapter.OAUTH_URLS
        assert 'authorize' in adapter.OAUTH_URLS

    @patch('etrade_adapter.requests')
    def test_etrade_get_auth_url(self, mock_requests, sample_config):
        """Test getting authorization URL"""
        from etrade_adapter import ETradeAdapter

        # Mock successful request token response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'oauth_token=test_token&oauth_token_secret=test_secret'
        mock_requests.post.return_value = mock_response

        adapter = ETradeAdapter(sample_config)
        auth_url = adapter.get_auth_url()

        assert auth_url is not None
        assert 'authorize' in auth_url
        assert 'test_token' in auth_url

    @patch('etrade_adapter.requests')
    def test_etrade_authenticate(self, mock_requests, sample_config):
        """Test authentication flow"""
        from etrade_adapter import ETradeAdapter

        # Mock access token response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'oauth_token=access_token&oauth_token_secret=access_secret'
        mock_requests.post.return_value = mock_response

        adapter = ETradeAdapter(sample_config)
        adapter.request_token = 'request_token'
        adapter.request_secret = 'request_secret'

        result = adapter.authenticate('verifier_code')

        assert result is True
        assert adapter.is_authenticated is True
        assert adapter.access_token == 'access_token'

    @patch('etrade_adapter.requests')
    def test_etrade_get_accounts(self, mock_requests, sample_config):
        """Test getting accounts"""
        from etrade_adapter import ETradeAdapter

        # Mock accounts response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'AccountListResponse': {
                'Accounts': {
                    'Account': [
                        {
                            'accountId': '12345678',
                            'accountIdKey': 'key123',
                            'accountType': 'INDIVIDUAL',
                            'accountName': 'Test Account'
                        }
                    ]
                }
            }
        }
        mock_requests.get.return_value = mock_response

        adapter = ETradeAdapter(sample_config)
        adapter.access_token = 'access_token'
        adapter.access_secret = 'access_secret'
        adapter._authenticated = True

        accounts = adapter.get_accounts()

        assert len(accounts) == 1
        assert accounts[0]['accountId'] == '12345678'

    @patch('etrade_adapter.requests')
    def test_etrade_get_quote(self, mock_requests, sample_config):
        """Test getting a stock quote"""
        from etrade_adapter import ETradeAdapter

        # Mock quote response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'QuoteResponse': {
                'QuoteData': [{
                    'All': {
                        'lastTrade': 500.0,
                        'bid': 499.50,
                        'ask': 500.50,
                        'totalVolume': 1000000,
                        'changeClose': 5.0,
                        'changeClosePercentage': 1.0
                    },
                    'dateTimeUTC': '2026-01-31T15:00:00'
                }]
            }
        }
        mock_requests.get.return_value = mock_response

        adapter = ETradeAdapter(sample_config)
        adapter.access_token = 'access_token'
        adapter.access_secret = 'access_secret'
        adapter._authenticated = True

        quote = adapter.get_quote('NVDA')

        assert quote is not None
        assert quote['symbol'] == 'NVDA'
        assert quote['last_price'] == 500.0
        assert quote['bid'] == 499.50
        assert quote['ask'] == 500.50
