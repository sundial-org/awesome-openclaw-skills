#!/usr/bin/env python3
"""
AgentGuard - Anomaly Detection Engine
Detects suspicious patterns and behavioral anomalies.
"""

import os
import json
import math
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum

CONFIG_DIR = Path.home() / ".agentguard"
BASELINE_DIR = CONFIG_DIR / "baselines"
ALERTS_DIR = CONFIG_DIR / "alerts"


class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    timestamp: str
    anomaly_type: str
    severity: Severity
    description: str
    details: Dict
    recommendation: str


@dataclass
class Baseline:
    """Behavioral baseline for comparison."""
    created_at: str
    updated_at: str
    learning_period_hours: int
    file_access_patterns: Dict
    api_call_patterns: Dict
    time_patterns: Dict
    volume_thresholds: Dict


class BaselineManager:
    """Manages behavioral baselines."""
    
    def __init__(self):
        self.baseline_file = BASELINE_DIR / "behavior_model.json"
        self.baseline = self._load_baseline()
        
    def _load_baseline(self) -> Optional[Baseline]:
        """Load existing baseline from disk."""
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file) as f:
                    data = json.load(f)
                    return Baseline(**data)
            except (json.JSONDecodeError, TypeError):
                return None
        return None
    
    def _save_baseline(self):
        """Save baseline to disk."""
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        if self.baseline:
            with open(self.baseline_file, "w") as f:
                data = asdict(self.baseline)
                data["severity"] = data.get("severity", "medium")  # Serialize enum
                json.dump(data, f, indent=2, default=str)
    
    def create_baseline(self, learning_hours: int = 24) -> Baseline:
        """Create a new baseline from observed behavior."""
        now = datetime.now().isoformat()
        self.baseline = Baseline(
            created_at=now,
            updated_at=now,
            learning_period_hours=learning_hours,
            file_access_patterns={
                "hourly_counts": defaultdict(list),
                "common_paths": defaultdict(int),
                "sensitive_access_rate": 0.0
            },
            api_call_patterns={
                "hourly_counts": defaultdict(list),
                "common_domains": defaultdict(int),
                "untrusted_rate": 0.0
            },
            time_patterns={
                "active_hours": list(range(8, 22)),  # 8 AM - 10 PM default
                "weekend_activity": False
            },
            volume_thresholds={
                "file_ops_per_hour": 100,
                "api_calls_per_hour": 50,
                "sensitive_access_per_day": 5
            }
        )
        self._save_baseline()
        return self.baseline
    
    def update_baseline(self, events: List[Dict]):
        """Update baseline with new observations."""
        if not self.baseline:
            self.create_baseline()
        
        self.baseline.updated_at = datetime.now().isoformat()
        self._save_baseline()


