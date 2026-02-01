#!/usr/bin/env python3
"""
Refactored Trading Agent - Composition-Based Design

Orchestrates all trading components using dependency injection and composition.
Clean, maintainable, testable architecture following SOLID principles.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add scripts directory to path
_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# Import components
from market import MarketDataProvider, MarketScanner
from indicators import IndicatorCalculator
from signals import SignalGenerator, RecommendationEngine
from risk import PositionSizer
from advanced_validation import AdvancedValidator
from advanced_analytics import AdvancedAnalytics
from pattern_recognition import PatternRecognition


class TradingAgent:
    """
    Refactored Trading Agent - Composition-Based Architecture

    Orchestrates trading components:
    - MarketDataProvider: Fetches market data
    - IndicatorCalculator: Calculates technical indicators
    - PatternRecognition: Detects chart patterns
    - SignalGenerator: Generates Bayesian signals
    - RecommendationEngine: Creates trading recommendations
    - PositionSizer: Calculates position sizes
    - AdvancedAnalytics: Monte Carlo, risk metrics
    - AdvancedValidator: Multi-stage validation

    Design: Dependency injection, composition over inheritance
    """

    def __init__(
        self,
        balance: float,
        exchange_name: str = 'binance',
        config: Dict = None
    ):
        """
        Initialize trading agent with composition

        Args:
            balance: Account balance in USD
            exchange_name: Exchange to use
            config: Optional configuration dict

        Raises:
            ValueError: If balance is invalid
            TypeError: If parameters have wrong type
        """
        # Validate inputs
        if not isinstance(balance, (int, float)):
            raise TypeError(f"Balance must be numeric, got {type(balance).__name__}")

        if balance <= 0:
            raise ValueError(f"Balance must be positive, got {balance}")

        if balance < 100:
            logger.warning(f"Balance ${balance} is very small - position sizing may be limited")

        if not isinstance(exchange_name, str):
            raise TypeError(f"Exchange name must be string, got {type(exchange_name).__name__}")

        self.balance = balance
        self.exchange_name = exchange_name
        self.config = config or {}

        # Initialize core components via dependency injection
        self.validator = AdvancedValidator(strict_mode=True)
        self.analytics = AdvancedAnalytics(confidence_level=0.95)
        self.pattern_engine = PatternRecognition(min_pattern_length=10)

        # Initialize extracted components
        self.data_provider = MarketDataProvider(
            exchange_name=exchange_name,
            validator=self.validator
        )

        self.indicator_calculator = IndicatorCalculator(
            validator=self.validator
        )

        self.signal_generator = SignalGenerator(
            analytics=self.analytics
        )

        self.recommendation_engine = RecommendationEngine()

        self.position_sizer = PositionSizer(
            analytics=self.analytics
        )

        self.market_scanner = MarketScanner(
            trading_agent=self  # Pass self for comprehensive_analysis access
        )

        # Analysis history
        self.analysis_history = []

        logger.info(f"Initialized TradingAgent with ${balance} balance on {exchange_name}")
        logger.info("Using refactored composition-based architecture")

    def comprehensive_analysis(
        self,
        symbol: str,
        timeframes: List[str] = None
    ) -> Dict:
        """
        Production-grade comprehensive analysis with multi-layer validation

        Process:
        1. Multi-timeframe data collection with validation
        2. Advanced indicator calculation with cross-verification
        3. Pattern recognition and chart analysis
        4. Probabilistic signal generation using Bayesian methods
        5. Monte Carlo simulation for risk scenarios
        6. Advanced risk metrics calculation
        7. Final validation and confidence scoring
        8. Position sizing if execution ready

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframes: List of timeframes (default: ['15m', '1h', '4h'])

        Returns:
            Dict with complete analysis including:
            - multi_timeframe_data: Indicators per timeframe
            - pattern_analysis: Chart patterns detected
            - probabilistic_signals: Bayesian signals
            - monte_carlo_scenarios: MC simulation results
            - advanced_metrics: Risk metrics
            - final_recommendation: Trading recommendation
            - execution_ready: Boolean if ready to trade
        """
        timeframes = timeframes or ['15m', '1h', '4h']

        print(f"\n{'='*80}")
        print(f"🔬 COMPREHENSIVE ANALYSIS: {symbol}")
        print(f"{'='*80}")

        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'timeframes_analyzed': [],
            'validation_stages_passed': [],
            'multi_timeframe_data': {},
            'pattern_analysis': {},
            'probabilistic_signals': {},
            'risk_assessment': {},
            'advanced_metrics': {},
            'monte_carlo_scenarios': {},
            'final_recommendation': {},
            'confidence_breakdown': {},
            'execution_ready': False
        }

        # Step 1: Multi-timeframe data collection
        print(f"\n📊 Stage 1: Multi-Timeframe Data Collection & Validation")

        timeframe_dataframes = {}
        for tf in timeframes:
            print(f"   Fetching {tf} data...")

            # Retry logic
            df = None
            for attempt in range(3):
                try:
                    df = self.data_provider.fetch_market_data(symbol, tf, limit=200)
                    if df is not None:
                        break
                except Exception as e:
                    if attempt < 2:
                        wait_time = 2 ** attempt
                        print(f"   ⚠️  Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"   ❌ All retries failed for {tf}: {str(e)[:100]}")

            if df is not None:
                timeframe_dataframes[tf] = df
                analysis['timeframes_analyzed'].append(tf)

                # Calculate indicators
                indicators = self.indicator_calculator.calculate_all(df)

                if 'error' not in indicators:
                    analysis['multi_timeframe_data'][tf] = indicators
                    print(f"   ✅ {tf} data validated and processed")
                else:
                    print(f"   ❌ {tf} indicator calculation failed")
            else:
                print(f"   ❌ {tf} data validation failed")

        # Need at least 2 timeframes
        if len(analysis['timeframes_analyzed']) < 2:
            analysis['final_recommendation'] = {
                'action': 'NO_TRADE',
                'reason': 'Insufficient valid timeframes',
                'confidence': 0
            }
            return analysis

        analysis['validation_stages_passed'].append('DATA_COLLECTION')

        # Step 2: Pattern Recognition
        print(f"\n🎯 Stage 2: Advanced Pattern Recognition & Technical Analysis")

        primary_tf = '1h' if '1h' in timeframe_dataframes else analysis['timeframes_analyzed'][0]
        primary_df = timeframe_dataframes[primary_tf]

        pattern_analysis = self.pattern_engine.analyze_comprehensive(primary_df)
        analysis['pattern_analysis'] = pattern_analysis

        if 'error' not in pattern_analysis:
            print(f"   ✅ Detected {len(pattern_analysis['patterns_detected'])} chart patterns")
            print(f"   ✅ Identified {len(pattern_analysis['support_levels'])} support / "
                  f"{len(pattern_analysis['resistance_levels'])} resistance levels")
            print(f"   ✅ Market Regime: {pattern_analysis.get('market_regime', {}).get('market_regime', 'UNKNOWN')}")
            analysis['validation_stages_passed'].append('PATTERN_RECOGNITION')

        # Step 3: Bayesian Signal Generation
        print(f"\n🧮 Stage 3: Bayesian Probabilistic Signal Generation")

        bayesian_signals = self.signal_generator.generate_signals(
            analysis['multi_timeframe_data'],
            pattern_analysis
        )
        analysis['probabilistic_signals'] = bayesian_signals
        print(f"   ✅ Bayesian probability: {bayesian_signals.get('bullish_probability', 0):.1f}% bullish")
        print(f"   ✅ Signal strength: {bayesian_signals.get('signal_strength', 'UNKNOWN')}")
        analysis['validation_stages_passed'].append('PROBABILISTIC_MODELING')

        # Step 4: Monte Carlo Simulation
        print(f"\n🎲 Stage 4: Monte Carlo Simulation for Risk Assessment")

        returns = primary_df['close'].pct_change().dropna()
        current_price = primary_df['close'].iloc[-1]

        monte_carlo = self.analytics.monte_carlo_simulation(
            current_price=current_price,
            returns=returns,
            days_ahead=5,
            num_simulations=10000
        )

        if 'error' not in monte_carlo:
            analysis['monte_carlo_scenarios'] = monte_carlo
            print(f"   ✅ Simulated 10,000 price scenarios")
            print(f"   ✅ Expected price (5 periods): ${monte_carlo['expected_price']}")
            print(f"   ✅ Profit probability: {monte_carlo['probability_profit']}%")
            analysis['validation_stages_passed'].append('MONTE_CARLO')

        # Step 5: Advanced Risk Metrics
        print(f"\n📈 Stage 5: Advanced Risk Metrics Calculation")

        position_value = self.balance * 0.10
        var_cvar = self.analytics.calculate_var_cvar(returns, position_value, 0.95)
        performance_metrics = self.analytics.calculate_advanced_metrics(returns, risk_free_rate=0.05)

        analysis['risk_assessment'] = {
            'var_cvar': var_cvar,
            'position_value_tested': position_value
        }
        analysis['advanced_metrics'] = performance_metrics

        if 'error' not in var_cvar and 'error' not in performance_metrics:
            print(f"   ✅ VaR (95%): ${abs(var_cvar.get('modified_var_dollar', 0)):.2f} maximum 1-day loss")
            print(f"   ✅ Sharpe Ratio: {performance_metrics.get('sharpe_ratio', 0):.2f}")
            print(f"   ✅ Win Rate: {performance_metrics.get('win_rate_pct', 0):.1f}%")
            analysis['validation_stages_passed'].append('RISK_METRICS')

        # Step 6: Generate Trading Recommendation
        print(f"\n🎯 Stage 6: Generating Final Trading Recommendation")

        recommendation = self.recommendation_engine.generate_recommendation(
            bayesian_signals=bayesian_signals,
            pattern_analysis=pattern_analysis,
            timeframe_data=analysis['multi_timeframe_data'],
            monte_carlo=monte_carlo,
            risk_metrics=performance_metrics,
            current_price=current_price,
            atr=analysis['multi_timeframe_data'][primary_tf]['atr']
        )

        analysis['final_recommendation'] = recommendation

        # Step 7: Signal Validation
        validation_report = self.validator.validate_trading_signal(recommendation)

        if validation_report['passed']:
            print(f"   ✅ Signal validation passed")
            analysis['execution_ready'] = True
            analysis['validation_stages_passed'].append('SIGNAL_VALIDATION')
        else:
            print(f"   ❌ Signal validation failed:")
            for failure in validation_report['critical_failures']:
                print(f"      {failure}")
            analysis['execution_ready'] = False
            recommendation['action'] = 'NO_TRADE'
            recommendation['reason'] = 'Failed final validation'

        # Step 8: Position Sizing
        if analysis['execution_ready'] and recommendation['action'] in ['LONG', 'SHORT']:
            position_sizing = self.position_sizer.calculate_position_size(
                entry_price=recommendation['entry_price'],
                stop_loss=recommendation['stop_loss'],
                balance=self.balance,
                risk_metrics=performance_metrics
            )
            recommendation['position_sizing'] = position_sizing

        # Store in history
        self.analysis_history.append(analysis)

        return analysis

    def scan_market(
        self,
        categories: Optional[List[str]] = None,
        timeframes: List[str] = None,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Scan market for trading opportunities

        Args:
            categories: List of categories to scan
            timeframes: Timeframes to analyze
            top_n: Number of top opportunities

        Returns:
            List of top opportunities
        """
        return self.market_scanner.scan_market(categories, timeframes, top_n)

    def display_scan_results(self, opportunities: List[Dict]):
        """Display market scan results"""
        self.market_scanner.display_scan_results(opportunities)

    def get_analysis_history(self) -> List[Dict]:
        """Get analysis history"""
        return self.analysis_history.copy()

    def clear_analysis_history(self):
        """Clear analysis history"""
        self.analysis_history.clear()
        logger.info("Analysis history cleared")
