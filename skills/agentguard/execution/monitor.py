#!/usr/bin/env python3
"""
AgentGuard - Core Monitoring Daemon
Monitors file access patterns and API calls in real-time.
"""

import os
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import queue

# Try to import watchdog for file monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    print("Warning: watchdog not installed. File monitoring limited.")

# Configuration
CONFIG_DIR = Path.home() / ".agentguard"
LOG_DIR = CONFIG_DIR / "logs"
BASELINE_DIR = CONFIG_DIR / "baselines"


@dataclass
class FileEvent:
    """Represents a file system event."""
    timestamp: str
    event_type: str  # created, modified, deleted, accessed
    path: str
    size: Optional[int] = None
    is_sensitive: bool = False
    hash: Optional[str] = None


@dataclass
class APIEvent:
    """Represents an API call event."""
    timestamp: str
    method: str
    url: str
    domain: str
    status_code: Optional[int] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None
    is_trusted: bool = True
    payload_hash: Optional[str] = None


class SensitivePathDetector:
    """Detects access to sensitive files and directories."""
    
    SENSITIVE_PATTERNS = [
        ".env",
        ".secrets",
        "credentials",
        "password",
        "token",
        "apikey",
        "api_key",
        "private_key",
        "id_rsa",
        "id_ed25519",
        ".ssh/",
        ".aws/",
        ".gnupg/",
        "keychain",
        ".netrc",
        "htpasswd",
    ]
    
    SENSITIVE_EXTENSIONS = [
        ".pem",
        ".key",
        ".p12",
        ".pfx",
        ".jks",
        ".keystore",
    ]
    
    @classmethod
    def is_sensitive(cls, path: str) -> bool:
        """Check if a path is considered sensitive."""
        path_lower = path.lower()
        
        # Check patterns
        for pattern in cls.SENSITIVE_PATTERNS:
            if pattern in path_lower:
                return True
        
        # Check extensions
        for ext in cls.SENSITIVE_EXTENSIONS:
            if path_lower.endswith(ext):
                return True
        
        return False


class FileAccessMonitor:
    """Monitors file system access patterns."""
    
    def __init__(self, watch_dirs: List[str], exclude_patterns: List[str] = None):
        self.watch_dirs = [Path(d).expanduser() for d in watch_dirs]
        self.exclude_patterns = exclude_patterns or []
        self.event_queue = queue.Queue()
        self.access_counts = defaultdict(int)
        self.observers = []
        
    def should_exclude(self, path: str) -> bool:
        """Check if path matches exclusion patterns."""
        for pattern in self.exclude_patterns:
            if pattern.endswith("**"):
                if pattern[:-2] in path:
                    return True
            elif pattern.startswith("*."):
                if path.endswith(pattern[1:]):
                    return True
            elif pattern in path:
                return True
        return False
    
    def start(self):
        """Start file monitoring."""
        if not HAS_WATCHDOG:
            print("File monitoring unavailable - install watchdog: pip install watchdog")
            return
        
        for watch_dir in self.watch_dirs:
            if watch_dir.exists():
                handler = self._create_handler()
                observer = Observer()
                observer.schedule(handler, str(watch_dir), recursive=True)
                observer.start()
                self.observers.append(observer)
                print(f"Monitoring: {watch_dir}")
    
    def _create_handler(self):
        """Create a file system event handler."""
        monitor = self
        
        class Handler(FileSystemEventHandler):
            def on_any_event(self, event: FileSystemEvent):
                if event.is_directory:
                    return
                if monitor.should_exclude(event.src_path):
                    return
                
                file_event = FileEvent(
                    timestamp=datetime.now().isoformat(),
                    event_type=event.event_type,
                    path=event.src_path,
                    is_sensitive=SensitivePathDetector.is_sensitive(event.src_path)
                )
                
                # Get file size for created/modified
                if event.event_type in ('created', 'modified'):
                    try:
                        file_event.size = os.path.getsize(event.src_path)
                    except OSError:
                        pass
                
                monitor.event_queue.put(file_event)
                monitor.access_counts[event.src_path] += 1
        
        return Handler()
    
    def stop(self):
        """Stop all observers."""
        for observer in self.observers:
            observer.stop()
            observer.join()
    
    def get_events(self, max_events: int = 100) -> List[FileEvent]:
        """Get queued events."""
        events = []
        while not self.event_queue.empty() and len(events) < max_events:
            events.append(self.event_queue.get_nowait())
        return events
    
    def get_hot_files(self, top_n: int = 10) -> List[tuple]:
        """Get most frequently accessed files."""
        return sorted(
            self.access_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]


class APICallMonitor:
    """Monitors outbound API calls."""
    
    def __init__(self, trusted_domains: List[str] = None):
        self.trusted_domains = set(trusted_domains or [])
        self.call_log = []
        self.domain_counts = defaultdict(int)
        
    def add_trusted_domain(self, domain: str):
        """Add a domain to trusted list."""
        self.trusted_domains.add(domain.lower())
        
    def remove_trusted_domain(self, domain: str):
        """Remove a domain from trusted list."""
        self.trusted_domains.discard(domain.lower())
    
    def is_trusted(self, domain: str) -> bool:
        """Check if domain is trusted."""
        domain_lower = domain.lower()
        for trusted in self.trusted_domains:
            if domain_lower == trusted or domain_lower.endswith(f".{trusted}"):
                return True
        return False
    
    def log_call(self, method: str, url: str, status_code: int = None,
                 request_size: int = None, response_size: int = None,
                 payload: Any = None) -> APIEvent:
        """Log an API call."""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        payload_hash = None
        if payload:
            payload_str = json.dumps(payload) if isinstance(payload, dict) else str(payload)
            payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()[:16]
        
        event = APIEvent(
            timestamp=datetime.now().isoformat(),
            method=method.upper(),
            url=url,
            domain=domain,
            status_code=status_code,
            request_size=request_size,
            response_size=response_size,
            is_trusted=self.is_trusted(domain),
            payload_hash=payload_hash
        )
        
        self.call_log.append(event)
        self.domain_counts[domain] += 1
        
        return event
    
    def get_untrusted_calls(self) -> List[APIEvent]:
        """Get all calls to untrusted domains."""
        return [e for e in self.call_log if not e.is_trusted]
    
    def get_domain_stats(self) -> Dict[str, Dict]:
        """Get statistics per domain."""
        stats = {}
        for domain, count in self.domain_counts.items():
            stats[domain] = {
                "count": count,
                "trusted": self.is_trusted(domain)
            }
        return stats


