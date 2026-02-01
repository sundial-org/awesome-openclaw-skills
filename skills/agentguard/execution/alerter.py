#!/usr/bin/env python3
"""
AgentGuard - Alert Dispatch System
Sends security alerts through configured channels.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

CONFIG_DIR = Path.home() / ".agentguard"
ALERTS_DIR = CONFIG_DIR / "alerts"


class AlertSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    TELEGRAM = "telegram"
    DISCORD = "discord"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CONSOLE = "console"


@dataclass
class Alert:
    """Security alert."""
    id: str
    timestamp: str
    severity: str
    title: str
    description: str
    details: Dict
    recommendation: str
    acknowledged: bool = False
    acknowledged_at: Optional[str] = None
    dispatched_to: List[str] = None


class AlertDispatcher:
    """Dispatches alerts to configured channels."""
    
    SEVERITY_ICONS = {
        "info": "🔵",
        "low": "🟢",
        "medium": "🟡",
        "high": "🟠",
        "critical": "🔴"
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or self._load_config()
        self.cooldown_tracker = {}
        
    def _load_config(self) -> Dict:
        """Load alert configuration."""
        config_file = CONFIG_DIR / "config.yaml"
        
        # Default config
        default = {
            "channels": ["console"],
            "cooldown_minutes": 15,
            "min_severity": "low",
            "batch_alerts": True,
            "telegram": {
                "enabled": False,
                "chat_id": None
            },
            "discord": {
                "enabled": False,
                "webhook_url": None
            },
            "email": {
                "enabled": False,
                "to": None
            }
        }
        
        if config_file.exists():
            try:
                import yaml
                with open(config_file) as f:
                    loaded = yaml.safe_load(f)
                    if loaded and "alerts" in loaded:
                        return {**default, **loaded["alerts"]}
            except ImportError:
                pass
        
        return default
    
    def _severity_level(self, severity: str) -> int:
        """Convert severity to numeric level."""
        levels = {
            "info": 0,
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }
        return levels.get(severity.lower(), 0)
    
    def _should_send(self, alert: Alert) -> bool:
        """Check if alert should be sent based on cooldown and severity."""
        # Check severity threshold
        min_level = self._severity_level(self.config.get("min_severity", "low"))
        alert_level = self._severity_level(alert.severity)
        
        if alert_level < min_level:
            return False
        
        # Check cooldown (except for critical)
        if alert.severity != "critical":
            cooldown = self.config.get("cooldown_minutes", 15)
            key = f"{alert.title}:{alert.severity}"
            
            last_sent = self.cooldown_tracker.get(key)
            if last_sent:
                elapsed = (datetime.now() - last_sent).total_seconds() / 60
                if elapsed < cooldown:
                    return False
            
            self.cooldown_tracker[key] = datetime.now()
        
        return True
    
    def format_alert(self, alert: Alert, format_type: str = "text") -> str:
        """Format alert for display."""
        icon = self.SEVERITY_ICONS.get(alert.severity, "⚪")
        
        if format_type == "text":
            return f"""
{icon} **AgentGuard Alert** [{alert.severity.upper()}]

**{alert.title}**

{alert.description}

**Details:**
{json.dumps(alert.details, indent=2)}

**Recommendation:**
{alert.recommendation}

