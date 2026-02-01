#!/usr/bin/env python3
"""
Test script for Congressional Trading System
Verifies all components are working correctly
"""

import json
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    try:
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        required_sections = ['etrade', 'trading', 'strategy', 'riskManagement']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing section: {section}")
                return False
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Account: ${config['trading'].get('initialCapital', 0):,.2f}")
        print(f"   Strategy: {config['strategy'].get('entryDelayDays', 0)}-day delay, {config['strategy'].get('holdingPeriodDays', 0)}-day hold")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\n🗄️ Testing database...")
    try:
        # Import here to avoid dependency issues if not installed
        from src.database import get_database
        
        db = get_database()
        stats = db.get_trade_stats()
        
        print(f"✅ Database initialized")
        print(f"   Total trades: {stats.get('total_discovered', 0)}")
        print(f"   Executed trades: {stats.get('total_executed', 0)}")
        return True
    except ImportError as e:
        print(f"⚠️ Database module not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_pdf_parser():
    """Test PDF parser initialization"""
    print("\n📄 Testing PDF parser...")
    try:
        from src.congress_tracker import CongressTracker
        
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        tracker = CongressTracker(config)
        print(f"✅ PDF parser initialized")
        print(f"   Data source: {tracker.data_source}")
        print(f"   Min trade size: ${tracker.min_trade_size:,.0f}")
        return True
    except ImportError as e:
        print(f"⚠️ PDF parser not available: {e}")
        return False
    except Exception as e:
        print(f"❌ PDF parser error: {e}")
        return False

def test_backtester():
    """Test backtester availability"""
    print("\n📈 Testing backtester...")
    try:
        from src.backtester import Backtester
        print(f"✅ Backtester available")
        return True
    except ImportError as e:
        print(f"⚠️ Backtester not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Backtester error: {e}")
        return False

def test_scripts():
    """Test script availability"""
    print("\n📜 Testing scripts...")
    scripts = [
        'scripts/run_bot.sh',
        'scripts/setup_cron.sh',
        'start_trading.sh',
        'stop_trading.sh',
        'monitor.sh'
    ]
    
    all_ok = True
    for script in scripts:
        if Path(script).exists():
            print(f"✅ {script} exists")
        else:
            print(f"❌ {script} missing")
            all_ok = False
    
    return all_ok

def test_directories():
    """Test required directories"""
    print("\n📁 Testing directories...")
    directories = [
        'data',
        'data/congress_trades',
        'data/backups',
        'logs',
        'logs/trading',
        'logs/cron'
    ]
    
    all_ok = True
    for directory in directories:
        if Path(directory).exists():
            print(f"✅ {directory}/ exists")
        else:
            print(f"❌ {directory}/ missing")
            all_ok = False
    
    return all_ok

def test_telegram():
    """Test Telegram configuration"""
    print("\n📱 Testing Telegram...")
    try:
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        telegram_config = config.get('notifications', {}).get('telegram', {})
        enabled = telegram_config.get('enabled', False)
        token = telegram_config.get('botToken', '')
        chat_id = telegram_config.get('chatId', '')
        
        if enabled and token and chat_id:
            print(f"✅ Telegram configured")
            print(f"   Bot token: {token[:10]}...")
            print(f"   Chat ID: {chat_id}")
            return True
        else:
            print(f"⚠️ Telegram not configured (optional)")
            return True  # Telegram is optional
    except Exception as e:
        print(f"❌ Telegram config error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CONGRESSIONAL TRADING SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("PDF Parser", test_pdf_parser),
        ("Backtester", test_backtester),
        ("Scripts", test_scripts),
        ("Directories", test_directories),
        ("Telegram", test_telegram)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready.")
        print("\nNext steps:")
        print("1. source venv/bin/activate")
        print("2. python3 src/main.py interactive")
        print("3. Select option 1 to authenticate with E*TRADE")
        print("4. ./start_trading.sh to begin automated trading")
        return 0
    elif passed >= total - 1:  # Allow one optional test to fail
        print("\n⚠️ MOST TESTS PASSED. System is mostly ready.")
        print("\nCheck the failed tests above and fix if needed.")
        return 1
    else:
        print("\n❌ MULTIPLE TESTS FAILED. System needs fixes.")
        return 1

if __name__ == "__main__":
    sys.exit(main())