#!/usr/bin/env python3
"""
stocks.py - Unified stock management for holdings and watchlist.

Single source of truth for:
- Holdings (stocks you own)
- Watchlist (stocks you're watching to buy)

Usage:
    from stocks import load_stocks, save_stocks, get_holdings, get_watchlist
    from stocks import add_to_watchlist, add_to_holdings, move_to_holdings

CLI:
    stocks.py list [--holdings|--watchlist]
    stocks.py add-watchlist TICKER [--target 380] [--notes "Buy zone"]
    stocks.py add-holding TICKER --name "Company" [--category "Tech"]
    stocks.py move TICKER  # watchlist → holdings (you bought it)
    stocks.py remove TICKER [--from holdings|watchlist]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Default path - can be overridden
STOCKS_FILE = Path(__file__).parent.parent / "config" / "stocks.json"


def load_stocks(path: Optional[Path] = None) -> dict:
    """Load the unified stocks file."""
    path = path or STOCKS_FILE
    if not path.exists():
        return {
            "version": "1.0",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "holdings": [],
            "watchlist": [],
            "alert_definitions": {}
        }
    
    with open(path, 'r') as f:
        return json.load(f)


def save_stocks(data: dict, path: Optional[Path] = None):
    """Save the unified stocks file."""
    path = path or STOCKS_FILE
    data["updated"] = datetime.now().strftime("%Y-%m-%d")
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def get_holdings(data: Optional[dict] = None) -> list:
    """Get list of holdings."""
    if data is None:
        data = load_stocks()
    return data.get("holdings", [])


def get_watchlist(data: Optional[dict] = None) -> list:
    """Get list of watchlist items."""
    if data is None:
        data = load_stocks()
    return data.get("watchlist", [])


def get_holding_tickers(data: Optional[dict] = None) -> set:
    """Get set of holding tickers for quick lookup."""
    holdings = get_holdings(data)
    return {h.get("ticker") for h in holdings}


def get_watchlist_tickers(data: Optional[dict] = None) -> set:
    """Get set of watchlist tickers for quick lookup."""
    watchlist = get_watchlist(data)
    return {w.get("ticker") for w in watchlist}


def add_to_watchlist(
    ticker: str,
    target: Optional[float] = None,
    stop: Optional[float] = None,
    notes: str = "",
    alerts: Optional[list] = None
) -> bool:
    """Add a stock to the watchlist."""
    data = load_stocks()
    
    # Check if already in watchlist
    for w in data["watchlist"]:
        if w.get("ticker") == ticker:
            # Update existing
            if target is not None:
                w["target"] = target
            if stop is not None:
                w["stop"] = stop
            if notes:
                w["notes"] = notes
            if alerts is not None:
                w["alerts"] = alerts
            save_stocks(data)
            return True
    
    # Add new
    data["watchlist"].append({
        "ticker": ticker,
        "target": target,
        "stop": stop,
        "alerts": alerts or [],
        "notes": notes
    })
    data["watchlist"].sort(key=lambda x: x.get("ticker", ""))
    save_stocks(data)
    return True


def add_to_holdings(
    ticker: str,
    name: str = "",
    category: str = "",
    notes: str = "",
    target: Optional[float] = None,
    stop: Optional[float] = None,
    alerts: Optional[list] = None
) -> bool:
    """Add a stock to holdings. Target/stop for 'buy more' alerts."""
    data = load_stocks()
    
    # Check if already in holdings
    for h in data["holdings"]:
        if h.get("ticker") == ticker:
            # Update existing
            if name:
                h["name"] = name
            if category:
                h["category"] = category
            if notes:
                h["notes"] = notes
            if target is not None:
                h["target"] = target
            if stop is not None:
                h["stop"] = stop
            if alerts is not None:
                h["alerts"] = alerts
            save_stocks(data)
            return True
    
    # Add new
    data["holdings"].append({
        "ticker": ticker,
        "name": name,
        "category": category,
        "notes": notes,
        "target": target,
        "stop": stop,
        "alerts": alerts or []
    })
    data["holdings"].sort(key=lambda x: x.get("ticker", ""))
    save_stocks(data)
    return True


def move_to_holdings(
    ticker: str,
    name: str = "",
    category: str = "",
    notes: str = ""
) -> bool:
    """Move a stock from watchlist to holdings (you bought it)."""
    data = load_stocks()
    
    # Find in watchlist
    watchlist_item = None
    for i, w in enumerate(data["watchlist"]):
        if w.get("ticker") == ticker:
            watchlist_item = data["watchlist"].pop(i)
            break
    
    if not watchlist_item:
        print(f"⚠️ {ticker} not found in watchlist", file=sys.stderr)
        return False
    
    # Add to holdings
    data["holdings"].append({
        "ticker": ticker,
        "name": name or watchlist_item.get("notes", ""),
        "category": category,
        "notes": notes or f"Bought (was on watchlist with target ${watchlist_item.get('target', 'N/A')})"
    })
    data["holdings"].sort(key=lambda x: x.get("ticker", ""))
    save_stocks(data)
    return True


def remove_stock(ticker: str, from_list: str = "both") -> bool:
    """Remove a stock from holdings, watchlist, or both."""
    data = load_stocks()
    removed = False
    
    if from_list in ("holdings", "both"):
        original_len = len(data["holdings"])
        data["holdings"] = [h for h in data["holdings"] if h.get("ticker") != ticker]
        if len(data["holdings"]) < original_len:
            removed = True
    
    if from_list in ("watchlist", "both"):
        original_len = len(data["watchlist"])
        data["watchlist"] = [w for w in data["watchlist"] if w.get("ticker") != ticker]
        if len(data["watchlist"]) < original_len:
            removed = True
    
    if removed:
        save_stocks(data)
    return removed


def list_stocks(show_holdings: bool = True, show_watchlist: bool = True):
    """Print stocks list."""
    data = load_stocks()
    
    if show_holdings:
        print(f"\n📊 HOLDINGS ({len(data['holdings'])})")
        print("-" * 50)
        for h in data["holdings"][:20]:
            print(f"  {h['ticker']:10} {h.get('name', '')[:30]}")
        if len(data["holdings"]) > 20:
            print(f"  ... and {len(data['holdings']) - 20} more")
    
    if show_watchlist:
        print(f"\n👀 WATCHLIST ({len(data['watchlist'])})")
        print("-" * 50)
        for w in data["watchlist"][:20]:
            target = f"${w['target']}" if w.get('target') else "no target"
            print(f"  {w['ticker']:10} {target:>10}  {w.get('notes', '')[:25]}")
        if len(data["watchlist"]) > 20:
            print(f"  ... and {len(data['watchlist']) - 20} more")


def main():
    parser = argparse.ArgumentParser(description="Unified stock management")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list
    list_parser = subparsers.add_parser("list", help="List stocks")
    list_parser.add_argument("--holdings", action="store_true", help="Show only holdings")
    list_parser.add_argument("--watchlist", action="store_true", help="Show only watchlist")
    
    # add-watchlist
    add_watch = subparsers.add_parser("add-watchlist", help="Add to watchlist")
    add_watch.add_argument("ticker", help="Stock ticker")
    add_watch.add_argument("--target", type=float, help="Target price")
    add_watch.add_argument("--stop", type=float, help="Stop loss")
    add_watch.add_argument("--notes", default="", help="Notes")
    
    # add-holding
    add_hold = subparsers.add_parser("add-holding", help="Add to holdings")
    add_hold.add_argument("ticker", help="Stock ticker")
    add_hold.add_argument("--name", default="", help="Company name")
    add_hold.add_argument("--category", default="", help="Category")
    add_hold.add_argument("--notes", default="", help="Notes")
    add_hold.add_argument("--target", type=float, help="Buy-more target price")
    add_hold.add_argument("--stop", type=float, help="Stop loss price")
    
    # move (watchlist → holdings)
    move = subparsers.add_parser("move", help="Move from watchlist to holdings")
    move.add_argument("ticker", help="Stock ticker")
    move.add_argument("--name", default="", help="Company name")
    move.add_argument("--category", default="", help="Category")
    
    # remove
    remove = subparsers.add_parser("remove", help="Remove stock")
    remove.add_argument("ticker", help="Stock ticker")
    remove.add_argument("--from", dest="from_list", choices=["holdings", "watchlist", "both"],
                        default="both", help="Remove from which list")
    
    # set-alert (for existing holdings)
    set_alert = subparsers.add_parser("set-alert", help="Set buy-more/stop alert on holding")
    set_alert.add_argument("ticker", help="Stock ticker")
    set_alert.add_argument("--target", type=float, help="Buy-more target price")
    set_alert.add_argument("--stop", type=float, help="Stop loss price")
    
    args = parser.parse_args()
    
    if args.command == "list":
        show_h = not args.watchlist or args.holdings
        show_w = not args.holdings or args.watchlist
        if not args.holdings and not args.watchlist:
            show_h = show_w = True
        list_stocks(show_holdings=show_h, show_watchlist=show_w)
    
    elif args.command == "add-watchlist":
        add_to_watchlist(args.ticker.upper(), args.target, args.stop, args.notes)
        print(f"✅ Added {args.ticker.upper()} to watchlist")
    
    elif args.command == "add-holding":
        add_to_holdings(args.ticker.upper(), args.name, args.category, args.notes,
                        args.target, args.stop)
        print(f"✅ Added {args.ticker.upper()} to holdings")
    
    elif args.command == "move":
        if move_to_holdings(args.ticker.upper(), args.name, args.category):
            print(f"✅ Moved {args.ticker.upper()} from watchlist to holdings")
    
    elif args.command == "remove":
        if remove_stock(args.ticker.upper(), args.from_list):
            print(f"✅ Removed {args.ticker.upper()}")
        else:
            print(f"⚠️ {args.ticker.upper()} not found")
    
    elif args.command == "set-alert":
        data = load_stocks()
        found = False
        for h in data["holdings"]:
            if h.get("ticker") == args.ticker.upper():
                if args.target is not None:
                    h["target"] = args.target
                if args.stop is not None:
                    h["stop"] = args.stop
                save_stocks(data)
                found = True
                print(f"✅ Set alert on {args.ticker.upper()}: target=${args.target}, stop=${args.stop}")
                break
        if not found:
            print(f"⚠️ {args.ticker.upper()} not found in holdings")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
