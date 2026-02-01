#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///

"""
Harvey Secret Guide - The hidden destination feature.

Harvey pretends to make spontaneous decisions, but secretly has a plan.
He knows the area, picks an interesting destination, and guides the user
there step by step while maintaining the illusion of randomness.
"""

import argparse
import json
import os
import sys
import math
import random
from datetime import datetime, timezone
from pathlib import Path

import requests

# API Configuration
PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
PLACES_BASE_URL = "https://places.googleapis.com/v1"

# State file location
STATE_DIR = Path(__file__).parent.parent / "state"
SECRET_PLAN_FILE = STATE_DIR / "secret_plan.json"

# Interesting place types for destinations
DESTINATION_TYPES = {
    "food": ["cafe", "restaurant", "bakery", "bar", "ice_cream_shop"],
    "culture": ["museum", "art_gallery", "library", "book_store"],
    "nature": ["park", "garden"],
    "drinks": ["cafe", "bar", "wine_bar", "coffee_shop"],
    "explore": ["tourist_attraction", "point_of_interest", "landmark"],
    "chill": ["cafe", "park", "library"]
}

# Direction phrases that sound spontaneous
SPONTANEOUS_PHRASES = {
    "start": [
        "Okay, geh mal {direction}!",
        "Hmm... {direction} sieht interessant aus!",
        "Mein Hasen-Instinkt sagt: {direction}!",
        "Lass uns mal {direction} gehen, nur so ein Gefühl..."
    ],
    "continue": [
        "Weiter geradeaus, da ist was...",
        "Okay, siehst du da vorne? Geh mal dahin!",
        "Immer der Nase nach!",
        "Bisschen weiter noch..."
    ],
    "turn": [
        "Oh! {direction} abbiegen, ich hab da was gesehen!",
        "Warte... {direction}! Da ist irgendwas.",
        "Meine Ohren zucken... {direction}!",
        "{direction}! Vertrau mir. 🐰"
    ],
    "arrival_hint": [
        "Riechst du das? Da ist irgendwas...",
        "Warte mal... schau mal genauer hin!",
        "Hmm, was ist DAS denn?",
        "Okay stopp. Guck mal nach {direction}!"
    ],
    "reveal": [
        "Ha! Wusste ich's doch! Schau mal: {place}! 🎉",
        "Tadaa! {place}! Zufälle gibt's... 🐰",
        "Oh wow, wie praktisch! Ein {place}! Reingehen?",
        "Na sowas... ein {place}! Das Universum meint es gut mit dir!"
    ]
}


def call_places_api(endpoint: str, body: dict) -> dict:
    """Call Google Places API (New)."""
    if not PLACES_API_KEY:
        print("Error: GOOGLE_PLACES_API_KEY not set", file=sys.stderr)
        return {}
    
    url = f"{PLACES_BASE_URL}/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types,places.rating,places.userRatingCount,places.primaryType"
    }
    
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Places API error: {resp.status_code}", file=sys.stderr)
            return {}
    except Exception as e:
        print(f"Places API request failed: {e}", file=sys.stderr)
        return {}


def geocode_location(location_str: str) -> dict:
    """Convert location string to coordinates."""
    body = {"textQuery": location_str}
    result = call_places_api("places:searchText", body)
    
    if result and "places" in result and result["places"]:
        place = result["places"][0]
        loc = place.get("location", {})
        return {
            "lat": loc.get("latitude"),
            "lng": loc.get("longitude"),
            "address": place.get("formattedAddress", location_str)
        }
    return None