class AnomalyDetector:
    """Detects anomalies based on behavioral patterns."""
    
    def __init__(self, sensitivity: str = "medium"):
        self.sensitivity = sensitivity
        self.baseline_manager = BaselineManager()
        self.thresholds = self._get_thresholds()
        
    def _get_thresholds(self) -> Dict:
        """Get detection thresholds based on sensitivity."""
        base = {
            "low": {
                "volume_multiplier": 3.0,
                "sensitive_access_limit": 10,
                "untrusted_api_limit": 20,
                "bulk_read_threshold": 50,
                "new_domain_alert": False
            },
            "medium": {
                "volume_multiplier": 2.0,
                "sensitive_access_limit": 5,
                "untrusted_api_limit": 10,
                "bulk_read_threshold": 25,
                "new_domain_alert": True
            },
            "high": {
                "volume_multiplier": 1.5,
                "sensitive_access_limit": 2,
                "untrusted_api_limit": 5,
                "bulk_read_threshold": 10,
                "new_domain_alert": True
            }
        }
        return base.get(self.sensitivity, base["medium"])
    
    def detect_bulk_file_access(self, file_events: List[Dict]) -> Optional[Anomaly]:
        """Detect bulk file reading patterns (potential exfiltration)."""
        # Count reads in last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_reads = [
            e for e in file_events
            if e.get("event_type") == "accessed" and
            datetime.fromisoformat(e.get("timestamp", "1970-01-01")) > one_hour_ago
        ]
        
        threshold = self.thresholds["bulk_read_threshold"]
        if len(recent_reads) > threshold:
            return Anomaly(
                timestamp=datetime.now().isoformat(),
                anomaly_type="bulk_file_access",
                severity=Severity.HIGH,
                description=f"Detected {len(recent_reads)} file reads in the last hour (threshold: {threshold})",
                details={
                    "count": len(recent_reads),
                    "threshold": threshold,
                    "sample_paths": [e.get("path") for e in recent_reads[:5]]
                },
                recommendation="Review file access patterns. This may indicate data exfiltration."
            )
        return None
    
    def detect_sensitive_access(self, file_events: List[Dict]) -> Optional[Anomaly]:
        """Detect access to sensitive files."""
        sensitive_events = [e for e in file_events if e.get("is_sensitive")]
        
        limit = self.thresholds["sensitive_access_limit"]
        if len(sensitive_events) > limit:
            return Anomaly(
                timestamp=datetime.now().isoformat(),
                anomaly_type="sensitive_file_access",
                severity=Severity.HIGH,
                description=f"Detected {len(sensitive_events)} accesses to sensitive files (limit: {limit})",
                details={
                    "count": len(sensitive_events),
                    "paths": [e.get("path") for e in sensitive_events]
                },
                recommendation="Verify these accesses are authorized. Consider restricting permissions."
            )
        
        # Single sensitive access is still noteworthy
        if sensitive_events:
            return Anomaly(
                timestamp=datetime.now().isoformat(),
                anomaly_type="sensitive_file_access",
                severity=Severity.MEDIUM,
                description=f"Access to sensitive file: {sensitive_events[0].get('path')}",
                details={
                    "path": sensitive_events[0].get("path"),
                    "event_type": sensitive_events[0].get("event_type")
                },
                recommendation="Ensure this access was intentional and authorized."
            )
        
        return None
    
    def detect_untrusted_api(self, api_events: List[Dict]) -> Optional[Anomaly]:
        """Detect calls to untrusted API endpoints."""
        untrusted = [e for e in api_events if not e.get("is_trusted")]
        
        limit = self.thresholds["untrusted_api_limit"]
        if len(untrusted) > limit:
            domains = list(set(e.get("domain") for e in untrusted))
            return Anomaly(
                timestamp=datetime.now().isoformat(),
                anomaly_type="untrusted_api_calls",
                severity=Severity.HIGH,
                description=f"Detected {len(untrusted)} calls to untrusted APIs",
                details={
                    "count": len(untrusted),
                    "domains": domains
                },
                recommendation="Review these API calls. Add trusted domains or block suspicious ones."
            )
        
        # Alert on new domains if sensitivity allows
        if untrusted and self.thresholds["new_domain_alert"]:
            return Anomaly(
                timestamp=datetime.now().isoformat(),
                anomaly_type="new_api_destination",
                severity=Severity.LOW,
                description=f"API call to untrusted domain: {untrusted[0].get('domain')}",
                details={
                    "domain": untrusted[0].get("domain"),
                    "url": untrusted[0].get("url"),
                    "method": untrusted[0].get("method")
                },
                recommendation="Verify this is a legitimate destination. Consider adding to trusted list."
            )
        
        return None
    
    def detect_credential_exposure(self, api_events: List[Dict]) -> Optional[Anomaly]:
        """Detect potential credential exposure in API payloads."""
        suspicious_keywords = [
            "password", "secret", "token", "apikey", "api_key",
            "authorization", "bearer", "credential"
        ]
        
        for event in api_events:
            url = event.get("url", "").lower()
            # Check if sensitive data might be in URL (very bad)
            for keyword in suspicious_keywords:
                if keyword in url:
                    return Anomaly(
                        timestamp=datetime.now().isoformat(),
                        anomaly_type="credential_exposure",
                        severity=Severity.CRITICAL,
                        description=f"Potential credential in URL: {keyword} detected",
                        details={
                            "url": event.get("url")[:100] + "...",  # Truncate for safety
                            "domain": event.get("domain"),
                            "method": event.get("method")
                        },
                        recommendation="URGENT: Review this request. Credentials should never be in URLs."
                    )
        return None
    
    def detect_time_anomaly(self, events: List[Dict]) -> Optional[Anomaly]:
        """Detect activity outside normal hours."""
        if not self.baseline_manager.baseline:
            return None
        
        active_hours = self.baseline_manager.baseline.time_patterns.get("active_hours", [])
        current_hour = datetime.now().hour
        
        if current_hour not in active_hours and events:
            return Anomaly(
                timestamp=datetime.now().isoformat(),
                anomaly_type="off_hours_activity",
                severity=Severity.LOW,
                description=f"Agent activity detected outside normal hours (hour: {current_hour})",
                details={
                    "current_hour": current_hour,
                    "normal_hours": active_hours,
                    "event_count": len(events)
                },
                recommendation="Verify this activity is expected. May be scheduled task or anomaly."
            )
        return None
    
    def detect_exfiltration_pattern(self, file_events: List[Dict], 
                                     api_events: List[Dict]) -> Optional[Anomaly]:
        """Detect potential data exfiltration (bulk read followed by network calls)."""
        # Look for pattern: many file reads followed by large API request
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        recent_reads = [
            e for e in file_events
            if datetime.fromisoformat(e.get("timestamp", "1970-01-01")) > one_hour_ago
        ]
        
        large_requests = [
            e for e in api_events
            if e.get("request_size", 0) > 10000 and  # > 10KB
            datetime.fromisoformat(e.get("timestamp", "1970-01-01")) > one_hour_ago
        ]
        
        if len(recent_reads) > 20 and large_requests:
            return Anomaly(
                timestamp=datetime.now().isoformat(),
                anomaly_type="potential_exfiltration",
                severity=Severity.CRITICAL,
                description="Pattern detected: bulk file reads followed by large outbound request",
                details={
                    "file_reads": len(recent_reads),
                    "large_requests": len(large_requests),
                    "destinations": [e.get("domain") for e in large_requests]
                },
                recommendation="URGENT: Investigate immediately. This pattern suggests data exfiltration."
            )
        return None
    
    def run_all_detections(self, file_events: List[Dict], 
                           api_events: List[Dict]) -> List[Anomaly]:
        """Run all detection methods and return anomalies."""
        anomalies = []
        
        detections = [
            self.detect_bulk_file_access(file_events),
            self.detect_sensitive_access(file_events),
            self.detect_untrusted_api(api_events),
            self.detect_credential_exposure(api_events),
            self.detect_time_anomaly(file_events + api_events),
            self.detect_exfiltration_pattern(file_events, api_events),
        ]
        
        for anomaly in detections:
            if anomaly:
                anomalies.append(anomaly)
        
        return anomalies


