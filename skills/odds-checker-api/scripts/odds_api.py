#!/usr/bin/env python3
"""Minimal CLI for Odds-API.io (v3)."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE_URL = "https://api.odds-api.io/v3"


def build_url(base_url, path, params):
    base = base_url.rstrip("/")
    clean_params = {k: v for k, v in params.items() if v is not None}
    query = urllib.parse.urlencode(clean_params)
    if query:
        return f"{base}{path}?{query}"
    return f"{base}{path}"


def request_json(url, timeout):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            text = raw.decode(charset, errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {exc.reason}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Unexpected non-JSON response: {text[:200]}") from exc


def get_api_key(args, required):
    key = args.api_key or os.getenv("ODDS_API_KEY")
    if required and not key:
        raise RuntimeError("Missing API key. Set ODDS_API_KEY or pass --api-key.")
    return key


def slug_from(obj):
    if isinstance(obj, dict):
        return obj.get("slug") or obj.get("name")
    return obj


def format_event(event):
    event_id = event.get("id")
    home = event.get("home") or ""
    away = event.get("away") or ""
    date = event.get("date") or ""
    status = event.get("status") or ""
    sport_slug = slug_from(event.get("sport")) or ""
    league_slug = slug_from(event.get("league")) or ""

    league_part = f"{sport_slug}/{league_slug}".strip("/")
    parts = [str(event_id), date, league_part, f"{home} vs {away}", status]
    return " | ".join([p for p in parts if p])


def print_events(events, limit):
    if limit is not None:
        events = events[:limit]
    for event in events:
        print(format_event(event))


def print_json(data):
    print(json.dumps(data, indent=2, sort_keys=True))


def command_sports(args):
    url = build_url(args.base_url, "/sports", {})
    if args.dry_run:
        print(url)
        return 0
    data = request_json(url, args.timeout)
    if args.json:
        print_json(data)
        return 0

    for sport in data:
        name = sport.get("name")
        slug = sport.get("slug")
        if name and slug:
            print(f"{slug} - {name}")
        else:
            print_json(sport)
    return 0


def command_bookmakers(args):
    url = build_url(args.base_url, "/bookmakers", {})
    if args.dry_run:
        print(url)
        return 0
    data = request_json(url, args.timeout)
    if args.json:
        print_json(data)
        return 0

    for bookmaker in data:
        active = bookmaker.get("active")
        if not args.all and not active:
            continue
        status = "active" if active else "inactive"
        name = bookmaker.get("name")
        print(f"{name} ({status})")
    return 0


def command_events(args):
    api_key = get_api_key(args, required=True)
    params = {
        "apiKey": api_key,
        "sport": args.sport,
        "league": args.league,
        "participantId": args.participant_id,
        "status": args.status,
        "from": args.from_time,
        "to": args.to_time,
        "bookmaker": args.bookmaker,
    }
    url = build_url(args.base_url, "/events", params)
    if args.dry_run:
        print(url)
        return 0
    data = request_json(url, args.timeout)
    if args.json:
        print_json(data)
    else:
        print_events(data, args.limit)
    return 0


def filter_events(events, sport_slug=None, league_slug=None):
    if not sport_slug and not league_slug:
        return events
    filtered = []
    for event in events:
        sport = slug_from(event.get("sport"))
        league = slug_from(event.get("league"))
        if sport_slug and sport_slug != sport:
            continue
        if league_slug and league_slug != league:
            continue
        filtered.append(event)
    return filtered


def command_search(args):
    api_key = get_api_key(args, required=True)
    params = {
        "apiKey": api_key,
        "query": args.query,
    }
    url = build_url(args.base_url, "/events/search", params)
    if args.dry_run:
        print(url)
        return 0
    data = request_json(url, args.timeout)
    data = filter_events(data, args.sport, args.league)
    if args.json:
        print_json(data)
    else:
        print_events(data, args.limit)
    return 0


def command_odds(args):
    api_key = get_api_key(args, required=True)
    params = {
        "apiKey": api_key,
        "eventId": args.event_id,
        "bookmakers": args.bookmakers,
    }
    url = build_url(args.base_url, "/odds", params)
    if args.dry_run:
        print(url)
        return 0
    data = request_json(url, args.timeout)
    if args.summary:
        home = data.get("home")
        away = data.get("away")
        date = data.get("date")
        status = data.get("status")
        bookmakers = sorted((data.get("bookmakers") or {}).keys())
        print(f"{home} vs {away}")
        if date:
            print(f"date: {date}")
        if status:
            print(f"status: {status}")
        if bookmakers:
            print("bookmakers:")
            for name in bookmakers:
                print(f"- {name}")
    else:
        print_json(data)
    return 0


def command_matchup(args):
    api_key = get_api_key(args, required=True)
    query = args.query
    if not query:
        if not args.home or not args.away:
            raise RuntimeError("Provide --query or both --home and --away.")
        query = f"{args.home} vs {args.away}"

    params = {
        "apiKey": api_key,
        "query": query,
    }
    url = build_url(args.base_url, "/events/search", params)
    if args.dry_run:
        print(url)
        return 0

    events = request_json(url, args.timeout)
    events = filter_events(events, args.sport, args.league)

    if not events:
        print("No events found.")
        return 1

    if args.pick is not None:
        if args.pick < 1 or args.pick > len(events):
            raise RuntimeError("--pick is out of range for the returned events.")
        event = events[args.pick - 1]
    elif len(events) == 1:
        event = events[0]
    else:
        print("Multiple events matched. Re-run with --pick or refine the query:")
        print_events(events, args.limit)
        return 1

    odds_args = argparse.Namespace(
        api_key=args.api_key,
        base_url=args.base_url,
        timeout=args.timeout,
        dry_run=args.dry_run,
        event_id=str(event.get("id")),
        bookmakers=args.bookmakers,
        summary=args.summary,
    )
    return command_odds(odds_args)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Odds-API.io CLI helper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--api-key", help="Odds-API.io API key")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="API base URL")
    parser.add_argument("--timeout", type=int, default=20, help="Request timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Print request URL without calling the API")

    subparsers = parser.add_subparsers(dest="command", required=True)

    sports = subparsers.add_parser("sports", help="List available sports")
    sports.add_argument("--json", action="store_true", help="Print full JSON response")
    sports.set_defaults(func=command_sports)

    bookmakers = subparsers.add_parser("bookmakers", help="List bookmakers")
    bookmakers.add_argument("--all", action="store_true", help="Include inactive bookmakers")
    bookmakers.add_argument("--json", action="store_true", help="Print full JSON response")
    bookmakers.set_defaults(func=command_bookmakers)

    events = subparsers.add_parser("events", help="List events for a sport")
    events.add_argument("--sport", required=True, help="Sport slug (e.g. football)")
    events.add_argument("--league", help="League slug")
    events.add_argument("--participant-id", help="Filter by participant ID")
    events.add_argument("--status", help="Comma-separated statuses (pending,live,settled)")
    events.add_argument("--from", dest="from_time", help="Start time (RFC3339)")
    events.add_argument("--to", dest="to_time", help="End time (RFC3339)")
    events.add_argument("--bookmaker", help="Filter by bookmaker name")
    events.add_argument("--limit", type=int, help="Limit number of results shown")
    events.add_argument("--json", action="store_true", help="Print full JSON response")
    events.set_defaults(func=command_events)

    search = subparsers.add_parser("search", help="Search events by team or league name")
    search.add_argument("--query", required=True, help="Search term (min 3 chars)")
    search.add_argument("--sport", help="Filter by sport slug")
    search.add_argument("--league", help="Filter by league slug")
    search.add_argument("--limit", type=int, help="Limit number of results shown")
    search.add_argument("--json", action="store_true", help="Print full JSON response")
    search.set_defaults(func=command_search)

    odds = subparsers.add_parser("odds", help="Fetch odds for a specific event")
    odds.add_argument("--event-id", required=True, help="Event ID")
    odds.add_argument("--bookmakers", required=True, help="Comma-separated bookmaker names")
    odds.add_argument("--summary", action="store_true", help="Print a compact summary")
    odds.set_defaults(func=command_odds)

    matchup = subparsers.add_parser("matchup", help="Search for a matchup and fetch odds")
    matchup.add_argument("--query", help="Search term (min 3 chars)")
    matchup.add_argument("--home", help="Home team name")
    matchup.add_argument("--away", help="Away team name")
    matchup.add_argument("--sport", help="Filter by sport slug")
    matchup.add_argument("--league", help="Filter by league slug")
    matchup.add_argument("--bookmakers", required=True, help="Comma-separated bookmaker names")
    matchup.add_argument("--pick", type=int, help="Pick event by 1-based index when multiple match")
    matchup.add_argument("--limit", type=int, help="Limit number of results shown")
    matchup.add_argument("--summary", action="store_true", help="Print a compact summary")
    matchup.set_defaults(func=command_matchup)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
