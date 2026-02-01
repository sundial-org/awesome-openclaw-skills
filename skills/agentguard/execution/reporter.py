#!/usr/bin/env python3
"""
AgentGuard - Security Report Generator
Generates comprehensive security reports for daily, weekly, or monthly periods.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

CONFIG_DIR = Path.home() / ".agentguard"
LOG_DIR = CONFIG_DIR / "logs"
ALERTS_DIR = CONFIG_DIR / "alerts"
REPORTS_DIR = CONFIG_DIR / "reports"


class ReportGenerator:
    """Generates security reports."""
    
    def __init__(self):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_date_range(self, period: str) -> Tuple[datetime, datetime]:
        """Get date range for report period."""
        end = datetime.now()
        
        if period == "daily":
            start = end - timedelta(days=1)
        elif period == "weekly":
            start = end - timedelta(weeks=1)
        elif period == "monthly":
            start = end - timedelta(days=30)
        else:
            start = end - timedelta(days=1)
        
        return start, end
    
    def _load_logs(self, category: str, start: datetime, end: datetime) -> List[Dict]:
        """Load logs for a category within date range."""
        logs = []
        current = start
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            log_file = LOG_DIR / category / f"{date_str}.jsonl"
            
            if log_file.exists():
                with open(log_file) as f:
                    for line in f:
                        if line.strip():
                            try:
                                logs.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
            
            current += timedelta(days=1)
        
        return logs
    
    def _load_alerts(self, start: datetime, end: datetime) -> List[Dict]:
        """Load alerts within date range."""
        alerts = []
        current = start
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            alert_file = ALERTS_DIR / f"{date_str}.json"
            
            if alert_file.exists():
                with open(alert_file) as f:
                    alerts.extend(json.load(f))
            
            current += timedelta(days=1)
        
        return alerts
    
    def _analyze_file_access(self, logs: List[Dict]) -> Dict:
        """Analyze file access patterns."""
        analysis = {
            "total_operations": len(logs),
            "by_type": defaultdict(int),
            "top_files": defaultdict(int),
            "sensitive_accesses": [],
            "hourly_distribution": defaultdict(int),
            "extensions": defaultdict(int)
        }
        
        for log in logs:
            action = log.get("action", "unknown")
            analysis["by_type"][action] += 1
            
            details = log.get("details", {})
            path = details.get("path", "")
            
            if path:
                analysis["top_files"][path] += 1
                
                ext = details.get("extension", "")
                if ext:
                    analysis["extensions"][ext] += 1
            
            # Check for sensitive access
            if "sensitive" in path.lower() or any(
                s in path.lower() for s in [".env", "secret", "password", "key"]
            ):
                analysis["sensitive_accesses"].append({
                    "path": path,
                    "action": action,
                    "timestamp": log.get("timestamp")
                })
            
            # Hourly distribution
            try:
                ts = datetime.fromisoformat(log.get("timestamp", ""))
                analysis["hourly_distribution"][ts.hour] += 1
            except ValueError:
                pass
        
        # Convert to regular dicts and sort
        analysis["by_type"] = dict(analysis["by_type"])
        analysis["extensions"] = dict(analysis["extensions"])
        analysis["hourly_distribution"] = dict(sorted(analysis["hourly_distribution"].items()))
        
        # Top 10 files
        sorted_files = sorted(analysis["top_files"].items(), key=lambda x: x[1], reverse=True)
        analysis["top_files"] = dict(sorted_files[:10])
        
        return analysis
    
    def _analyze_api_calls(self, logs: List[Dict]) -> Dict:
        """Analyze API call patterns."""
        analysis = {
            "total_calls": len(logs),
            "by_method": defaultdict(int),
            "by_domain": defaultdict(int),
            "by_status": defaultdict(int),
            "untrusted_domains": set(),
            "large_requests": [],
            "errors": []
        }
        
        for log in logs:
            method = log.get("action", "UNKNOWN")
            analysis["by_method"][method] += 1
            
            details = log.get("details", {})
            domain = details.get("domain", "unknown")
            analysis["by_domain"][domain] += 1
            
            status = details.get("status_code")
            if status:
                analysis["by_status"][str(status)] += 1
                if status >= 400:
                    analysis["errors"].append({
                        "url": details.get("url", "")[:100],
                        "status": status,
                        "timestamp": log.get("timestamp")
                    })
            
            # Check for large requests
            req_size = details.get("request_size", 0)
            if req_size and req_size > 10000:  # > 10KB
                analysis["large_requests"].append({
                    "domain": domain,
                    "size": req_size,
                    "timestamp": log.get("timestamp")
                })
        
        # Convert to regular dicts
        analysis["by_method"] = dict(analysis["by_method"])
        analysis["by_domain"] = dict(sorted(
            analysis["by_domain"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:15])
        analysis["by_status"] = dict(analysis["by_status"])
        analysis["untrusted_domains"] = list(analysis["untrusted_domains"])
        
        return analysis
    
    def _analyze_communications(self, logs: List[Dict]) -> Dict:
        """Analyze external communications."""
        analysis = {
            "total_communications": len(logs),
            "by_type": defaultdict(int),
            "destinations": defaultdict(int),
            "timeline": []
        }
        
        for log in logs:
            comm_type = log.get("action", "unknown")
            analysis["by_type"][comm_type] += 1
            
            details = log.get("details", {})
            dest = details.get("destination", "unknown")
            analysis["destinations"][dest] += 1
            
            analysis["timeline"].append({
                "type": comm_type,
                "destination": dest,
                "timestamp": log.get("timestamp")
            })
        
        analysis["by_type"] = dict(analysis["by_type"])
        analysis["destinations"] = dict(sorted(
            analysis["destinations"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
        
        return analysis
    
    def _analyze_alerts(self, alerts: List[Dict]) -> Dict:
        """Analyze alerts."""
        analysis = {
            "total_alerts": len(alerts),
            "by_severity": defaultdict(int),
            "by_type": defaultdict(int),
            "acknowledged": 0,
            "unacknowledged": 0,
            "critical_alerts": [],
            "high_alerts": []
        }
        
        for alert in alerts:
            severity = alert.get("severity", "info")
            analysis["by_severity"][severity] += 1
            
            alert_type = alert.get("title", "Unknown")
            analysis["by_type"][alert_type] += 1
            
            if alert.get("acknowledged"):
                analysis["acknowledged"] += 1
            else:
                analysis["unacknowledged"] += 1
            
            if severity == "critical":
                analysis["critical_alerts"].append(alert)
            elif severity == "high":
                analysis["high_alerts"].append(alert)
        
        analysis["by_severity"] = dict(analysis["by_severity"])
        analysis["by_type"] = dict(analysis["by_type"])
        
        return analysis
    
    def _calculate_threat_level(self, alert_analysis: Dict, 
                                 file_analysis: Dict,
                                 api_analysis: Dict) -> Tuple[str, str]:
        """Calculate overall threat level."""
        score = 0
        reasons = []
        
        # Critical alerts = immediate concern
        critical_count = alert_analysis["by_severity"].get("critical", 0)
        high_count = alert_analysis["by_severity"].get("high", 0)
        
        if critical_count > 0:
            score += 40
            reasons.append(f"{critical_count} critical alerts")
        
        if high_count > 0:
            score += high_count * 10
            reasons.append(f"{high_count} high-severity alerts")
        
        # Sensitive file access
        sensitive_count = len(file_analysis.get("sensitive_accesses", []))
        if sensitive_count > 5:
            score += 20
            reasons.append(f"{sensitive_count} sensitive file accesses")
        elif sensitive_count > 0:
            score += 10
        
        # Unacknowledged alerts
        unack = alert_analysis.get("unacknowledged", 0)
        if unack > 10:
            score += 15
            reasons.append(f"{unack} unacknowledged alerts")
        
        # Error rate in API calls
        error_count = len(api_analysis.get("errors", []))
        total_api = api_analysis.get("total_calls", 1)
        error_rate = error_count / max(total_api, 1)
        if error_rate > 0.1:  # >10% error rate
            score += 10
            reasons.append(f"High API error rate ({error_rate:.1%})")
        
        # Determine level
        if score >= 50:
            level = "CRITICAL"
            color = "🔴"
        elif score >= 30:
            level = "HIGH"
            color = "🟠"
        elif score >= 15:
            level = "MEDIUM"
            color = "🟡"
        elif score >= 5:
            level = "LOW"
            color = "🟢"
        else:
            level = "MINIMAL"
            color = "🔵"
        
        reason_text = "; ".join(reasons) if reasons else "No significant issues detected"
        
        return f"{color} {level}", reason_text
    
    def _generate_recommendations(self, alert_analysis: Dict,
                                    file_analysis: Dict,
                                    api_analysis: Dict) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        # Based on alerts
        if alert_analysis.get("unacknowledged", 0) > 5:
            recommendations.append(
                "📋 **Review unacknowledged alerts** - "
                f"{alert_analysis['unacknowledged']} alerts need attention"
            )
        
        if alert_analysis["by_severity"].get("critical", 0) > 0:
            recommendations.append(
                "🚨 **URGENT: Address critical alerts immediately** - "
                "These require immediate investigation"
            )
        
        # Based on file access
        if len(file_analysis.get("sensitive_accesses", [])) > 0:
            recommendations.append(
                "🔐 **Review sensitive file accesses** - "
                "Verify all credential file accesses were authorized"
            )
        
        # Based on API calls
        if len(api_analysis.get("errors", [])) > 10:
            recommendations.append(
                "⚠️ **Investigate API errors** - "
                "High error rate may indicate configuration issues or attacks"
            )
        
        if len(api_analysis.get("large_requests", [])) > 5:
            recommendations.append(
                "📤 **Review large outbound requests** - "
                "Verify large data transfers are expected"
            )
        
        if not recommendations:
            recommendations.append(
                "✅ **All clear** - No immediate actions required. "
                "Continue monitoring and maintain good security hygiene."
            )
        
        return recommendations
    
    def generate_report(self, period: str = "daily") -> str:
        """Generate a comprehensive security report."""
        start, end = self._get_date_range(period)
        
        # Load data
        file_logs = self._load_logs("file_access", start, end)
        api_logs = self._load_logs("api_call", start, end)
        comm_logs = self._load_logs("communication", start, end)
        alerts = self._load_alerts(start, end)
        
        # Analyze
        file_analysis = self._analyze_file_access(file_logs)
        api_analysis = self._analyze_api_calls(api_logs)
        comm_analysis = self._analyze_communications(comm_logs)
        alert_analysis = self._analyze_alerts(alerts)
        
        # Calculate threat level
        threat_level, threat_reason = self._calculate_threat_level(
            alert_analysis, file_analysis, api_analysis
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            alert_analysis, file_analysis, api_analysis
        )
        
        # Build report
        report = f"""# 🛡️ AgentGuard Security Report