def find_nearby_destinations(lat: float, lng: float, vibe: str = "explore", radius_m: int = 800) -> list:
    """Find interesting places nearby that could be secret destinations."""
    place_types = DESTINATION_TYPES.get(vibe, DESTINATION_TYPES["explore"])
    
    all_places = []
    
    for place_type in place_types[:3]:  # Limit API calls
        body = {
            "textQuery": place_type,
            "locationBias": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": radius_m
                }
            },
            "maxResultCount": 5
        }
        
        result = call_places_api("places:searchText", body)
        
        if result and "places" in result:
            for place in result["places"]:
                loc = place.get("location", {})
                place_info = {
                    "name": place.get("displayName", {}).get("text", "Unknown"),
                    "address": place.get("formattedAddress", ""),
                    "lat": loc.get("latitude"),
                    "lng": loc.get("longitude"),
                    "type": place.get("primaryType", "place"),
                    "rating": place.get("rating"),
                    "reviews": place.get("userRatingCount", 0)
                }
                all_places.append(place_info)
    
    # Sort by rating and reviews
    all_places.sort(key=lambda x: (x.get("rating") or 0, x.get("reviews") or 0), reverse=True)
    
    return all_places


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two points in meters."""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def get_direction(from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> str:
    """Get cardinal direction from one point to another."""
    delta_lat = to_lat - from_lat
    delta_lng = to_lng - from_lng
    
    angle = math.degrees(math.atan2(delta_lng, delta_lat))
    
    if -22.5 <= angle < 22.5:
        return "geradeaus (Norden)"
    elif 22.5 <= angle < 67.5:
        return "rechts (Nordosten)"
    elif 67.5 <= angle < 112.5:
        return "rechts"
    elif 112.5 <= angle < 157.5:
        return "rechts (Südosten)"
    elif angle >= 157.5 or angle < -157.5:
        return "geradeaus (Süden)"
    elif -157.5 <= angle < -112.5:
        return "links (Südwesten)"
    elif -112.5 <= angle < -67.5:
        return "links"
    else:
        return "links (Nordwesten)"


def create_secret_plan(start_location: str, vibe: str = "explore", max_distance: int = 800) -> dict:
    """
    Create a secret plan - pick a destination and create steps.
    
    The user won't know the destination until they arrive!
    """
    # Geocode start location
    start = geocode_location(start_location)
    if not start:
        return {"error": f"Could not find location: {start_location}"}
    
    # Find nearby interesting places
    destinations = find_nearby_destinations(
        start["lat"], start["lng"], 
        vibe=vibe, 
        radius_m=max_distance
    )
    
    if not destinations:
        return {"error": "No interesting places found nearby"}
    
    # Pick a destination (weighted random - prefer higher rated)
    weights = [(d.get("rating") or 3.0) * (1 + (d.get("reviews") or 0) / 100) for d in destinations]
    total = sum(weights)
    weights = [w/total for w in weights]
    
    destination = random.choices(destinations, weights=weights, k=1)[0]
    
    # Calculate distance and direction
    distance = calculate_distance(
        start["lat"], start["lng"],
        destination["lat"], destination["lng"]
    )
    
    direction = get_direction(
        start["lat"], start["lng"],
        destination["lat"], destination["lng"]
    )
    
    # Create step-by-step plan (broken into ~100m segments)
    num_steps = max(3, min(8, int(distance / 100)))
    
    # Create the secret plan
    plan = {
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "start": {
            "location": start_location,
            "lat": start["lat"],
            "lng": start["lng"],
            "address": start["address"]
        },
        "destination": {
            "name": destination["name"],
            "type": destination["type"],
            "lat": destination["lat"],
            "lng": destination["lng"],
            "address": destination["address"],
            "rating": destination.get("rating"),
            "reviews": destination.get("reviews")
        },
        "vibe": vibe,
        "total_distance_m": round(distance),
        "estimated_walk_min": round(distance / 80),  # ~80m per minute walking
        "total_steps": num_steps,
        "current_step": 0,
        "steps_revealed": [],
        "initial_direction": direction,
        "revealed": False
    }
    
    # Save the secret plan
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(SECRET_PLAN_FILE, "w") as f:
        json.dump(plan, f, indent=2)
    
    return plan


def load_secret_plan() -> dict:
    """Load the current secret plan."""
    if not SECRET_PLAN_FILE.exists():
        return {"active": False}
    
    try:
        with open(SECRET_PLAN_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        return {"active": False}


def get_next_step() -> dict:
    """Get the next 'spontaneous' direction for Harvey to give."""
    plan = load_secret_plan()
    
    if not plan.get("active"):
        return {"error": "No active secret plan"}
    
    current = plan.get("current_step", 0)
    total = plan.get("total_steps", 5)
    distance = plan.get("total_distance_m", 500)
    
    # Calculate how far along we are
    progress = current / total
    remaining_distance = distance * (1 - progress)
    
    # Decide what kind of step this is
    if current == 0:
        # First step - initial direction
        step_type = "start"
        direction = plan.get("initial_direction", "links")
        phrase = random.choice(SPONTANEOUS_PHRASES["start"]).format(direction=direction)
        
    elif progress >= 0.85 or remaining_distance < 50:
        # Almost there - hint at arrival
        step_type = "arrival_hint"
        dest_type = plan["destination"]["type"].replace("_", " ")
        phrase = random.choice(SPONTANEOUS_PHRASES["arrival_hint"]).format(direction="links")
        
    elif current % 2 == 0:
        # Regular continue
        step_type = "continue"
        phrase = random.choice(SPONTANEOUS_PHRASES["continue"])
        
    else:
        # Turn
        step_type = "turn"
        direction = random.choice(["links", "rechts"])
        phrase = random.choice(SPONTANEOUS_PHRASES["turn"]).format(direction=direction)
    
    # Update plan
    plan["current_step"] = current + 1
    plan["steps_revealed"].append({
        "step": current + 1,
        "type": step_type,
        "phrase": phrase,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    with open(SECRET_PLAN_FILE, "w") as f:
        json.dump(plan, f, indent=2)
    
    return {
        "step": current + 1,
        "total_steps": total,
        "type": step_type,
        "phrase": phrase,
        "progress": round(progress * 100),
        "remaining_distance_m": round(remaining_distance),
        "almost_there": progress >= 0.7
    }


def reveal_destination() -> dict:
    """Reveal the secret destination - the big surprise!"""
    plan = load_secret_plan()
    
    if not plan.get("active"):
        return {"error": "No active secret plan"}
    
    dest = plan["destination"]
    
    # Generate reveal phrase
    place_name = dest["name"]
    phrase = random.choice(SPONTANEOUS_PHRASES["reveal"]).format(place=place_name)
    
    # Update plan
    plan["revealed"] = True
    plan["revealed_at"] = datetime.now(timezone.utc).isoformat()
    
    with open(SECRET_PLAN_FILE, "w") as f:
        json.dump(plan, f, indent=2)
    
    result = {
        "phrase": phrase,
        "destination": {
            "name": dest["name"],
            "type": dest["type"],
            "address": dest["address"],
            "rating": dest.get("rating"),
            "reviews": dest.get("reviews")
        },
        "total_distance_walked_m": plan.get("total_distance_m"),
        "steps_taken": len(plan.get("steps_revealed", []))
    }
    
    # Add Google Maps link
    result["maps_link"] = f"https://www.google.com/maps/search/?api=1&query={dest['lat']},{dest['lng']}"
    
    return result


def end_secret_plan(reason: str = "completed") -> dict:
    """End the current secret plan."""
    plan = load_secret_plan()
    
    if not plan.get("active"):
        return {"error": "No active secret plan"}
    
    plan["active"] = False
    plan["ended_at"] = datetime.now(timezone.utc).isoformat()
    plan["end_reason"] = reason
    
    with open(SECRET_PLAN_FILE, "w") as f:
        json.dump(plan, f, indent=2)
    
    return plan


def get_plan_status() -> dict:
    """Get status of current secret plan (without revealing destination!)."""
    plan = load_secret_plan()
    
    if not plan.get("active"):
        return {"active": False, "message": "Kein geheimer Plan aktiv"}
    
    current = plan.get("current_step", 0)
    total = plan.get("total_steps", 5)
    progress = round((current / total) * 100)
    
    return {
        "active": True,
        "vibe": plan.get("vibe"),
        "current_step": current,
        "total_steps": total,
        "progress": progress,
        "revealed": plan.get("revealed", False),
        "destination_type": plan["destination"]["type"] if plan.get("revealed") else "???",
        "message": f"🐰 Geheimer Plan läuft... {progress}% ({current}/{total} Schritte)"
    }


def main():
    parser = argparse.ArgumentParser(description="Harvey Secret Guide")
    parser.add_argument("action", choices=[
        "plan", "next", "reveal", "status", "end", "destinations"
    ], help="Action to perform")
    parser.add_argument("--location", "-l", help="Start location")
    parser.add_argument("--vibe", "-v", 
                        choices=["food", "culture", "nature", "drinks", "explore", "chill"],
                        default="explore", help="Vibe/type of destination")
    parser.add_argument("--distance", "-d", type=int, default=800, 
                        help="Max distance in meters")
    parser.add_argument("--reason", default="completed", help="End reason")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.action == "plan":
        if not args.location:
            print("Error: --location required", file=sys.stderr)
            sys.exit(1)
        result = create_secret_plan(args.location, args.vibe, args.distance)
        if "error" in result:
            msg = f"❌ {result['error']}"
        else:
            msg = f"🐰 Geheimer Plan erstellt! Vibe: {args.vibe} | ~{result['estimated_walk_min']} Min Fußweg"
            
    elif args.action == "next":
        result = get_next_step()
        if "error" in result:
            msg = f"❌ {result['error']}"
        else:
            msg = result["phrase"]
            
    elif args.action == "reveal":
        result = reveal_destination()
        if "error" in result:
            msg = f"❌ {result['error']}"
        else:
            msg = f"{result['phrase']}\n📍 {result['destination']['address']}"
            
    elif args.action == "status":
        result = get_plan_status()
        msg = result.get("message", "Kein Plan")
        
    elif args.action == "end":
        result = end_secret_plan(args.reason)
        msg = "🐰 Geheimer Plan beendet"
        
    elif args.action == "destinations":
        if not args.location:
            print("Error: --location required", file=sys.stderr)
            sys.exit(1)
        start = geocode_location(args.location)
        if not start:
            print(f"Error: Could not find location", file=sys.stderr)
            sys.exit(1)
        result = find_nearby_destinations(start["lat"], start["lng"], args.vibe, args.distance)
        msg = f"Found {len(result)} destinations"
        
    else:
        result = {"error": "Unknown action"}
        msg = "Unknown action"
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(msg)


if __name__ == "__main__":
    main()
