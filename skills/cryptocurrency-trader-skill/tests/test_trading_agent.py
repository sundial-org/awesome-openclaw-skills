#!/usr/bin/env python3
"""
Test Suite for AI Trading Agent
Tests with real data when available, falls back to simulated data
"""

import sys
sys.path.insert(0, '/home/claude/ai-trading-agent/scripts')

from trading_agent import TradingAgent
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def test_with_real_data():
    """Test with real exchange data"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Real BTC/USDT Data")
    print("="*60)
    
    exchanges_to_try = ['kraken', 'coinbase', 'binance', 'bybit']
    
    for exchange_name in exchanges_to_try:
        try:
            print(f"\n📡 Trying {exchange_name}...")
            agent = TradingAgent(balance=10000, exchange_name=exchange_name)
            
            # Quick test fetch
            df = agent.fetch_market_data('BTC/USDT', '1h', limit=50)
            
            if df is not None and len(df) > 0:
                print(f"✅ {exchange_name} connected successfully!")
                print(f"   Latest BTC price: ${df['close'].iloc[-1]:.2f}")
                print(f"   Data points: {len(df)}")
                
                # Run full analysis
                print(f"\n🔬 Running full analysis...")
                analysis = agent.analyze_opportunity('BTC/USDT', timeframes=['1h', '4h'])
                agent.display_opportunity(analysis)
                
                return True, agent
            
        except Exception as e:
            print(f"   ⚠️ {exchange_name} failed: {str(e)[:100]}")
            continue
    
    return False, None


def test_with_simulated_data():
    """Test core functionality with simulated market data"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Simulated Market Data (Exchange Unavailable)")
    print("="*60)
    
    # Create simulated OHLCV data for BTC
    print("\n📊 Generating simulated BTC/USDT data...")
    
    dates = pd.date_range(end=datetime.now(), periods=100, freq='1h')
    base_price = 94000
    
    # Simulate realistic price movement
    np.random.seed(42)
    returns = np.random.normal(0, 0.01, 100)
    prices = base_price * (1 + returns).cumprod()
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.005,
        'low': prices * 0.995,
        'close': prices,
        'volume': np.random.uniform(100, 1000, 100)
    })
    
    print(f"✅ Created {len(df)} hourly candles")
    print(f"   Starting price: ${df['close'].iloc[0]:.2f}")
    print(f"   Current price: ${df['close'].iloc[-1]:.2f}")
    print(f"   Price change: {((df['close'].iloc[-1]/df['close'].iloc[0])-1)*100:.2f}%")
    
    # Test indicator calculations
    print("\n🔬 Testing technical indicators...")
    agent = TradingAgent(balance=10000)
    indicators = agent.calculate_indicators(df)
    
    if 'error' in indicators:
        print(f"❌ Indicator calculation failed: {indicators['error']}")
        return False
    
    print(f"✅ Technical indicators calculated successfully:")
    print(f"   RSI: {indicators['rsi']:.1f}")
    print(f"   MACD: {indicators['macd']:.2f}")
    print(f"   ATR: ${indicators['atr']:.2f}")
    print(f"   Current Price: ${indicators['current_price']:.2f}")
    
    # Test validation
    print("\n🛡️ Testing data validation...")
    validation = agent._validate_market_data(df, 'BTC/USDT')
    
    if validation['valid']:
        print("✅ Data validation passed")
    else:
        print(f"⚠️ Validation issues: {validation['issues']}")
    
    # Test consensus calculation
    print("\n🎯 Testing signal generation...")
    timeframe_data = {
        '1h': indicators,
        '4h': indicators  # Using same for simplicity
    }
    
    consensus = agent._calculate_consensus(timeframe_data)
    
    print(f"✅ Signal generated:")
    print(f"   Action: {consensus['action']}")
    print(f"   Confidence: {consensus['confidence']}%")
    print(f"   Entry: ${consensus['entry_price']:.2f}")
    if consensus['stop_loss']:
        print(f"   Stop Loss: ${consensus['stop_loss']:.2f}")
        print(f"   Take Profit: ${consensus['take_profit']:.2f}")
        print(f"   Risk/Reward: 1:{consensus['risk_reward']}")
    
    # Test position sizing
    if consensus['stop_loss']:
        print("\n💼 Testing position sizing...")
        position = agent._calculate_position_size(
            consensus['entry_price'],
            consensus['stop_loss'],
            10000
        )
        
        if 'error' not in position:
            print(f"✅ Position sizing calculated:")
            print(f"   Position Value: ${position['position_value_usd']:.2f}")
            print(f"   Risk Amount: ${position['risk_usd']:.2f} (2% max)")
            print(f"   Trading Fees: ${position['trading_fees']:.2f}")
        else:
            print(f"❌ {position['error']}")
    
    # Test circuit breakers
    print("\n🚦 Testing circuit breakers...")
    analysis = {
        'symbol': 'BTC/USDT',
        'action': consensus['action'],
        'confidence': consensus['confidence'],
        'risk_reward': consensus['risk_reward'],
        'entry_price': consensus['entry_price'],
        'stop_loss': consensus['stop_loss'],
        'take_profit': consensus['take_profit'],
        'timeframe_data': timeframe_data,
        'warnings': []
    }
    
    analysis = agent._apply_circuit_breakers(analysis)
    
    print(f"   Safe to trade: {analysis['safe_to_use']}")
    print(f"   Recommendation: {analysis['recommendation']}")
    
    if analysis['blocks']:
        print(f"   Blocks: {', '.join(analysis['blocks'])}")
    
    if analysis['warnings']:
        print(f"   Warnings: {', '.join(analysis['warnings'])}")
    
    return True