class AgentGuardMonitor:
    """Main monitoring orchestrator."""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._load_config()
        self.file_monitor = None
        self.api_monitor = None
        self.running = False
        self._setup_dirs()
        
    def _setup_dirs(self):
        """Create necessary directories."""
        for dir_path in [CONFIG_DIR, LOG_DIR, BASELINE_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for logs
        for subdir in ["file_access", "api_calls", "communications"]:
            (LOG_DIR / subdir).mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict:
        """Load configuration from file."""
        config_file = CONFIG_DIR / "config.yaml"
        if config_file.exists():
            try:
                import yaml
                with open(config_file) as f:
                    return yaml.safe_load(f)
            except ImportError:
                # Fall back to JSON config
                json_config = CONFIG_DIR / "config.json"
                if json_config.exists():
                    with open(json_config) as f:
                        return json.load(f)
        
        # Return defaults
        return {
            "monitoring": {
                "enabled": True,
                "file_watch_dirs": ["~/clawd", "~/.clawdbot"],
                "exclude_patterns": ["*.log", "node_modules/**", ".git/**"]
            },
            "api_monitoring": {
                "trusted_domains": [
                    "api.anthropic.com",
                    "api.openai.com",
                    "api.telegram.org"
                ]
            }
        }
    
    def start(self):
        """Start all monitors."""
        if self.running:
            print("Monitor already running")
            return
        
        monitoring_config = self.config.get("monitoring", {})
        api_config = self.config.get("api_monitoring", {})
        
        # Start file monitor
        self.file_monitor = FileAccessMonitor(
            watch_dirs=monitoring_config.get("file_watch_dirs", ["~/clawd"]),
            exclude_patterns=monitoring_config.get("exclude_patterns", [])
        )
        self.file_monitor.start()
        
        # Initialize API monitor
        self.api_monitor = APICallMonitor(
            trusted_domains=api_config.get("trusted_domains", [])
        )
        
        self.running = True
        print("AgentGuard monitoring started")
        
    def stop(self):
        """Stop all monitors."""
        if self.file_monitor:
            self.file_monitor.stop()
        self.running = False
        print("AgentGuard monitoring stopped")
    
    def status(self) -> Dict:
        """Get current monitoring status."""
        return {
            "running": self.running,
            "file_monitor": {
                "active": self.file_monitor is not None,
                "watched_dirs": [str(d) for d in (self.file_monitor.watch_dirs if self.file_monitor else [])]
            },
            "api_monitor": {
                "active": self.api_monitor is not None,
                "trusted_domains": list(self.api_monitor.trusted_domains) if self.api_monitor else []
            }
        }
    
    def get_summary(self) -> Dict:
        """Get monitoring summary."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "status": "running" if self.running else "stopped"
        }
        
        if self.file_monitor:
            events = self.file_monitor.get_events()
            sensitive_events = [e for e in events if e.is_sensitive]
            summary["file_access"] = {
                "recent_events": len(events),
                "sensitive_accesses": len(sensitive_events),
                "hot_files": self.file_monitor.get_hot_files(5)
            }
        
        if self.api_monitor:
            untrusted = self.api_monitor.get_untrusted_calls()
            summary["api_calls"] = {
                "total_logged": len(self.api_monitor.call_log),
                "untrusted_calls": len(untrusted),
                "domain_stats": self.api_monitor.get_domain_stats()
            }
        
        return summary


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="AgentGuard Security Monitor")
    parser.add_argument("command", choices=["start", "stop", "status", "summary"],
                        help="Command to execute")
    parser.add_argument("--watch-dir", action="append", dest="watch_dirs",
                        help="Additional directories to watch")
    parser.add_argument("--daemon", action="store_true",
                        help="Run as daemon")
    
    args = parser.parse_args()
    
    monitor = AgentGuardMonitor()
    
    if args.command == "start":
        monitor.start()
        if args.daemon:
            try:
                while True:
                    time.sleep(60)
                    # Periodic summary
                    summary = monitor.get_summary()
                    if summary.get("file_access", {}).get("sensitive_accesses", 0) > 0:
                        print(f"Alert: Sensitive file access detected")
            except KeyboardInterrupt:
                monitor.stop()
        else:
            print(json.dumps(monitor.status(), indent=2))
            
    elif args.command == "stop":
        monitor.stop()
        
    elif args.command == "status":
        print(json.dumps(monitor.status(), indent=2))
        
    elif args.command == "summary":
        # For summary, we need to start briefly to get data
        monitor.start()
        time.sleep(2)  # Collect some events
        summary = monitor.get_summary()
        monitor.stop()
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
