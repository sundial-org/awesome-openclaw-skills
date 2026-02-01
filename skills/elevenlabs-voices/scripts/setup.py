#!/usr/bin/env python3
"""
ElevenLabs Voices - Interactive Setup Wizard
Creates config.json with API key and user preferences.
Run this on first use or to reconfigure settings.
"""

import json
import os
import re
import sys
from pathlib import Path

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def print_banner():
    """Print welcome banner."""
    print(f"""
{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎙️  ElevenLabs Voices - Setup Wizard                    ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝{Colors.RESET}
""")
    print(f"{Colors.DIM}Welcome! Let's configure your ElevenLabs integration.{Colors.RESET}")
    print(f"{Colors.DIM}This will create a config.json file in the skill directory.{Colors.RESET}")
    print()
    print(f"{Colors.GREEN}🔒 Privacy: Your API key is stored locally only.{Colors.RESET}")
    print(f"{Colors.GREEN}   It never leaves your machine and is in .gitignore.{Colors.RESET}")
    print()

def validate_api_key(key: str) -> bool:
    """Validate ElevenLabs API key format."""
    # ElevenLabs keys are typically 32 hex characters
    if not key:
        return False
    # Allow various formats - ElevenLabs uses different key formats
    if len(key) < 20:
        return False
    # Basic check for alphanumeric key
    if not re.match(r'^[a-zA-Z0-9_-]+$', key):
        return False
    return True

def get_input(prompt: str, required: bool = True, default: str = None) -> str:
    """Get user input with optional default."""
    if default:
        prompt = f"{prompt} [{Colors.DIM}{default}{Colors.RESET}]: "
    else:
        prompt = f"{prompt}: "
    
    while True:
        value = input(f"{Colors.CYAN}>{Colors.RESET} {prompt}").strip()
        if not value and default:
            return default
        if not value and required:
            print(f"{Colors.RED}  This field is required.{Colors.RESET}")
            continue
        return value

def get_choice(prompt: str, options: list, default: str = None) -> str:
    """Get user choice from a list of options."""
    print(f"\n{Colors.BOLD}{prompt}{Colors.RESET}")
    for i, opt in enumerate(options, 1):
        marker = f"{Colors.GREEN}*{Colors.RESET}" if opt == default else " "
        print(f"  {marker} {i}. {opt}")
    
    while True:
        choice = input(f"\n{Colors.CYAN}>{Colors.RESET} Enter number [1-{len(options)}]: ").strip()
        if not choice and default:
            return default
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print(f"{Colors.RED}  Please enter a number between 1 and {len(options)}.{Colors.RESET}")