_Time: {alert.timestamp}_
""".strip()
        
        elif format_type == "compact":
            return f"{icon} [{alert.severity.upper()}] {alert.title}: {alert.description}"
        
        elif format_type == "json":
            return json.dumps(asdict(alert), indent=2)
        
        return str(alert)
    
    def dispatch_console(self, alert: Alert):
        """Print alert to console."""
        print(self.format_alert(alert, "text"))
        print("-" * 50)
    
    def dispatch_telegram(self, alert: Alert) -> bool:
        """Send alert via Telegram (uses Clawdbot's message tool)."""
        # This would integrate with Clawdbot's message tool
        # For now, we output the command that should be run
        message = self.format_alert(alert, "text")
        
        print(f"[Telegram Alert] Would send to Telegram:")
        print(message)
        
        # In actual usage, this would call:
        # message --action send --target <chat_id> --message "<message>"
        return True
    
    def dispatch_discord(self, alert: Alert) -> bool:
        """Send alert via Discord webhook."""
        webhook_url = self.config.get("discord", {}).get("webhook_url")
        if not webhook_url:
            return False
        
        # Format for Discord embed
        color_map = {
            "info": 0x3498db,
            "low": 0x2ecc71,
            "medium": 0xf1c40f,
            "high": 0xe67e22,
            "critical": 0xe74c3c
        }
        
        embed = {
            "title": f"{self.SEVERITY_ICONS.get(alert.severity)} {alert.title}",
            "description": alert.description,
            "color": color_map.get(alert.severity, 0x95a5a6),
            "fields": [
                {"name": "Severity", "value": alert.severity.upper(), "inline": True},
                {"name": "Time", "value": alert.timestamp, "inline": True},
                {"name": "Recommendation", "value": alert.recommendation}
            ],
            "footer": {"text": "AgentGuard Security Monitor"}
        }
        
        print(f"[Discord Alert] Would POST to webhook:")
        print(json.dumps({"embeds": [embed]}, indent=2))
        
        return True
    
    def dispatch_webhook(self, alert: Alert, webhook_url: str) -> bool:
        """Send alert to a generic webhook."""
        payload = {
            "source": "agentguard",
            "alert": asdict(alert)
        }
        
        print(f"[Webhook Alert] Would POST to {webhook_url}:")
        print(json.dumps(payload, indent=2))
        
        return True
    
    def dispatch(self, alert: Alert) -> List[str]:
        """Dispatch alert to all configured channels."""
        if not self._should_send(alert):
            return []
        
        dispatched = []
        channels = self.config.get("channels", ["console"])
        
        for channel in channels:
            try:
                if channel == "console":
                    self.dispatch_console(alert)
                    dispatched.append("console")
                elif channel == "telegram":
                    if self.dispatch_telegram(alert):
                        dispatched.append("telegram")
                elif channel == "discord":
                    if self.dispatch_discord(alert):
                        dispatched.append("discord")
                elif channel == "webhook":
                    webhook_url = self.config.get("webhook_url")
                    if webhook_url and self.dispatch_webhook(alert, webhook_url):
                        dispatched.append("webhook")
            except Exception as e:
                print(f"Error dispatching to {channel}: {e}")
        
        # Save alert record
        self._save_alert(alert, dispatched)
        
        return dispatched
    
    def _save_alert(self, alert: Alert, dispatched_to: List[str]):
        """Save alert to disk."""
        ALERTS_DIR.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        alert_file = ALERTS_DIR / f"{today}.json"
        
        existing = []
        if alert_file.exists():
            with open(alert_file) as f:
                existing = json.load(f)
        
        alert_data = asdict(alert)
        alert_data["dispatched_to"] = dispatched_to
        existing.append(alert_data)
        
        with open(alert_file, "w") as f:
            json.dump(existing, f, indent=2)
    
    def get_alerts(self, date: Optional[str] = None, 
                   severity: Optional[str] = None,
                   acknowledged: Optional[bool] = None,
                   limit: int = 100) -> List[Dict]:
        """Retrieve alerts with optional filters."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        alert_file = ALERTS_DIR / f"{date}.json"
        
        if not alert_file.exists():
            return []
        
        with open(alert_file) as f:
            alerts = json.load(f)
        
        # Apply filters
        if severity:
            alerts = [a for a in alerts if a.get("severity") == severity]
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a.get("acknowledged") == acknowledged]
        
        return alerts[:limit]
    
    def acknowledge_alert(self, alert_id: str, date: Optional[str] = None) -> bool:
        """Mark an alert as acknowledged."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        alert_file = ALERTS_DIR / f"{date}.json"
        
        if not alert_file.exists():
            return False
        
        with open(alert_file) as f:
            alerts = json.load(f)
        
        for alert in alerts:
            if alert.get("id") == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().isoformat()
                
                with open(alert_file, "w") as f:
                    json.dump(alerts, f, indent=2)
                return True
        
        return False
    
    def get_unacknowledged_count(self, days: int = 7) -> Dict[str, int]:
        """Get count of unacknowledged alerts by severity."""
        counts = {"info": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            alerts = self.get_alerts(date, acknowledged=False, limit=1000)
            for alert in alerts:
                severity = alert.get("severity", "info")
                counts[severity] = counts.get(severity, 0) + 1
        
        return counts


def create_alert(severity: str, title: str, description: str,
                 details: Dict, recommendation: str) -> Alert:
    """Factory function to create alerts."""
    import uuid
    
    return Alert(
        id=str(uuid.uuid4())[:8],
        timestamp=datetime.now().isoformat(),
        severity=severity,
        title=title,
        description=description,
        details=details,
        recommendation=recommendation
    )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AgentGuard Alert Dispatcher")
    parser.add_argument("command", choices=["send", "list", "ack", "stats"],
                        help="Command to execute")
    parser.add_argument("--severity", choices=["info", "low", "medium", "high", "critical"],
                        default="medium", help="Alert severity")
    parser.add_argument("--title", type=str, help="Alert title")
    parser.add_argument("--description", type=str, help="Alert description")
    parser.add_argument("--details", type=str, help="JSON details")
    parser.add_argument("--recommendation", type=str, help="Recommendation")
    parser.add_argument("--date", type=str, help="Date for listing (YYYY-MM-DD)")
    parser.add_argument("--alert-id", type=str, help="Alert ID for acknowledgment")
    parser.add_argument("--limit", type=int, default=100, help="Max alerts to return")
    
    args = parser.parse_args()
    
    dispatcher = AlertDispatcher()
    
    if args.command == "send":
        if not args.title or not args.description:
            print("Error: --title and --description required")
            return
        
        details = {}
        if args.details:
            details = json.loads(args.details)
        
        alert = create_alert(
            severity=args.severity,
            title=args.title,
            description=args.description,
            details=details,
            recommendation=args.recommendation or "Review this alert and take appropriate action."
        )
        
        dispatched = dispatcher.dispatch(alert)
        print(f"Alert {alert.id} dispatched to: {', '.join(dispatched) or 'none (filtered)'}")
        
    elif args.command == "list":
        alerts = dispatcher.get_alerts(args.date, limit=args.limit)
        for alert in alerts:
            icon = AlertDispatcher.SEVERITY_ICONS.get(alert.get("severity"), "⚪")
            ack = "✓" if alert.get("acknowledged") else "○"
            print(f"{ack} {icon} [{alert.get('id')}] {alert.get('title')}")
        print(f"\nTotal: {len(alerts)} alerts")
        
    elif args.command == "ack":
        if not args.alert_id:
            print("Error: --alert-id required")
            return
        
        if dispatcher.acknowledge_alert(args.alert_id, args.date):
            print(f"Alert {args.alert_id} acknowledged")
        else:
            print(f"Alert {args.alert_id} not found")
            
    elif args.command == "stats":
        counts = dispatcher.get_unacknowledged_count()
        print("Unacknowledged alerts (last 7 days):")
        for severity, count in counts.items():
            icon = AlertDispatcher.SEVERITY_ICONS.get(severity, "⚪")
            print(f"  {icon} {severity.upper()}: {count}")


if __name__ == "__main__":
    main()
