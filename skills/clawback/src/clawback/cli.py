#!/usr/bin/env python3
"""
ClawBack CLI - Command line interface for the Congressional Trade Mirror Bot
"""

import argparse
import json
import os
import sys
from pathlib import Path


def get_config_dir():
    """Get the configuration directory, creating if needed."""
    # Check for local config first (development mode)
    local_config = Path.cwd() / "config"
    if local_config.exists():
        return local_config

    # Use user's home directory for installed mode
    config_dir = Path.home() / ".clawback"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_data_dir():
    """Get the data directory, creating if needed."""
    local_data = Path.cwd() / "data"
    if local_data.exists():
        return local_data

    data_dir = Path.home() / ".clawback" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def is_first_run():
    """Check if this is the first run (no secrets configured)."""
    config_dir = get_config_dir()
    secrets_path = config_dir / "secrets.json"

    if not secrets_path.exists():
        return True

    try:
        with open(secrets_path) as f:
            secrets = json.load(f)
        # Check if any real values are set
        return not secrets.get("BROKER_API_KEY") or secrets.get("BROKER_API_KEY") == ""
    except:
        return True


def create_default_config():
    """Create default configuration files if they don't exist."""
    config_dir = get_config_dir()
    config_path = config_dir / "config.json"

    if not config_path.exists():
        default_config = {
            "broker": {
                "adapter": "etrade",
                "environment": "sandbox",
                "credentials": {
                    "apiKey": "${BROKER_API_KEY}",
                    "apiSecret": "${BROKER_API_SECRET}"
                }
            },
            "trading": {
                "accountId": "${BROKER_ACCOUNT_ID}",
                "initialCapital": 50000,
                "tradeScalePercentage": 0.05,
                "maxPositionPercentage": 0.05,
                "maxPositions": 20,
                "dailyLossLimit": 0.03,
                "portfolioStopLoss": 0.15,
                "positionStopLoss": 0.08,
                "tradeDelayDays": 3,
                "holdingPeriodDays": 30,
                "marketHoursOnly": True,
                "marketTimezone": "America/New_York",
                "marketOpen": "09:30",
                "marketClose": "16:00"
            },
            "schedule": {
                "disclosureCheckTimes": ["10:00", "14:00", "18:00"],
                "timezone": "America/New_York"
            },
            "strategy": {
                "entryDelayDays": 3,
                "holdingPeriodDays": 30,
                "purchasesOnly": True,
                "minimumTradeSize": 50000,
                "maxSectorExposure": 0.25,
                "prioritizeLeadership": True,
                "multiMemberBonus": True
            },
            "congress": {
                "dataSource": "official",
                "pollIntervalHours": 24,
                "minimumTradeSize": 50000,
                "tradeTypes": ["purchase"],
                "includeSenate": True,
                "targetPoliticians": [
                    {"name": "Nancy Pelosi", "chamber": "house", "priority": 1},
                    {"name": "Dan Crenshaw", "chamber": "house", "priority": 2},
                    {"name": "Tommy Tuberville", "chamber": "senate", "priority": 2},
                    {"name": "Marjorie Taylor Greene", "chamber": "house", "priority": 3}
                ]
            },
            "riskManagement": {
                "maxDrawdown": 0.15,
                "dailyLossLimit": 0.03,
                "positionStopLoss": 0.08,
                "trailingStopActivation": 0.10,
                "trailingStopPercent": 0.05,
                "consecutiveLossLimit": 3
            },
            "logging": {
                "level": "info",
                "file": "logs/trading.log",
                "maxSize": "10MB",
                "maxFiles": 10
            },
            "database": {
                "path": "data/trading.db"
            },
            "notifications": {
                "telegram": {
                    "enabled": False,
                    "botToken": "${TELEGRAM_BOT_TOKEN}",
                    "chatId": "${TELEGRAM_CHAT_ID}"
                }
            }
        }

        config_dir.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"Created default config at {config_path}")


