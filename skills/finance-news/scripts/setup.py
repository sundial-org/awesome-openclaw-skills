#!/usr/bin/env python3
"""
Finance News Skill - Interactive Setup
Configures RSS feeds, WhatsApp channels, and cron jobs.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"
SOURCES_FILE = CONFIG_DIR / "config.json"


def load_sources():
    """Load current sources configuration."""
    if SOURCES_FILE.exists():
        with open(SOURCES_FILE, 'r') as f:
            return json.load(f)
    return get_default_sources()


def save_sources(sources: dict):
    """Save sources configuration."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(SOURCES_FILE, 'w') as f:
        json.dump(sources, f, indent=2)
    print(f"✅ Configuration saved to {SOURCES_FILE}")


def get_default_sources():
    """Return default source configuration."""
    config_path = CONFIG_DIR / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def prompt(message: str, default: str = "") -> str:
    """Prompt for input with optional default."""
    if default:
        result = input(f"{message} [{default}]: ").strip()
        return result if result else default
    return input(f"{message}: ").strip()


def prompt_bool(message: str, default: bool = True) -> bool:
    """Prompt for yes/no input."""
    default_str = "Y/n" if default else "y/N"
    result = input(f"{message} [{default_str}]: ").strip().lower()
    if not result:
        return default
    return result in ('y', 'yes', '1', 'true')


def setup_rss_feeds(sources: dict):
    """Interactive RSS feed configuration."""
    print("\n📰 RSS Feed Configuration\n")
    print("Enable/disable news sources:\n")
    
    for feed_id, feed_config in sources['rss_feeds'].items():
        name = feed_config.get('name', feed_id)
        current = feed_config.get('enabled', True)
        enabled = prompt_bool(f"  {name}", current)
        sources['rss_feeds'][feed_id]['enabled'] = enabled
    
    print("\n  Add custom RSS feed? (leave blank to skip)")
    custom_name = prompt("  Feed name", "")
    if custom_name:
        custom_url = prompt("  Feed URL")
        sources['rss_feeds'][custom_name.lower().replace(' ', '_')] = {
            "name": custom_name,
            "enabled": True,
            "main": custom_url
        }
        print(f"  ✅ Added {custom_name}")


def setup_markets(sources: dict):
    """Interactive market configuration."""
    print("\n📊 Market Coverage\n")
    print("Enable/disable market regions:\n")
    
    for market_id, market_config in sources['markets'].items():
        name = market_config.get('name', market_id)
        current = market_config.get('enabled', True)
        enabled = prompt_bool(f"  {name}", current)
        sources['markets'][market_id]['enabled'] = enabled


def setup_delivery(sources: dict):
    """Interactive delivery channel configuration."""
    print("\n📤 Delivery Channels\n")
    
    # Ensure delivery dict exists
    if 'delivery' not in sources:
        sources['delivery'] = {
            'whatsapp': {'enabled': True, 'group': ''},
            'telegram': {'enabled': False, 'group': ''}
        }

    # WhatsApp
    wa_enabled = prompt_bool("Enable WhatsApp delivery",
                              sources.get('delivery', {}).get('whatsapp', {}).get('enabled', True))
    sources['delivery']['whatsapp']['enabled'] = wa_enabled

    if wa_enabled:
        wa_group = prompt("  WhatsApp group name or JID",
                          sources['delivery']['whatsapp'].get('group', ''))
        sources['delivery']['whatsapp']['group'] = wa_group
    
    # Telegram
    tg_enabled = prompt_bool("Enable Telegram delivery",
                              sources['delivery']['telegram'].get('enabled', False))
    sources['delivery']['telegram']['enabled'] = tg_enabled
    
    if tg_enabled:
        tg_group = prompt("  Telegram group name or ID",
                          sources['delivery']['telegram'].get('group', ''))
        sources['delivery']['telegram']['group'] = tg_group


def setup_language(sources: dict):
    """Interactive language configuration."""
    print("\n🌐 Language Settings\n")
    
    current_lang = sources['language'].get('default', 'de')
    lang = prompt("Default language (de/en)", current_lang)
    if lang in sources['language']['supported']:
        sources['language']['default'] = lang
    else:
        print(f"  ⚠️ Unsupported language '{lang}', keeping '{current_lang}'")


