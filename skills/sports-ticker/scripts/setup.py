#!/usr/bin/env python3
"""
🏆 Sports Ticker - Interactive Setup Wizard

First-run onboarding that guides you through:
- Selecting your sports
- Picking your favorite teams/drivers
- Configuring alerts & preferences
- Setting quiet hours

Run: python3 scripts/setup.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from espn import search_team, SPORT_MAPPING

# Paths
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config.json"
CONFIG_EXAMPLE = SKILL_DIR / "config.example.json"

# ═══════════════════════════════════════════════════════════════════════════════
# SPORT CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════════

SPORTS = {
    "soccer": {
        "name": "Soccer/Football",
        "emoji": "⚽",
        "espn_sport": "soccer",
        "popular_teams": [
            ("Real Madrid", "86", ["esp.1", "uefa.champions"], "⚪"),
            ("Barcelona", "83", ["esp.1", "uefa.champions"], "🔵🔴"),
            ("Manchester United", "360", ["eng.1", "uefa.europa"], "🔴"),
            ("Liverpool", "364", ["eng.1", "uefa.champions"], "🔴"),
            ("Bayern Munich", "132", ["ger.1", "uefa.champions"], "🔴⚪"),
            ("Paris Saint-Germain", "160", ["fra.1", "uefa.champions"], "🔵🔴"),
            ("Juventus", "111", ["ita.1", "uefa.champions"], "⚪⚫"),
            ("Manchester City", "382", ["eng.1", "uefa.champions"], "🩵"),
            ("Chelsea", "363", ["eng.1", "uefa.europa"], "🔵"),
            ("Arsenal", "359", ["eng.1", "uefa.champions"], "🔴⚪"),
        ],
        "leagues": {
            "eng.1": "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            "esp.1": "La Liga 🇪🇸",
            "ger.1": "Bundesliga 🇩🇪",
            "ita.1": "Serie A 🇮🇹",
            "fra.1": "Ligue 1 🇫🇷",
            "uefa.champions": "Champions League 🏆",
            "usa.1": "MLS 🇺🇸",
        }
    },
    "nfl": {
        "name": "NFL",
        "emoji": "🏈",
        "espn_sport": "football",
        "popular_teams": [
            ("Kansas City Chiefs", "12", ["nfl"], "🔴🟡"),
            ("Dallas Cowboys", "6", ["nfl"], "⭐"),
            ("New England Patriots", "17", ["nfl"], "🔵🔴"),
            ("San Francisco 49ers", "25", ["nfl"], "🔴🟡"),
            ("Green Bay Packers", "9", ["nfl"], "💚🟡"),
            ("Philadelphia Eagles", "21", ["nfl"], "🦅"),
            ("Buffalo Bills", "2", ["nfl"], "🔵🔴"),
            ("Miami Dolphins", "15", ["nfl"], "🐬"),
            ("Las Vegas Raiders", "13", ["nfl"], "⚫"),
            ("Denver Broncos", "7", ["nfl"], "🧡🔵"),
        ],
        "leagues": {"nfl": "NFL 🏈"}
    },
    "nba": {
        "name": "NBA",
        "emoji": "🏀",
        "espn_sport": "basketball",
        "popular_teams": [
            ("Los Angeles Lakers", "13", ["nba"], "💜💛"),
            ("Golden State Warriors", "9", ["nba"], "💙💛"),
            ("Boston Celtics", "2", ["nba"], "☘️"),
            ("Chicago Bulls", "4", ["nba"], "🐂"),
            ("Miami Heat", "14", ["nba"], "🔥"),
            ("Brooklyn Nets", "17", ["nba"], "⚫⚪"),
            ("New York Knicks", "18", ["nba"], "🔵🧡"),
            ("Phoenix Suns", "21", ["nba"], "🌞"),
            ("Dallas Mavericks", "6", ["nba"], "🐴"),
            ("Milwaukee Bucks", "15", ["nba"], "🦌"),
        ],
        "leagues": {"nba": "NBA 🏀"}
    },
    "nhl": {
        "name": "NHL",
        "emoji": "🏒",
        "espn_sport": "hockey",
        "popular_teams": [
            ("Toronto Maple Leafs", "10", ["nhl"], "🍁"),
            ("New York Rangers", "4", ["nhl"], "🔵🔴"),
            ("Montreal Canadiens", "8", ["nhl"], "🔵⚪🔴"),
            ("Boston Bruins", "1", ["nhl"], "🐻"),
            ("Chicago Blackhawks", "4", ["nhl"], "🪶"),
            ("Edmonton Oilers", "22", ["nhl"], "🛢️"),
            ("Detroit Red Wings", "17", ["nhl"], "🐙"),
            ("Vegas Golden Knights", "37", ["nhl"], "⚔️"),
            ("Colorado Avalanche", "21", ["nhl"], "🏔️"),
            ("Pittsburgh Penguins", "5", ["nhl"], "🐧"),
        ],
        "leagues": {"nhl": "NHL 🏒"}
    },
    "mlb": {
        "name": "MLB",
        "emoji": "⚾",
        "espn_sport": "baseball",
        "popular_teams": [
            ("New York Yankees", "10", ["mlb"], "⚾"),
            ("Los Angeles Dodgers", "19", ["mlb"], "💙"),
            ("Boston Red Sox", "2", ["mlb"], "🔴"),
            ("Chicago Cubs", "16", ["mlb"], "🐻"),
            ("Atlanta Braves", "15", ["mlb"], "🪓"),
            ("Houston Astros", "18", ["mlb"], "⭐"),
            ("San Francisco Giants", "26", ["mlb"], "🧡⚫"),
            ("St. Louis Cardinals", "24", ["mlb"], "🐦"),
            ("Philadelphia Phillies", "22", ["mlb"], "🔔"),
            ("San Diego Padres", "25", ["mlb"], "🟤🟡"),
        ],
        "leagues": {"mlb": "MLB ⚾"}
    },
    "f1": {
        "name": "Formula 1",
        "emoji": "🏎️",
        "espn_sport": "racing",
        "popular_teams": [
            ("Red Bull Racing", "1", ["f1"], "🔵🔴"),
            ("Ferrari", "2", ["f1"], "🔴"),
            ("Mercedes", "3", ["f1"], "⚫🩵"),
            ("McLaren", "4", ["f1"], "🧡"),
            ("Aston Martin", "5", ["f1"], "💚"),
            ("Alpine", "6", ["f1"], "💙"),
            ("Williams", "7", ["f1"], "💙"),
            ("Haas", "8", ["f1"], "⚫🔴"),
            ("RB (AlphaTauri)", "9", ["f1"], "🔵"),
            ("Sauber (Stake)", "10", ["f1"], "💚"),
        ],
        "leagues": {"f1": "Formula 1 🏎️"}
    }
}

ALERT_TYPES = {
    "live": {
        "name": "Live Scores",
        "emoji": "⚡",
        "description": "Real-time alerts for every goal/score/major event"
    },
    "final": {
        "name": "Final Only",
        "emoji": "🏁",
        "description": "Just the final results when games end"
    },
    "digest": {
        "name": "Daily Digest",
        "emoji": "📰",
        "description": "One summary of all your teams' results each day"
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def clear_screen():
    """Clear terminal screen."""
    print("\033[2J\033[H", end="")

def print_header(title: str, emoji: str = "🏆"):
    """Print a fun header."""
    width = 60
    print()
    print("═" * width)
    print(f"{emoji}  {title.upper()}")
    print("═" * width)
    print()

def print_divider():
    """Print a subtle divider."""
    print("\n" + "─" * 50 + "\n")

def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    response = input(prompt).strip()
    return response if response else default

def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} ({default_str}): ").strip().lower()
    
    if not response:
        return default
    return response in ("y", "yes", "yeah", "yep", "si", "ja")

def get_time(prompt: str) -> str:
    """Get time input in HH:MM format."""
    while True:
        response = input(f"{prompt} (HH:MM, e.g. 22:00): ").strip()
        if not response:
            return None
        
        try:
            # Validate format
            parts = response.split(":")
            if len(parts) == 2:
                h, m = int(parts[0]), int(parts[1])
                if 0 <= h <= 23 and 0 <= m <= 59:
                    return f"{h:02d}:{m:02d}"
        except:
            pass
        
        print("❌ Please enter time as HH:MM (e.g. 22:00 or 07:30)")

def select_multiple(prompt: str, options: list, show_numbers: bool = True) -> list:
    """Allow user to select multiple items from a list."""
    print(f"\n{prompt}")
    print("Enter numbers separated by commas, or 'all' for everything")
    print()
    
    for i, (key, name) in enumerate(options, 1):
        print(f"  [{i}] {name}")
    
    print()
    response = input("Your choices: ").strip().lower()
    
    if response in ("all", "*", "a"):
        return [key for key, _ in options]
    
    selected = []
    try:
        nums = [int(x.strip()) for x in response.split(",") if x.strip()]
        for n in nums:
            if 1 <= n <= len(options):
                selected.append(options[n-1][0])
    except:
        pass
    
    return selected

# ═══════════════════════════════════════════════════════════════════════════════
# ONBOARDING STEPS
# ═══════════════════════════════════════════════════════════════════════════════

def step_welcome():
    """Welcome screen."""
    clear_screen()
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🏆  SPORTS TICKER  🏆                                       ║
    ║                                                               ║
    ║   ⚽ 🏈 🏀 🏒 ⚾ 🏎️                                            ║
    ║                                                               ║
    ║   Never miss a goal, touchdown, or checkered flag!           ║
    ║   Let's set up your personalized sports alerts.              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    input("Press ENTER to start... ")

def step_select_sports() -> list:
    """Step 1: Which sports do you follow?"""
    print_header("Step 1: Pick Your Sports", "📺")
    
    print("Which sports do you follow? (Select all that apply)\n")
    
    options = [(k, f"{v['emoji']} {v['name']}") for k, v in SPORTS.items()]
    selected = select_multiple("", options, show_numbers=True)
    
    if not selected:
        print("\n⚠️  You need to select at least one sport!")
        return step_select_sports()
    
    sport_names = [SPORTS[s]["emoji"] + " " + SPORTS[s]["name"] for s in selected]
    print(f"\n✅ Great choices! You selected: {', '.join(sport_names)}")
    input("\nPress ENTER to continue...")
    return selected

def step_select_teams(sports: list) -> list:
    """Step 2: Pick teams for each sport."""
    all_teams = []
    
    for sport_key in sports:
        sport = SPORTS[sport_key]
        print_header(f"Step 2: Your {sport['name']} Teams", sport['emoji'])
        
        print(f"Which {sport['name']} teams do you want to follow?\n")
        print("Popular teams:\n")
        
        # Show popular teams
        options = []
        for i, (name, espn_id, leagues, emoji) in enumerate(sport["popular_teams"], 1):
            options.append((espn_id, f"{emoji} {name}"))
            print(f"  [{i:2}] {emoji} {name}")
        
        print(f"\n  [{len(options)+1}] 🔍 Search for another team")
        print()
        
        response = input("Your choices (comma-separated numbers): ").strip()
        
        selected_ids = []
        search_requested = False
        
        try:
            nums = [int(x.strip()) for x in response.split(",") if x.strip()]
            for n in nums:
                if n == len(options) + 1:
                    search_requested = True
                elif 1 <= n <= len(options):
                    selected_ids.append(n - 1)
        except:
            pass
        
        # Add selected popular teams
        for idx in selected_ids:
            name, espn_id, leagues, emoji = sport["popular_teams"][idx]
            all_teams.append({
                "name": name,
                "short_name": name.split()[-1] if len(name.split()) > 1 else name,
                "emoji": emoji,
                "sport": sport["espn_sport"],
                "espn_id": espn_id,
                "espn_leagues": leagues,
                "enabled": True
            })
        
        # Search for custom teams
        if search_requested:
            while True:
                print()
                team_name = input("🔍 Enter team name to search (or 'done'): ").strip()
                if team_name.lower() in ("done", "d", ""):
                    break
                
                print(f"\nSearching for '{team_name}'...\n")
                results = search_team(team_name, sport["espn_sport"])
                
                if results:
                    seen = set()
                    unique_results = []
                    for r in results[:10]:  # Limit to 10
                        key = (r['id'], r['name'])
                        if key not in seen:
                            seen.add(key)
                            unique_results.append(r)
                    
                    for i, r in enumerate(unique_results, 1):
                        print(f"  [{i}] {r['name']} ({r['league_name']})")
                    
                    pick = input("\nSelect team number (or skip): ").strip()
                    try:
                        idx = int(pick) - 1
                        if 0 <= idx < len(unique_results):
                            r = unique_results[idx]
                            emoji = input(f"Emoji for {r['name']} [{sport['emoji']}]: ").strip() or sport['emoji']
                            
                            all_teams.append({
                                "name": r['name'],
                                "short_name": r['name'].split()[-1],
                                "emoji": emoji,
                                "sport": sport["espn_sport"],
                                "espn_id": r['id'],
                                "espn_leagues": [r['league']],
                                "enabled": True
                            })
                            print(f"✅ Added {r['name']}!")
                    except:
                        pass
                else:
                    print("No results found. Try a different name.")
        
        if not any(t["sport"] == sport["espn_sport"] for t in all_teams):
            print(f"\n⚠️  No {sport['name']} teams selected. Skipping...")
        else:
            team_count = len([t for t in all_teams if t["sport"] == sport["espn_sport"]])
            print(f"\n✅ {team_count} {sport['name']} team(s) added!")
        
        input("\nPress ENTER to continue...")
    
    return all_teams

def step_alert_preferences() -> dict:
    """Step 3: How do you want alerts?"""
    print_header("Step 3: Alert Style", "🔔")
    
    print("How do you want to receive alerts?\n")
    
    for i, (key, info) in enumerate(ALERT_TYPES.items(), 1):
        print(f"  [{i}] {info['emoji']} {info['name']}")
        print(f"      {info['description']}\n")
    
    choice = input("Your choice (1-3) [1]: ").strip() or "1"
    
    try:
        idx = int(choice) - 1
        alert_style = list(ALERT_TYPES.keys())[idx]
    except:
        alert_style = "live"
    
    selected = ALERT_TYPES[alert_style]
    print(f"\n✅ {selected['emoji']} {selected['name']} it is!")
    
    # Build alerts config based on choice
    if alert_style == "live":
        alerts = {
            "goals": True,
            "touchdowns": True,
            "red_cards": True,
            "halftime": True,
            "fulltime": True,
            "kickoff": True,
            "mode": "live"
        }
    elif alert_style == "final":
        alerts = {
            "goals": False,
            "touchdowns": False,
            "red_cards": False,
            "halftime": False,
            "fulltime": True,
            "kickoff": False,
            "mode": "final"
        }
    else:  # digest
        alerts = {
            "goals": False,
            "touchdowns": False,
            "red_cards": False,
            "halftime": False,
            "fulltime": False,
            "kickoff": False,
            "mode": "digest"
        }
    
    input("\nPress ENTER to continue...")
    return alerts

def step_game_reminders() -> bool:
    """Step 4: Game-day reminders?"""
    print_header("Step 4: Game-Day Reminders", "⏰")
    
    print("Want a heads-up before your teams play?\n")
    print("  📅 Get notified 30 minutes before kick-off/tip-off")
    print("  🎮 Never miss the start of a game again!\n")
    
    enabled = get_yes_no("Enable game-day reminders?", default=True)
    
    if enabled:
        print("\n✅ ⏰ You'll get a 30-minute heads-up before games!")
    else:
        print("\n👍 No problem, you'll just get live alerts.")
    
    input("\nPress ENTER to continue...")
    return enabled

def step_quiet_hours() -> dict:
    """Step 5: Quiet hours?"""
    print_header("Step 5: Quiet Hours (Optional)", "🌙")
    
    print("Some games run late! Set quiet hours to pause alerts.\n")
    print("During quiet hours, alerts are saved and sent when you wake up.\n")
    
    if not get_yes_no("Set up quiet hours?", default=False):
        print("\n👍 No quiet hours - you'll get alerts 24/7!")
        input("\nPress ENTER to continue...")
        return None
    
    print()
    start = get_time("Quiet hours START")
    end = get_time("Quiet hours END")
    
    if start and end:
        print(f"\n✅ 🌙 Quiet hours: {start} to {end}")
        input("\nPress ENTER to continue...")
        return {"start": start, "end": end}
    
    print("\n👍 No quiet hours set.")
    input("\nPress ENTER to continue...")
    return None

def step_summary(config: dict):
    """Show final summary."""
    print_header("Setup Complete!", "🎉")
    
    print("Here's your configuration:\n")
    
    # Teams by sport
    teams_by_sport = {}
    for team in config.get("teams", []):
        sport = team.get("sport", "other")
        if sport not in teams_by_sport:
            teams_by_sport[sport] = []
        teams_by_sport[sport].append(team)
    
    for sport, teams in teams_by_sport.items():
        sport_emoji = {"soccer": "⚽", "football": "🏈", "basketball": "🏀", 
                       "hockey": "🏒", "baseball": "⚾", "racing": "🏎️"}.get(sport, "🏆")
        print(f"  {sport_emoji} {sport.upper()}")
        for t in teams:
            print(f"     {t.get('emoji', '')} {t['name']}")
        print()
    
    # Alert style
    mode = config.get("alerts", {}).get("mode", "live")
    mode_display = {"live": "⚡ Live Scores", "final": "🏁 Final Only", "digest": "📰 Daily Digest"}
    print(f"  🔔 Alerts: {mode_display.get(mode, mode)}")
    
    # Reminders
    if config.get("preferences", {}).get("game_reminders"):
        print("  ⏰ Game-day reminders: ON")
    
    # Quiet hours
    quiet = config.get("preferences", {}).get("quiet_hours")
    if quiet:
        print(f"  🌙 Quiet hours: {quiet['start']} - {quiet['end']}")
    
    print()
    print("═" * 50)
    print()
    print(f"Config saved to: {CONFIG_FILE}")
    print()
    print("🚀 You're all set! Here's what you can do next:")
    print()
    print("  python3 scripts/ticker.py           # Check your teams now")
    print("  python3 scripts/live_monitor.py     # Start live monitoring")
    print("  python3 scripts/setup_crons.py      # Set up auto-alerts")
    print()
    print("Enjoy the games! ⚽🏈🏀🏒⚾🏎️")
    print()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ONBOARDING FLOW
# ═══════════════════════════════════════════════════════════════════════════════

def run_onboarding():
    """Run the full onboarding wizard."""
    try:
        # Step 0: Welcome
        step_welcome()
        
        # Step 1: Select sports
        selected_sports = step_select_sports()
        
        # Step 2: Select teams for each sport
        teams = step_select_teams(selected_sports)
        
        if not teams:
            print("\n❌ No teams configured. Please run setup again.")
            return
        
        # Step 3: Alert preferences
        alerts = step_alert_preferences()
        
        # Step 4: Game-day reminders
        game_reminders = step_game_reminders()
        
        # Step 5: Quiet hours
        quiet_hours = step_quiet_hours()
        
        # Build final config
        config = {
            "teams": teams,
            "alerts": alerts,
            "preferences": {
                "game_reminders": game_reminders,
                "quiet_hours": quiet_hours
            },
            "_setup_completed": datetime.now().isoformat()
        }
        
        # Save config
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        
        # Show summary
        step_summary(config)
        
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled. Run again anytime!")
        sys.exit(0)

def find_team_id(team_name: str, sport: str = "soccer"):
    """Search for a team's ESPN ID."""
    print(f"🔍 Searching for '{team_name}' in {sport}...\n")
    
    results = search_team(team_name, sport)
    
    if results:
        seen = set()
        print("Found:\n")
        for r in results:
            key = (r['id'], r['name'])
            if key not in seen:
                seen.add(key)
                print(f"  ESPN ID: {r['id']:6} | {r['name']:30} | {r['league_name']}")
    else:
        print("No teams found. Tips:")
        print("  - Try the official team name (e.g., 'Manchester United')")
        print("  - Check available leagues: python3 scripts/espn.py leagues [sport]")
        print("  - Some lower leagues may not be indexed")