def run_setup():
    """Run interactive setup wizard."""
    print()
    print("=" * 60)
    print("  ClawBack - Congressional Trade Mirror Bot")
    print("  First-Time Setup")
    print("=" * 60)
    print()

    config_dir = get_config_dir()
    secrets = {}

    # Step 1: Environment selection
    print("STEP 1: Select Environment")
    print("-" * 40)
    print("  [1] Sandbox (for testing - no real trades)")
    print("  [2] Production (real trading with real money)")
    print()

    while True:
        choice = input("  Select environment (1 or 2): ").strip()
        if choice in ["1", "2"]:
            break
        print("  Invalid choice. Please enter 1 or 2.")

    environment = "sandbox" if choice == "1" else "production"
    print(f"  ✓ Selected: {environment}")
    print()

    # Step 2: Broker credentials
    print("STEP 2: E*TRADE API Credentials")
    print("-" * 40)
    if environment == "sandbox":
        print("  Get sandbox keys from: https://developer.etrade.com/")
    else:
        print("  Get production keys from: https://us.etrade.com/etx/ris/apikey")
    print()

    secrets['BROKER_API_KEY'] = input("  API Key: ").strip()
    secrets['BROKER_API_SECRET'] = input("  API Secret: ").strip()
    print()

    # Save secrets temporarily for auth
    secrets['BROKER_ACCOUNT_ID'] = ''
    secrets['TELEGRAM_BOT_TOKEN'] = ''
    secrets['TELEGRAM_CHAT_ID'] = ''

    secrets_path = config_dir / "secrets.json"
    config_dir.mkdir(parents=True, exist_ok=True)
    with open(secrets_path, 'w') as f:
        json.dump(secrets, f, indent=2)

    # Create/update config with environment
    create_default_config()
    config_path = config_dir / "config.json"
    with open(config_path) as f:
        config = json.load(f)
    config['broker']['environment'] = environment
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    # Step 3: Authenticate
    print("STEP 3: Broker Authentication")
    print("-" * 40)
    print("  Connecting to E*TRADE...")

    try:
        from clawback.config_loader import load_config
        from clawback.broker_adapter import get_broker_adapter

        config = load_config(str(config_path))
        broker = get_broker_adapter(config)

        auth_url = broker.get_auth_url()
        if not auth_url:
            print("  ✗ Failed to connect. Please check your API credentials.")
            return False

        print()
        print("  Please visit this URL to authorize ClawBack:")
        print()
        print(f"  {auth_url}")
        print()
        verifier = input("  Enter the verification code: ").strip()

        if not broker.authenticate(verifier):
            print("  ✗ Authentication failed. Please try again.")
            return False

        print("  ✓ Authentication successful!")
        print()

        # Step 4: Account selection
        print("STEP 4: Select Trading Account")
        print("-" * 40)

        accounts = broker.get_accounts()
        if not accounts:
            print("  ✗ No accounts found.")
            return False

        print("  Available accounts:")
        for i, acc in enumerate(accounts, 1):
            acc_type = acc.get('accountType', 'Unknown')
            acc_desc = acc.get('accountDesc', acc.get('accountName', 'N/A'))
            print(f"    [{i}] {acc['accountId']} - {acc_desc} ({acc_type})")
        print()

        while True:
            choice = input(f"  Select account (1-{len(accounts)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(accounts):
                    break
            except ValueError:
                pass
            print("  Invalid choice. Please try again.")

        selected_account = accounts[idx]['accountId']
        secrets['BROKER_ACCOUNT_ID'] = selected_account
        print(f"  ✓ Selected account: {selected_account}")
        print()

        # Save access tokens
        tokens_path = config_dir / ".access_tokens.json"
        tokens = {
            'access_token': broker.access_token,
            'access_secret': broker.access_secret
        }
        with open(tokens_path, 'w') as f:
            json.dump(tokens, f)

    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        print("  Please ensure all dependencies are installed.")
        return False
    except Exception as e:
        print(f"  ✗ Error during authentication: {e}")
        secrets['BROKER_ACCOUNT_ID'] = input("  Enter Account ID manually: ").strip()

    # Step 5: Telegram (optional)
    print("STEP 5: Telegram Notifications (Optional)")
    print("-" * 40)
    print("  Telegram sends you alerts for trades and errors.")
    print()

    telegram = input("  Enable Telegram notifications? (y/n): ").strip().lower()
    if telegram == 'y':
        print()
        print("  To set up Telegram:")
        print("    1. Message @BotFather on Telegram to create a bot")
        print("    2. Message @userinfobot to get your Chat ID")
        print()
        secrets['TELEGRAM_BOT_TOKEN'] = input("  Bot Token: ").strip()
        secrets['TELEGRAM_CHAT_ID'] = input("  Chat ID: ").strip()

        # Update config to enable Telegram
        with open(config_path) as f:
            config = json.load(f)
        config['notifications']['telegram']['enabled'] = True
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    # Save final secrets
    with open(secrets_path, 'w') as f:
        json.dump(secrets, f, indent=2)

    # Done!
    print()
    print("=" * 60)
    print("  ✓ Setup Complete!")
    print("=" * 60)
    print()
    print(f"  Environment:  {environment}")
    print(f"  Account ID:   {secrets.get('BROKER_ACCOUNT_ID', 'Not set')}")
    print(f"  Telegram:     {'Enabled' if secrets.get('TELEGRAM_BOT_TOKEN') else 'Disabled'}")
    print(f"  Config:       {config_path}")
    print()
    print("  Run 'clawback run' to start the trading bot!")
    print("  Run 'clawback status' to check system status.")
    print()

    return True


def run_interactive():
    """Run interactive trading mode."""
    config_dir = get_config_dir()
    config_path = config_dir / "config.json"

    if not config_path.exists():
        print("No configuration found. Running setup first...")
        if not run_setup():
            return

    try:
        # Change to config directory for relative paths
        original_dir = os.getcwd()
        os.chdir(config_dir.parent if config_dir.name == "config" else config_dir.parent)

        from clawback.main import TradingBot
        from clawback.config_loader import load_config

        config = load_config(str(config_path))
        bot = TradingBot(config)
        bot.run_interactive()

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        os.chdir(original_dir)


def run_daemon():
    """Run as background daemon."""
    config_dir = get_config_dir()
    config_path = config_dir / "config.json"

    if not config_path.exists():
        print("No configuration found. Please run 'clawback setup' first.")
        return

    try:
        from clawback.main import TradingBot
        from clawback.config_loader import load_config

        config = load_config(str(config_path))
        bot = TradingBot(config)
        bot.run()

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        raise


def show_status():
    """Show current system status."""
    config_dir = get_config_dir()
    config_path = config_dir / "config.json"
    secrets_path = config_dir / "secrets.json"
    tokens_path = config_dir / ".access_tokens.json"

    print()
    print("=" * 50)
    print("  ClawBack System Status")
    print("=" * 50)
    print()

    # Config status
    if config_path.exists():
        print(f"  ✓ Config: {config_path}")
        try:
            with open(config_path) as f:
                config = json.load(f)
            env = config.get('broker', {}).get('environment', 'unknown')
            print(f"    Environment: {env}")
        except:
            print("    (unable to read)")
    else:
        print(f"  ✗ Config: Not found")

    # Secrets status
    if secrets_path.exists():
        print(f"  ✓ Secrets: Configured")
        try:
            with open(secrets_path) as f:
                secrets = json.load(f)
            has_broker = bool(secrets.get('BROKER_API_KEY'))
            has_telegram = bool(secrets.get('TELEGRAM_BOT_TOKEN'))
            print(f"    Broker API: {'✓' if has_broker else '✗'}")
            print(f"    Telegram: {'✓' if has_telegram else '✗'}")
            if secrets.get('BROKER_ACCOUNT_ID'):
                print(f"    Account: {secrets['BROKER_ACCOUNT_ID']}")
        except:
            print("    (unable to read)")
    else:
        print(f"  ✗ Secrets: Not configured")

    # Tokens status
    if tokens_path.exists():
        print(f"  ✓ Auth Tokens: Saved")
    else:
        print(f"  ✗ Auth Tokens: Not authenticated")

    print()

    # Test broker connection if configured
    if config_path.exists() and secrets_path.exists() and tokens_path.exists():
        print("  Testing broker connection...")
        try:
            from clawback.config_loader import load_config
            from clawback.broker_adapter import get_broker_adapter

            config = load_config(str(config_path))
            broker = get_broker_adapter(config)

            with open(tokens_path) as f:
                tokens = json.load(f)
            broker.access_token = tokens.get('access_token')
            broker.access_secret = tokens.get('access_secret')
            broker._authenticated = True

            balance = broker.get_account_balance()
            if balance:
                print(f"  ✓ Broker: Connected")
                print(f"    Balance: ${balance.get('total_value', 0):,.2f}")
            else:
                print(f"  ⚠ Broker: Connected but no balance (may need re-auth)")
        except Exception as e:
            print(f"  ✗ Broker: Error - {e}")

    print()


def test_telegram():
    """Test Telegram notifications."""
    config_dir = get_config_dir()
    config_path = config_dir / "config.json"

    if not config_path.exists():
        print("No configuration found. Please run 'clawback setup' first.")
        return

    try:
        from clawback.config_loader import load_config
        from clawback.telegram_notifier import TelegramNotifier

        config = load_config(str(config_path))
        # TelegramNotifier expects the notifications section
        notifier = TelegramNotifier(config.get('notifications', {}))

        print("Sending test message to Telegram...")
        if notifier.send_test_message():
            print("✓ Test message sent! Check your Telegram.")
        else:
            print("✗ Failed to send. Check your bot token and chat ID.")

    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='clawback',
        description='ClawBack - Congressional Trade Mirror Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  setup      Run interactive setup wizard
  run        Start the trading bot (interactive mode)
  daemon     Run as background service
  status     Show system status
  test       Test Telegram notifications

Examples:
  clawback setup     # First-time setup
  clawback run       # Start trading bot
  clawback status    # Check system status
"""
    )

    parser.add_argument(
        'command',
        nargs='?',
        default=None,
        choices=['setup', 'run', 'daemon', 'status', 'test'],
        help='Command to run'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Auto-run setup on first run
    if args.command is None:
        if is_first_run():
            print("Welcome to ClawBack! Let's get you set up.")
            run_setup()
        else:
            parser.print_help()
        return

    # Execute command
    if args.command == 'setup':
        run_setup()
    elif args.command == 'run':
        if is_first_run():
            print("No configuration found. Running setup first...")
            if run_setup():
                run_interactive()
        else:
            run_interactive()
    elif args.command == 'daemon':
        run_daemon()
    elif args.command == 'status':
        show_status()
    elif args.command == 'test':
        test_telegram()


if __name__ == '__main__':
    main()
