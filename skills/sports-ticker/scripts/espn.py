#!/usr/bin/env python3
"""
ESPN Sports API - FREE live scores with goal scorers, cards, and more!

No API key required. Works for:
- Football/Soccer (Premier League, Champions League, La Liga, Serie A, etc.)
- NFL, NBA, MLB, NHL (American sports)
- And many more...

Base URL: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}
"""

import urllib.request
import json
import sys
from typing import Optional
from pathlib import Path

# ESPN API Base
BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

# Sport-to-URL mapping
SPORT_MAPPING = {
    "soccer": "soccer",
    "football": "football",  # American football
    "basketball": "basketball",
    "hockey": "hockey",
    "baseball": "baseball",
    "racing": "racing",
}

# League display names by sport
LEAGUES = {
    "soccer": {
        # European
        "eng.1": "Premier League",
        "eng.2": "Championship",
        "esp.1": "La Liga",
        "ger.1": "Bundesliga",
        "ita.1": "Serie A",
        "fra.1": "Ligue 1",
        "ned.1": "Eredivisie",
        "por.1": "Primeira Liga",
        "ger.1": "German Bundesliga",
        # European competitions
        "uefa.champions": "Champions League",
        "uefa.europa": "Europa League",
        "uefa.europa.conf": "Conference League",
        # Americas
        "usa.1": "MLS",
        "mex.1": "Liga MX",
        "bra.1": "Brasileirão",
        "arg.1": "Argentine Primera",
        # International
        "fifa.world": "World Cup",
        "uefa.euro": "Euros",
    },
    "football": {
        "nfl": "NFL",
    },
    "basketball": {
        "nba": "NBA",
        "wnba": "WNBA",
        "mens-college-basketball": "NCAA Basketball (M)",
        "womens-college-basketball": "NCAA Basketball (W)",
    },
    "hockey": {
        "nhl": "NHL",
    },
    "baseball": {
        "mlb": "MLB",
    },
    "racing": {
        "f1": "Formula 1",
    },
}

# Backward compatibility
FOOTBALL_LEAGUES = LEAGUES["soccer"]

def api_request(endpoint: str) -> dict:
    """Make request to ESPN API (no auth needed!)."""
    url = f"{BASE_URL}/{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

def get_scoreboard(sport: str = "soccer", league: str = "eng.1") -> dict:
    """Get current scoreboard for a league."""
    return api_request(f"{sport}/{league}/scoreboard")

def get_match_details(event_id: str, sport: str = "soccer", league: str = "eng.1") -> dict:
    """Get detailed match info including events."""
    return api_request(f"{sport}/{league}/summary?event={event_id}")

def get_all_teams(league: str = "eng.1", sport: str = "soccer") -> list:
    """Get ALL teams in a league (not just today's matches)."""
    sport_url = SPORT_MAPPING.get(sport, sport)
    data = api_request(f"{sport_url}/{league}/teams")
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    return [t.get("team", {}) for t in teams]

def search_team(team_name: str, sport: str = "soccer", leagues: list = None) -> list:
    """Search for a team across leagues using the teams endpoint."""
    if leagues is None:
        # Default leagues based on sport
        if sport == "soccer":
            leagues = ["eng.1", "esp.1", "ger.1", "ita.1", "fra.1", "uefa.champions"]
        elif sport == "football":
            leagues = ["nfl"]
        elif sport == "basketball":
            leagues = ["nba"]
        elif sport == "hockey":
            leagues = ["nhl"]
        elif sport == "baseball":
            leagues = ["mlb"]
        elif sport == "racing":
            leagues = ["f1"]
        else:
            leagues = []
    
    team_lower = team_name.lower()
    results = []
    sport_leagues = LEAGUES.get(sport, {})
    
    for league in leagues:
        try:
            teams = get_all_teams(league, sport)
            for team in teams:
                if team_lower in team.get("displayName", "").lower() or \
                   team_lower in team.get("shortDisplayName", "").lower() or \
                   team_lower in team.get("nickname", "").lower():
                    results.append({
                        "id": team.get("id"),
                        "name": team.get("displayName"),
                        "short": team.get("shortDisplayName"),
                        "sport": sport,
                        "league": league,
                        "league_name": sport_leagues.get(league, league)
                    })
        except Exception:
            continue
    
    return results

