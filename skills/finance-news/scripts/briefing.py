#!/usr/bin/env python3
"""
Briefing Generator - Main entry point for market briefings.
Generates and optionally sends to WhatsApp group.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from utils import ensure_venv

SCRIPT_DIR = Path(__file__).parent

ensure_venv()


def send_to_whatsapp(message: str, group_name: str | None = None):
    """Send message to WhatsApp group via openclaw message tool."""
    if not group_name:
        group_name = os.environ.get('FINANCE_NEWS_TARGET', '')
    if not group_name:
        print("❌ No target specified. Set FINANCE_NEWS_TARGET env var or use --group", file=sys.stderr)
        return False
    # Use openclaw message tool
    try:
        result = subprocess.run(
            [
                'openclaw', 'message', 'send',
                '--channel', 'whatsapp',
                '--target', group_name,
                '--message', message
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Sent to WhatsApp group: {group_name}", file=sys.stderr)
            return True
        else:
            print(f"⚠️ WhatsApp send failed: {result.stderr}", file=sys.stderr)
            return False
    
    except Exception as e:
        print(f"❌ WhatsApp error: {e}", file=sys.stderr)
        return False


def generate_and_send(args):
    """Generate briefing and optionally send to WhatsApp."""
    
    # Determine briefing type based on current time or args
    if args.time:
        briefing_time = args.time
    else:
        hour = datetime.now().hour
        briefing_time = 'morning' if hour < 12 else 'evening'
    
    # Generate the briefing
    cmd = [
        sys.executable, SCRIPT_DIR / 'summarize.py',
        '--time', briefing_time,
        '--style', args.style,
        '--lang', args.lang
    ]

    if args.deadline is not None:
        cmd.extend(['--deadline', str(args.deadline)])

    if args.fast:
        cmd.append('--fast')

    if args.llm:
        cmd.append('--llm')
        cmd.extend(['--model', args.model])

    if args.debug:
        cmd.append('--debug')
    
    # Always use JSON for internal processing to handle splits
    cmd.append('--json')
    
    print(f"📊 Generating {briefing_time} briefing...", file=sys.stderr)
    
    timeout = args.deadline if args.deadline is not None else 300
    timeout = max(1, int(timeout))
    if args.deadline is not None:
        timeout = timeout + 5
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=timeout
    )
    
    if result.returncode != 0:
        print(f"❌ Briefing generation failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    try:
        data = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        # Fallback if not JSON (shouldn't happen with --json)
        print(f"⚠️ Failed to parse briefing JSON", file=sys.stderr)
        print(result.stdout)
        return result.stdout

    # Output handling
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        # Print for humans
        if data.get('macro_message'):
             print(data['macro_message'])
        if data.get('portfolio_message'):
             print("\n" + "="*20 + "\n")
             print(data['portfolio_message'])
    
    # Send to WhatsApp if requested
    if args.send and args.group:
        # Message 1: Macro
        macro_msg = data.get('macro_message') or data.get('summary', '')
        if macro_msg:
            send_to_whatsapp(macro_msg, args.group)
        
        # Message 2: Portfolio (if exists)
        portfolio_msg = data.get('portfolio_message')
        if portfolio_msg:
            send_to_whatsapp(portfolio_msg, args.group)
            
    return data.get('macro_message', '')


def main():
    parser = argparse.ArgumentParser(description='Briefing Generator')
    parser.add_argument('--time', choices=['morning', 'evening'], 
                        help='Briefing type (auto-detected if not specified)')
    parser.add_argument('--style', choices=['briefing', 'analysis', 'headlines'],
                        default='briefing', help='Summary style')
    parser.add_argument('--lang', choices=['en', 'de'], default='en',
                        help='Output language')
    parser.add_argument('--send', action='store_true',
                        help='Send to WhatsApp group')
    parser.add_argument('--group', default=os.environ.get('FINANCE_NEWS_TARGET', ''),
                        help='WhatsApp group name or JID (default: FINANCE_NEWS_TARGET env var)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    parser.add_argument('--deadline', type=int, default=None,
                        help='Overall deadline in seconds')
    parser.add_argument('--llm', action='store_true', help='Use LLM summary')
    parser.add_argument('--model', choices=['claude', 'minimax', 'gemini'],
                        default='claude', help='LLM model (only with --llm)')
    parser.add_argument('--fast', action='store_true',
                        help='Use fast mode (shorter timeouts, fewer items)')
    parser.add_argument('--debug', action='store_true',
                        help='Write debug log with sources')
    
    args = parser.parse_args()
    generate_and_send(args)


if __name__ == '__main__':
    main()
