#!/usr/bin/env python3
"""
Earnings Calendar - Track earnings dates for portfolio stocks.

Features:
- Fetch earnings dates from FMP API
- Show upcoming earnings in daily briefing
- Alert 24h before earnings release
- Cache results to avoid API spam

Usage:
    earnings.py list              # Show all upcoming earnings
    earnings.py check             # Check what's reporting today/this week
    earnings.py refresh           # Force refresh earnings data
"""

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Paths
SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"
CACHE_DIR = SCRIPT_DIR.parent / "cache"
PORTFOLIO_FILE = CONFIG_DIR / "portfolio.csv"
EARNINGS_CACHE = CACHE_DIR / "earnings_calendar.json"
MANUAL_EARNINGS = CONFIG_DIR / "manual_earnings.json"  # For JP/other stocks not in Finnhub

# OpenBB binary path
OPENBB_BINARY = None
try:
    env_path = os.environ.get('OPENBB_QUOTE_BIN')
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        OPENBB_BINARY = env_path
    else:
        OPENBB_BINARY = shutil.which('openbb-quote')
except Exception:
    pass

# API Keys
def get_fmp_key() -> str:
    """Get FMP API key from environment or .env file."""
    key = os.environ.get("FMP_API_KEY", "")
    if not key:
        env_file = Path.home() / ".openclaw" / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("FMP_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    return key


def load_portfolio() -> list[dict]:
    """Load portfolio from CSV."""
    if not PORTFOLIO_FILE.exists():
        return []
    with open(PORTFOLIO_FILE, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_earnings_cache() -> dict:
    """Load cached earnings data."""
    if EARNINGS_CACHE.exists():
        try:
            return json.loads(EARNINGS_CACHE.read_text())
        except Exception:
            pass
    return {"last_updated": None, "earnings": {}}


def load_manual_earnings() -> dict:
    """
    Load manually-entered earnings dates (for JP stocks not in Finnhub).
    Format: {"6857.T": {"date": "2026-01-30", "time": "amc", "note": "Q3 FY2025"}, ...}
    """
    if MANUAL_EARNINGS.exists():
        try:
            data = json.loads(MANUAL_EARNINGS.read_text())
            # Filter out metadata keys (starting with _)
            return {k: v for k, v in data.items() if not k.startswith("_") and isinstance(v, dict)}
        except Exception:
            pass
    return {}


def save_earnings_cache(data: dict):
    """Save earnings data to cache."""
    CACHE_DIR.mkdir(exist_ok=True)
    EARNINGS_CACHE.write_text(json.dumps(data, indent=2, default=str))


def get_finnhub_key() -> str:
    """Get Finnhub API key from environment or .env file."""
    key = os.environ.get("FINNHUB_API_KEY", "")
    if not key:
        env_file = Path.home() / ".openclaw" / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("FINNHUB_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    return key


def fetch_all_earnings_finnhub(days_ahead: int = 60) -> dict:
    """
    Fetch all earnings for the next N days from Finnhub.
    Returns dict keyed by symbol: {"AAPL": {...}, ...}
    """
    finnhub_key = get_finnhub_key()
    if not finnhub_key:
        return {}
    
    from_date = datetime.now().strftime("%Y-%m-%d")
    to_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    url = f"https://finnhub.io/api/v1/calendar/earnings?from={from_date}&to={to_date}&token={finnhub_key}"
    
    try:
        req = Request(url, headers={"User-Agent": "finance-news/1.0"})
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            
            earnings_by_symbol = {}
            for entry in data.get("earningsCalendar", []):
                symbol = entry.get("symbol")
                if symbol:
                    earnings_by_symbol[symbol] = {
                        "date": entry.get("date"),
                        "time": entry.get("hour", ""),  # bmo/amc
                        "eps_estimate": entry.get("epsEstimate"),
                        "revenue_estimate": entry.get("revenueEstimate"),
                        "quarter": entry.get("quarter"),
                        "year": entry.get("year"),
                    }
            return earnings_by_symbol
    except Exception as e:
        print(f"❌ Finnhub error: {e}", file=sys.stderr)
        return {}


def normalize_ticker_for_lookup(ticker: str) -> list[str]:
    """
    Convert portfolio ticker to possible Finnhub symbols.
    Returns list of possible formats to try.
    """
    variants = [ticker]
    
    # Japanese stocks: 6857.T -> try 6857
    if ticker.endswith('.T'):
        base = ticker.replace('.T', '')
        variants.extend([base, f"{base}.T"])
    
    # Singapore stocks: D05.SI -> try D05
    elif ticker.endswith('.SI'):
        base = ticker.replace('.SI', '')
        variants.extend([base, f"{base}.SI"])
    
    return variants


def fetch_earnings_for_portfolio(portfolio: list[dict]) -> dict:
    """
    Fetch earnings dates for portfolio stocks using Finnhub bulk API.
    More efficient than per-ticker calls.
    """
    # Get all earnings for next 60 days
    all_earnings = fetch_all_earnings_finnhub(days_ahead=60)
    
    if not all_earnings:
        return {}
    
    # Match portfolio tickers to earnings data
    results = {}
    for stock in portfolio:
        ticker = stock["symbol"]
        variants = normalize_ticker_for_lookup(ticker)
        
        for variant in variants:
            if variant in all_earnings:
                results[ticker] = all_earnings[variant]
                break
    
    return results


def refresh_earnings(portfolio: list[dict], force: bool = False) -> dict:
    """Refresh earnings data for all portfolio stocks."""
    finnhub_key = get_finnhub_key()
    if not finnhub_key:
        print("❌ FINNHUB_API_KEY not found", file=sys.stderr)
        return {}
    
    cache = load_earnings_cache()
    
    # Check if cache is fresh (< 6 hours old)
    if not force and cache.get("last_updated"):
        try:
            last = datetime.fromisoformat(cache["last_updated"])
            if datetime.now() - last < timedelta(hours=6):
                print(f"📦 Using cached data (updated {last.strftime('%H:%M')})")
                return cache
        except Exception:
            pass
    
    print(f"🔄 Fetching earnings calendar from Finnhub...")
    
    # Use bulk fetch - much more efficient
    earnings = fetch_earnings_for_portfolio(portfolio)
    
    # Merge manual earnings (for JP stocks not in Finnhub)
    manual = load_manual_earnings()
    if manual:
        print(f"📝 Merging {len(manual)} manual entries...")
        for ticker, data in manual.items():
            if ticker not in earnings:  # Manual data fills gaps
                earnings[ticker] = data
    
    found = len(earnings)
    total = len(portfolio)
    print(f"✅ Found earnings data for {found}/{total} stocks")
    
    if earnings:
        for ticker, data in sorted(earnings.items(), key=lambda x: x[1].get("date", "")):
            print(f"  • {ticker}: {data.get('date', '?')}")
    
    cache = {
        "last_updated": datetime.now().isoformat(),
        "earnings": earnings
    }
    save_earnings_cache(cache)
    
    return cache


def list_earnings(args):
    """List all upcoming earnings for portfolio."""
    portfolio = load_portfolio()
    if not portfolio:
        print("📂 Portfolio empty")
        return
    
    cache = refresh_earnings(portfolio, force=args.refresh)
    earnings = cache.get("earnings", {})
    
    if not earnings:
        print("\n❌ No earnings dates found")
        return
    
    # Sort by date
    sorted_earnings = sorted(
        [(ticker, data) for ticker, data in earnings.items() if data.get("date")],
        key=lambda x: x[1]["date"]
    )
    
    print(f"\n📅 Upcoming Earnings ({len(sorted_earnings)} stocks)\n")
    
    today = datetime.now().date()
    
    for ticker, data in sorted_earnings:
        date_str = data["date"]
        try:
            ed = datetime.strptime(date_str, "%Y-%m-%d").date()
            days_until = (ed - today).days
            
            # Emoji based on timing
            if days_until < 0:
                emoji = "✅"  # Past
                timing = f"{-days_until}d ago"
            elif days_until == 0:
                emoji = "🔴"  # Today!
                timing = "TODAY"
            elif days_until == 1:
                emoji = "🟡"  # Tomorrow
                timing = "TOMORROW"
            elif days_until <= 7:
                emoji = "🟠"  # This week
                timing = f"in {days_until}d"
            else:
                emoji = "⚪"  # Later
                timing = f"in {days_until}d"
            
            # Time of day
            time_str = ""
            if data.get("time") == "bmo":
                time_str = " (pre-market)"
            elif data.get("time") == "amc":
                time_str = " (after-close)"
            
            # EPS estimate
            eps_str = ""
            if data.get("eps_estimate"):
                eps_str = f" | Est: ${data['eps_estimate']:.2f}"
            
            # Stock name from portfolio
            stock_name = next((s["name"] for s in portfolio if s["symbol"] == ticker), ticker)
            
            print(f"{emoji} {date_str} ({timing}): **{ticker}** — {stock_name}{time_str}{eps_str}")
            
        except ValueError:
            print(f"⚪ {date_str}: {ticker}")
    
    print()


def check_earnings(args):
    """Check earnings for today and this week (briefing format)."""
    portfolio = load_portfolio()
    if not portfolio:
        return

    cache = load_earnings_cache()

    # Auto-refresh if cache is stale
    if not cache.get("last_updated"):
        cache = refresh_earnings(portfolio, force=False)
    else:
        try:
            last = datetime.fromisoformat(cache["last_updated"])
            if datetime.now() - last > timedelta(hours=12):
                cache = refresh_earnings(portfolio, force=False)
        except Exception:
            cache = refresh_earnings(portfolio, force=False)

    earnings = cache.get("earnings", {})
    if not earnings:
        return

    today = datetime.now().date()
    week_only = getattr(args, 'week', False)

    # For weekly mode (Sunday cron), show Mon-Fri of upcoming week
    # Calculation: weekday() returns 0=Mon, 6=Sun. (7 - weekday) % 7 gives days until next Monday.
    # Special case: if today is Monday (result=0), we want next Monday (7 days), not today.
    if week_only:
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0 and today.weekday() != 0:
            days_until_monday = 7
        week_start = today + timedelta(days=days_until_monday)
        week_end = week_start + timedelta(days=4)  # Mon-Fri
    else:
        week_end = today + timedelta(days=7)

    today_list = []
    week_list = []

    for ticker, data in earnings.items():
        if not data.get("date"):
            continue
        try:
            ed = datetime.strptime(data["date"], "%Y-%m-%d").date()
            stock = next((s for s in portfolio if s["symbol"] == ticker), None)
            name = stock["name"] if stock else ticker
            category = stock.get("category", "") if stock else ""

            entry = {
                "ticker": ticker,
                "name": name,
                "date": ed,
                "time": data.get("time", ""),
                "eps_estimate": data.get("eps_estimate"),
                "category": category,
            }

            if week_only:
                # Weekly mode: only show week range
                if week_start <= ed <= week_end:
                    week_list.append(entry)
            else:
                # Daily mode: today + this week
                if ed == today:
                    today_list.append(entry)
                elif today < ed <= week_end:
                    week_list.append(entry)
        except ValueError:
            continue
    
    # Handle JSON output
    if getattr(args, 'json', False):
        if week_only:
            result = {
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "earnings": [
                    {
                        "ticker": e["ticker"],
                        "name": e["name"],
                        "date": e["date"].isoformat(),
                        "time": e["time"],
                        "eps_estimate": e.get("eps_estimate"),
                        "category": e.get("category", ""),
                    }
                    for e in sorted(week_list, key=lambda x: x["date"])
                ],
            }
        else:
            result = {
                "today": [
                    {
                        "ticker": e["ticker"],
                        "name": e["name"],
                        "date": e["date"].isoformat(),
                        "time": e["time"],
                        "eps_estimate": e.get("eps_estimate"),
                        "category": e.get("category", ""),
                    }
                    for e in sorted(today_list, key=lambda x: x.get("time", "zzz"))
                ],
                "this_week": [
                    {
                        "ticker": e["ticker"],
                        "name": e["name"],
                        "date": e["date"].isoformat(),
                        "time": e["time"],
                        "eps_estimate": e.get("eps_estimate"),
                        "category": e.get("category", ""),
                    }
                    for e in sorted(week_list, key=lambda x: x["date"])
                ],
            }
        print(json.dumps(result, indent=2))
        return

    # Translations
    lang = getattr(args, 'lang', 'en')
    if lang == "de":
        labels = {
            "today": "EARNINGS HEUTE",
            "week": "EARNINGS DIESE WOCHE",
            "week_preview": "EARNINGS NÄCHSTE WOCHE",
            "pre": "vor Börseneröffnung",
            "post": "nach Börsenschluss",
            "pre_short": "vor",
            "post_short": "nach",
            "est": "Erw",
            "none": "Keine Earnings diese Woche",
            "none_week": "Keine Earnings nächste Woche",
        }
    else:
        labels = {
            "today": "EARNINGS TODAY",
            "week": "EARNINGS THIS WEEK",
            "week_preview": "EARNINGS NEXT WEEK",
            "pre": "pre-market",
            "post": "after-close",
            "pre_short": "pre",
            "post_short": "post",
            "est": "Est",
            "none": "No earnings this week",
            "none_week": "No earnings next week",
        }

    # Date header
    date_str = datetime.now().strftime("%b %d, %Y") if lang == "en" else datetime.now().strftime("%d. %b %Y")

    # Output for briefing
    output = []

    # Daily mode: show today's earnings
    if not week_only and today_list:
        output.append(f"📅 {labels['today']} — {date_str}\n")
        for e in sorted(today_list, key=lambda x: x.get("time", "zzz")):
            time_str = f" ({labels['pre']})" if e["time"] == "bmo" else f" ({labels['post']})" if e["time"] == "amc" else ""
            eps_str = f" — {labels['est']}: ${e['eps_estimate']:.2f}" if e.get("eps_estimate") else ""
            output.append(f"• {e['ticker']} — {e['name']}{time_str}{eps_str}")
        output.append("")

    if week_list:
        # Use different header for weekly preview mode
        week_label = labels['week_preview'] if week_only else labels['week']
        if week_only:
            # Show date range for weekly preview
            week_range = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"
            output.append(f"📅 {week_label} ({week_range})\n")
        else:
            output.append(f"📅 {week_label}\n")
        for e in sorted(week_list, key=lambda x: x["date"]):
            day_name = e["date"].strftime("%a %d.%m")
            time_str = f" ({labels['pre_short']})" if e["time"] == "bmo" else f" ({labels['post_short']})" if e["time"] == "amc" else ""
            output.append(f"• {day_name}: {e['ticker']} — {e['name']}{time_str}")
        output.append("")

    if output:
        print("\n".join(output))
    else:
        if args.verbose:
            no_earnings_label = labels['none_week'] if week_only else labels['none']
            print(f"📅 {no_earnings_label}")


def get_briefing_section() -> str:
    """Get earnings section for daily briefing (called by briefing.py)."""
    from io import StringIO
    import contextlib

    # Capture check output
    class Args:
        verbose = False

    f = StringIO()
    with contextlib.redirect_stdout(f):
        check_earnings(Args())

    return f.getvalue()


def get_earnings_context(symbols: list[str]) -> list[dict]:
    """
    Get recent earnings data (beats/misses) for symbols using OpenBB.

    Returns list of dicts with: symbol, eps_actual, eps_estimate, surprise, revenue_actual, revenue_estimate
    """
    if not OPENBB_BINARY:
        return []

    results = []
    for symbol in symbols[:10]:  # Limit to 10 symbols
        try:
            result = subprocess.run(
                [OPENBB_BINARY, symbol, '--earnings'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    if isinstance(data, list) and data:
                        results.append({
                            'symbol': symbol,
                            'earnings': data[0] if isinstance(data[0], dict) else {}
                        })
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass
    return results


def get_analyst_ratings(symbols: list[str]) -> list[dict]:
    """
    Get analyst upgrades/downgrades for symbols using OpenBB.

    Returns list of dicts with: symbol, rating, target_price, firm, direction
    """
    if not OPENBB_BINARY:
        return []

    results = []
    for symbol in symbols[:10]:  # Limit to 10 symbols
        try:
            result = subprocess.run(
                [OPENBB_BINARY, symbol, '--rating'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    if isinstance(data, list) and data:
                        results.append({
                            'symbol': symbol,
                            'rating': data[0] if isinstance(data[0], dict) else {}
                        })
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass
    return results


def main():
    parser = argparse.ArgumentParser(description="Earnings Calendar Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List all upcoming earnings")
    list_parser.add_argument("--refresh", "-r", action="store_true", help="Force refresh")
    list_parser.set_defaults(func=list_earnings)
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check today/this week")
    check_parser.add_argument("--verbose", "-v", action="store_true")
    check_parser.add_argument("--json", action="store_true", help="JSON output")
    check_parser.add_argument("--lang", default="en", help="Output language (en, de)")
    check_parser.add_argument("--week", action="store_true", help="Show full week preview (for weekly cron)")
    check_parser.set_defaults(func=check_earnings)
    
    # refresh command
    refresh_parser = subparsers.add_parser("refresh", help="Force refresh all data")
    refresh_parser.set_defaults(func=lambda a: refresh_earnings(load_portfolio(), force=True))
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
