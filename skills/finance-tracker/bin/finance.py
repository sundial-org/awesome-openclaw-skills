#!/usr/bin/env python3
"""
Finance Tracker CLI
Track expenses with natural language

Usage:
    finance add <amount> "<description>"
    finance report [today|week|month|year|all]
    finance recent [n]
    finance search "<query>"
    finance categories
    finance export [csv|json]
    finance currency [code]
    finance help
"""

import sys
import os
import json

# Add lib to path - resolve symlinks
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(script_dir, '..', 'lib'))

from categories import detect_category, get_emoji, list_categories, CATEGORIES
from storage import get_storage
from reports import generate_report, list_recent, search_transactions
from parser import parse_expense, parse_amount, format_confirmation, format_error
from portfolio import get_portfolio, Portfolio
from trends import analyze_trends, compare_periods, get_budget_status


def cmd_add(args):
    """Add an expense."""
    if len(args) < 2:
        print(format_error("parse_failed", "Usage: finance add 50000 \"lunch\""))
        return 1
    
    # Parse amount
    try:
        amount = int(args[0].replace('k', '000').replace('K', '000'))
    except ValueError:
        amount = parse_amount(args[0])
    
    if amount is None or amount <= 0:
        print(format_error("invalid_amount"))
        return 1
    
    # Get description
    description = " ".join(args[1:]).strip('"\'')
    
    if not description:
        print(format_error("no_description"))
        return 1
    
    # Add transaction
    storage = get_storage()
    tx = storage.add_transaction(amount, description)
    
    print(format_confirmation(
        tx["amount"],
        tx["category"],
        tx["description"],
        storage.get_currency()
    ))
    
    return 0


def cmd_report(args):
    """Generate spending report."""
    period = args[0] if args else "month"
    print(generate_report(period))
    return 0


def cmd_recent(args):
    """List recent transactions."""
    n = int(args[0]) if args else 5
    print(list_recent(n))
    return 0


def cmd_search(args):
    """Search transactions."""
    if not args:
        print(format_error("parse_failed", "Usage: finance search \"food\""))
        return 1
    
    query = " ".join(args).strip('"\'')
    print(search_transactions(query))
    return 0


def cmd_categories(args):
    """List all categories."""
    print(list_categories())
    return 0


def cmd_export(args):
    """Export transactions."""
    format_type = args[0] if args else "csv"
    storage = get_storage()
    
    if format_type == "csv":
        print(storage.export_csv())
    elif format_type == "json":
        transactions = storage.get_transactions()
        print(json.dumps(transactions, indent=2, ensure_ascii=False))
    else:
        print(f"Unknown format: {format_type}. Use 'csv' or 'json'.")
        return 1
    
    return 0


def cmd_currency(args):
    """Get or set currency."""
    storage = get_storage()
    
    if args:
        storage.set_currency(args[0])
        print(f"✅ Currency set to {args[0].upper()}")
    else:
        print(f"💱 Currency: {storage.get_currency()}")
    
    return 0


def cmd_income(args):
    """Log income."""
    if len(args) < 2:
        print("❌ Usage: finance income 5000000 \"salary\"")
        return 1
    
    try:
        amount = int(args[0].replace('k', '000').replace('K', '000'))
    except ValueError:
        print("❌ Invalid amount")
        return 1
    
    description = " ".join(args[1:]).strip('"\'')
    
    # Detect income type
    income_type = "other"
    desc_lower = description.lower()
    if any(w in desc_lower for w in ["salary", "wage", "paycheck"]):
        income_type = "salary"
    elif any(w in desc_lower for w in ["freelance", "gig", "contract"]):
        income_type = "freelance"
    elif any(w in desc_lower for w in ["business", "sales", "revenue"]):
        income_type = "business"
    elif any(w in desc_lower for w in ["dividend", "interest", "investment"]):
        income_type = "investment"
    elif any(w in desc_lower for w in ["gift", "bonus"]):
        income_type = "gift"
    
    portfolio = get_portfolio()
    income = portfolio.add_income(amount, description, income_type)
    
    emoji = Portfolio.INCOME_TYPES.get(income_type, {}).get("emoji", "💰")
    print(f"✅ Income logged: {emoji} {amount:,} UZS — {description}")
    return 0


