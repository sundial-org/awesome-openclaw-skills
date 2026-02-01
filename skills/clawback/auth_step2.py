#!/usr/bin/env python3
"""Step 2: Complete auth with verification code"""
import json
import sys
sys.path.append('src')
from config_loader import load_config
from broker_adapter import get_broker_adapter

if len(sys.argv) < 2:
    print("Usage: python3 auth_step2.py <verification_code>")
    sys.exit(1)

verifier = sys.argv[1]

# Load config with secrets
config = load_config('config/config.json')

# Load saved state
with open('.auth_state.json', 'r') as f:
    state = json.load(f)

broker = get_broker_adapter(config)
broker.request_token = state['request_token']
broker.request_secret = state['request_secret']

success = broker.authenticate(verifier)

if success:
    print("Authentication successful!")

    # Save access tokens for future use
    tokens = {
        'access_token': broker.access_token,
        'access_secret': broker.access_secret
    }
    with open('.access_tokens.json', 'w') as f:
        json.dump(tokens, f)

    # Get and display accounts
    accounts = broker.get_accounts()
    print(f"\nFound {len(accounts)} account(s):")
    for acc in accounts:
        print(f"  - {acc.get('accountId')}: {acc.get('accountDesc', 'N/A')}")

    # Get balance
    if accounts:
        balance = broker.get_account_balance()
        if balance:
            print(f"\nAccount Balance:")
            print(f"  Cash available: ${balance['cash_available']:,.2f}")
            print(f"  Total value: ${balance['total_value']:,.2f}")
else:
    print("Authentication failed")
    sys.exit(1)