def save_anomalies(anomalies: List[Anomaly]):
    """Save detected anomalies to disk."""
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    alert_file = ALERTS_DIR / f"{today}.json"
    
    existing = []
    if alert_file.exists():
        with open(alert_file) as f:
            existing = json.load(f)
    
    for anomaly in anomalies:
        data = asdict(anomaly)
        data["severity"] = anomaly.severity.value  # Convert enum to string
        existing.append(data)
    
    with open(alert_file, "w") as f:
        json.dump(existing, f, indent=2)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AgentGuard Anomaly Detector")
    parser.add_argument("command", choices=["detect", "baseline", "status"],
                        help="Command to execute")
    parser.add_argument("--sensitivity", choices=["low", "medium", "high"],
                        default="medium", help="Detection sensitivity")
    parser.add_argument("--input", type=str, help="Input events file (JSON)")
    
    args = parser.parse_args()
    
    detector = AnomalyDetector(sensitivity=args.sensitivity)
    
    if args.command == "baseline":
        baseline = detector.baseline_manager.create_baseline()
        print(f"Baseline created at {baseline.created_at}")
        
    elif args.command == "detect":
        file_events = []
        api_events = []
        
        if args.input:
            with open(args.input) as f:
                data = json.load(f)
                file_events = data.get("file_events", [])
                api_events = data.get("api_events", [])
        
        anomalies = detector.run_all_detections(file_events, api_events)
        
        if anomalies:
            save_anomalies(anomalies)
            for a in anomalies:
                severity_icon = {
                    Severity.INFO: "🔵",
                    Severity.LOW: "🟢",
                    Severity.MEDIUM: "🟡",
                    Severity.HIGH: "🟠",
                    Severity.CRITICAL: "🔴"
                }.get(a.severity, "⚪")
                print(f"{severity_icon} [{a.severity.value.upper()}] {a.description}")
        else:
            print("✅ No anomalies detected")
            
    elif args.command == "status":
        baseline = detector.baseline_manager.baseline
        if baseline:
            print(f"Baseline: Created {baseline.created_at}")
            print(f"Last updated: {baseline.updated_at}")
            print(f"Sensitivity: {args.sensitivity}")
        else:
            print("No baseline established. Run 'baseline' command first.")


if __name__ == "__main__":
    main()