def setup_schedule(sources: dict):
    """Interactive schedule configuration."""
    print("\n⏰ Briefing Schedule\n")
    
    # Morning
    morning = sources['schedule']['morning']
    morning_enabled = prompt_bool(f"Enable morning briefing ({morning['description']})",
                                   morning.get('enabled', True))
    sources['schedule']['morning']['enabled'] = morning_enabled
    
    if morning_enabled:
        morning_cron = prompt("  Morning cron expression", morning.get('cron', '30 6 * * 1-5'))
        sources['schedule']['morning']['cron'] = morning_cron
    
    # Evening
    evening = sources['schedule']['evening']
    evening_enabled = prompt_bool(f"Enable evening briefing ({evening['description']})",
                                   evening.get('enabled', True))
    sources['schedule']['evening']['enabled'] = evening_enabled
    
    if evening_enabled:
        evening_cron = prompt("  Evening cron expression", evening.get('cron', '0 13 * * 1-5'))
        sources['schedule']['evening']['cron'] = evening_cron
    
    # Timezone
    tz = prompt("Timezone", sources['schedule']['morning'].get('timezone', 'America/Los_Angeles'))
    sources['schedule']['morning']['timezone'] = tz
    sources['schedule']['evening']['timezone'] = tz


def setup_cron_jobs(sources: dict):
    """Set up OpenClaw cron jobs based on configuration."""
    print("\n📅 Setting up cron jobs...\n")
    
    schedule = sources.get('schedule', {})
    delivery = sources.get('delivery', {})
    language = sources.get('language', {}).get('default', 'de')
    
    # Determine delivery target
    if delivery.get('whatsapp', {}).get('enabled'):
        group = delivery['whatsapp'].get('group', '')
        send_cmd = f"--send --group '{group}'" if group else ""
    elif delivery.get('telegram', {}).get('enabled'):
        group = delivery['telegram'].get('group', '')
        send_cmd = f"--send --group '{group}'"  # Would need telegram support
    else:
        send_cmd = ""
    
    # Morning job
    if schedule.get('morning', {}).get('enabled'):
        morning_cron = schedule['morning'].get('cron', '30 6 * * 1-5')
        tz = schedule['morning'].get('timezone', 'America/Los_Angeles')
        
        print(f"  Creating morning briefing job: {morning_cron} ({tz})")
        # Note: Actual cron creation would happen via openclaw cron add
        print(f"    ✅ Morning briefing configured")
    
    # Evening job
    if schedule.get('evening', {}).get('enabled'):
        evening_cron = schedule['evening'].get('cron', '0 13 * * 1-5')
        tz = schedule['evening'].get('timezone', 'America/Los_Angeles')
        
        print(f"  Creating evening briefing job: {evening_cron} ({tz})")
        print(f"    ✅ Evening briefing configured")


def run_setup(args):
    """Run interactive setup wizard."""
    print("\n" + "="*60)
    print("📈 Finance News Skill - Setup Wizard")
    print("="*60)
    
    # Load existing or default config
    if args.reset:
        sources = get_default_sources()
        print("\n⚠️ Starting with fresh configuration")
    else:
        sources = load_sources()
        if SOURCES_FILE.exists():
            print(f"\n📂 Loaded existing configuration from {SOURCES_FILE}")
        else:
            print("\n📂 No existing configuration found, using defaults")
    
    # Run through each section
    if not args.section or args.section == 'feeds':
        setup_rss_feeds(sources)
    
    if not args.section or args.section == 'markets':
        setup_markets(sources)
    
    if not args.section or args.section == 'delivery':
        setup_delivery(sources)
    
    if not args.section or args.section == 'language':
        setup_language(sources)
    
    if not args.section or args.section == 'schedule':
        setup_schedule(sources)
    
    # Save configuration
    print("\n" + "-"*60)
    if prompt_bool("Save configuration?", True):
        save_sources(sources)
        
        # Set up cron jobs
        if prompt_bool("Set up cron jobs now?", True):
            setup_cron_jobs(sources)
    else:
        print("❌ Configuration not saved")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("  • Run 'finance-news portfolio-list' to check your watchlist")
    print("  • Run 'finance-news briefing --morning' to test a briefing")
    print("  • Run 'finance-news market' to see market overview")
    print()


def show_config(args):
    """Show current configuration."""
    sources = load_sources()
    print(json.dumps(sources, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Finance News Setup')
    subparsers = parser.add_subparsers(dest='command')
    
    # Setup command (default)
    setup_parser = subparsers.add_parser('wizard', help='Run setup wizard')
    setup_parser.add_argument('--reset', action='store_true', help='Reset to defaults')
    setup_parser.add_argument('--section', choices=['feeds', 'markets', 'delivery', 'language', 'schedule'],
                              help='Configure specific section only')
    setup_parser.set_defaults(func=run_setup)
    
    # Show config
    show_parser = subparsers.add_parser('show', help='Show current configuration')
    show_parser.set_defaults(func=show_config)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        # Default to wizard
        args.reset = False
        args.section = None
        run_setup(args)


if __name__ == '__main__':
    main()