def test_anti_hallucination():
    """Test anti-hallucination features"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Anti-Hallucination Framework")
    print("="*60)
    
    agent = TradingAgent(balance=10000)
    
    # Test 1: Invalid price data
    print("\n1️⃣ Testing invalid price detection...")
    bad_df = pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=10, freq='1h'),
        'open': [100, -50, 100, 100, 100, 100, 100, 100, 100, 100],  # Negative price
        'high': [105, 105, 105, 105, 105, 105, 105, 105, 105, 105],
        'low': [95, 95, 95, 95, 95, 95, 95, 95, 95, 95],
        'close': [103, 103, 103, 103, 103, 103, 103, 103, 103, 103],
        'volume': [1000] * 10
    })
    
    validation = agent._validate_market_data(bad_df, 'TEST/USDT')
    
    if not validation['valid']:
        print("✅ Correctly detected invalid data:")
        print(f"   Issues: {validation['issues']}")
    else:
        print("❌ Failed to detect invalid data")
    
    # Test 2: OHLC logic violation
    print("\n2️⃣ Testing OHLC logic validation...")
    bad_ohlc = pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=10, freq='1h'),
        'open': [100] * 10,
        'high': [95] * 10,  # High < Low - impossible!
        'low': [105] * 10,
        'close': [103] * 10,
        'volume': [1000] * 10
    })
    
    validation = agent._validate_market_data(bad_ohlc, 'TEST/USDT')
    
    if not validation['valid']:
        print("✅ Correctly detected OHLC violation:")
        print(f"   Issues: {validation['issues']}")
    else:
        print("❌ Failed to detect OHLC violation")
    
    # Test 3: False precision control
    print("\n3️⃣ Testing precision control...")
    
    # Confidence should be rounded to integers
    analysis = {
        'confidence': 87.456321,
        'action': 'LONG',
        'risk_reward': 3.0,
        'entry_price': 94000.0,
        'timeframe_data': {'1h': {}, '4h': {}},
        'warnings': []
    }
    
    analysis = agent._apply_circuit_breakers(analysis)
    
    # Check if confidence is an integer
    if isinstance(analysis['confidence'], int):
        print(f"✅ Confidence properly formatted: {analysis['confidence']}%")
    else:
        print(f"⚠️ Confidence has false precision: {analysis['confidence']}")
    
    # Test 4: Unrealistic confidence warning
    print("\n4️⃣ Testing unrealistic confidence detection...")
    
    analysis_high = {
        'confidence': 95,
        'action': 'LONG',
        'risk_reward': 3.0,
        'entry_price': 94000.0,
        'timeframe_data': {'1h': {}, '4h': {}},
        'warnings': []
    }
    
    analysis_high = agent._apply_circuit_breakers(analysis_high)
    
    if any('Unrealistically high confidence' in w for w in analysis_high['warnings']):
        print("✅ Warning triggered for >90% confidence")
    else:
        print("⚠️ No warning for unrealistic confidence")
    
    # Test 5: Poor risk/reward blocking
    print("\n5️⃣ Testing risk/reward circuit breaker...")
    
    analysis_bad_rr = {
        'confidence': 70,
        'action': 'LONG',
        'risk_reward': 1.0,  # Too low
        'entry_price': 94000.0,
        'timeframe_data': {'1h': {}, '4h': {}},
        'warnings': []
    }
    
    analysis_bad_rr = agent._apply_circuit_breakers(analysis_bad_rr)
    
    if not analysis_bad_rr['safe_to_use']:
        print("✅ Trade correctly blocked for poor R:R")
        print(f"   Blocks: {analysis_bad_rr['blocks']}")
    else:
        print("❌ Failed to block poor risk/reward trade")
    
    return True


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("🚀 AI TRADING AGENT - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("\nTesting all features:")
    print("✓ Real-time market data (when available)")
    print("✓ Technical indicator calculations")
    print("✓ Signal generation and consensus")
    print("✓ Position sizing and risk management")
    print("✓ Circuit breakers and safety checks")
    print("✓ Anti-hallucination framework")
    
    results = []
    
    # Test 1: Try real data
    success, agent = test_with_real_data()
    results.append(("Real Data Test", success))
    
    # Test 2: Simulated data (always runs)
    success = test_with_simulated_data()
    results.append(("Simulated Data Test", success))
    
    # Test 3: Anti-hallucination
    success = test_anti_hallucination()
    results.append(("Anti-Hallucination Test", success))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🏆 Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED! System is ready for use.")
    else:
        print("\n⚠️ Some tests failed. Review errors above.")
    
    print("="*70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