def cmd_asset(args):
    """Manage assets."""
    if len(args) < 1:
        portfolio = get_portfolio()
        print(portfolio.get_portfolio_report())
        return 0
    
    action = args[0].lower()
    portfolio = get_portfolio()
    
    if action == "add" and len(args) >= 3:
        name = args[1].strip('"\'')
        try:
            value = int(args[2].replace('k', '000').replace('K', '000'))
        except ValueError:
            print("❌ Invalid value")
            return 1
        
        asset_type = args[3] if len(args) > 3 else "other"
        asset = portfolio.add_asset(name, value, asset_type)
        
        emoji = Portfolio.ASSET_TYPES.get(asset_type, {}).get("emoji", "📦")
        print(f"✅ Asset added: {emoji} {name} = {value:,} UZS")
        return 0
    
    elif action == "remove" and len(args) >= 2:
        name = args[1].strip('"\'')
        if portfolio.remove_asset(name):
            print(f"✅ Removed: {name}")
        else:
            print(f"❌ Asset not found: {name}")
        return 0
    
    elif action == "list":
        print(portfolio.get_portfolio_report())
        return 0
    
    else:
        print("Usage: finance asset [add|remove|list] ...")
        return 1


def cmd_portfolio(args):
    """Show portfolio/net worth."""
    portfolio = get_portfolio()
    print(portfolio.get_portfolio_report())
    return 0


def cmd_trends(args):
    """Analyze spending trends."""
    days = int(args[0]) if args else 90
    print(analyze_trends(days))
    return 0


def cmd_compare(args):
    """Compare spending between periods."""
    days = int(args[0]) if args else 30
    print(compare_periods(days, days))
    return 0


def cmd_budget(args):
    """Check budget status."""
    if not args:
        print("Usage: finance budget <daily_amount>")
        print("Example: finance budget 100000")
        return 1
    
    try:
        daily = int(args[0].replace('k', '000').replace('K', '000'))
    except ValueError:
        print("❌ Invalid amount")
        return 1
    
    print(get_budget_status(daily))
    return 0


def cmd_help(args):
    """Show help."""
    help_text = """
💰 Finance Tracker — Complete Personal Finance Management

EXPENSES:
  finance add <amount> "<desc>"     Log an expense
  finance report [period]           View spending report
  finance recent [n]                List recent transactions
  finance search "<query>"          Search transactions

INCOME:
  finance income <amount> "<desc>"  Log income

PORTFOLIO:
  finance asset add "<name>" <value> [type]  Add/update asset
  finance asset remove "<name>"              Remove asset
  finance asset list                         List all assets
  finance portfolio                          Show net worth

ANALYSIS:
  finance trends [days]             Analyze spending patterns
  finance compare [days]            Compare periods
  finance budget <daily_amount>     Check against budget

OTHER:
  finance categories                List expense categories
  finance export [csv|json]         Export data
  finance currency [code]           Get/set currency

EXAMPLES:
  finance add 50000 "lunch at cafe"
  finance income 5000000 "salary"
  finance asset add "Bank Account" 10000000 cash
  finance trends 30
  finance budget 100k

ASSET TYPES: cash, stocks, crypto, realestate, savings, investments

TIPS:
  • Use 'k' for thousands: 50k = 50,000
  • Categories are auto-detected
  • Data stored in ~/.finance-tracker/
"""
    print(help_text)
    return 0


def main():
    if len(sys.argv) < 2:
        cmd_help([])
        return 0
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    commands = {
        "add": cmd_add,
        "report": cmd_report,
        "recent": cmd_recent,
        "search": cmd_search,
        "categories": cmd_categories,
        "export": cmd_export,
        "currency": cmd_currency,
        "income": cmd_income,
        "asset": cmd_asset,
        "portfolio": cmd_portfolio,
        "networth": cmd_portfolio,
        "trends": cmd_trends,
        "analyze": cmd_trends,
        "compare": cmd_compare,
        "budget": cmd_budget,
        "help": cmd_help,
        "--help": cmd_help,
        "-h": cmd_help,
    }
    
    if command in commands:
        return commands[command](args)
    else:
        print(f"Unknown command: {command}")
        print("Run 'finance help' for usage.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
