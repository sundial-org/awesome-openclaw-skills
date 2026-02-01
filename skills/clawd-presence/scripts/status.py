#!/usr/bin/env python3
"""
Update agent presence status.

Usage:
    python3 status.py work "Building feature X"
    python3 status.py idle
    python3 status.py think "Analyzing options"
    python3 status.py alert "Need human input"
    python3 status.py sleep
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import NoReturn

STATE_FILE = Path(__file__).parent.parent / "state.json"

VALID_STATES = frozenset({"idle", "work", "think", "alert", "sleep"})


def print_usage() -> NoReturn:
    """Print usage and exit."""
    print("Usage: status.py <state> [message]")
    print(f"States: {', '.join(sorted(VALID_STATES))}")
    print()
    print("Examples:")
    print('  status.py work "Building feature"')
    print('  status.py think "Analyzing data"')
    print("  status.py idle")
    sys.exit(1)


def update_status(state: str, message: str = "") -> bool:
    """
    Update the presence state file.
    
    Args:
        state: One of idle, work, think, alert, sleep
        message: Optional status message
        
    Returns:
        True on success, False on failure
    """
    state = state.lower().strip()
    message = message.strip()
    
    if state not in VALID_STATES:
        print(f"Error: Invalid state '{state}'", file=sys.stderr)
        print(f"Valid states: {', '.join(sorted(VALID_STATES))}", file=sys.stderr)
        return False
    
    data = {
        "state": state,
        "message": message,
        "updated": time.time(),
    }
    
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except (IOError, OSError) as e:
        print(f"Error writing state file: {e}", file=sys.stderr)
        return False
    
    # Output confirmation
    if message:
        print(f"{state.upper()}: {message}")
    else:
        print(state.upper())
    
    return True


def main() -> None:
    """Entry point."""
    if len(sys.argv) < 2:
        print_usage()
    
    state = sys.argv[1]
    
    # Handle help flags
    if state in ("-h", "--help", "help"):
        print_usage()
    
    message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    
    success = update_status(state, message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
