#!/usr/bin/env python3
"""
Price Target Alerts - Track buy zone alerts for stocks.

Features:
- Set price target alerts (buy zone triggers)
- Check alerts against current prices
- Snooze, update, delete alerts
- Multi-currency support (USD, EUR, JPY, SGD, MXN)

Usage:
    alerts.py list                           # Show all alerts
    alerts.py set CRWD 400 --note 'Kaufzone' # Set alert
    alerts.py check                          # Check triggered alerts
    alerts.py delete CRWD                    # Delete alert
    alerts.py snooze CRWD --days 7           # Snooze for 7 days
    alerts.py update CRWD 380                # Update target price
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from utils import ensure_venv

ensure_venv()

# Lazy import to avoid numpy issues at module load
fetch_market_data = None

def get_fetch_market_data():
    global fetch_market_data
    if fetch_market_data is None:
        from fetch_news import fetch_market_data as fmd
        fetch_market_data = fmd
    return fetch_market_data

SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"
ALERTS_FILE = CONFIG_DIR / "alerts.json"

SUPPORTED_CURRENCIES = ["USD", "EUR", "JPY", "SGD", "MXN"]


def load_alerts() -> dict:
    """Load alerts from JSON file."""
    if not ALERTS_FILE.exists():
        return {"_meta": {"version": 1, "supported_currencies": SUPPORTED_CURRENCIES}, "alerts": []}
    return json.loads(ALERTS_FILE.read_text())


def save_alerts(data: dict) -> None:
    """Save alerts to JSON file."""
    data["_meta"]["updated_at"] = datetime.now().isoformat()
    ALERTS_FILE.write_text(json.dumps(data, indent=2))


def get_alert_by_ticker(alerts: list, ticker: str) -> dict | None:
    """Find alert by ticker."""
    ticker = ticker.upper()
    for alert in alerts:
        if alert["ticker"] == ticker:
            return alert
    return None


def format_price(price: float, currency: str) -> str:
    """Format price with currency symbol."""
    symbols = {"USD": "$", "EUR": "€", "JPY": "¥", "SGD": "S$", "MXN": "MX$"}
    symbol = symbols.get(currency, currency + " ")
    if currency == "JPY":
        return f"{symbol}{price:,.0f}"
    return f"{symbol}{price:,.2f}"


def cmd_list(args) -> None:
    """List all alerts."""
    data = load_alerts()
    alerts = data.get("alerts", [])
    
    if not alerts:
        print("📭 No price alerts set")
        return
    
    print(f"📊 Price Alerts ({len(alerts)} total)\n")
    
    now = datetime.now()
    active = []
    snoozed = []
    
    for alert in alerts:
        snooze_until = alert.get("snooze_until")
        if snooze_until and datetime.fromisoformat(snooze_until) > now:
            snoozed.append(alert)
        else:
            active.append(alert)
    
    if active:
        print("### Active Alerts")
        for a in active:
            target = format_price(a["target_price"], a.get("currency", "USD"))
            note = f' — "{a["note"]}"' if a.get("note") else ""
            user = f" (by {a['set_by']})" if a.get("set_by") else ""
            print(f"  • {a['ticker']}: {target}{note}{user}")
        print()
    
    if snoozed:
        print("### Snoozed")
        for a in snoozed:
            target = format_price(a["target_price"], a.get("currency", "USD"))
            until = datetime.fromisoformat(a["snooze_until"]).strftime("%Y-%m-%d")
            print(f"  • {a['ticker']}: {target} (until {until})")
        print()


def cmd_set(args) -> None:
    """Set a new alert."""
    data = load_alerts()
    alerts = data.get("alerts", [])
    ticker = args.ticker.upper()
    
    # Check if alert exists
    existing = get_alert_by_ticker(alerts, ticker)
    if existing:
        print(f"⚠️ Alert for {ticker} already exists. Use 'update' to change target.")
        return
    
    # Validate target price
    if args.target <= 0:
        print(f"❌ Target price must be greater than 0")
        return
    
    currency = args.currency.upper() if args.currency else "USD"
    if currency not in SUPPORTED_CURRENCIES:
        print(f"❌ Currency {currency} not supported. Use: {', '.join(SUPPORTED_CURRENCIES)}")
        return
    
    # Warn about currency mismatch based on ticker suffix
    ticker_currency_map = {
        ".T": "JPY",      # Tokyo
        ".SI": "SGD",     # Singapore
        ".MX": "MXN",     # Mexico
        ".DE": "EUR", ".F": "EUR", ".PA": "EUR",  # Europe
    }
    expected_currency = "USD"  # Default for US stocks
    for suffix, curr in ticker_currency_map.items():
        if ticker.endswith(suffix):
            expected_currency = curr
            break
    
    if currency != expected_currency:
        print(f"⚠️ Warning: {ticker} trades in {expected_currency}, but alert set in {currency}")
    
    # Fetch current price (optional - may fail if numpy broken)
    current_price = None
    try:
        quotes = get_fetch_market_data()([ticker], timeout=10)
        if ticker in quotes and quotes[ticker].get("price"):
            current_price = quotes[ticker]["price"]
    except Exception as e:
        print(f"⚠️ Could not fetch current price: {e}", file=sys.stderr)
    
    alert = {
        "ticker": ticker,
        "target_price": args.target,
        "currency": currency,
        "note": args.note or "",
        "set_by": args.user or "",
        "set_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "active",
        "snooze_until": None,
        "triggered_count": 0,
        "last_triggered": None,
    }
    
    alerts.append(alert)
    data["alerts"] = alerts
    save_alerts(data)
    
    target_str = format_price(args.target, currency)
    print(f"✅ Alert set: {ticker} under {target_str}")
    if current_price:
        pct_diff = ((current_price - args.target) / current_price) * 100
        current_str = format_price(current_price, currency)
        print(f"   Current: {current_str} ({pct_diff:+.1f}% to target)")


def cmd_delete(args) -> None:
    """Delete an alert."""
    data = load_alerts()
    alerts = data.get("alerts", [])
    ticker = args.ticker.upper()
    
    new_alerts = [a for a in alerts if a["ticker"] != ticker]
    if len(new_alerts) == len(alerts):
        print(f"❌ No alert found for {ticker}")
        return
    
    data["alerts"] = new_alerts
    save_alerts(data)
    print(f"🗑️ Alert deleted: {ticker}")


def cmd_snooze(args) -> None:
    """Snooze an alert."""
    data = load_alerts()
    alerts = data.get("alerts", [])
    ticker = args.ticker.upper()
    
    alert = get_alert_by_ticker(alerts, ticker)
    if not alert:
        print(f"❌ No alert found for {ticker}")
        return
    
    days = args.days or 7
    snooze_until = datetime.now() + timedelta(days=days)
    alert["snooze_until"] = snooze_until.isoformat()
    save_alerts(data)
    print(f"😴 Alert snoozed: {ticker} until {snooze_until.strftime('%Y-%m-%d')}")


def cmd_update(args) -> None:
    """Update alert target price."""
    data = load_alerts()
    alerts = data.get("alerts", [])
    ticker = args.ticker.upper()
    
    alert = get_alert_by_ticker(alerts, ticker)
    if not alert:
        print(f"❌ No alert found for {ticker}")
        return
    
    # Validate target price
    if args.target <= 0:
        print(f"❌ Target price must be greater than 0")
        return
    
    old_target = alert["target_price"]
    alert["target_price"] = args.target
    if args.note:
        alert["note"] = args.note
    save_alerts(data)
    
    currency = alert.get("currency", "USD")
    old_str = format_price(old_target, currency)
    new_str = format_price(args.target, currency)
    print(f"✏️ Alert updated: {ticker} {old_str} → {new_str}")


def cmd_check(args) -> None:
    """Check alerts against current prices."""
    data = load_alerts()
    alerts = data.get("alerts", [])
    
    if not alerts:
        if args.json:
            print(json.dumps({"triggered": [], "watching": []}))
        else:
            print("📭 No alerts to check")
        return
    
    now = datetime.now()
    active_alerts = []
    for alert in alerts:
        snooze_until = alert.get("snooze_until")
        if snooze_until and datetime.fromisoformat(snooze_until) > now:
            continue
        active_alerts.append(alert)
    
    if not active_alerts:
        if args.json:
            print(json.dumps({"triggered": [], "watching": []}))
        else:
            print("📭 All alerts snoozed")
        return
    
    # Fetch prices for all active alerts
    tickers = [a["ticker"] for a in active_alerts]
    quotes = get_fetch_market_data()(tickers, timeout=30)
    
    triggered = []
    watching = []
    
    for alert in active_alerts:
        ticker = alert["ticker"]
        target = alert["target_price"]
        currency = alert.get("currency", "USD")
        
        quote = quotes.get(ticker, {})
        price = quote.get("price")
        
        if price is None:
            continue
        
        # Divide-by-zero protection
        if target == 0:
            pct_diff = 0
        else:
            pct_diff = ((price - target) / target) * 100
        
        result = {
            "ticker": ticker,
            "target_price": target,
            "current_price": price,
            "currency": currency,
            "pct_from_target": round(pct_diff, 2),
            "note": alert.get("note", ""),
            "set_by": alert.get("set_by", ""),
        }
        
        if price <= target:
            triggered.append(result)
            # Update triggered count (only once per day to avoid inflation)
            last_triggered = alert.get("last_triggered")
            today = now.strftime("%Y-%m-%d")
            if not last_triggered or not last_triggered.startswith(today):
                alert["triggered_count"] = alert.get("triggered_count", 0) + 1
            alert["last_triggered"] = now.isoformat()
        else:
            watching.append(result)
    
    save_alerts(data)
    
    if args.json:
        print(json.dumps({"triggered": triggered, "watching": watching}, indent=2))
        return

    # Translations
    lang = getattr(args, 'lang', 'en')
    if lang == "de":
        labels = {
            "title": "PREISWARNUNGEN",
            "in_zone": "IN KAUFZONE",
            "buy": "KAUFEN!",
            "target": "Ziel",
            "watching": "BEOBACHTUNG",
            "to_target": "noch",
            "no_data": "Keine Preisdaten für Alerts verfügbar",
        }
    else:
        labels = {
            "title": "PRICE ALERTS",
            "in_zone": "IN BUY ZONE",
            "buy": "BUY SIGNAL",
            "target": "target",
            "watching": "WATCHING",
            "to_target": "to target",
            "no_data": "No price data available for alerts",
        }

    # Date header
    date_str = datetime.now().strftime("%b %d, %Y") if lang == "en" else datetime.now().strftime("%d. %b %Y")
    print(f"📊 {labels['title']} — {date_str}\n")

    # Human-readable output
    if triggered:
        print(f"🟢 {labels['in_zone']}:\n")
        for t in triggered:
            target_str = format_price(t["target_price"], t["currency"])
            current_str = format_price(t["current_price"], t["currency"])
            note = f'\n   "{t["note"]}"' if t.get("note") else ""
            user = f" — {t['set_by']}" if t.get("set_by") else ""
            print(f"• {t['ticker']}: {current_str} ({labels['target']}: {target_str}) ← {labels['buy']}{note}{user}")
        print()

    if watching:
        print(f"⏳ {labels['watching']}:\n")
        for w in sorted(watching, key=lambda x: x["pct_from_target"]):
            target_str = format_price(w["target_price"], w["currency"])
            current_str = format_price(w["current_price"], w["currency"])
            print(f"• {w['ticker']}: {current_str} ({labels['target']}: {target_str}) — {labels['to_target']} {abs(w['pct_from_target']):.1f}%")
        print()

    if not triggered and not watching:
        print(f"📭 {labels['no_data']}")


def check_alerts() -> dict:
    """
    Check alerts and return results for briefing integration.
    Returns: {"triggered": [...], "watching": [...]}
    """
    data = load_alerts()
    alerts = data.get("alerts", [])
    
    if not alerts:
        return {"triggered": [], "watching": []}
    
    now = datetime.now()
    active_alerts = [
        a for a in alerts
        if not a.get("snooze_until") or datetime.fromisoformat(a["snooze_until"]) <= now
    ]
    
    if not active_alerts:
        return {"triggered": [], "watching": []}
    
    tickers = [a["ticker"] for a in active_alerts]
    quotes = get_fetch_market_data()(tickers, timeout=30)
    
    triggered = []
    watching = []
    
    for alert in active_alerts:
        ticker = alert["ticker"]
        target = alert["target_price"]
        currency = alert.get("currency", "USD")
        
        quote = quotes.get(ticker, {})
        price = quote.get("price")
        
        if price is None:
            continue
        
        # Divide-by-zero protection
        if target == 0:
            pct_diff = 0
        else:
            pct_diff = ((price - target) / target) * 100
        
        result = {
            "ticker": ticker,
            "target_price": target,
            "current_price": price,
            "currency": currency,
            "pct_from_target": round(pct_diff, 2),
            "note": alert.get("note", ""),
            "set_by": alert.get("set_by", ""),
        }
        
        if price <= target:
            triggered.append(result)
            # Update triggered count (only once per day to avoid inflation)
            last_triggered = alert.get("last_triggered")
            today = now.strftime("%Y-%m-%d")
            if not last_triggered or not last_triggered.startswith(today):
                alert["triggered_count"] = alert.get("triggered_count", 0) + 1
            alert["last_triggered"] = now.isoformat()
        else:
            watching.append(result)
    
    save_alerts(data)
    return {"triggered": triggered, "watching": watching}


def main():
    parser = argparse.ArgumentParser(description="Price target alerts")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # list
    subparsers.add_parser("list", help="List all alerts")
    
    # set
    set_parser = subparsers.add_parser("set", help="Set new alert")
    set_parser.add_argument("ticker", help="Stock ticker")
    set_parser.add_argument("target", type=float, help="Target price")
    set_parser.add_argument("--note", help="Note/reason")
    set_parser.add_argument("--user", help="Who set the alert")
    set_parser.add_argument("--currency", default="USD", help="Currency (USD, EUR, JPY, SGD, MXN)")
    
    # delete
    del_parser = subparsers.add_parser("delete", help="Delete alert")
    del_parser.add_argument("ticker", help="Stock ticker")
    
    # snooze
    snooze_parser = subparsers.add_parser("snooze", help="Snooze alert")
    snooze_parser.add_argument("ticker", help="Stock ticker")
    snooze_parser.add_argument("--days", type=int, default=7, help="Days to snooze")
    
    # update
    update_parser = subparsers.add_parser("update", help="Update alert target")
    update_parser.add_argument("ticker", help="Stock ticker")
    update_parser.add_argument("target", type=float, help="New target price")
    update_parser.add_argument("--note", help="Update note")
    
    # check
    check_parser = subparsers.add_parser("check", help="Check alerts against prices")
    check_parser.add_argument("--json", action="store_true", help="JSON output")
    check_parser.add_argument("--lang", default="en", help="Output language (en, de)")
    
    args = parser.parse_args()
    
    if args.command == "list":
        cmd_list(args)
    elif args.command == "set":
        cmd_set(args)
    elif args.command == "delete":
        cmd_delete(args)
    elif args.command == "snooze":
        cmd_snooze(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()
