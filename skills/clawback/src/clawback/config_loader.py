"""
ClawBack - Configuration Loader
Reads configuration with support for environment variables and secrets management
"""
import json
import os
import re
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Environment variable pattern: ${VAR_NAME}
ENV_PATTERN = re.compile(r'\$\{([^}]+)\}')


def substitute_env_vars(value: Any) -> Any:
    """Recursively substitute environment variables in config values"""
    if isinstance(value, str):
        # Check for ${VAR} pattern
        match = ENV_PATTERN.fullmatch(value)
        if match:
            var_name = match.group(1)
            env_value = os.environ.get(var_name)
            if env_value:
                return env_value
            else:
                logger.warning(f"Environment variable {var_name} not set")
                return value
        # Also handle partial substitution
        def replace_var(m):
            var_name = m.group(1)
            return os.environ.get(var_name, m.group(0))
        return ENV_PATTERN.sub(replace_var, value)
    elif isinstance(value, dict):
        return {k: substitute_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [substitute_env_vars(item) for item in value]
    return value


def load_secrets(secrets_path: str = None) -> Dict[str, str]:
    """Load secrets from a JSON file"""
    if secrets_path is None:
        # Try common locations
        locations = [
            'config/secrets.json',
            '.secrets.json',
            os.path.expanduser('~/.clawback/secrets.json'),
            os.path.expanduser('~/.config/clawback/secrets.json')
        ]
        for loc in locations:
            if os.path.exists(loc):
                secrets_path = loc
                break

    if secrets_path and os.path.exists(secrets_path):
        try:
            with open(secrets_path) as f:
                secrets = json.load(f)
            logger.info(f"Loaded secrets from {secrets_path}")
            return secrets
        except Exception as e:
            logger.warning(f"Could not load secrets from {secrets_path}: {e}")

    return {}


def load_config(config_path: str = 'config/config.json') -> Dict[str, Any]:
    """
    Load configuration with environment variable substitution

    Priority order:
    1. Environment variables (highest)
    2. Secrets file (config/secrets.json or ~/.clawback/secrets.json)
    3. Config file values (lowest)
    """
    # Load base config
    if not os.path.exists(config_path):
        # Try template
        template_path = config_path.replace('.json', '.template.json')
        if os.path.exists(template_path):
            logger.warning(f"Config not found, using template: {template_path}")
            config_path = template_path
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path) as f:
        config = json.load(f)

    # Load secrets and set as environment variables (if not already set)
    secrets = load_secrets()
    for key, value in secrets.items():
        if key not in os.environ:
            os.environ[key] = str(value)

    # Substitute environment variables
    config = substitute_env_vars(config)

    # Remove comment fields
    def remove_comments(obj):
        if isinstance(obj, dict):
            return {k: remove_comments(v) for k, v in obj.items()
                    if not k.startswith('_')}
        elif isinstance(obj, list):
            return [remove_comments(item) for item in obj]
        return obj

    config = remove_comments(config)

    return config


def create_secrets_template():
    """Create a template secrets file"""
    template = {
        "_instructions": "Fill in your API keys and secrets. This file should NEVER be committed to git.",
        "BROKER_API_KEY": "your-broker-api-key",
        "BROKER_API_SECRET": "your-broker-api-secret",
        "BROKER_ACCOUNT_ID": "your-account-id",
        "TELEGRAM_BOT_TOKEN": "your-telegram-bot-token",
        "TELEGRAM_CHAT_ID": "your-telegram-chat-id"
    }
    return template


