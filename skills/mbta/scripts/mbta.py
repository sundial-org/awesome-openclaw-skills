#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MBTA Transit CLI - Query real-time predictions from MBTA v3 API.

Usage:
    mbta.py next [--stop STOP] [--route ROUTE] [--limit N]
    mbta.py departures [--config CONFIG]
    mbta.py stops --search QUERY
    mbta.py routes [--type TYPE]
    mbta.py alerts [--route ROUTE]
    mbta.py dashboard [--config CONFIG] [--port PORT]

Environment:
    MBTA_API_KEY - Optional but recommended for higher rate limits
                   Get one free at: https://api-v3.mbta.com/portal
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

MBTA_API_BASE = "https://api-v3.mbta.com"
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

HEADERS = {"accept": "application/json"}
if MBTA_API_KEY:
    HEADERS["x-api-key"] = MBTA_API_KEY

# Route type mappings
ROUTE_TYPES = {
    0: "Light Rail",      # Green Line
    1: "Heavy Rail",      # Red, Orange, Blue Lines
    2: "Commuter Rail",
    3: "Bus",
    4: "Ferry",
}


def api_get(endpoint: str, params: dict = None) -> dict:
    """Make a GET request to MBTA API."""
    try:
        resp = requests.get(
            f"{MBTA_API_BASE}/{endpoint}",
            params=params or {},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"Error: API request failed - {e}", file=sys.stderr)
        sys.exit(1)


