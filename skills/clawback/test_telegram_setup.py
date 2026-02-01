#!/usr/bin/env python3
"""
Test Telegram setup for congressional trading system
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_loader import load_config
from telegram_notifier import TelegramNotifier

def test_telegram():
    """Test Telegram notification setup"""

    # Load config with secrets
    config = load_config('config/config.json')
    
    # Initialize notifier with notifications config
    notifier = TelegramNotifier(config.get('notifications', {}))
    
    if not notifier.enabled:
        print("❌ Telegram is disabled in config")
        print("Please enable it in config/config.json and add your bot token and chat ID")
        return False
    
    print("Testing Telegram notifications...")
    
    # Test 1: Send test message with broker info
    print("1. Sending test message...")
    # Try to get broker name from config
    broker_name = config.get('broker', {}).get('adapter', 'Unknown').upper()
    if notifier.send_test_message(broker_name=broker_name, is_authenticated=False):
        print("   ✅ Test message sent successfully!")
    else:
        print("   ❌ Failed to send test message")
        return False
    
    # Test 2: Send trade alert
    print("2. Testing trade alert...")
    trade_details = {
        'symbol': 'AAPL',
        'quantity': 10,
        'price': 150.50,
        'total': 1505.00,
        'reason': 'Congressional trade: Nancy Pelosi'
    }
    if notifier.send_trade_alert('BUY', trade_details):
        print("   ✅ Trade alert sent successfully!")
    else:
        print("   ❌ Failed to send trade alert")
    
    # Test 3: Send congressional alert
    print("3. Testing congressional alert...")
    congress_trade = {
        'politician': 'Nancy Pelosi',
        'ticker': 'MSFT',
        'transaction_type': 'BUY',
        'amount': 500000,
        'transaction_date': '2026-01-31'
    }
    if notifier.send_congressional_alert(congress_trade):
        print("   ✅ Congressional alert sent successfully!")
    else:
        print("   ❌ Failed to send congressional alert")
    
    # Test 4: Send error alert
    print("4. Testing error alert...")
    if notifier.send_error_alert('Connection Error', 'Failed to connect to broker API', 'During authentication'):
        print("   ✅ Error alert sent successfully!")
    else:
        print("   ❌ Failed to send error alert")
    
    print("\n" + "="*50)
    print("✅ Telegram setup test completed!")
    print("Check your Telegram app for all test messages.")
    print("If you didn't receive them, check your bot token and chat ID.")
    
    return True

if __name__ == "__main__":
    success = test_telegram()
    sys.exit(0 if success else 1)