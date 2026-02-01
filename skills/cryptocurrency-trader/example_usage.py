#!/usr/bin/env python3
"""
AI Trading Skill - Example Usage

This script demonstrates how to use the AI Trading skill
from Claude Code or other Python environments.
"""

import sys
import os

# Add scripts directory to path
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, SCRIPT_DIR)


def example_basic_analysis():
    """Example: Basic cryptocurrency analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Analysis")
    print("="*80)

    from trading_agent_refactored import TradingAgent

    # Initialize agent with $10,000 balance
    agent = TradingAgent(balance=10000)

    # Analyze Bitcoin
    print("\nAnalyzing BTC/USDT...")
    analysis = agent.comprehensive_analysis('BTC/USDT')

    # Display key results
    rec = analysis.get('final_recommendation', {})
    print(f"\n✅ Analysis Complete:")
    print(f"   Action: {rec.get('action', 'N/A')}")
    print(f"   Confidence: {rec.get('confidence', 0)}%")
    print(f"   Entry Price: ${rec.get('entry_price', 0):,.2f}")

    if rec.get('stop_loss'):
        print(f"   Stop Loss: ${rec.get('stop_loss'):,.2f}")
    if rec.get('take_profit'):
        print(f"   Take Profit: ${rec.get('take_profit'):,.2f}")

    print(f"   Risk/Reward: {rec.get('risk_reward', 'N/A')}")
    print(f"   Execution Ready: {analysis.get('execution_ready', False)}")

    return analysis


def example_pattern_recognition():
    """Example: Pattern recognition only"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Pattern Recognition")
    print("="*80)

    from pattern_recognition_refactored import PatternRecognition
    from market.data_provider import MarketDataProvider

    # Initialize components
    data_provider = MarketDataProvider(exchange_name='binance')
    pattern_engine = PatternRecognition(min_pattern_length=20)

    # Fetch market data
    print("\nFetching market data for ETH/USDT...")
    df = data_provider.fetch_market_data('ETH/USDT', timeframe='1h', limit=100)

    if df is not None:
        # Analyze patterns
        print("Analyzing patterns...")
        analysis = pattern_engine.analyze_comprehensive(df)

        # Display patterns found
        patterns = analysis.get('patterns_detected', [])
        print(f"\n✅ Found {len(patterns)} patterns:")
        for p in patterns[:5]:  # Show first 5
            print(f"   - {p.get('pattern')}: {p.get('bias')} "
                  f"({p.get('confidence', 0)}% confidence)")

        # Display support/resistance
        print(f"\nSupport Levels: {analysis.get('support_levels', [])}")
        print(f"Resistance Levels: {analysis.get('resistance_levels', [])}")

        # Display trend
        trend = analysis.get('trend_analysis', {})
        if not trend.get('error'):
            print(f"\nTrend: {trend.get('short_term', {}).get('direction')}")
            print(f"Trend Strength: {trend.get('trend_strength')}")

        print(f"\nOverall Bias: {analysis.get('overall_bias')} "
              f"({analysis.get('confidence', 0)}% confidence)")

    return analysis if df is not None else None