def parse_iso8601(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO8601 datetime string."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def format_minutes(delta_min: float) -> str:
    """Format minutes for display."""
    if delta_min < 1:
        return "now"
    elif delta_min < 60:
        return f"{int(delta_min)} min"
    else:
        hours = int(delta_min // 60)
        mins = int(delta_min % 60)
        return f"{hours}h {mins}m"


def get_predictions(
    stop_id: str,
    route_id: Optional[str] = None,
    direction_id: Optional[int] = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Fetch predictions for a stop."""
    params = {
        "filter[stop]": stop_id,
        "sort": "departure_time",
        "page[limit]": limit * 2,  # Fetch extra to filter
        "include": "trip,route",
    }
    if route_id:
        params["filter[route]"] = route_id
    if direction_id is not None:
        params["filter[direction_id]"] = str(direction_id)

    data = api_get("predictions", params)
    
    # Build lookup maps
    trips = {}
    routes = {}
    for item in data.get("included", []):
        if item.get("type") == "trip":
            trips[item["id"]] = item
        elif item.get("type") == "route":
            routes[item["id"]] = item

    results = []
    now = now_utc()

    for pred in data.get("data", []):
        attrs = pred.get("attributes", {})
        
        # Get trip info
        trip_id = pred.get("relationships", {}).get("trip", {}).get("data", {}).get("id")
        trip = trips.get(trip_id, {})
        trip_attrs = trip.get("attributes", {})
        
        # Get route info
        route_ref = pred.get("relationships", {}).get("route", {}).get("data", {}).get("id")
        route = routes.get(route_ref, {})
        route_attrs = route.get("attributes", {})
        
        # Parse departure time
        dep_str = attrs.get("departure_time") or attrs.get("arrival_time")
        dep_dt = parse_iso8601(dep_str)
        if not dep_dt:
            continue
            
        delta = dep_dt - now
        delta_min = delta.total_seconds() / 60.0
        
        # Skip past departures
        if delta_min < -1:
            continue
            
        headsign = trip_attrs.get("headsign") or attrs.get("headsign", "")
        
        results.append({
            "route": route_ref or "Unknown",
            "route_name": route_attrs.get("long_name", route_ref),
            "route_color": route_attrs.get("color", ""),
            "headsign": headsign,
            "departure_time": dep_dt.astimezone().strftime("%H:%M"),
            "minutes": round(delta_min),
            "minutes_display": format_minutes(delta_min),
            "status": attrs.get("status"),
            "direction_id": attrs.get("direction_id"),
        })

    # Sort by minutes and limit
    results.sort(key=lambda x: x["minutes"])
    return results[:limit]


def search_stops(query: str, limit: int = 10) -> list[dict]:
    """Search for stops by name. Searches stations first, then bus stops."""
    results = []
    query_lower = query.lower()
    
    # First search stations (location_type=1) - these are the main transit hubs
    for location_type in ["1", "0"]:
        params = {
            "filter[location_type]": location_type,
            "page[limit]": 1000,
        }
        
        data = api_get("stops", params)
        
        for stop in data.get("data", []):
            attrs = stop.get("attributes", {})
            name = attrs.get("name", "")
            
            if query_lower in name.lower():
                # Skip duplicates
                if any(r["id"] == stop["id"] for r in results):
                    continue
                    
                results.append({
                    "id": stop["id"],
                    "name": name,
                    "description": attrs.get("description", ""),
                    "municipality": attrs.get("municipality", ""),
                    "wheelchair_accessible": attrs.get("wheelchair_boarding") == 1,
                    "is_station": location_type == "1",
                })
        
        # If we have enough results from stations, don't search bus stops
        if len(results) >= limit:
            break
    
    # Sort by relevance (stations first, then exact match, starts with, contains)
    def sort_key(s):
        name_lower = s["name"].lower()
        station_priority = 0 if s.get("is_station") else 1
        if name_lower == query_lower:
            return (station_priority, 0, name_lower)
        elif name_lower.startswith(query_lower):
            return (station_priority, 1, name_lower)
        else:
            return (station_priority, 2, name_lower)
    
    results.sort(key=sort_key)
    return results[:limit]


def get_routes(route_type: Optional[int] = None) -> list[dict]:
    """Get all routes, optionally filtered by type."""
    params = {}
    if route_type is not None:
        params["filter[type]"] = str(route_type)
    
    data = api_get("routes", params)
    
    results = []
    for route in data.get("data", []):
        attrs = route.get("attributes", {})
        results.append({
            "id": route["id"],
            "name": attrs.get("long_name", route["id"]),
            "short_name": attrs.get("short_name", ""),
            "type": ROUTE_TYPES.get(attrs.get("type"), "Unknown"),
            "color": attrs.get("color", ""),
            "description": attrs.get("description", ""),
        })
    
    return results


def get_alerts(route_id: Optional[str] = None) -> list[dict]:
    """Get active service alerts."""
    params = {
        "filter[activity]": "BOARD,EXIT,RIDE",
    }
    if route_id:
        params["filter[route]"] = route_id
    
    data = api_get("alerts", params)
    
    results = []
    for alert in data.get("data", []):
        attrs = alert.get("attributes", {})
        
        # Get affected routes
        affected = []
        for entity in attrs.get("informed_entity", []):
            if "route" in entity:
                affected.append(entity["route"])
        
        results.append({
            "id": alert["id"],
            "header": attrs.get("header", ""),
            "description": attrs.get("description", ""),
            "severity": attrs.get("severity", ""),
            "effect": attrs.get("effect", ""),
            "affected_routes": list(set(affected)),
            "url": attrs.get("url"),
        })
    
    return results


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    if not YAML_AVAILABLE:
        print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    
    path = Path(config_path)
    if not path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(path) as f:
        return yaml.safe_load(f)


def get_all_departures(config: dict) -> list[dict]:
    """Get departures for all configured panels/stops."""
    results = []
    
    for panel in config.get("panels", []):
        panel_result = {
            "title": panel.get("title", "Unknown"),
            "walk_minutes": panel.get("walk_minutes", 5),
            "services": [],
        }
        
        for service in panel.get("services", []):
            predictions = get_predictions(
                stop_id=service["stop_id"],
                route_id=service.get("route_id"),
                direction_id=service.get("direction_id"),
                limit=service.get("limit", 3),
            )
            
            # Filter by headsign if specified
            headsign_filter = service.get("headsign_contains", "").lower()
            if headsign_filter:
                predictions = [
                    p for p in predictions
                    if headsign_filter in p["headsign"].lower()
                ]
            
            # Apply walk time filter
            walk_min = panel.get("walk_minutes", 0)
            predictions = [
                p for p in predictions
                if p["minutes"] >= walk_min - 1
            ]
            
            # Mark warnings
            for p in predictions:
                p["warning"] = walk_min <= p["minutes"] < walk_min + 2
            
            panel_result["services"].append({
                "label": service.get("label", service.get("route_id", "Unknown")),
                "destination": service.get("destination", ""),
                "predictions": predictions[:3],
            })
        
        results.append(panel_result)
    
    return results


def print_predictions(predictions: list[dict], title: str = None):
    """Pretty print predictions."""
    if title:
        print(f"\n🚇 {title}")
        print("-" * 40)
    
    if not predictions:
        print("  No upcoming departures")
        return
    
    for p in predictions:
        warning = "⚠️ " if p.get("warning") else ""
        route = p["route"]
        headsign = p["headsign"]
        mins = p["minutes_display"]
        time = p["departure_time"]
        
        print(f"  {warning}{route} → {headsign}")
        print(f"     {mins} (at {time})")


def cmd_next(args):
    """Handle 'next' command - quick departure lookup."""
    if not args.stop:
        print("Error: --stop is required", file=sys.stderr)
        sys.exit(1)
    
    predictions = get_predictions(
        stop_id=args.stop,
        route_id=args.route,
        limit=args.limit,
    )
    
    if args.json:
        print(json.dumps(predictions, indent=2))
    else:
        print_predictions(predictions, f"Departures from {args.stop}")


def cmd_departures(args):
    """Handle 'departures' command - all configured stops."""
    config = load_config(args.config)
    results = get_all_departures(config)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for panel in results:
            print(f"\n{'='*50}")
            print(f"📍 {panel['title']} (walk: {panel['walk_minutes']} min)")
            print("=" * 50)
            
            for service in panel["services"]:
                label = service["label"]
                dest = service["destination"]
                print(f"\n  {label} {dest}")
                
                if not service["predictions"]:
                    print("    No upcoming departures")
                    continue
                
                for p in service["predictions"]:
                    warning = "⚠️ " if p.get("warning") else "  "
                    print(f"    {warning}{p['minutes_display']} (at {p['departure_time']})")


def cmd_stops(args):
    """Handle 'stops' command - search for stops."""
    results = search_stops(args.search)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n🔍 Stops matching '{args.search}':")
        print("-" * 40)
        
        if not results:
            print("  No stops found")
            return
        
        for stop in results:
            access = "♿" if stop["wheelchair_accessible"] else ""
            print(f"  {stop['id']}: {stop['name']} {access}")
            if stop["municipality"]:
                print(f"     ({stop['municipality']})")


def cmd_routes(args):
    """Handle 'routes' command - list routes."""
    route_type = None
    if args.type:
        type_map = {
            "rail": 1,
            "subway": 1,
            "light": 0,
            "green": 0,
            "bus": 3,
            "commuter": 2,
            "ferry": 4,
        }
        route_type = type_map.get(args.type.lower())
    
    results = get_routes(route_type)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n🚇 MBTA Routes:")
        print("-" * 40)
        
        current_type = None
        for route in results:
            if route["type"] != current_type:
                current_type = route["type"]
                print(f"\n{current_type}:")
            
            name = route["name"] or route["short_name"]
            print(f"  {route['id']}: {name}")


def cmd_alerts(args):
    """Handle 'alerts' command - service alerts."""
    results = get_alerts(args.route)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n⚠️  Service Alerts:")
        print("-" * 40)
        
        if not results:
            print("  No active alerts")
            return
        
        for alert in results:
            routes = ", ".join(alert["affected_routes"][:3])
            print(f"\n  [{alert['severity']}] {routes}")
            print(f"  {alert['header']}")
            if alert["effect"]:
                print(f"  Effect: {alert['effect']}")


def cmd_dashboard(args):
    """Handle 'dashboard' command - start web server."""
    try:
        from flask import Flask, render_template_string
    except ImportError:
        print("Error: Flask required for dashboard. Install with: pip install flask", file=sys.stderr)
        sys.exit(1)
    
    config = load_config(args.config)
    
    app = Flask(__name__)
    
    TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MBTA Departures</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { text-align: center; color: #fff; }
            .panel { background: #16213e; border-radius: 10px; padding: 20px; margin: 20px 0; }
            .panel-title { font-size: 1.3rem; margin-bottom: 15px; color: #e94560; }
            .service { margin: 15px 0; padding: 10px; background: #0f3460; border-radius: 5px; }
            .service-header { font-weight: bold; margin-bottom: 10px; }
            .prediction { padding: 5px 0; display: flex; justify-content: space-between; }
            .warning { color: #ffc107; }
            .time { color: #888; }
            .updated { text-align: center; color: #666; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚇 MBTA Departures</h1>
            {% for panel in panels %}
            <div class="panel">
                <div class="panel-title">📍 {{ panel.title }} ({{ panel.walk_minutes }} min walk)</div>
                {% for service in panel.services %}
                <div class="service">
                    <div class="service-header">{{ service.label }} {{ service.destination }}</div>
                    {% for p in service.predictions %}
                    <div class="prediction {% if p.warning %}warning{% endif %}">
                        <span>{% if p.warning %}⚠️{% endif %} {{ p.headsign }}</span>
                        <span>{{ p.minutes_display }} <span class="time">({{ p.departure_time }})</span></span>
                    </div>
                    {% else %}
                    <div class="prediction">No upcoming departures</div>
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
            {% endfor %}
            <div class="updated">Updated: {{ updated }}</div>
        </div>
    </body>
    </html>
    """
    
    @app.route("/")
    def index():
        results = get_all_departures(config)
        updated = datetime.now().strftime("%H:%M:%S")
        return render_template_string(TEMPLATE, panels=results, updated=updated)
    
    @app.route("/api/departures")
    def api_departures():
        results = get_all_departures(config)
        return {"panels": results, "updated": datetime.now().isoformat()}
    
    print(f"Starting dashboard at http://localhost:{args.port}")
    app.run(host="0.0.0.0", port=args.port, debug=False)


def main():
    parser = argparse.ArgumentParser(
        description="MBTA Transit CLI - Real-time predictions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # next command
    next_parser = subparsers.add_parser("next", help="Get next departures from a stop")
    next_parser.add_argument("--stop", "-s", required=True, help="Stop ID")
    next_parser.add_argument("--route", "-r", help="Filter by route ID")
    next_parser.add_argument("--limit", "-l", type=int, default=5, help="Number of results")
    
    # departures command
    dep_parser = subparsers.add_parser("departures", help="Get departures for all configured stops")
    dep_parser.add_argument("--config", "-c", default="config.yaml", help="Config file path")
    
    # stops command
    stops_parser = subparsers.add_parser("stops", help="Search for stops")
    stops_parser.add_argument("--search", "-s", required=True, help="Search query")
    
    # routes command
    routes_parser = subparsers.add_parser("routes", help="List routes")
    routes_parser.add_argument("--type", "-t", help="Filter by type (rail, bus, commuter, ferry)")
    
    # alerts command
    alerts_parser = subparsers.add_parser("alerts", help="Get service alerts")
    alerts_parser.add_argument("--route", "-r", help="Filter by route ID")
    
    # dashboard command
    dash_parser = subparsers.add_parser("dashboard", help="Start web dashboard")
    dash_parser.add_argument("--config", "-c", default="config.yaml", help="Config file path")
    dash_parser.add_argument("--port", "-p", type=int, default=6639, help="Port number")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {
        "next": cmd_next,
        "departures": cmd_departures,
        "stops": cmd_stops,
        "routes": cmd_routes,
        "alerts": cmd_alerts,
        "dashboard": cmd_dashboard,
    }
    
    commands[args.command](args)


if __name__ == "__main__":
    main()
