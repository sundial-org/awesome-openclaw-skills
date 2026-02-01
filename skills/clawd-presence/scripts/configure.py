#!/usr/bin/env python3
"""
Configure agent presence display.

Usage:
    python3 configure.py --auto              # Auto-detect from clawdbot config
    python3 configure.py --letter A
    python3 configure.py --name "ATLAS"
    python3 configure.py --timeout 300
    python3 configure.py --letter C --name "CLAUDE" --timeout 600
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

CONFIG_FILE = Path(__file__).parent.parent / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "letter": "A",
    "name": "AGENT",
    "idle_timeout": 300,
}

# Common clawdbot config locations
CLAWDBOT_CONFIG_PATHS = [
    Path.home() / ".config" / "clawd" / "config.yaml",
    Path.home() / ".config" / "clawd" / "config.yml",
    Path.home() / ".clawd" / "config.yaml",
    Path.home() / ".clawd" / "config.yml",
    Path.home() / ".config" / "clawdbot" / "config.yaml",
    Path.home() / ".config" / "clawdbot" / "config.yml",
]


def load_config() -> dict[str, Any]:
    """Load existing config or defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    result = DEFAULT_CONFIG.copy()
                    result.update(data)
                    return result
        except (json.JSONDecodeError, IOError, OSError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict[str, Any]) -> bool:
    """Save config to file. Returns True on success."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except (IOError, OSError) as e:
        print(f"Error saving config: {e}", file=sys.stderr)
        return False


def get_clawdbot_agent_name() -> str | None:
    """Try to read agent name from clawdbot config."""
    try:
        import yaml
    except ImportError:
        return None
    
    for config_path in CLAWDBOT_CONFIG_PATHS:
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    if not isinstance(config, dict):
                        continue
                    
                    # Try common config structures
                    # agent.name
                    if "agent" in config and isinstance(config["agent"], dict):
                        name = config["agent"].get("name")
                        if name and isinstance(name, str):
                            return name
                    
                    # Top-level name
                    if "name" in config and isinstance(config["name"], str):
                        return config["name"]
                        
            except Exception:
                continue
    
    return None


def validate_letter(letter: str) -> str | None:
    """Validate and normalize letter. Returns None if invalid."""
    if not letter:
        return None
    letter = letter.strip().upper()
    if len(letter) == 1 and letter.isalpha():
        return letter
    return None


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Configure agent presence display",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  configure.py --auto                    # Auto-detect from clawdbot
  configure.py --letter A --name AGENT   # Manual setup
  configure.py --timeout 600             # 10 minute idle timeout
  configure.py --show                    # View current config
        """,
    )
    
    parser.add_argument(
        "--auto", "-a", action="store_true",
        help="Auto-detect letter and name from clawdbot config"
    )
    parser.add_argument(
        "--letter", "-l", type=str,
        help="Monogram letter (A-Z)"
    )
    parser.add_argument(
        "--name", "-n", type=str,
        help="Display name shown at bottom"
    )
    parser.add_argument(
        "--timeout", "-t", type=int,
        help="Auto-idle timeout in seconds (0 to disable)"
    )
    parser.add_argument(
        "--show", "-s", action="store_true",
        help="Show current configuration"
    )
    
    args = parser.parse_args()
    config = load_config()
    
    if args.show:
        print(json.dumps(config, indent=2))
        return
    
    changed = False
    
    # Auto-detect from clawdbot
    if args.auto:
        agent_name = get_clawdbot_agent_name()
        if agent_name:
            first_letter = validate_letter(agent_name[0])
            if first_letter:
                config["letter"] = first_letter
                config["name"] = agent_name.upper()
                changed = True
                print(f"Auto-detected: {agent_name} → letter '{first_letter}'")
            else:
                print(f"Auto-detected name '{agent_name}' but first char is not A-Z")
        else:
            print("Could not auto-detect agent name from clawdbot config")
            print("Tip: Install PyYAML (pip install pyyaml) if not installed")
            if not any([args.letter, args.name, args.timeout]):
                sys.exit(1)
    
    # Manual letter
    if args.letter:
        letter = validate_letter(args.letter)
        if letter:
            config["letter"] = letter
            changed = True
        else:
            print(f"Error: Invalid letter '{args.letter}'. Must be A-Z.", file=sys.stderr)
            sys.exit(1)
    
    # Name
    if args.name:
        config["name"] = args.name.strip().upper()
        changed = True
    
    # Timeout
    if args.timeout is not None:
        config["idle_timeout"] = max(0, args.timeout)
        changed = True
    
    # Save if changed
    if changed:
        if save_config(config):
            print("Configuration updated:")
            print(json.dumps(config, indent=2))
        else:
            sys.exit(1)
    else:
        print("Current configuration:")
        print(json.dumps(config, indent=2))
        print()
        print("Use --help to see options")


if __name__ == "__main__":
    main()