def setup_config_interactive():
    """Interactive setup for configuration with account selection"""
    print("\n" + "="*60)
    print("  ClawBack - Configuration Setup")
    print("="*60)

    secrets = {}

    # Step 1: Environment selection
    print("\n1. Select Environment")
    print("   [1] Sandbox (for testing)")
    print("   [2] Production (real trading)")
    env_choice = input("   Choice (1/2): ").strip()
    environment = "sandbox" if env_choice == "1" else "production"
    print(f"   Selected: {environment}")

    # Step 2: API Credentials
    print("\n2. Broker API Credentials")
    if environment == "sandbox":
        print("   Get sandbox keys from https://developer.etrade.com/")
    else:
        print("   Get production keys from https://us.etrade.com/etx/ris/apikey")

    secrets['BROKER_API_KEY'] = input("   API Key: ").strip()
    secrets['BROKER_API_SECRET'] = input("   API Secret: ").strip()

    # Step 3: Authenticate and list accounts
    print("\n3. Authenticating with E*TRADE...")

    # Save temp secrets for authentication
    secrets_path = 'config/secrets.json'
    os.makedirs('config', exist_ok=True)
    secrets['BROKER_ACCOUNT_ID'] = ''  # Placeholder
    secrets['TELEGRAM_BOT_TOKEN'] = ''
    secrets['TELEGRAM_CHAT_ID'] = ''
    with open(secrets_path, 'w') as f:
        json.dump(secrets, f, indent=2)

    # Update config with environment
    config_path = 'config/config.json'
    template_path = 'config/config.template.json'
    if not os.path.exists(config_path) and os.path.exists(template_path):
        import shutil
        shutil.copy(template_path, config_path)

    # Load and update config with environment
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        config['broker']['environment'] = environment
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    try:
        from .broker_adapter import get_broker_adapter

        # Reload config with secrets
        config = load_config(config_path)
        adapter = get_broker_adapter(config)

        # Get auth URL
        auth_url = adapter.get_auth_url()
        if not auth_url:
            print("   Failed to get authorization URL")
            return

        # Save auth state
        auth_state = {
            'request_token': adapter.request_token,
            'request_secret': adapter.request_secret
        }
        with open('.auth_state.json', 'w') as f:
            json.dump(auth_state, f)

        print(f"\n   Please visit this URL to authorize:")
        print(f"   {auth_url}")
        print()
        verifier = input("   Enter verification code: ").strip()

        # Authenticate
        if not adapter.authenticate(verifier):
            print("   Authentication failed")
            return

        print("   ✅ Authentication successful!")

        # Get accounts
        print("\n4. Select Trading Account")
        accounts = adapter.get_accounts()

        if not accounts:
            print("   No accounts found")
            return

        print("   Available accounts:")
        for i, acc in enumerate(accounts, 1):
            acc_type = acc.get('accountType', 'Unknown')
            acc_desc = acc.get('accountDesc', acc.get('accountName', 'N/A'))
            print(f"   [{i}] {acc['accountId']} - {acc_desc} ({acc_type})")

        while True:
            choice = input(f"\n   Select account (1-{len(accounts)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(accounts):
                    selected_account = accounts[idx]['accountId']
                    break
            except ValueError:
                pass
            print("   Invalid choice, try again")

        secrets['BROKER_ACCOUNT_ID'] = selected_account
        print(f"   ✅ Selected account: {selected_account}")

        # Save access tokens
        tokens = {
            'access_token': adapter.access_token,
            'access_secret': adapter.access_secret
        }
        with open('.access_tokens.json', 'w') as f:
            json.dump(tokens, f)
        print("   ✅ Access tokens saved")

    except ImportError:
        print("   Broker adapter not available, skipping authentication")
        secrets['BROKER_ACCOUNT_ID'] = input("   Account ID (manual entry): ").strip()
    except Exception as e:
        print(f"   Error during authentication: {e}")
        secrets['BROKER_ACCOUNT_ID'] = input("   Account ID (manual entry): ").strip()

    # Step 4: Telegram setup
    print("\n5. Telegram Notifications (Optional)")
    telegram = input("   Enable Telegram? (y/n): ").strip().lower()
    if telegram == 'y':
        print("   Create a bot with @BotFather and get your chat ID from @userinfobot")
        secrets['TELEGRAM_BOT_TOKEN'] = input("   Bot Token: ").strip()
        secrets['TELEGRAM_CHAT_ID'] = input("   Chat ID: ").strip()

    # Save final secrets
    with open(secrets_path, 'w') as f:
        json.dump(secrets, f, indent=2)

    print("\n" + "="*60)
    print("  ✅ Setup Complete!")
    print("="*60)
    print(f"  Environment: {environment}")
    print(f"  Account ID: {secrets['BROKER_ACCOUNT_ID']}")
    print(f"  Telegram: {'Enabled' if secrets.get('TELEGRAM_BOT_TOKEN') else 'Disabled'}")
    print()
    print("  Run 'python3 src/main.py interactive' to start trading!")
    print("="*60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup_config_interactive()
    else:
        # Test loading config
        try:
            config = load_config()
            print("Configuration loaded successfully!")
            broker = config.get('broker', {})
            print(f"  Broker adapter: {broker.get('adapter', 'not set')}")
            env = broker.get('environment', 'production')
            print(f"  Environment: {env}")
        except Exception as e:
            print(f"Error loading config: {e}")