**Period:** {period.capitalize()}  
**Range:** {start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Threat Level: {threat_level}

{threat_reason}

---

## 📊 Executive Summary

| Metric | Count |
|--------|-------|
| Total File Operations | {file_analysis['total_operations']:,} |
| Total API Calls | {api_analysis['total_calls']:,} |
| Total Communications | {comm_analysis['total_communications']:,} |
| Total Alerts | {alert_analysis['total_alerts']:,} |
| Unacknowledged Alerts | {alert_analysis['unacknowledged']:,} |

---

## 🚨 Alerts Breakdown

| Severity | Count |
|----------|-------|
| 🔴 Critical | {alert_analysis['by_severity'].get('critical', 0)} |
| 🟠 High | {alert_analysis['by_severity'].get('high', 0)} |
| 🟡 Medium | {alert_analysis['by_severity'].get('medium', 0)} |
| 🟢 Low | {alert_analysis['by_severity'].get('low', 0)} |
| 🔵 Info | {alert_analysis['by_severity'].get('info', 0)} |

"""
        
        # Critical alerts detail
        if alert_analysis['critical_alerts']:
            report += "### Critical Alerts (Require Immediate Attention)\n\n"
            for alert in alert_analysis['critical_alerts'][:5]:
                report += f"- **{alert.get('title')}**: {alert.get('description')}\n"
            report += "\n"
        
        # File access section
        report += f"""---

## 📁 File Access Analysis

**Total Operations:** {file_analysis['total_operations']:,}

### Operations by Type
"""
        for op_type, count in file_analysis['by_type'].items():
            report += f"- {op_type}: {count:,}\n"
        
        if file_analysis['sensitive_accesses']:
            report += f"\n### ⚠️ Sensitive File Accesses ({len(file_analysis['sensitive_accesses'])})\n\n"
            for access in file_analysis['sensitive_accesses'][:10]:
                report += f"- `{access['path']}` ({access['action']})\n"
        
        # API calls section
        report += f"""
---

## 🌐 API Call Analysis

**Total Calls:** {api_analysis['total_calls']:,}

### Top Domains
"""
        for domain, count in list(api_analysis['by_domain'].items())[:10]:
            report += f"- {domain}: {count:,}\n"
        
        if api_analysis['errors']:
            report += f"\n### ❌ API Errors ({len(api_analysis['errors'])})\n"
            for error in api_analysis['errors'][:5]:
                report += f"- Status {error['status']}: `{error['url']}`\n"
        
        # Communications section
        report += f"""
---

## 📡 External Communications

**Total:** {comm_analysis['total_communications']:,}

### By Type
"""
        for comm_type, count in comm_analysis['by_type'].items():
            report += f"- {comm_type}: {count:,}\n"
        
        # Recommendations
        report += """
---

## 💡 Recommendations

"""
        for rec in recommendations:
            report += f"{rec}\n\n"
        
        # Footer
        report += """
---

*Report generated by AgentGuard Security Monitor*
"""
        
        return report
    
    def save_report(self, report: str, period: str = "daily") -> Path:
        """Save report to disk."""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today}_{period}_report.md"
        report_path = REPORTS_DIR / filename
        
        with open(report_path, "w") as f:
            f.write(report)
        
        return report_path


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AgentGuard Report Generator")
    parser.add_argument("command", choices=["generate", "list"],
                        help="Command to execute")
    parser.add_argument("--period", choices=["daily", "weekly", "monthly"],
                        default="daily", help="Report period")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--format", choices=["markdown", "json"],
                        default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    generator = ReportGenerator()
    
    if args.command == "generate":
        report = generator.generate_report(args.period)
        
        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w") as f:
                f.write(report)
            print(f"Report saved to: {output_path}")
        else:
            saved_path = generator.save_report(report, args.period)
            print(report)
            print(f"\n📄 Report saved to: {saved_path}")
    
    elif args.command == "list":
        reports = sorted(REPORTS_DIR.glob("*.md"), reverse=True)
        print("Available reports:")
        for report in reports[:20]:
            print(f"  - {report.name}")


if __name__ == "__main__":
    main()
