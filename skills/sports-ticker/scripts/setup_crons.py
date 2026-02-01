#!/usr/bin/env python3
"""
Setup cron jobs for sports-ticker skill.

Creates:
1. football-match-check - Daily check at 9 AM user timezone
2. spurs-live-ticker - Template for live match monitoring (disabled)
3. spurs-reminder - Template for match day reminders (disabled)

Usage:
    python3 setup_crons.py <telegram_id> <timezone>
    python3 setup_crons.py 123456789 "Europe/London"
    python3 setup_crons.py --list  # Show cron configs only
"""

import sys
import json
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"


def get_cron_configs(telegram_id: str, timezone: str) -> list[dict]:
    """Generate cron job configurations."""
    
    return [
        {
            "name": "football-match-check",
            "description": "Daily morning check for team matches. Auto-updates live-ticker schedule when matches found.",
            "schedule": {
                "kind": "cron",
                "expr": "0 9 * * *",  # 9 AM daily
                "tz": timezone
            },
            "channel": {
                "type": "telegram",
                "id": telegram_id
            },
            "payload": {
                "message": f"""Check if any configured teams in {SKILL_DIR}/config.json play today using the live_monitor.py script.

If a match is found:
1. Note the kickoff time
2. Update the 'spurs-live-ticker' cron to start 5 mins before kickoff and run every 2 mins for 3 hours
3. Update the 'spurs-reminder' cron to fire 30 mins before kickoff
4. Enable both crons

If no match today, ensure live-ticker and reminder crons are disabled."""
            },
            "enabled": True
        },
        {
            "name": "spurs-live-ticker",
            "description": "Live match monitoring - runs every 2 mins during matches. Auto-scheduled by match-check.",
            "schedule": {
                "kind": "cron",
                "expr": "*/2 * * * *",  # Every 2 minutes (will be updated dynamically)
                "tz": timezone
            },
            "channel": {
                "type": "telegram",
                "id": telegram_id
            },
            "payload": {
                "message": f"Run python3 {SCRIPT_DIR}/live_monitor.py and send me any new events (goals, cards, halftime, fulltime). Only message if there are updates."
            },
            "enabled": False  # Disabled by default - match-check enables it
        },
        {
            "name": "spurs-reminder",
            "description": "Pre-match reminder - fires 30 mins before kickoff. Auto-scheduled by match-check.",
            "schedule": {
                "kind": "cron",
                "expr": "0 14 * * *",  # Placeholder - gets updated dynamically
                "tz": timezone
            },
            "channel": {
                "type": "telegram",
                "id": telegram_id
            },
            "payload": {
                "message": f"Run python3 {SCRIPT_DIR}/live_monitor.py --upcoming to get today's match details, then send me a reminder that the match starts in 30 minutes with opponent, competition, and kickoff time."
            },
            "enabled": False  # Disabled by default - match-check enables it
        }
    ]


def create_cron_via_openclaw(cron_config: dict) -> bool:
    """Attempt to create cron via openclaw CLI."""
    try:
        # Try using openclaw cron create
        cmd = [
            "openclaw", "cron", "create",
            "--name", cron_config["name"],
            "--schedule", json.dumps(cron_config["schedule"]),
            "--channel", json.dumps(cron_config["channel"]),
            "--payload", json.dumps(cron_config["payload"]),
        ]
        if not cron_config.get("enabled", True):
            cmd.append("--disabled")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def print_manual_instructions(crons: list[dict]):
    """Print manual setup instructions."""
    print("\n" + "="*60)
    print("📋 MANUAL CRON SETUP INSTRUCTIONS")
    print("="*60)
    print("\nAsk Claude/OpenClaw to create these cron jobs:\n")
    
    for cron in crons:
        print(f"\n### {cron['name']}")
        print(f"Description: {cron['description']}")
        print(f"Schedule: {cron['schedule']['expr']} ({cron['schedule']['tz']})")
        print(f"Enabled: {cron['enabled']}")
        print(f"\nPayload message:")
        print(f"  {cron['payload']['message'][:200]}...")
        print("-"*40)
    
    print("\n💡 TIP: Copy-paste this to OpenClaw:")
    print("-"*40)
    print(f"""
Please create these 3 cron jobs for sports-ticker:

1. **football-match-check** (enabled)
   - Schedule: `0 9 * * *` (9 AM daily)
   - Task: Check for team matches, auto-update live-ticker schedule

2. **spurs-live-ticker** (disabled)
   - Schedule: `*/2 * * * *` (every 2 mins, placeholder)
   - Task: Run live_monitor.py during matches

3. **spurs-reminder** (disabled)
   - Schedule: placeholder (gets set by match-check)
   - Task: Pre-match reminder 30 mins before kickoff

Timezone: {crons[0]['schedule']['tz']}
Channel: Telegram {crons[0]['channel']['id']}
""")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        # Just show example configs
        crons = get_cron_configs("YOUR_TELEGRAM_ID", "Europe/London")
        print(json.dumps(crons, indent=2))
        return
    
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nExamples:")
        print("  python3 setup_crons.py 123456789 'Europe/London'")
        print("  python3 setup_crons.py 123456789 'America/New_York'")
        print("  python3 setup_crons.py --list")
        sys.exit(1)
    
    telegram_id = sys.argv[1]
    timezone = sys.argv[2]
    
    print(f"🏆 Sports Ticker - Cron Setup")
    print(f"="*40)
    print(f"Telegram ID: {telegram_id}")
    print(f"Timezone: {timezone}")
    print()
    
    crons = get_cron_configs(telegram_id, timezone)
    
    # Try openclaw CLI first
    print("Attempting to create crons via openclaw CLI...")
    success_count = 0
    
    for cron in crons:
        print(f"  Creating '{cron['name']}'...", end=" ")
        if create_cron_via_openclaw(cron):
            print("✅")
            success_count += 1
        else:
            print("❌ (manual setup needed)")
    
    if success_count == len(crons):
        print(f"\n✅ All {len(crons)} cron jobs created successfully!")
        print("\n📌 How it works:")
        print("  1. 'football-match-check' runs daily at 9 AM")
        print("  2. If a match is found, it updates 'spurs-live-ticker' schedule")
        print("  3. 'spurs-live-ticker' then runs every 2 mins during the match")
        print("  4. 'spurs-reminder' fires 30 mins before kickoff")
    else:
        print(f"\n⚠️  {len(crons) - success_count} cron(s) need manual setup.")
        print_manual_instructions(crons)
    
    # Also save configs to file for reference
    config_file = SKILL_DIR / "cron_configs.json"
    with open(config_file, "w") as f:
        json.dump(crons, f, indent=2)
    print(f"\n📄 Cron configs saved to: {config_file}")


if __name__ == "__main__":
    main()