def find_team_match(team_id: str, leagues: list = None, sport: str = "soccer") -> Optional[dict]:
    """Find a match for a specific team."""
    if leagues is None:
        leagues = ["eng.1", "uefa.champions"]
    
    for league in leagues:
        try:
            data = get_scoreboard(sport, league)
            for event in data.get("events", []):
                for comp in event.get("competitions", []):
                    for competitor in comp.get("competitors", []):
                        if str(competitor.get("team", {}).get("id")) == str(team_id):
                            return {
                                "event": event,
                                "league": league,
                                "event_id": event.get("id"),
                                "sport": sport
                            }
        except Exception:
            continue
    
    return None

def get_match_events(event_id: str, sport: str = "soccer", league: str = "eng.1") -> list:
    """Get key events (goals, cards) from a match."""
    details = get_match_details(event_id, sport, league)
    return details.get("keyEvents", [])

def format_event(event: dict, sport: str = "soccer") -> str:
    """Format a match/game event for display."""
    event_type = event.get("type", {}).get("text", "")
    clock = event.get("clock", {}).get("displayValue", "?'")
    team = event.get("team", {}).get("displayName", "")
    
    participants = event.get("participants", [])
    player = participants[0].get("athlete", {}).get("displayName", "") if participants else ""
    
    # Soccer events
    if sport == "soccer":
        if "Goal" in event_type:
            detail = ""
            if "Own Goal" in event_type:
                detail = " (OG)"
            elif "Penalty" in event_type:
                detail = " (pen)"
            return f"⚽ {clock} {player}{detail} ({team})"
        elif "Yellow" in event_type:
            return f"🟨 {clock} {player} ({team})"
        elif "Red" in event_type:
            return f"🟥 {clock} {player} ({team})"
        elif "Substitution" in event_type:
            return f"🔄 {clock} {player} ({team})"
    
    # American Football events
    elif sport == "football":
        if "Touchdown" in event_type:
            return f"🏈 {clock} TOUCHDOWN - {player} ({team})"
        elif "Field Goal" in event_type:
            return f"🎯 {clock} Field Goal - {player} ({team})"
        elif "Interception" in event_type:
            return f"🔒 {clock} INT - {player} ({team})"
    
    # Basketball events
    elif sport == "basketball":
        if "Three Point" in event_type or "3PT" in event_type:
            return f"🎯 {clock} 3-pointer - {player} ({team})"
        elif "Dunk" in event_type:
            return f"💪 {clock} DUNK - {player} ({team})"
    
    # Hockey events
    elif sport == "hockey":
        if "Goal" in event_type:
            return f"🏒 {clock} GOAL - {player} ({team})"
        elif "Penalty" in event_type:
            return f"⏱️ {clock} Penalty - {player} ({team})"
    
    # Baseball events
    elif sport == "baseball":
        if "Home Run" in event_type or "HR" in event_type:
            return f"⚾ {clock} HOME RUN - {player} ({team})"
    
    return f"📋 {clock} {event_type}: {player}"

