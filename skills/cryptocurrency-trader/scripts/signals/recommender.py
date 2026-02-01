#!/usr/bin/env python3
"""
Recommendation Engine - Extracted from EnhancedTradingAgent

Generates trading recommendations with confidence scoring.
Single Responsibility: Generate actionable trading recommendations
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Generates trading recommendations with confidence scoring

    Responsibilities:
    - Determine trading action (LONG/SHORT/WAIT)
    - Calculate confidence scores
    - Set entry, stop-loss, and take-profit levels
    - Calculate risk/reward ratios
    - Provide detailed recommendation breakdown
    """

    def __init__(self, atr_stop_multiplier: float = 2.0, atr_target_multiplier: float = 3.0):
        """
        Initialize recommendation engine

        Args:
            atr_stop_multiplier: ATR multiplier for stop-loss (default: 2.0)
            atr_target_multiplier: ATR multiplier for take-profit (default: 3.0)
        """
        self.atr_stop_multiplier = atr_stop_multiplier
        self.atr_target_multiplier = atr_target_multiplier
        logger.info("Initialized RecommendationEngine")

    def generate_recommendation(
        self,
        bayesian_signals: Dict,
        pattern_analysis: Dict,
        timeframe_data: Dict,
        monte_carlo: Dict,
        risk_metrics: Dict,
        current_price: float,
        atr: float
    ) -> Dict:
        """
        Generate final trading recommendation with confidence scoring

        Production-ready output for real-world application.

        Args:
            bayesian_signals: Bayesian probability results
            pattern_analysis: Pattern analysis results
            timeframe_data: Multi-timeframe indicator data
            monte_carlo: Monte Carlo simulation results
            risk_metrics: Risk metrics (Sharpe, win rate, etc.)
            current_price: Current market price
            atr: Average True Range

        Returns:
            Dict with recommendation:
            - action: 'LONG', 'SHORT', or 'WAIT'
            - confidence: 0-95 confidence score
            - entry_price: Recommended entry price
            - stop_loss: Stop-loss level
            - take_profit: Take-profit level
            - risk_reward: Risk/reward ratio
            - confidence_breakdown: List of adjustments
        """
        try:
            # Determine action based on Bayesian probability
            bullish_prob = bayesian_signals.get('bullish_probability', 50)

            if bullish_prob > 60:
                action = 'LONG'
                base_confidence = int(bayesian_signals.get('confidence', 50))
            elif bullish_prob < 40:
                action = 'SHORT'
                base_confidence = int(bayesian_signals.get('confidence', 50))
            else:
                action = 'WAIT'
                base_confidence = 0

            # Adjust confidence based on additional factors
            confidence_adjustments = self._calculate_confidence_adjustments(
                action,
                pattern_analysis,
                monte_carlo,
                risk_metrics
            )

            # Calculate final confidence
            final_confidence = base_confidence + sum(adj[1] for adj in confidence_adjustments)
            final_confidence = max(0, min(95, final_confidence))  # Cap between 0-95

            # Calculate price levels
            price_levels = self._calculate_price_levels(action, current_price, atr)

            # Build recommendation
            recommendation = {
                'action': action,
                'confidence': final_confidence,
                'confidence_breakdown': confidence_adjustments,
                'entry_price': round(price_levels['entry'], 2),
                'stop_loss': round(price_levels['stop_loss'], 2) if price_levels['stop_loss'] else None,
                'take_profit': round(price_levels['take_profit'], 2) if price_levels['take_profit'] else None,
                'risk_reward': price_levels['risk_reward'],
                'bayesian_probability': {
                    'bullish': bayesian_signals.get('bullish_probability', 0),
                    'bearish': bayesian_signals.get('bearish_probability', 0)
                },
                'signal_strength': bayesian_signals.get('signal_strength', 'UNKNOWN'),
                'pattern_bias': pattern_analysis.get('overall_bias', 'NEUTRAL'),
                'monte_carlo_profit_prob': monte_carlo.get('probability_profit', 0),
                'sharpe_ratio': risk_metrics.get('sharpe_ratio', 0)
            }

            logger.info(f"Generated recommendation: {action} with {final_confidence}% confidence")
            return recommendation

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return {
                'action': 'WAIT',
                'confidence': 0,
                'error': str(e)
            }

    def _calculate_confidence_adjustments(
        self,
        action: str,
        pattern_analysis: Dict,
        monte_carlo: Dict,
        risk_metrics: Dict
    ) -> List[Tuple[str, int]]:
        """
        Calculate confidence adjustments based on additional factors

        Args:
            action: Trading action (LONG/SHORT/WAIT)
            pattern_analysis: Pattern analysis results
            monte_carlo: Monte Carlo results
            risk_metrics: Risk metrics

        Returns:
            List of (reason, adjustment) tuples
        """
        adjustments = []

        # Pattern confirmation
        pattern_bias = pattern_analysis.get('overall_bias', 'NEUTRAL')
        if (action == 'LONG' and pattern_bias == 'BULLISH') or \
           (action == 'SHORT' and pattern_bias == 'BEARISH'):
            adjustments.append(('Pattern Confirmation', +10))
        elif (action == 'LONG' and pattern_bias == 'BEARISH') or \
             (action == 'SHORT' and pattern_bias == 'BULLISH'):
            adjustments.append(('Pattern Conflict', -15))

        # Monte Carlo probability
        if 'probability_profit' in monte_carlo:
            profit_prob = monte_carlo['probability_profit']
            if profit_prob > 60:
                adjustments.append(('Monte Carlo Favorable', +5))
            elif profit_prob < 45:
                adjustments.append(('Monte Carlo Unfavorable', -10))

        # Sharpe ratio
        sharpe = risk_metrics.get('sharpe_ratio', 0)
        if sharpe > 1.0:
            adjustments.append(('Strong Sharpe Ratio', +5))
        elif sharpe < 0:
            adjustments.append(('Negative Sharpe', -10))

        # Win rate
        win_rate = risk_metrics.get('win_rate_pct', 0)
        if win_rate > 55:
            adjustments.append(('High Win Rate', +5))
        elif win_rate < 45:
            adjustments.append(('Low Win Rate', -5))

        return adjustments

    def _calculate_price_levels(
        self,
        action: str,
        entry_price: float,
        atr: float
    ) -> Dict:
        """
        Calculate entry, stop-loss, and take-profit levels

        Args:
            action: Trading action (LONG/SHORT/WAIT)
            entry_price: Entry price
            atr: Average True Range

        Returns:
            Dict with entry, stop_loss, take_profit, risk_reward
        """
        if action == 'LONG':
            stop_loss = entry_price - (self.atr_stop_multiplier * atr)
            take_profit = entry_price + (self.atr_target_multiplier * atr)
        elif action == 'SHORT':
            stop_loss = entry_price + (self.atr_stop_multiplier * atr)
            take_profit = entry_price - (self.atr_target_multiplier * atr)
        else:
            # WAIT action - no levels
            return {
                'entry': entry_price,
                'stop_loss': None,
                'take_profit': None,
                'risk_reward': 0
            }

        # Calculate risk/reward ratio
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        risk_reward = round(reward / risk, 1) if risk > 0 else 0

        return {
            'entry': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward': risk_reward
        }

    def validate_recommendation(self, recommendation: Dict) -> Tuple[bool, List[str]]:
        """
        Validate recommendation for safety

        Args:
            recommendation: Generated recommendation dict

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check required fields
        if 'action' not in recommendation:
            issues.append("Missing action")

        if 'confidence' not in recommendation:
            issues.append("Missing confidence")

        # Check confidence range
        confidence = recommendation.get('confidence', 0)
        if not 0 <= confidence <= 95:
            issues.append(f"Confidence {confidence} out of range [0, 95]")

        # Check risk/reward ratio for actionable recommendations
        if recommendation.get('action') in ['LONG', 'SHORT']:
            risk_reward = recommendation.get('risk_reward', 0)
            if risk_reward < 1.5:
                issues.append(f"Risk/reward {risk_reward} below minimum 1.5")

        is_valid = len(issues) == 0
        return is_valid, issues