def check_first_run() -> bool:
    """Check if this is the first run (no config exists)."""
    return not CONFIG_FILE.exists()

# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # No args - run onboarding (or interactive menu if config exists)
        if check_first_run():
            run_onboarding()
        else:
            print("🏆 Sports Ticker Setup\n")
            print("Config already exists! Options:\n")
            print("  1. Run setup wizard again (overwrites config)")
            print("  2. Find a team ID")
            print("  3. Exit")
            
            choice = input("\nChoice (1-3): ").strip()
            
            if choice == "1":
                confirm = get_yes_no("\n⚠️  This will replace your current config. Continue?", default=False)
                if confirm:
                    run_onboarding()
                else:
                    print("👍 Keeping existing config.")
            elif choice == "2":
                name = input("Team name: ").strip()
                sport = input("Sport (soccer/football/basketball/hockey/baseball/racing) [soccer]: ").strip() or "soccer"
                if name:
                    find_team_id(name, sport)
            else:
                print("👋 Bye!")
    
    elif sys.argv[1] == "find":
        # Find team ID
        if len(sys.argv) < 3:
            print("Usage: setup.py find <team_name> [sport]")
            print("Sports: soccer, football, basketball, hockey, baseball, racing")
        else:
            args = sys.argv[2:]
            sport = "soccer"
            if args and args[-1] in SPORT_MAPPING:
                sport = args[-1]
                team_name = " ".join(args[:-1])
            else:
                team_name = " ".join(args)
            find_team_id(team_name, sport)
    
    elif sys.argv[1] == "--force":
        # Force run onboarding
        run_onboarding()
    
    else:
        print("🏆 Sports Ticker Setup")
        print()
        print("Usage:")
        print("  setup.py                      - Interactive setup (or menu if config exists)")
        print("  setup.py --force              - Run setup wizard (even if config exists)")
        print("  setup.py find <team> [sport]  - Find team ESPN ID")
        print()
        print("Sports: soccer, football, basketball, hockey, baseball, racing")