def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no response."""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{Colors.CYAN}>{Colors.RESET} {prompt} [{default_str}]: ").strip().lower()
        if not response:
            return default
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print(f"{Colors.RED}  Please enter 'y' or 'n'.{Colors.RESET}")

def get_optional_number(prompt: str) -> float | None:
    """Get optional numeric input."""
    while True:
        value = input(f"{Colors.CYAN}>{Colors.RESET} {prompt} [skip]: ").strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            print(f"{Colors.RED}  Please enter a valid number or press Enter to skip.{Colors.RESET}")

def run_setup():
    """Run the interactive setup wizard."""
    print_banner()
    
    config = {}
    
    # Step 1: API Key (required)
    print(f"\n{Colors.BOLD}━━━ Step 1/6: API Key ━━━{Colors.RESET}")
    print(f"{Colors.DIM}Get your API key from: https://elevenlabs.io/app/settings/api-keys{Colors.RESET}")
    print()
    
    while True:
        api_key = get_input("Enter your ElevenLabs API key", required=True)
        if validate_api_key(api_key):
            config['apiKey'] = api_key
            print(f"{Colors.GREEN}  ✓ API key accepted{Colors.RESET}")
            break
        print(f"{Colors.RED}  Invalid API key format. Keys are typically 32+ alphanumeric characters.{Colors.RESET}")
    
    # Step 2: Default Voice
    print(f"\n{Colors.BOLD}━━━ Step 2/6: Default Voice ━━━{Colors.RESET}")
    popular_voices = [
        "Rachel (warm, friendly - recommended)",
        "Adam (narrator, documentaries)",
        "Bella (professional, business)",
        "Antoni (deep, confident)",
        "George (British storyteller)",
        "Alice (British educator)",
        "Brian (comforting, calm)",
        "Matilda (corporate, news)",
        "Liam (social media, energetic)"
    ]
    voice_choice = get_choice("Choose your default voice:", popular_voices, default="Rachel (warm, friendly - recommended)")
    config['defaultVoice'] = voice_choice.split(' ')[0].lower()
    print(f"{Colors.GREEN}  ✓ Default voice: {config['defaultVoice']}{Colors.RESET}")
    
    # Step 3: Default Language
    print(f"\n{Colors.BOLD}━━━ Step 3/6: Default Language ━━━{Colors.RESET}")
    languages = [
        "English (en)",
        "German (de)",
        "Spanish (es)",
        "French (fr)",
        "Italian (it)",
        "Portuguese (pt)",
        "Dutch (nl)",
        "Polish (pl)",
        "Japanese (ja)",
        "Korean (ko)",
        "Chinese (zh)"
    ]
    lang_choice = get_choice("Default language for synthesis:", languages, default="English (en)")
    # Extract language code from parentheses
    config['defaultLanguage'] = lang_choice.split('(')[1].rstrip(')')
    print(f"{Colors.GREEN}  ✓ Default language: {config['defaultLanguage']}{Colors.RESET}")
    
    # Step 4: Audio Quality
    print(f"\n{Colors.BOLD}━━━ Step 4/6: Audio Quality ━━━{Colors.RESET}")
    print(f"{Colors.DIM}Higher quality uses more API quota.{Colors.RESET}")
    qualities = [
        "standard (faster, smaller files)",
        "high (better quality, larger files)"
    ]
    quality_choice = get_choice("Audio quality preference:", qualities, default="standard (faster, smaller files)")
    config['audioQuality'] = quality_choice.split(' ')[0]
    print(f"{Colors.GREEN}  ✓ Audio quality: {config['audioQuality']}{Colors.RESET}")
    
    # Step 5: Cost Tracking
    print(f"\n{Colors.BOLD}━━━ Step 5/6: Cost Tracking ━━━{Colors.RESET}")
    print(f"{Colors.DIM}Track character usage and estimate costs.{Colors.RESET}")
    config['costTracking'] = get_yes_no("Enable cost tracking?", default=True)
    status = "enabled" if config['costTracking'] else "disabled"
    print(f"{Colors.GREEN}  ✓ Cost tracking: {status}{Colors.RESET}")
    
    # Step 6: Budget Limit (optional)
    print(f"\n{Colors.BOLD}━━━ Step 6/6: Budget Limit ━━━{Colors.RESET}")
    print(f"{Colors.DIM}Optional: Set a monthly spending limit (in USD).{Colors.RESET}")
    print(f"{Colors.DIM}You'll get a warning when approaching this limit.{Colors.RESET}")
    budget = get_optional_number("Monthly budget limit (USD)")
    if budget is not None:
        config['monthlyBudget'] = budget
        print(f"{Colors.GREEN}  ✓ Monthly budget: ${budget:.2f}{Colors.RESET}")
    else:
        print(f"{Colors.DIM}  ✓ No budget limit set{Colors.RESET}")
    
    # Add metadata
    config['_version'] = '2.1.0'
    config['_created'] = True
    
    return config

def save_config(config: dict, path: Path):
    """Save configuration to JSON file."""
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"\n{Colors.GREEN}✓ Configuration saved to: {path}{Colors.RESET}")

def print_summary(config: dict):
    """Print configuration summary."""
    print(f"""
{Colors.CYAN}{Colors.BOLD}━━━ Configuration Summary ━━━{Colors.RESET}

  API Key:        {Colors.DIM}****{config['apiKey'][-4:]}{Colors.RESET}
  Default Voice:  {config['defaultVoice']}
  Language:       {config['defaultLanguage']}
  Audio Quality:  {config['audioQuality']}
  Cost Tracking:  {'enabled' if config['costTracking'] else 'disabled'}
  Monthly Budget: {f"${config['monthlyBudget']:.2f}" if config.get('monthlyBudget') else 'not set'}
""")

def print_next_steps():
    """Print next steps after setup."""
    print(f"""{Colors.CYAN}{Colors.BOLD}━━━ You're all set! ━━━{Colors.RESET}

{Colors.BOLD}Try these commands:{Colors.RESET}

  # Generate speech
  python3 scripts/tts.py --text "Hello world" --voice rachel

  # List all voices
  python3 scripts/tts.py --list

  # Generate sound effects
  python3 scripts/sfx.py --prompt "Thunder rumbling"

  # Check usage stats
  python3 scripts/tts.py --stats

{Colors.DIM}Full documentation: SKILL.md{Colors.RESET}
""")

def main():
    """Main entry point."""
    # Determine config path (skill root directory)
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    config_path = skill_dir / 'config.json'
    
    # Check if config already exists
    if config_path.exists():
        print(f"\n{Colors.YELLOW}⚠ Configuration already exists at: {config_path}{Colors.RESET}")
        if not get_yes_no("Do you want to reconfigure?", default=False):
            print(f"{Colors.DIM}Setup cancelled. Existing config preserved.{Colors.RESET}")
            return 0
        print()
    
    try:
        config = run_setup()
        save_config(config, config_path)
        print_summary(config)
        print_next_steps()
        return 0
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled.{Colors.RESET}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