def format_match(event: dict, include_events: bool = True, sport: str = "soccer", league: str = "eng.1") -> str:
    """Format a full match/game summary."""
    lines = []
    
    status = event.get("status", {})
    status_desc = status.get("type", {}).get("description", "Unknown")
    clock = status.get("displayClock", "")
    
    # Status header (sport-specific terminology)
    if status_desc == "In Progress":
        lines.append(f"🔴 LIVE {clock}")
    elif status_desc == "Halftime":
        if sport in ["football", "basketball"]:
            lines.append("⏸️ HALFTIME")
        else:
            lines.append("⏸️ HALFTIME")
    elif "End of" in status_desc:  # Basketball/Hockey periods
        lines.append(f"⏸️ {status_desc}")
    elif status_desc == "Final":
        if sport == "soccer":
            lines.append("🏁 FULL TIME")
        else:
            lines.append("🏁 FINAL")
    else:
        lines.append(f"📅 {status_desc}")
    
    # Teams and score
    competitions = event.get("competitions", [{}])[0]
    competitors = competitions.get("competitors", [])
    
    home = away = ""
    home_score = away_score = "0"
    
    for c in competitors:
        team_name = c.get("team", {}).get("displayName", "?")
        score = c.get("score", "0")
        if c.get("homeAway") == "home":
            home, home_score = team_name, score
        else:
            away, away_score = team_name, score
    
    lines.append(f"**{home} {home_score} - {away_score} {away}**")
    
    # Events
    if include_events:
        event_id = event.get("id")
        if event_id:
            try:
                events = get_match_events(event_id, sport, league)
                if events:
                    lines.append("")
                    for e in events[-8:]:
                        lines.append(format_event(e, sport))
            except Exception:
                pass
    
    return "\n".join(lines)

def list_leagues(sport: str = None):
    """List available leagues by sport."""
    if sport:
        if sport in LEAGUES:
            print(f"Available {sport.title()} Leagues:\n")
            for code, name in sorted(LEAGUES[sport].items(), key=lambda x: x[1]):
                print(f"  {code:20} {name}")
        else:
            print(f"Sport '{sport}' not found. Available: {', '.join(LEAGUES.keys())}")
    else:
        print("Available Leagues by Sport:\n")
        for sport_name, leagues in LEAGUES.items():
            print(f"\n{sport_name.upper()}:")
            for code, name in sorted(leagues.items(), key=lambda x: x[1]):
                print(f"  {code:20} {name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ESPN Sports API - Free live data!")
        print("\nUsage:")
        print("  espn.py leagues [sport]           - List available leagues")
        print("  espn.py scoreboard [league] [sport] - Get scoreboard (default: eng.1 soccer)")
        print("  espn.py search <team> [sport]     - Search for a team (default: soccer)")
        print("  espn.py match <event_id> [league] [sport] - Get match details")
        print("\nSupported sports: soccer, football, basketball, hockey, baseball, racing")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "leagues":
        sport = sys.argv[2] if len(sys.argv) > 2 else None
        list_leagues(sport)
    
    elif cmd == "scoreboard":
        league = sys.argv[2] if len(sys.argv) > 2 else "eng.1"
        sport = sys.argv[3] if len(sys.argv) > 3 else "soccer"
        data = get_scoreboard(sport, league)
        sport_leagues = LEAGUES.get(sport, {})
        print(f"=== {sport_leagues.get(league, league)} ===\n")
        for event in data.get("events", []):
            print(format_match(event, include_events=False, sport=sport, league=league))
            print()
    
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: espn.py search <team_name> [sport]")
            sys.exit(1)
        # Find where sport might be (last arg if it's a known sport)
        args = sys.argv[2:]
        sport = "soccer"
        if args and args[-1] in SPORT_MAPPING:
            sport = args[-1]
            team = " ".join(args[:-1])
        else:
            team = " ".join(args)
        
        results = search_team(team, sport)
        if results:
            print(f"Found teams matching '{team}' in {sport}:\n")
            for r in results:
                print(f"  ID: {r['id']:6} | {r['name']:30} | {r['league_name']}")
        else:
            print(f"No teams found matching '{team}' in {sport}")
    
    elif cmd == "match":
        if len(sys.argv) < 3:
            print("Usage: espn.py match <event_id> [league] [sport]")
            sys.exit(1)
        event_id = sys.argv[2]
        league = sys.argv[3] if len(sys.argv) > 3 else "eng.1"
        sport = sys.argv[4] if len(sys.argv) > 4 else "soccer"
        details = get_match_details(event_id, sport, league)
        event = details.get("header", {}).get("competitions", [{}])[0]
        # Reconstruct event format
        print(f"Match details for event {event_id}")
