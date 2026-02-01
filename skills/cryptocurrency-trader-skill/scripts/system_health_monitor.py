#!/usr/bin/env python3
"""
System Health Monitor

Monitors system components health, detects failures, and provides
graceful degradation strategies.

Component of Phase 4: Optimization (+0.1 reliability)
"""

import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status of a single component"""
    component_name: str
    status: HealthStatus
    last_check: str
    error_count: int = 0
    last_error: Optional[str] = None
    response_time_ms: float = 0.0
    success_rate: float = 1.0


class SystemHealthMonitor:
    """
    Monitors health of system components

    Responsibilities:
    - Track component health status
    - Detect component failures
    - Record error patterns
    - Provide graceful degradation strategies
    - Generate health reports

    Design: Single Responsibility, Circuit Breaker pattern
    """

    # Error thresholds for status determination
    ERROR_THRESHOLDS = {
        'degraded': 0.05,   # 5% error rate
        'failing': 0.15,    # 15% error rate
        'failed': 0.50      # 50% error rate
    }

    # Response time thresholds (ms)
    RESPONSE_TIME_THRESHOLDS = {
        'good': 1000,
        'acceptable': 5000,
        'slow': 10000
    }

    def __init__(
        self,
        check_interval_seconds: int = 60,
        history_size: int = 100
    ):
        """
        Initialize system health monitor

        Args:
            check_interval_seconds: Seconds between health checks
            history_size: Number of health records to keep per component
        """
        self.check_interval = check_interval_seconds
        self.history_size = history_size

        # Component health tracking
        self.components: Dict[str, ComponentHealth] = {}
        self.component_history: Dict[str, List[Dict]] = {}

        # Overall system health
        self.system_status = HealthStatus.HEALTHY
        self.last_full_check = None

        logger.info(f"Initialized SystemHealthMonitor (check interval: {check_interval_seconds}s)")

    def register_component(
        self,
        component_name: str,
        health_check_func: Optional[Callable] = None
    ) -> None:
        """
        Register a component for health monitoring

        Args:
            component_name: Name of component
            health_check_func: Optional function to check component health
        """
        if component_name not in self.components:
            self.components[component_name] = ComponentHealth(
                component_name=component_name,
                status=HealthStatus.UNKNOWN,
                last_check=datetime.now().isoformat(),
                error_count=0,
                success_rate=1.0
            )
            self.component_history[component_name] = []

            logger.info(f"Registered component: {component_name}")

    def record_component_call(
        self,
        component_name: str,
        success: bool,
        response_time_ms: float = 0.0,
        error: Optional[str] = None
    ) -> None:
        """
        Record a component call result

        Args:
            component_name: Name of component
            success: Whether call was successful
            response_time_ms: Response time in milliseconds
            error: Error message if failed
        """
        # Ensure component is registered
        if component_name not in self.components:
            self.register_component(component_name)

        component = self.components[component_name]

        # Record in history
        record = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'response_time_ms': response_time_ms,
            'error': error
        }

        history = self.component_history[component_name]
        history.append(record)

        # Keep only recent history
        if len(history) > self.history_size:
            history.pop(0)

        # Update component health
        if not success:
            component.error_count += 1
            component.last_error = error

        component.last_check = datetime.now().isoformat()
        component.response_time_ms = response_time_ms

        # Calculate success rate from history
        if history:
            successful_calls = sum(1 for r in history if r['success'])
            component.success_rate = successful_calls / len(history)

        # Update status based on success rate
        component.status = self._determine_status(component.success_rate, response_time_ms)

        # Log significant status changes
        if component.status in [HealthStatus.FAILING, HealthStatus.FAILED]:
            logger.warning(f"Component {component_name} status: {component.status.value} "
                         f"(success rate: {component.success_rate:.1%})")

    def _determine_status(
        self,
        success_rate: float,
        response_time_ms: float
    ) -> HealthStatus:
        """
        Determine health status from metrics

        Args:
            success_rate: Success rate (0-1)
            response_time_ms: Response time in milliseconds

        Returns:
            HealthStatus
        """
        error_rate = 1 - success_rate

        # Failed
        if error_rate >= self.ERROR_THRESHOLDS['failed']:
            return HealthStatus.FAILED

        # Failing
        if error_rate >= self.ERROR_THRESHOLDS['failing']:
            return HealthStatus.FAILING

        # Degraded (either by error rate or response time)
        if (error_rate >= self.ERROR_THRESHOLDS['degraded'] or
            response_time_ms > self.RESPONSE_TIME_THRESHOLDS['slow']):
            return HealthStatus.DEGRADED

        # Healthy
        return HealthStatus.HEALTHY

    def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """
        Get health status of a component

        Args:
            component_name: Name of component

        Returns:
            ComponentHealth or None if not registered
        """
        return self.components.get(component_name)

    def get_system_health(self) -> Dict:
        """
        Get overall system health status

        Returns:
            System health dictionary
        """
        if not self.components:
            return {
                'status': HealthStatus.UNKNOWN.value,
                'message': 'No components registered',
                'components': {}
            }

        # Count component statuses
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.FAILING: 0,
            HealthStatus.FAILED: 0,
            HealthStatus.UNKNOWN: 0
        }

        for component in self.components.values():
            status_counts[component.status] += 1

        # Determine overall system status
        if status_counts[HealthStatus.FAILED] > 0:
            system_status = HealthStatus.FAILED
        elif status_counts[HealthStatus.FAILING] > 0:
            system_status = HealthStatus.FAILING
        elif status_counts[HealthStatus.DEGRADED] > 0:
            system_status = HealthStatus.DEGRADED
        elif status_counts[HealthStatus.UNKNOWN] == len(self.components):
            system_status = HealthStatus.UNKNOWN
        else:
            system_status = HealthStatus.HEALTHY

        self.system_status = system_status
        self.last_full_check = datetime.now()

        # Component details
        component_details = {
            name: {
                'status': comp.status.value,
                'success_rate': comp.success_rate,
                'error_count': comp.error_count,
                'response_time_ms': comp.response_time_ms,
                'last_error': comp.last_error
            }
            for name, comp in self.components.items()
        }

        return {
            'status': system_status.value,
            'timestamp': datetime.now().isoformat(),
            'components_total': len(self.components),
            'components_healthy': status_counts[HealthStatus.HEALTHY],
            'components_degraded': status_counts[HealthStatus.DEGRADED],
            'components_failing': status_counts[HealthStatus.FAILING],
            'components_failed': status_counts[HealthStatus.FAILED],
            'component_details': component_details
        }

    def get_degradation_strategy(self) -> Dict:
        """
        Get strategy for graceful degradation based on component health

        Returns:
            Degradation strategy dictionary
        """
        system_health = self.get_system_health()
        status = HealthStatus(system_health['status'])

        strategy = {
            'status': status.value,
            'recommendations': [],
            'disabled_features': [],
            'fallback_options': []
        }

        # Analyze each component
        for name, comp in self.components.items():
            comp_status = comp.status

            if comp_status == HealthStatus.FAILED:
                strategy['recommendations'].append(
                    f"Component {name} has failed - disable dependent features"
                )
                strategy['disabled_features'].append(name)

                # Suggest fallbacks
                fallback = self._get_component_fallback(name)
                if fallback:
                    strategy['fallback_options'].append({
                        'failed_component': name,
                        'fallback': fallback
                    })

            elif comp_status == HealthStatus.FAILING:
                strategy['recommendations'].append(
                    f"Component {name} is failing - consider using fallback"
                )

            elif comp_status == HealthStatus.DEGRADED:
                strategy['recommendations'].append(
                    f"Component {name} is degraded - monitor closely"
                )

        # Overall recommendations
        if status == HealthStatus.FAILED:
            strategy['recommendations'].insert(0,
                "CRITICAL: System health failed - recommend emergency maintenance mode"
            )
        elif status == HealthStatus.FAILING:
            strategy['recommendations'].insert(0,
                "WARNING: System health failing - enable fallback modes"
            )
        elif status == HealthStatus.DEGRADED:
            strategy['recommendations'].insert(0,
                "CAUTION: System health degraded - increased monitoring recommended"
            )

        return strategy

    def _get_component_fallback(self, component_name: str) -> Optional[str]:
        """
        Get fallback option for a component

        Args:
            component_name: Name of failed component

        Returns:
            Fallback component name or strategy
        """
        fallbacks = {
            'MultiSourceDataAggregator': 'Use single exchange (Binance)',
            'BacktestValidator': 'Skip backtest validation, reduce confidence',
            'MarketContextAnalyzer': 'Use simplified BTC trend analysis',
            'CorrelationAnalyzer': 'Skip correlation analysis',
            'HistoricalAccuracyTracker': 'Use default accuracy priors',
            'AdaptiveParameterSelector': 'Use default timeframes (15m, 1h, 4h)'
        }

        return fallbacks.get(component_name)

    def reset_component(self, component_name: str) -> None:
        """
        Reset a component's health tracking

        Args:
            component_name: Name of component to reset
        """
        if component_name in self.components:
            self.components[component_name] = ComponentHealth(
                component_name=component_name,
                status=HealthStatus.UNKNOWN,
                last_check=datetime.now().isoformat(),
                error_count=0,
                success_rate=1.0
            )
            self.component_history[component_name] = []

            logger.info(f"Reset component health: {component_name}")

    def generate_health_report(self) -> str:
        """
        Generate human-readable health report

        Returns:
            Health report string
        """
        health = self.get_system_health()
        strategy = self.get_degradation_strategy()

        report_lines = [
            "=" * 60,
            "SYSTEM HEALTH REPORT",
            "=" * 60,
            f"Timestamp: {health['timestamp']}",
            f"Overall Status: {health['status'].upper()}",
            "",
            "Component Status:",
            "-" * 60
        ]

        for name, details in health['component_details'].items():
            status_symbol = {
                'healthy': '✓',
                'degraded': '⚠',
                'failing': '⚠⚠',
                'failed': '✗',
                'unknown': '?'
            }.get(details['status'], '?')

            report_lines.append(
                f"{status_symbol} {name:30s} {details['status']:10s} "
                f"Success: {details['success_rate']:5.1%} "
                f"RT: {details['response_time_ms']:6.0f}ms"
            )

        if strategy['recommendations']:
            report_lines.extend([
                "",
                "Recommendations:",
                "-" * 60
            ])
            for i, rec in enumerate(strategy['recommendations'], 1):
                report_lines.append(f"{i}. {rec}")

        if strategy['fallback_options']:
            report_lines.extend([
                "",
                "Fallback Options:",
                "-" * 60
            ])
            for option in strategy['fallback_options']:
                report_lines.append(
                    f"• {option['failed_component']} → {option['fallback']}"
                )

        report_lines.append("=" * 60)

        return "\n".join(report_lines)

    def export_health_data(self) -> Dict:
        """
        Export all health data for analysis

        Returns:
            Complete health data dictionary
        """
        return {
            'system_health': self.get_system_health(),
            'components': {
                name: asdict(comp)
                for name, comp in self.components.items()
            },
            'history': self.component_history,
            'degradation_strategy': self.get_degradation_strategy()
        }


# Convenience functions
def create_health_monitor() -> SystemHealthMonitor:
    """
    Factory function to create SystemHealthMonitor

    Returns:
        SystemHealthMonitor instance
    """
    return SystemHealthMonitor()


def check_system_health(monitor: SystemHealthMonitor) -> Dict:
    """
    Quick system health check

    Args:
        monitor: SystemHealthMonitor instance

    Returns:
        System health dictionary
    """
    return monitor.get_system_health()
