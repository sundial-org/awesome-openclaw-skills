#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Harvey Journey Tracker - Maintains continuity during walks and explorations.
Tracks locations, observations, directions, and schedules proactive check-ins.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# State file location
STATE_DIR = Path(__file__).parent.parent / "state"
JOURNEY_FILE = STATE_DIR / "journey.json"
CHECKIN_FILE = STATE_DIR / "checkin_schedule.json"

# Default check-in intervals (minutes)
CHECKIN_INTERVALS = {
    "walk": 5,        # Every 5 minutes during walks
    "restaurant": 10, # Every 10 minutes at restaurant
    "waiting": 7,     # Every 7 minutes while waiting
    "bored": 15       # Every 15 minutes when just chatting
}


def load_journey() -> dict:
    """Load current journey state."""
    if not JOURNEY_FILE.exists():
        return {"active": False, "events": []}
    try:
        with open(JOURNEY_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return {"active": False, "events": []}


def save_journey(journey: dict) -> None:
    """Save journey state."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(JOURNEY_FILE, "w") as f:
        json.dump(journey, f, indent=2, default=str)


def start_journey(mode: str = "walk", start_location: str = None) -> dict:
    """Start a new journey/exploration."""
    now = datetime.now(timezone.utc)
    
    journey = {
        "active": True,
        "mode": mode,
        "started_at": now.isoformat(),
        "start_location": start_location,
        "current_location": start_location,
        "last_direction": None,
        "events": [],
        "things_seen": [],
        "mood": None,
        "destinations_mentioned": [],
        "last_checkin": now.isoformat(),
        "checkin_count": 0
    }
    
    save_journey(journey)
    schedule_next_checkin(mode)
    return journey


def add_event(event_type: str, content: str, location: str = None) -> dict:
    """
    Add an event to the journey timeline.
    
    Event types:
    - direction: Harvey gave a direction ("go right")
    - observation: User saw something ("I see a park")
    - location: User's current location
    - mood: User expressed feeling
    - destination: A place mentioned as potential destination
    - action: User did something ("bought coffee")
    """
    journey = load_journey()
    
    if not journey.get("active"):
        return {"error": "No active journey"}
    
    now = datetime.now(timezone.utc)
    
    event = {
        "type": event_type,
        "content": content,
        "timestamp": now.isoformat(),
        "location": location
    }
    
    journey["events"].append(event)
    
    # Update specific trackers based on event type
    if event_type == "location":
        journey["current_location"] = content
    elif event_type == "direction":
        journey["last_direction"] = content
    elif event_type == "observation":
        journey["things_seen"].append(content)
        # Keep last 10 observations
        journey["things_seen"] = journey["things_seen"][-10:]
    elif event_type == "mood":
        journey["mood"] = content
    elif event_type == "destination":
        journey["destinations_mentioned"].append(content)
    
    save_journey(journey)
    return event


def get_context() -> dict:
    """
    Get current journey context for Harvey to reference.
    This is what Harvey "remembers" about the ongoing journey.
    """
    journey = load_journey()
    
    if not journey.get("active"):
        return {"active": False}
    
    # Calculate duration
    started = datetime.fromisoformat(journey["started_at"])
    now = datetime.now(timezone.utc)
    duration_min = int((now - started).total_seconds() / 60)
    
    # Get recent events (last 5)
    recent_events = journey.get("events", [])[-5:]
    
    # Build context summary
    context = {
        "active": True,
        "mode": journey.get("mode"),
        "duration_minutes": duration_min,
        "start_location": journey.get("start_location"),
        "current_location": journey.get("current_location"),
        "last_direction": journey.get("last_direction"),
        "things_seen": journey.get("things_seen", []),
        "mood": journey.get("mood"),
        "destinations_mentioned": journey.get("destinations_mentioned", []),
        "recent_events": recent_events,
        "event_count": len(journey.get("events", [])),
        "checkin_count": journey.get("checkin_count", 0)
    }
    
    # Generate a natural summary for Harvey
    summary_parts = []
    
    if journey.get("start_location"):
        summary_parts.append(f"Started at: {journey['start_location']}")
    
    if journey.get("current_location") and journey["current_location"] != journey.get("start_location"):
        summary_parts.append(f"Now at: {journey['current_location']}")
    
    if journey.get("last_direction"):
        summary_parts.append(f"Last direction: {journey['last_direction']}")
    
    if journey.get("things_seen"):
        summary_parts.append(f"Seen: {', '.join(journey['things_seen'][-3:])}")
    
    if journey.get("mood"):
        summary_parts.append(f"Mood: {journey['mood']}")
    
    context["summary"] = " | ".join(summary_parts) if summary_parts else "Just started"
    
    return context


def record_checkin() -> dict:
    """Record that a check-in happened."""
    journey = load_journey()
    
    if not journey.get("active"):
        return {"error": "No active journey"}
    
    journey["last_checkin"] = datetime.now(timezone.utc).isoformat()
    journey["checkin_count"] = journey.get("checkin_count", 0) + 1
    
    save_journey(journey)
    schedule_next_checkin(journey.get("mode", "walk"))
    
    return {"checkin_count": journey["checkin_count"]}


def schedule_next_checkin(mode: str) -> dict:
    """Schedule the next proactive check-in."""
    interval = CHECKIN_INTERVALS.get(mode, 5)
    now = datetime.now(timezone.utc)
    next_checkin = now + timedelta(minutes=interval)
    
    schedule = {
        "scheduled_at": now.isoformat(),
        "checkin_at": next_checkin.isoformat(),
        "mode": mode,
        "interval_minutes": interval
    }
    
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHECKIN_FILE, "w") as f:
        json.dump(schedule, f, indent=2)
    
    return schedule


def is_checkin_due() -> dict:
    """Check if a proactive check-in is due."""
    if not CHECKIN_FILE.exists():
        return {"due": False}
    
    try:
        with open(CHECKIN_FILE) as f:
            schedule = json.load(f)
        
        checkin_at = datetime.fromisoformat(schedule["checkin_at"])
        now = datetime.now(timezone.utc)
        
        return {
            "due": now >= checkin_at,
            "scheduled_for": schedule["checkin_at"],
            "mode": schedule.get("mode"),
            "overdue_minutes": max(0, int((now - checkin_at).total_seconds() / 60))
        }
    except (json.JSONDecodeError, KeyError):
        return {"due": False}


def get_checkin_prompt() -> str:
    """Generate a contextual check-in prompt for Harvey."""
    context = get_context()
    
    if not context.get("active"):
        return ""
    
    checkin_count = context.get("checkin_count", 0)
    mode = context.get("mode", "walk")
    things_seen = context.get("things_seen", [])
    last_direction = context.get("last_direction")
    
    # Different prompts based on context
    if mode == "walk":
        if checkin_count == 0:
            return "Und, bist du losgegangen? Was siehst du?"
        elif last_direction and checkin_count < 3:
            return f"Hey! Bist du {last_direction} gegangen? Wo bist du jetzt?"
        elif things_seen:
            last_seen = things_seen[-1]
            return f"Bist du noch bei {last_seen}? Oder schon weiter?"
        else:
            prompts = [
                "Hey, wo bist du gerade? Was siehst du?",
                "Alles gut? Was passiert um dich herum?",
                "Und? Irgendwas Interessantes entdeckt?",
                "Wie sieht's aus? Beschreib mal, was du siehst!"
            ]
            return prompts[checkin_count % len(prompts)]
    
    elif mode == "restaurant":
        prompts = [
            "Schon bestellt? Was gibt's?",
            "Wie schmeckt's?",
            "Und, wie ist die Atmosphäre so?"
        ]
        return prompts[checkin_count % len(prompts)]
    
    return "Hey, wie läuft's?"


def end_journey(reason: str = "completed") -> dict:
    """End the current journey."""
    journey = load_journey()
    
    if not journey.get("active"):
        return {"error": "No active journey"}
    
    journey["active"] = False
    journey["ended_at"] = datetime.now(timezone.utc).isoformat()
    journey["end_reason"] = reason
    
    # Calculate stats
    started = datetime.fromisoformat(journey["started_at"])
    ended = datetime.fromisoformat(journey["ended_at"])
    journey["total_duration_minutes"] = int((ended - started).total_seconds() / 60)
    journey["total_events"] = len(journey.get("events", []))
    
    save_journey(journey)
    
    # Clear check-in schedule
    if CHECKIN_FILE.exists():
        CHECKIN_FILE.unlink()
    
    return journey


def main():
    parser = argparse.ArgumentParser(description="Harvey Journey Tracker")
    parser.add_argument("action", choices=[
        "start", "event", "context", "checkin", "checkin-due", 
        "checkin-prompt", "end", "status"
    ], help="Action to perform")
    parser.add_argument("--mode", "-m", default="walk", help="Journey mode")
    parser.add_argument("--location", "-l", help="Location")
    parser.add_argument("--type", "-t", help="Event type")
    parser.add_argument("--content", "-c", help="Event content")
    parser.add_argument("--reason", default="completed", help="End reason")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.action == "start":
        result = start_journey(args.mode, args.location)
        msg = f"🚶 Journey started ({args.mode})"
    elif args.action == "event":
        if not args.type or not args.content:
            print("Error: --type and --content required", file=sys.stderr)
            sys.exit(1)
        result = add_event(args.type, args.content, args.location)
        msg = f"📝 Event recorded: {args.type}"
    elif args.action == "context":
        result = get_context()
        msg = result.get("summary", "No active journey")
    elif args.action == "checkin":
        result = record_checkin()
        msg = f"✅ Check-in #{result.get('checkin_count', 0)}"
    elif args.action == "checkin-due":
        result = is_checkin_due()
        msg = "⏰ Check-in due!" if result.get("due") else "⏳ Not yet"
    elif args.action == "checkin-prompt":
        prompt = get_checkin_prompt()
        result = {"prompt": prompt}
        msg = prompt or "No active journey"
    elif args.action == "end":
        result = end_journey(args.reason)
        if "error" not in result:
            msg = f"🏁 Journey ended: {result.get('total_duration_minutes', 0)} min, {result.get('total_events', 0)} events"
        else:
            msg = result["error"]
    elif args.action == "status":
        result = get_context()
        if result.get("active"):
            msg = f"🚶 Active: {result.get('duration_minutes', 0)} min | {result.get('summary', '')}"
        else:
            msg = "💤 No active journey"
    else:
        result = {"error": "Unknown action"}
        msg = "Unknown action"
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(msg)


if __name__ == "__main__":
    main()
