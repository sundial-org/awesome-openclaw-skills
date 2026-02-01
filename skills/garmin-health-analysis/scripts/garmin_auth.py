#!/usr/bin/env python3
"""
Garmin Connect authentication helper.
Handles login and stores session tokens.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import argparse

try:
    from garminconnect import Garmin, GarminConnectAuthenticationError, GarminConnectConnectionError
except ImportError:
    print("❌ garminconnect library not installed", file=sys.stderr)
    print("Install with: pip3 install garminconnect", file=sys.stderr)
    sys.exit(1)

TOKEN_DIR = Path.home() / ".clawdbot" / "garmin"
CONFIG_FILE = Path(__file__).parent.parent / "config.json"


def load_config():
    """Load credentials from config file."""
    if not CONFIG_FILE.exists():
        return None
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Failed to load config: {e}", file=sys.stderr)
        return None


def login(email, password):
    """Perform login and save tokens using garminconnect's tokenstore."""
    try:
        print(f"🔐 Logging in as {email}...", file=sys.stderr)
        
        # Create token directory
        TOKEN_DIR.mkdir(parents=True, exist_ok=True)
        tokenstore = str(TOKEN_DIR)
        
        # Create client and login (don't pass tokenstore on first login)
        client = Garmin(email, password)
        client.login()  # Initial login without tokenstore
        
        # Save tokens to tokenstore
        client.garth.dump(tokenstore)
        print(f"✅ Tokens saved to {tokenstore}", file=sys.stderr)
        
        # Test the connection
        try:
            profile = client.get_user_summary(datetime.now().strftime("%Y-%m-%d"))
            print(f"✅ Login successful! User: {profile.get('displayName', 'Unknown')}", file=sys.stderr)
        except Exception as e:
            print(f"✅ Login successful! (Unable to fetch profile: {e})", file=sys.stderr)
        
        # Make tokenstore directory secure
        TOKEN_DIR.chmod(0o700)
        
        return True
        
    except GarminConnectAuthenticationError as e:
        print(f"❌ Authentication failed: {e}", file=sys.stderr)
        print("Check your email/password and try again.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Login error: {e}", file=sys.stderr)
        return False


def get_client():
    """Get authenticated Garmin client, using saved tokens if available."""
    tokenstore = str(TOKEN_DIR)
    
    if not TOKEN_DIR.exists():
        return None
    
    try:
        # Try to use saved tokens
        client = Garmin()
        client.login(tokenstore=tokenstore)
        
        # Test if tokens still work
        client.get_user_summary(datetime.now().strftime("%Y-%m-%d"))
        return client
        
    except Exception as e:
        print(f"⚠️  Saved tokens expired or invalid: {e}", file=sys.stderr)
        return None


def check_status():
    """Check if we have valid authentication."""
    tokenstore = str(TOKEN_DIR)
    
    if not TOKEN_DIR.exists():
        print("❌ Not authenticated", file=sys.stderr)
        print("Run: python3 scripts/garmin_auth.py login", file=sys.stderr)
        return False
    
    print(f"✅ Token store found at {tokenstore}", file=sys.stderr)
    
    # Test if they work
    client = get_client()
    if client:
        try:
            profile = client.get_user_summary(datetime.now().strftime("%Y-%m-%d"))
            print(f"✅ Authentication valid! User: {profile.get('displayName', 'Unknown')}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"⚠️  Tokens may be expired: {e}", file=sys.stderr)
            return False
    
    print("❌ Authentication invalid. Please login again.", file=sys.stderr)
    return False


def main():
    parser = argparse.ArgumentParser(description="Garmin Connect authentication")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Login command
    login_parser = subparsers.add_parser("login", help="Login to Garmin Connect")
    login_parser.add_argument("--email", help="Garmin account email (or set via env/config)")
    login_parser.add_argument("--password", help="Garmin account password (or set via env/config)")
    
    # Status command
    subparsers.add_parser("status", help="Check authentication status")
    
    args = parser.parse_args()
    
    if args.command == "login":
        email = args.email
        password = args.password
        
        # Priority: CLI args > config.json > environment variables
        if not email or not password:
            config = load_config()
            if config:
                email = email or config.get("email")
                password = password or config.get("password")
        
        if not email or not password:
            email = email or os.getenv("GARMIN_EMAIL")
            password = password or os.getenv("GARMIN_PASSWORD")
        
        if not email or not password:
            print("❌ Email and password required", file=sys.stderr)
            print("Set via:", file=sys.stderr)
            print("  1. CLI: --email and --password", file=sys.stderr)
            print("  2. Config: create config.json from config.example.json", file=sys.stderr)
            print("  3. Env vars: GARMIN_EMAIL and GARMIN_PASSWORD", file=sys.stderr)
            print("  4. Clawdbot config: skills.entries.garmin-health-analysis.env", file=sys.stderr)
            sys.exit(1)
        
        success = login(email, password)
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        success = check_status()
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
