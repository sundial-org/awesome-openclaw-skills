#!/usr/bin/env python3
"""
Institutional Flow Tracker - Main Screening Script

Screens for stocks with significant institutional ownership changes by analyzing
13F filings data. Identifies stocks where smart money is accumulating or distributing.

Usage:
    python3 track_institutional_flow.py --top 50 --min-change-percent 10
    python3 track_institutional_flow.py --sector Technology --min-institutions 20
    python3 track_institutional_flow.py --api-key YOUR_KEY --output results.json

Requirements:
    - FMP API key (set FMP_API_KEY environment variable or pass --api-key)
    - Free tier: 250 requests/day (sufficient for ~40-50 stocks)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import time

try:
    import requests
except ImportError:
    print("Error: 'requests' library not installed. Install with: pip install requests")
    sys.exit(1)


class InstitutionalFlowTracker:
    """Track institutional ownership changes across stocks"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.base_url_v4 = "https://financialmodelingprep.com/api/v4"

    def get_stock_screener(
        self,
        market_cap_min: int = 1000000000,
        limit: int = 500
    ) -> List[Dict]:
        """Get list of stocks meeting market cap criteria"""
        url = f"{self.base_url}/stock-screener"
        params = {
            "marketCapMoreThan": market_cap_min,
            "limit": limit,
            "apikey": self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching stock screener: {e}")
            return []

    def get_institutional_holders(self, symbol: str) -> List[Dict]:
        """Get institutional holders for a specific stock"""
        url = f"{self.base_url}/institutional-holder/{symbol}"
        params = {"apikey": self.api_key}

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching institutional holders for {symbol}: {e}")
            return []

    def calculate_ownership_metrics(
        self,
        symbol: str,
        company_name: str,
        market_cap: float
    ) -> Optional[Dict]:
        """Calculate institutional ownership metrics for a stock"""
        holders = self.get_institutional_holders(symbol)

        if not holders or len(holders) < 2:
            return None

        # Group by date to get quarterly snapshots
        quarters = {}
        for holder in holders:
            date = holder.get('dateReported', '')
            if not date:
                continue
            if date not in quarters:
                quarters[date] = []
            quarters[date].append(holder)

        # Need at least 2 quarters for comparison
        if len(quarters) < 2:
            return None

        # Get most recent 2 quarters
        sorted_quarters = sorted(quarters.keys(), reverse=True)
        current_q = sorted_quarters[0]
        previous_q = sorted_quarters[1]

        current_holders = quarters[current_q]
        previous_holders = quarters[previous_q]

        # Calculate aggregate metrics
        current_total_shares = sum(h.get('totalShares', 0) for h in current_holders)
        previous_total_shares = sum(h.get('totalShares', 0) for h in previous_holders)

        # Calculate changes
        shares_change = current_total_shares - previous_total_shares
        if previous_total_shares > 0:
            percent_change = (shares_change / previous_total_shares) * 100
        else:
            percent_change = 0

        # Count institutions
        current_count = len(current_holders)
        previous_count = len(previous_holders)
        institution_change = current_count - previous_count

        # Calculate dollar value (approximate)
        # Note: This is approximate as we don't have exact prices
        current_value = sum(h.get('totalInvested', 0) for h in current_holders)
        previous_value = sum(h.get('totalInvested', 0) for h in previous_holders)
        value_change = current_value - previous_value

        # Get top holders
        top_holders = sorted(
            current_holders,
            key=lambda x: x.get('totalShares', 0),
            reverse=True
        )[:10]

        top_holder_names = [
            {
                'name': h.get('holder', 'Unknown'),
                'shares': h.get('totalShares', 0),
                'change': h.get('change', 0)
            }
            for h in top_holders
        ]

        return {
            'symbol': symbol,
            'company_name': company_name,
            'market_cap': market_cap,
            'current_quarter': current_q,
            'previous_quarter': previous_q,
            'current_total_shares': current_total_shares,
            'previous_total_shares': previous_total_shares,
            'shares_change': shares_change,
            'percent_change': round(percent_change, 2),
            'current_institution_count': current_count,
            'previous_institution_count': previous_count,
            'institution_count_change': institution_change,
            'current_value': current_value,
            'previous_value': previous_value,
            'value_change': value_change,
            'top_holders': top_holder_names
        }

    def screen_stocks(
        self,
        min_market_cap: int = 1000000000,
        min_change_percent: float = 10.0,
        min_institutions: int = 10,
        sector: Optional[str] = None,
        top: int = 50,
        sort_by: str = 'ownership_change'
    ) -> List[Dict]:
        """Screen for stocks with significant institutional changes"""

        print(f"Fetching stocks with market cap >= ${min_market_cap:,}...")
        stocks = self.get_stock_screener(market_cap_min=min_market_cap, limit=500)

        if not stocks:
            print("No stocks found in screener")
            return []

        # Filter by sector if specified
        if sector:
            stocks = [s for s in stocks if s.get('sector', '').lower() == sector.lower()]
            print(f"Filtered to {len(stocks)} stocks in {sector} sector")

        print(f"Analyzing institutional ownership for {len(stocks)} stocks...")
        print("This may take a few minutes. Please wait...\n")

        results = []
        for i, stock in enumerate(stocks, 1):
            symbol = stock.get('symbol', '')
            company_name = stock.get('companyName', '')
            market_cap = stock.get('marketCap', 0)

            if i % 10 == 0:
                print(f"Progress: {i}/{len(stocks)} stocks analyzed...")

            # Rate limiting: max 5 requests per second
            time.sleep(0.2)

            metrics = self.calculate_ownership_metrics(symbol, company_name, market_cap)

            if metrics:
                # Apply filters
                if abs(metrics['percent_change']) >= min_change_percent:
                    if metrics['current_institution_count'] >= min_institutions:
                        results.append(metrics)

        print(f"\nFound {len(results)} stocks meeting criteria")

        # Sort results
        if sort_by == 'ownership_change':
            results.sort(key=lambda x: abs(x['percent_change']), reverse=True)
        elif sort_by == 'institution_count_change':
            results.sort(key=lambda x: abs(x['institution_count_change']), reverse=True)
        elif sort_by == 'dollar_value_change':
            results.sort(key=lambda x: abs(x['value_change']), reverse=True)

        return results[:top]

    def generate_report(self, results: List[Dict], output_file: str = None):
        """Generate markdown report from screening results"""

        if not results:
            print("No results to report")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Institutional Flow Analysis Report
**Generated:** {timestamp}
**Stocks Analyzed:** {len(results)}

## Summary

This report identifies stocks with significant institutional ownership changes based on 13F filings data.

### Key Findings

**Top Accumulators (Institutions Buying):**
"""

        # Top accumulators
        accumulators = [r for r in results if r['percent_change'] > 0][:10]
        if accumulators:
            report += "\n| Symbol | Company | Ownership Change | Institution Change | Top Holder |\n"
            report += "|--------|---------|-----------------|-------------------|------------|\n"
            for r in accumulators:
                top_holder = r['top_holders'][0]['name'] if r['top_holders'] else 'N/A'
                report += f"| {r['symbol']} | {r['company_name'][:30]} | **+{r['percent_change']}%** | +{r['institution_count_change']} | {top_holder[:30]} |\n"
        else:
            report += "\nNo significant accumulation detected.\n"

        report += "\n**Top Distributors (Institutions Selling):**\n"

        # Top distributors
        distributors = [r for r in results if r['percent_change'] < 0][:10]
        if distributors:
            report += "\n| Symbol | Company | Ownership Change | Institution Change | Previously Top Holder |\n"
            report += "|--------|---------|-----------------|-------------------|-----------------------|\n"
            for r in distributors:
                top_holder = r['top_holders'][0]['name'] if r['top_holders'] else 'N/A'
                report += f"| {r['symbol']} | {r['company_name'][:30]} | **{r['percent_change']}%** | {r['institution_count_change']} | {top_holder[:30]} |\n"
        else:
            report += "\nNo significant distribution detected.\n"

        report += "\n## Detailed Results\n\n"

        for r in results[:20]:  # Top 20 detailed
            direction = "Accumulation" if r['percent_change'] > 0 else "Distribution"
            report += f"""### {r['symbol']} - {r['company_name']}

**Signal:** {direction} ({r['percent_change']:+.2f}% institutional ownership change)

**Metrics:**
- Market Cap: ${r['market_cap']:,.0f}
- Current Quarter: {r['current_quarter']}
- Previous Quarter: {r['previous_quarter']}
- Institution Count Change: {r['institution_count_change']:+d} ({r['previous_institution_count']} → {r['current_institution_count']})
- Total Shares Change: {r['shares_change']:+,.0f}
- Estimated Value Change: ${r['value_change']:+,.0f}

**Top 5 Current Holders:**
"""
            for i, holder in enumerate(r['top_holders'][:5], 1):
                report += f"{i}. {holder['name']}: {holder['shares']:,} shares (Change: {holder['change']:+,})\n"

            report += "\n---\n\n"

        report += f"""
## Interpretation Guide

**Strong Accumulation (>15% increase):**
- Monitor for potential breakout
- Validate with fundamental analysis
- Consider initiating/adding to position

**Moderate Accumulation (7-15% increase):**
- Positive signal
- Combine with other analysis
- Watch for continuation

**Strong Distribution (>15% decrease):**
- Warning sign
- Re-evaluate thesis
- Consider trimming/exiting

**Moderate Distribution (7-15% decrease):**
- Early warning
- Monitor closely
- Tighten stop-loss

For detailed interpretation framework, see:
`institutional-flow-tracker/references/interpretation_framework.md`

---

**Data Source:** Financial Modeling Prep API (13F Filings)
**Note:** 13F data has ~45-day reporting lag. Use as confirming indicator, not real-time signal.
"""

        # Save to file
        if output_file:
            output_path = output_file if output_file.endswith('.md') else f"{output_file}.md"
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {output_path}")
        else:
            output_path = f"institutional_flow_screening_{datetime.now().strftime('%Y%m%d')}.md"
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {output_path}")

        return report


def main():
    parser = argparse.ArgumentParser(
        description='Track institutional ownership changes across stocks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Screen top 50 stocks by institutional change (>10%)
  python3 track_institutional_flow.py --top 50 --min-change-percent 10

  # Focus on Technology sector
  python3 track_institutional_flow.py --sector Technology --min-institutions 20

  # Custom screening with output
  python3 track_institutional_flow.py --min-market-cap 2000000000 --top 100 --output results.json
        """
    )

    parser.add_argument(
        '--api-key',
        type=str,
        default=os.getenv('FMP_API_KEY'),
        help='FMP API key (or set FMP_API_KEY environment variable)'
    )
    parser.add_argument(
        '--top',
        type=int,
        default=50,
        help='Number of top stocks to return (default: 50)'
    )
    parser.add_argument(
        '--min-change-percent',
        type=float,
        default=10.0,
        help='Minimum %% change in institutional ownership (default: 10.0)'
    )
    parser.add_argument(
        '--min-market-cap',
        type=int,
        default=1000000000,
        help='Minimum market cap in dollars (default: 1B)'
    )
    parser.add_argument(
        '--sector',
        type=str,
        help='Filter by specific sector (e.g., Technology, Healthcare)'
    )
    parser.add_argument(
        '--min-institutions',
        type=int,
        default=10,
        help='Minimum number of institutional holders (default: 10)'
    )
    parser.add_argument(
        '--sort-by',
        type=str,
        choices=['ownership_change', 'institution_count_change', 'dollar_value_change'],
        default='ownership_change',
        help='Sort results by metric (default: ownership_change)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for JSON results'
    )

    args = parser.parse_args()

    # Validate API key
    if not args.api_key:
        print("Error: FMP API key required")
        print("Set FMP_API_KEY environment variable or pass --api-key argument")
        print("Get free API key at: https://financialmodelingprep.com/developer/docs")
        sys.exit(1)

    # Initialize tracker
    tracker = InstitutionalFlowTracker(args.api_key)

    # Run screening
    results = tracker.screen_stocks(
        min_market_cap=args.min_market_cap,
        min_change_percent=args.min_change_percent,
        min_institutions=args.min_institutions,
        sector=args.sector,
        top=args.top,
        sort_by=args.sort_by
    )

    # Save JSON results if requested
    if args.output:
        json_output = args.output if args.output.endswith('.json') else f"{args.output}.json"
        with open(json_output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"JSON results saved to: {json_output}")

    # Generate markdown report
    tracker.generate_report(results)

    # Print summary
    if results:
        print("\n" + "="*80)
        print("TOP 10 INSTITUTIONAL FLOW CHANGES")
        print("="*80)
        print(f"{'Symbol':<8} {'Company':<30} {'Change':>10} {'Institutions':>12}")
        print("-"*80)
        for r in results[:10]:
            print(f"{r['symbol']:<8} {r['company_name'][:30]:<30} {r['percent_change']:>9.2f}% {r['institution_count_change']:>+11d}")


if __name__ == '__main__':
    main()
