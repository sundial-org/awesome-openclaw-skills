#!/usr/bin/env python3
"""Manually add congressional trades to the tracking file"""
import json
import os
import sys
from datetime import datetime

TRADES_FILE = 'congressional_trades.json'

def load_trades():
    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_trades(trades):
    with open(TRADES_FILE, 'w') as f:
        json.dump(trades, f, indent=2)

def add_trade():
    print("=== Add Pelosi Trade ===")
    print()

    ticker = input("Stock ticker (e.g., NVDA): ").strip().upper()
    if not ticker:
        print("Ticker required")
        return

    tx_type = input("Transaction type (purchase/sale): ").strip().lower()
    if tx_type not in ['purchase', 'sale']:
        print("Must be 'purchase' or 'sale'")
        return

    amount = input("Estimated amount (e.g., 500000): ").strip()
    try:
        amount = float(amount.replace(',', '').replace('$', ''))
    except:
        print("Invalid amount")
        return

    tx_date = input(f"Transaction date (YYYY-MM-DD, default today): ").strip()
    if not tx_date:
        tx_date = datetime.now().strftime('%Y-%m-%d')

    trade = {
        'transaction_date': tx_date,
        'disclosure_date': datetime.now().strftime('%Y-%m-%d'),
        'ticker': ticker,
        'symbol': ticker,
        'asset_name': f'{ticker} Stock',
        'transaction_type': tx_type,
        'amount': amount,
        'amount_range': f'${amount:,.0f}',
        'representative': 'Hon. Nancy Pelosi',
        'source': 'manual'
    }

    trades = load_trades()
    trades.insert(0, trade)  # Add to beginning
    save_trades(trades)

    print()
    print(f"✓ Added: {ticker} {tx_type} ${amount:,.0f} on {tx_date}")
    print(f"Total trades in file: {len(trades)}")

def list_trades():
    trades = load_trades()
    if not trades:
        print("No trades in file")
        return

    print(f"=== {len(trades)} Trades ===")
    for t in trades[:10]:
        print(f"{t['transaction_date']} | {t['ticker']:6} | {t['transaction_type']:8} | {t['amount_range']}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_trades()
    else:
        add_trade()
