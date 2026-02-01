# Unit Tests

## Setup

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest

# Run with coverage
pytest --cov=scripts --cov-report=html

# Run specific test file
pytest tests/test_portfolio.py
```

## Test Structure

- `test_portfolio.py` - Portfolio CRUD operations
- `test_fetch_news.py` - RSS feed parsing with mocked responses
- `test_setup.py` - Setup wizard validation
- `fixtures/` - Sample RSS and portfolio data

## Coverage Target

60%+ coverage for core functions (portfolio, fetch_news, setup).

## Notes

- Tests use `tmp_path` for file isolation
- Network calls are mocked with `unittest.mock`
- `pytest-mock` provides `mocker` fixture for advanced mocking
