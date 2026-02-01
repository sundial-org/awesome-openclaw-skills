#!/usr/bin/env python3
"""
AgentGuard - Structured Logging Handler
Logs all agent activities with sanitization and structured format.
"""

import os
import json
import hashlib
import argparse
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re

CONFIG_DIR = Path.home() / ".agentguard"
LOG_DIR = CONFIG_DIR / "logs"


class LogCategory(Enum):
    FILE_ACCESS = "file_access"
    API_CALL = "api_call"
    COMMUNICATION = "communication"
    SYSTEM = "system"


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    category: str
    action: str
    details: Dict
    sanitized: bool = False
    hash: Optional[str] = None


class SensitiveDataSanitizer:
    """Sanitizes sensitive data in logs."""
    
    SENSITIVE_PATTERNS = [
        (r'(api[_-]?key["\s:=]+)["\']?[\w-]+["\']?', r'\1[REDACTED]'),
        (r'(password["\s:=]+)["\']?[^"\',\s]+["\']?', r'\1[REDACTED]'),
        (r'(secret["\s:=]+)["\']?[^"\',\s]+["\']?', r'\1[REDACTED]'),
        (r'(token["\s:=]+)["\']?[\w.-]+["\']?', r'\1[REDACTED]'),
        (r'(bearer\s+)[\w.-]+', r'\1[REDACTED]'),
        (r'(authorization["\s:=]+)["\']?[^"\',\s]+["\']?', r'\1[REDACTED]'),
        (r'(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)', r'[EMAIL_REDACTED]'),
        (r'(\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b)', r'[CARD_REDACTED]'),
        (r'(sk-[a-zA-Z0-9]{20,})', r'[API_KEY_REDACTED]'),
        (r'(ghp_[a-zA-Z0-9]{36})', r'[GITHUB_TOKEN_REDACTED]'),
    ]
    
    @classmethod
    def sanitize(cls, text: str) -> str:
        """Remove sensitive data from text."""
        result = text
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
    
    @classmethod
    def sanitize_dict(cls, data: Dict) -> Dict:
        """Sanitize all string values in a dictionary."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = cls.sanitize(value)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize(v) if isinstance(v, str) 
                    else cls.sanitize_dict(v) if isinstance(v, dict)
                    else v
                    for v in value
                ]
            else:
                sanitized[key] = value
        return sanitized
    
    @classmethod
    def hash_sensitive(cls, text: str) -> str:
        """Create a hash of sensitive data for correlation without exposure."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]


