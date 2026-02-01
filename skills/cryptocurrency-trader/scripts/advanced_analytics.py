#!/usr/bin/env python3
"""
Advanced Analytics and Probabilistic Modeling Module
Implements sophisticated mathematical computations for trading analysis
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class AdvancedAnalytics:
    """
    Advanced statistical and probabilistic analysis for trading
    Production-grade mathematical computations with rigorous validation
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize analytics engine

        Args:
            confidence_level: Confidence level for statistical tests (default 95%)
        """
        self.confidence_level = confidence_level
        self.simulation_cache = {}

    def monte_carlo_simulation(
        self,
        current_price: float,
        returns: pd.Series,
        days_ahead: int = 5,
        num_simulations: int = 10000
    ) -> Dict:
        """
        Monte Carlo simulation for price prediction with confidence intervals
        Uses geometric Brownian motion with actual return distribution
        """
        if len(returns) < 30:
            return {'error': 'Insufficient data for Monte Carlo simulation (need 30+ periods)'}

        # Calculate statistical parameters from actual returns
        mean_return = returns.mean()
        std_return = returns.std()

        # Validate parameters
        if std_return == 0 or np.isnan(mean_return) or np.isnan(std_return):
            return {'error': 'Invalid return statistics for simulation'}

        # Run simulations with overflow protection
        simulations = np.zeros((num_simulations, days_ahead))
        simulations[:, 0] = current_price

        # Cap extreme moves to prevent overflow
        max_exponent = 5.0  # exp(5) ≈ 148x, exp(-5) ≈ 0.0067x

        for sim in range(num_simulations):
            for day in range(1, days_ahead):
                # Geometric Brownian Motion with Itô's Lemma correction
                # The drift term must be adjusted by -0.5*σ² to avoid systematic bias
                # This ensures E[S(t+1)] = S(t) * exp(μ) rather than being biased upward
                drift = mean_return - 0.5 * std_return**2
                shock = std_return * np.random.randn()

                # Clamp exponent to prevent overflow
                exponent = np.clip(drift + shock, -max_exponent, max_exponent)

                try:
                    new_value = simulations[sim, day-1] * np.exp(exponent)

                    # Validate result is finite
                    if np.isfinite(new_value) and new_value > 0:
                        simulations[sim, day] = new_value
                    else:
                        # If invalid, use previous value (no change)
                        simulations[sim, day] = simulations[sim, day-1]

                except (OverflowError, FloatingPointError):
                    # Fallback to previous value on overflow
                    simulations[sim, day] = simulations[sim, day-1]

        # Calculate statistics with validation
        final_prices = simulations[:, -1]

        # Filter out any invalid values
        valid_prices = final_prices[np.isfinite(final_prices) & (final_prices > 0)]

        if len(valid_prices) < num_simulations * 0.9:  # Less than 90% valid
            return {'error': 'Monte Carlo simulation produced too many invalid results'}
        percentiles = [5, 25, 50, 75, 95]
        price_percentiles = np.percentile(valid_prices, percentiles)

        # Calculate probabilities using valid prices
        prob_profit = (valid_prices > current_price).sum() / len(valid_prices)
        prob_loss = (valid_prices < current_price).sum() / len(valid_prices)

        # Expected value
        expected_price = valid_prices.mean()
        expected_return = (expected_price / current_price - 1) * 100

        return {
            'num_simulations': num_simulations,
            'days_ahead': days_ahead,
            'current_price': round(current_price, 2),
            'expected_price': round(expected_price, 2),
            'expected_return_pct': round(expected_return, 2),
            'price_5th_percentile': round(price_percentiles[0], 2),
            'price_25th_percentile': round(price_percentiles[1], 2),
            'price_median': round(price_percentiles[2], 2),
            'price_75th_percentile': round(price_percentiles[3], 2),
            'price_95th_percentile': round(price_percentiles[4], 2),
            'probability_profit': round(prob_profit * 100, 1),
            'probability_loss': round(prob_loss * 100, 1),
            'worst_case_5pct': round((price_percentiles[0] / current_price - 1) * 100, 2),
            'best_case_5pct': round((price_percentiles[4] / current_price - 1) * 100, 2)
        }

    def bayesian_signal_probability(
        self,
        indicator_signals: List[Tuple[str, bool]],
        prior_accuracy: Dict[str, float] = None
    ) -> Dict:
        """
        Bayesian probability calculation for signal confidence
        Combines multiple indicators using Bayes' theorem

        Args:
            indicator_signals: List of (indicator_name, bullish_signal) tuples
            prior_accuracy: Historical accuracy rates for each indicator
        """
        # Default prior accuracies if not provided
        if prior_accuracy is None:
            prior_accuracy = {
                'RSI': 0.65,
                'MACD': 0.68,
                'BB': 0.62,
                'Volume': 0.60,
                'Trend': 0.70
            }

        # Start with neutral prior (50% probability)
        prior_prob = 0.50

        # Apply Bayes' theorem for each indicator
        for indicator, is_bullish in indicator_signals:
            accuracy = prior_accuracy.get(indicator, 0.60)

            if is_bullish:
                # P(Bullish|Signal) = P(Signal|Bullish) * P(Bullish) / P(Signal)
                likelihood = accuracy  # P(Signal|Bullish)
                false_positive_rate = 1 - accuracy  # P(Signal|Bearish)

                # Calculate posterior probability
                numerator = likelihood * prior_prob
                denominator = likelihood * prior_prob + false_positive_rate * (1 - prior_prob)

                if denominator > 0:
                    posterior_prob = numerator / denominator
                else:
                    posterior_prob = prior_prob

                prior_prob = posterior_prob
            else:
                # Bearish signal - inverse the calculation
                likelihood = accuracy
                false_negative_rate = 1 - accuracy

                numerator = false_negative_rate * prior_prob
                denominator = false_negative_rate * prior_prob + likelihood * (1 - prior_prob)

                if denominator > 0:
                    posterior_prob = numerator / denominator
                else:
                    posterior_prob = prior_prob

                prior_prob = posterior_prob

        # Calculate confidence
        confidence = abs(prior_prob - 0.5) * 2 * 100  # Convert to 0-100 scale

        return {
            'bullish_probability': round(prior_prob * 100, 1),
            'bearish_probability': round((1 - prior_prob) * 100, 1),
            'confidence': round(confidence, 1),
            'signal_strength': 'STRONG' if confidence > 60 else 'MODERATE' if confidence > 40 else 'WEAK',
            'num_indicators': len(indicator_signals)
        }

    def calculate_var_cvar(
        self,
        returns: pd.Series,
        position_value: float,
        confidence_level: float = 0.95
    ) -> Dict:
        """
        Calculate Value at Risk (VaR) and Conditional VaR (CVaR)
        Uses both parametric and historical methods for robust estimation
        """
        if len(returns) < 30:
            return {'error': 'Insufficient data for VaR calculation (need 30+ periods)'}

        # Historical VaR
        var_percentile = (1 - confidence_level) * 100
        historical_var = np.percentile(returns, var_percentile)
        historical_var_dollar = position_value * historical_var

        # Parametric VaR (assuming normal distribution)
        z_score = stats.norm.ppf(1 - confidence_level)
        parametric_var = returns.mean() + z_score * returns.std()
        parametric_var_dollar = position_value * parametric_var

        # CVaR (Expected Shortfall) - average of losses beyond VaR
        cvar = returns[returns <= historical_var].mean()
        cvar_dollar = position_value * cvar

        # Modified VaR (accounts for skewness and kurtosis)
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)

        z_modified = (z_score +
                     (z_score**2 - 1) * skewness / 6 +
                     (z_score**3 - 3*z_score) * kurtosis / 24 -
                     (2*z_score**3 - 5*z_score) * skewness**2 / 36)

        modified_var = returns.mean() + z_modified * returns.std()
        modified_var_dollar = position_value * modified_var

        return {
            'confidence_level': confidence_level * 100,
            'historical_var_pct': round(historical_var * 100, 2),
            'historical_var_dollar': round(historical_var_dollar, 2),
            'parametric_var_pct': round(parametric_var * 100, 2),
            'parametric_var_dollar': round(parametric_var_dollar, 2),
            'modified_var_pct': round(modified_var * 100, 2),
            'modified_var_dollar': round(modified_var_dollar, 2),
            'cvar_pct': round(cvar * 100, 2),
            'cvar_dollar': round(cvar_dollar, 2),
            'interpretation': f"95% confidence: Maximum 1-day loss won't exceed ${abs(modified_var_dollar):.2f}"
        }

    def calculate_advanced_metrics(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.05
    ) -> Dict:
        """
        Calculate advanced risk-adjusted performance metrics
        Sharpe, Sortino, Calmar, and Information Ratio
        """
        if len(returns) < 30:
            return {'error': 'Insufficient data for metric calculation (need 30+ periods)'}

        # Annualization factors (assuming hourly data)
        periods_per_year = 24 * 365

        # Mean and std
        mean_return = returns.mean()
        std_return = returns.std()

        # Sharpe Ratio
        excess_return = mean_return - (risk_free_rate / periods_per_year)
        sharpe_ratio = (excess_return / std_return) * np.sqrt(periods_per_year) if std_return > 0 else 0

        # Sortino Ratio (uses downside deviation only)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else std_return
        sortino_ratio = (excess_return / downside_std) * np.sqrt(periods_per_year) if downside_std > 0 else 0

        # Maximum Drawdown and Calmar Ratio
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        annualized_return = mean_return * periods_per_year
        calmar_ratio = abs(annualized_return / max_drawdown) if max_drawdown != 0 else 0

        # Win Rate
        win_rate = (returns > 0).sum() / len(returns) * 100

        # Profit Factor
        gross_profit = returns[returns > 0].sum()
        gross_loss = abs(returns[returns < 0].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Skewness and Kurtosis
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)

        return {
            'sharpe_ratio': round(sharpe_ratio, 2),
            'sortino_ratio': round(sortino_ratio, 2),
            'calmar_ratio': round(calmar_ratio, 2),
            'max_drawdown_pct': round(max_drawdown * 100, 2),
            'win_rate_pct': round(win_rate, 1),
            'profit_factor': round(profit_factor, 2),
            'skewness': round(skewness, 2),
            'kurtosis': round(kurtosis, 2),
            'annualized_return_pct': round(annualized_return * 100, 2),
            'annualized_volatility_pct': round(std_return * np.sqrt(periods_per_year) * 100, 2)
        }

    def garch_volatility_forecast(
        self,
        returns: pd.Series,
        horizon: int = 5
    ) -> Dict:
        """
        GARCH(1,1) volatility forecasting
        More sophisticated than simple historical volatility
        """
        if len(returns) < 100:
            return {'error': 'Insufficient data for GARCH model (need 100+ periods)'}

        try:
            # Simple GARCH(1,1) estimation
            # omega + alpha * eps_{t-1}^2 + beta * sigma_{t-1}^2

            # Remove mean
            returns_demeaned = returns - returns.mean()

            # Initialize parameters
            initial_var = returns_demeaned.var()

            # Long-term variance (omega)
            omega = initial_var * 0.01

            # GARCH coefficients (simplified estimation)
            alpha = 0.10  # Weight on past shocks
            beta = 0.85   # Weight on past variance

            # Ensure stationarity: alpha + beta < 1
            if alpha + beta >= 1:
                alpha = 0.08
                beta = 0.90

            # Forecast volatility
            current_var = returns_demeaned.iloc[-20:].var()
            forecast_vars = []

            for h in range(horizon):
                if h == 0:
                    next_var = omega + alpha * (returns_demeaned.iloc[-1]**2) + beta * current_var
                else:
                    # Multi-step ahead forecast
                    next_var = omega + (alpha + beta) * forecast_vars[-1]

                forecast_vars.append(next_var)
                current_var = next_var

            # Convert variance to volatility (standard deviation)
            forecast_vols = [np.sqrt(var) for var in forecast_vars]

            # Annualize (assuming hourly data)
            annualization_factor = np.sqrt(24 * 365)
            forecast_vols_annual = [vol * annualization_factor * 100 for vol in forecast_vols]

            return {
                'horizon': horizon,
                'current_volatility_pct': round(np.sqrt(current_var) * annualization_factor * 100, 2),
                'forecast_volatility_pct': [round(vol, 2) for vol in forecast_vols_annual],
                'average_forecast_vol_pct': round(np.mean(forecast_vols_annual), 2),
                'volatility_trend': 'INCREASING' if forecast_vols[-1] > forecast_vols[0] else 'DECREASING',
                'model': 'GARCH(1,1)'
            }

        except Exception as e:
            return {'error': f'GARCH model failed: {str(e)}'}

    def optimal_position_size_kelly(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        account_balance: float,
        max_position_pct: float = 0.20
    ) -> Dict:
        """
        Calculate optimal position size using Kelly Criterion
        More sophisticated than fixed percentage risk
        """
        # Validate inputs
        if not (0 < win_rate < 1):
            return {'error': 'Win rate must be between 0 and 1'}

        if avg_win <= 0 or avg_loss <= 0:
            return {'error': 'Average win and loss must be positive'}

        # Kelly formula: f* = (p * b - q) / b
        # where p = win rate, q = loss rate, b = win/loss ratio
        q = 1 - win_rate
        b = avg_win / avg_loss if avg_loss > 0 else 0

        kelly_pct = (win_rate * b - q) / b if b > 0 else 0

        # Limit Kelly percentage (full Kelly is too aggressive)
        # Use fractional Kelly (typically 25-50% of full Kelly)
        fractional_kelly_pct = kelly_pct * 0.25  # Conservative: 1/4 Kelly
        aggressive_kelly_pct = kelly_pct * 0.50  # Aggressive: 1/2 Kelly

        # Cap at maximum position size
        fractional_kelly_pct = min(fractional_kelly_pct, max_position_pct)
        aggressive_kelly_pct = min(aggressive_kelly_pct, max_position_pct)

        # Calculate dollar amounts
        conservative_size = account_balance * fractional_kelly_pct
        aggressive_size = account_balance * aggressive_kelly_pct

        return {
            'full_kelly_pct': round(kelly_pct * 100, 2),
            'conservative_pct': round(fractional_kelly_pct * 100, 2),
            'aggressive_pct': round(aggressive_kelly_pct * 100, 2),
            'conservative_dollar': round(conservative_size, 2),
            'aggressive_dollar': round(aggressive_size, 2),
            'recommendation': 'Use conservative sizing for stability',
            'warning': 'Full Kelly is too aggressive - use fractional Kelly' if kelly_pct > 0.25 else None
        }

    def correlation_analysis(
        self,
        returns1: pd.Series,
        returns2: pd.Series,
        window: int = 50
    ) -> Dict:
        """
        Analyze correlation between two assets
        Useful for portfolio diversification
        """
        if len(returns1) < window or len(returns2) < window:
            return {'error': f'Insufficient data for correlation analysis (need {window}+ periods)'}

        # Align series
        combined = pd.DataFrame({'asset1': returns1, 'asset2': returns2}).dropna()

        if len(combined) < window:
            return {'error': 'Insufficient overlapping data'}

        # Overall correlation
        pearson_corr = combined['asset1'].corr(combined['asset2'])

        # Rolling correlation
        rolling_corr = combined['asset1'].rolling(window).corr(combined['asset2'])

        # Current correlation
        current_corr = rolling_corr.iloc[-1]

        # Correlation stability
        corr_std = rolling_corr.std()

        # Statistical significance test
        n = len(combined)
        t_stat = pearson_corr * np.sqrt(n - 2) / np.sqrt(1 - pearson_corr**2)
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))

        return {
            'pearson_correlation': round(pearson_corr, 3),
            'current_correlation': round(current_corr, 3),
            'correlation_stability': round(corr_std, 3),
            'correlation_strength': self._interpret_correlation(pearson_corr),
            'statistically_significant': p_value < 0.05,
            'p_value': round(p_value, 4),
            'sample_size': n
        }

    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(corr)
        if abs_corr < 0.3:
            return 'WEAK'
        elif abs_corr < 0.7:
            return 'MODERATE'
        else:
            return 'STRONG'

    def hypothesis_test_signal(
        self,
        returns_after_signal: pd.Series,
        benchmark_returns: pd.Series
    ) -> Dict:
        """
        Statistical hypothesis testing for signal effectiveness
        Tests if signal generates statistically significant outperformance
        """
        if len(returns_after_signal) < 10:
            return {'error': 'Insufficient data for hypothesis test (need 10+ observations)'}

        # H0: Signal returns = Benchmark returns
        # H1: Signal returns != Benchmark returns

        # Align series
        combined = pd.DataFrame({
            'signal': returns_after_signal,
            'benchmark': benchmark_returns
        }).dropna()

        if len(combined) < 10:
            return {'error': 'Insufficient overlapping data'}

        # Paired t-test
        t_stat, p_value = stats.ttest_rel(combined['signal'], combined['benchmark'])

        # Calculate effect size (Cohen's d)
        diff = combined['signal'] - combined['benchmark']
        cohens_d = diff.mean() / diff.std() if diff.std() > 0 else 0

        # Average outperformance
        avg_outperformance = diff.mean() * 100

        return {
            't_statistic': round(t_stat, 3),
            'p_value': round(p_value, 4),
            'statistically_significant': p_value < 0.05,
            'cohens_d': round(cohens_d, 3),
            'effect_size': 'LARGE' if abs(cohens_d) > 0.8 else 'MEDIUM' if abs(cohens_d) > 0.5 else 'SMALL',
            'avg_outperformance_pct': round(avg_outperformance, 3),
            'sample_size': len(combined),
            'conclusion': 'Signal shows significant edge' if p_value < 0.05 and avg_outperformance > 0 else 'No significant edge detected'
        }