def example_risk_analysis():
    """Example: Risk metrics calculation"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Risk Analysis")
    print("="*80)

    from advanced_analytics import AdvancedAnalytics
    from market.data_provider import MarketDataProvider
    import pandas as pd

    # Initialize components
    analytics = AdvancedAnalytics(confidence_level=0.95)
    data_provider = MarketDataProvider(exchange_name='binance')

    # Fetch data
    print("\nFetching data for SOL/USDT...")
    df = data_provider.fetch_market_data('SOL/USDT', timeframe='1h', limit=200)

    if df is not None:
        # Calculate returns
        returns = df['close'].pct_change().dropna()

        # Position value (example: $1000 position)
        position_value = 1000

        # Calculate VaR and CVaR
        print("\nCalculating risk metrics...")
        var, cvar = analytics.calculate_var_cvar(returns, position_value, confidence_level=0.95)

        print(f"\n✅ Risk Metrics:")
        print(f"   Value at Risk (95%): ${var:.2f}")
        print(f"   Conditional VaR (95%): ${cvar:.2f}")

        # Calculate performance metrics
        metrics = analytics.calculate_advanced_metrics(returns)
        print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 'N/A')}")
        print(f"   Sortino Ratio: {metrics.get('sortino_ratio', 'N/A')}")
        print(f"   Max Drawdown: {metrics.get('max_drawdown_pct', 'N/A')}%")

        return {'var': var, 'cvar': cvar, 'metrics': metrics}

    return None


def example_market_scan():
    """Example: Market scanning for opportunities"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Market Scanning")
    print("="*80)

    from trading_agent_refactored import TradingAgent

    # Initialize agent
    agent = TradingAgent(balance=10000)

    # Check if market scanner available
    if hasattr(agent, 'market_scanner'):
        print("\nScanning market for top 3 opportunities...")
        opportunities = agent.market_scanner.scan_market(
            categories=['Major Coins', 'AI Tokens'],
            top_n=3
        )

        if opportunities:
            print(f"\n✅ Found {len(opportunities)} opportunities:")
            for i, opp in enumerate(opportunities, 1):
                rec = opp.get('final_recommendation', {})
                print(f"\n{i}. {opp.get('symbol')}")
                print(f"   Action: {rec.get('action')}")
                print(f"   Confidence: {rec.get('confidence')}%")
                print(f"   EV Score: {opp.get('ev_score')}")

            return opportunities
        else:
            print("\n⚠️  No execution-ready opportunities found")
    else:
        print("\n⚠️  Market scanner not available in this agent version")

    return []


def example_component_usage():
    """Example: Using individual components"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Using Individual Components")
    print("="*80)

    from patterns import (
        TrendAnalyzer,
        VolumeAnalyzer,
        MarketRegimeDetector
    )
    from market.data_provider import MarketDataProvider

    # Initialize components
    data_provider = MarketDataProvider(exchange_name='binance')
    trend_analyzer = TrendAnalyzer()
    volume_analyzer = VolumeAnalyzer()
    regime_detector = MarketRegimeDetector()

    # Fetch data
    print("\nFetching data for BNB/USDT...")
    df = data_provider.fetch_market_data('BNB/USDT', timeframe='1h', limit=100)

    if df is not None:
        # Trend analysis
        print("\n1. Trend Analysis:")
        trend = trend_analyzer.analyze_comprehensive(df)
        if not trend.get('error'):
            print(f"   Short-term: {trend['short_term']['direction']}")
            print(f"   Medium-term: {trend['medium_term']['direction']}")
            print(f"   Strength: {trend['trend_strength']}")
            print(f"   Aligned: {trend['aligned']}")

        # Volume analysis
        print("\n2. Volume Analysis:")
        volume = volume_analyzer.analyze_comprehensive(df)
        if not volume.get('error'):
            print(f"   Status: {volume['volume_status']}")
            print(f"   OBV Trend: {volume['obv_trend']}")
            print(f"   VPT Trend: {volume['vpt_trend']}")
            print(f"   Confirmation: {volume['confirmation']}")

        # Market regime
        print("\n3. Market Regime:")
        regime = regime_detector.detect_regime(df)
        if not regime.get('error'):
            print(f"   Market: {regime['market_regime']}")
            print(f"   Volatility: {regime['volatility_regime']}")
            print(f"   Strategy: {regime['recommended_strategy']}")

        return {'trend': trend, 'volume': volume, 'regime': regime}

    return None


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("AI TRADING SKILL - USAGE EXAMPLES")
    print("="*80)
    print("\nThis script demonstrates various ways to use the AI Trading skill.")
    print("Each example shows a different use case.\n")

    try:
        # Run examples
        print("\n[1/5] Running basic analysis example...")
        example_basic_analysis()

        print("\n[2/5] Running pattern recognition example...")
        example_pattern_recognition()

        print("\n[3/5] Running risk analysis example...")
        example_risk_analysis()

        print("\n[4/5] Running market scan example...")
        example_market_scan()

        print("\n[5/5] Running component usage example...")
        example_component_usage()

        print("\n" + "="*80)
        print("✅ All examples completed successfully!")
        print("="*80)
        print("\nYou can now use these patterns in your own code.")
        print("See CLAUDE_CODE_USAGE.md for more details.\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