class AgentLogger:
    """Main logging handler."""
    
    def __init__(self, hash_sensitive: bool = True, retention_days: int = 30):
        self.hash_sensitive = hash_sensitive
        self.retention_days = retention_days
        self._setup_dirs()
        
    def _setup_dirs(self):
        """Create log directories."""
        for category in LogCategory:
            (LOG_DIR / category.value).mkdir(parents=True, exist_ok=True)
    
    def _get_log_file(self, category: LogCategory) -> Path:
        """Get today's log file for a category."""
        today = datetime.now().strftime("%Y-%m-%d")
        return LOG_DIR / category.value / f"{today}.jsonl"
    
    def log(self, category: LogCategory, action: str, details: Dict) -> LogEntry:
        """Log an event."""
        # Sanitize if needed
        sanitized_details = details
        if self.hash_sensitive:
            sanitized_details = SensitiveDataSanitizer.sanitize_dict(details)
        
        # Create entry
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            category=category.value,
            action=action,
            details=sanitized_details,
            sanitized=self.hash_sensitive,
            hash=hashlib.sha256(json.dumps(details, sort_keys=True).encode()).hexdigest()[:16]
        )
        
        # Write to file
        log_file = self._get_log_file(category)
        with open(log_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")
        
        return entry
    
    def log_file_access(self, path: str, event_type: str, 
                        size: Optional[int] = None) -> LogEntry:
        """Log a file access event."""
        return self.log(
            LogCategory.FILE_ACCESS,
            event_type,
            {
                "path": path,
                "size": size,
                "filename": os.path.basename(path),
                "extension": os.path.splitext(path)[1]
            }
        )
    
    def log_api_call(self, method: str, url: str, status_code: Optional[int] = None,
                     request_size: Optional[int] = None, 
                     response_size: Optional[int] = None) -> LogEntry:
        """Log an API call."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        return self.log(
            LogCategory.API_CALL,
            method.upper(),
            {
                "url": SensitiveDataSanitizer.sanitize(url),
                "domain": parsed.netloc,
                "path": parsed.path,
                "status_code": status_code,
                "request_size": request_size,
                "response_size": response_size
            }
        )
    
    def log_communication(self, comm_type: str, destination: str,
                          message_hash: Optional[str] = None,
                          size: Optional[int] = None) -> LogEntry:
        """Log external communication."""
        return self.log(
            LogCategory.COMMUNICATION,
            comm_type,
            {
                "destination": destination,
                "message_hash": message_hash or SensitiveDataSanitizer.hash_sensitive(destination),
                "size": size
            }
        )
    
    def log_system(self, action: str, details: Dict) -> LogEntry:
        """Log system events."""
        return self.log(LogCategory.SYSTEM, action, details)
    
    def get_logs(self, category: LogCategory, 
                 date: Optional[str] = None,
                 limit: int = 100) -> List[Dict]:
        """Retrieve logs for a category."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        log_file = LOG_DIR / category.value / f"{date}.jsonl"
        
        if not log_file.exists():
            return []
        
        logs = []
        with open(log_file) as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
                    if len(logs) >= limit:
                        break
        
        return logs
    
    def get_all_logs(self, date: Optional[str] = None, limit: int = 100) -> Dict[str, List]:
        """Get logs from all categories."""
        result = {}
        for category in LogCategory:
            result[category.value] = self.get_logs(category, date, limit)
        return result
    
    def cleanup_old_logs(self):
        """Remove logs older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        deleted = 0
        
        for category in LogCategory:
            category_dir = LOG_DIR / category.value
            for log_file in category_dir.glob("*.jsonl"):
                try:
                    file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
                    if file_date < cutoff:
                        log_file.unlink()
                        deleted += 1
                except ValueError:
                    continue
        
        return deleted
    
    def compress_old_logs(self, days_before_compress: int = 7):
        """Compress logs older than N days."""
        cutoff = datetime.now() - timedelta(days=days_before_compress)
        compressed = 0
        
        for category in LogCategory:
            category_dir = LOG_DIR / category.value
            for log_file in category_dir.glob("*.jsonl"):
                if log_file.suffix == ".gz":
                    continue
                try:
                    file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
                    if file_date < cutoff:
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(str(log_file) + '.gz', 'wb') as f_out:
                                f_out.write(f_in.read())
                        log_file.unlink()
                        compressed += 1
                except ValueError:
                    continue
        
        return compressed
    
    def get_stats(self, date: Optional[str] = None) -> Dict:
        """Get logging statistics."""
        logs = self.get_all_logs(date, limit=10000)
        
        stats = {
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "totals": {},
            "by_action": {}
        }
        
        for category, entries in logs.items():
            stats["totals"][category] = len(entries)
            action_counts = {}
            for entry in entries:
                action = entry.get("action", "unknown")
                action_counts[action] = action_counts.get(action, 0) + 1
            stats["by_action"][category] = action_counts
        
        return stats


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AgentGuard Logger")
    parser.add_argument("command", choices=["log", "view", "stats", "cleanup", "compress"],
                        help="Command to execute")
    parser.add_argument("--category", choices=["file_access", "api_call", "communication", "system"],
                        help="Log category")
    parser.add_argument("--action", type=str, help="Action for logging")
    parser.add_argument("--details", type=str, help="JSON details for logging")
    parser.add_argument("--date", type=str, help="Date for viewing (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=100, help="Max entries to return")
    parser.add_argument("--retention", type=int, default=30, help="Retention days")
    
    args = parser.parse_args()
    
    logger = AgentLogger(retention_days=args.retention)
    
    if args.command == "log":
        if not args.category or not args.action:
            print("Error: --category and --action required for logging")
            return
        
        details = {}
        if args.details:
            details = json.loads(args.details)
        
        category = LogCategory(args.category)
        entry = logger.log(category, args.action, details)
        print(f"Logged: {entry.hash}")
        
    elif args.command == "view":
        if args.category:
            logs = logger.get_logs(LogCategory(args.category), args.date, args.limit)
        else:
            logs = logger.get_all_logs(args.date, args.limit)
        print(json.dumps(logs, indent=2))
        
    elif args.command == "stats":
        stats = logger.get_stats(args.date)
        print(json.dumps(stats, indent=2))
        
    elif args.command == "cleanup":
        deleted = logger.cleanup_old_logs()
        print(f"Deleted {deleted} old log files")
        
    elif args.command == "compress":
        compressed = logger.compress_old_logs()
        print(f"Compressed {compressed} log files")


if __name__ == "__main__":
    main()
