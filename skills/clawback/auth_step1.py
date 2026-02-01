#!/usr/bin/env python3
"""Step 1: Get request token and save state"""
import json
import sys
sys.path.append('src')
from config_loader import load_config
from broker_adapter import get_broker_adapter

config = load_config('config/config.json')

broker = get_broker_adapter(config)
auth_url = broker.get_auth_url()

if auth_url:
    # Save token state
    state = {
        'request_token': broker.request_token,
        'request_secret': broker.request_secret
    }
    with open('.auth_state.json', 'w') as f:
        json.dump(state, f)

    print(f"AUTH_URL: {auth_url}")
else:
    print("Failed to get request token")
    sys.exit(1)
