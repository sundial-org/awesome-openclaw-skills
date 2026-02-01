#!/usr/bin/env python3
"""
Research Module - Deep research using Gemini CLI.
Crawls articles, finds correlations, researches companies.
Outputs research_report.md for later analysis.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from utils import ensure_venv

from fetch_news import PortfolioError, get_market_news, get_portfolio_news

SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"
OUTPUT_DIR = SCRIPT_DIR.parent / "research"


ensure_venv()


def format_market_data(market_data: dict) -> str:
    """Format market data for research prompt."""
    lines = ["## Market Data\n"]
    
    for region, data in market_data.get('markets', {}).items():
        lines.append(f"### {data['name']}")
        for symbol, idx in data.get('indices', {}).items():
            if 'data' in idx and idx['data']:
                price = idx['data'].get('price', 'N/A')
                change_pct = idx['data'].get('change_percent', 0)
                emoji = '📈' if change_pct >= 0 else '📉'
                lines.append(f"- {idx['name']}: {price} ({change_pct:+.2f}%) {emoji}")
        lines.append("")
    
    return '\n'.join(lines)


def format_headlines(headlines: list) -> str:
    """Format headlines for research prompt."""
    lines = ["## Current Headlines\n"]
    
    for article in headlines[:20]:
        source = article.get('source', 'Unknown')
        title = article.get('title', '')
        link = article.get('link', '')
        lines.append(f"- [{source}] {title}")
        if link:
            lines.append(f"  URL: {link}")
    
    return '\n'.join(lines)


def format_portfolio_news(portfolio_data: dict) -> str:
    """Format portfolio news for research prompt."""
    lines = ["## Portfolio Analysis\n"]
    
    for symbol, data in portfolio_data.get('stocks', {}).items():
        quote = data.get('quote', {})
        price = quote.get('price', 'N/A')
        change_pct = quote.get('change_percent', 0)
        
        lines.append(f"### {symbol} (${price}, {change_pct:+.2f}%)")
        
        for article in data.get('articles', [])[:5]:
            title = article.get('title', '')
            link = article.get('link', '')
            lines.append(f"- {title}")
            if link:
                lines.append(f"  URL: {link}")
        lines.append("")
    
    return '\n'.join(lines)


def gemini_available() -> bool:
    return shutil.which('gemini') is not None


def research_with_gemini(content: str, focus_areas: list = None) -> str:
    """Perform deep research using Gemini CLI.
    
    Args:
        content: Combined market/headlines/portfolio content
        focus_areas: Optional list of focus areas (e.g., ['earnings', 'macro', 'sectors'])
    
    Returns:
        Research report text
    """
    focus_prompt = ""
    if focus_areas:
        focus_prompt = f"""
Focus areas for the research:
{', '.join(f'- {area}' for area in focus_areas)}

Go deep on each area.
"""
    
    prompt = f"""You are an experienced investment research analyst.

Your task is to deliver deep research on current market developments.

{focus_prompt}
Please analyze the following market data:

{content}

## Analysis Requirements:

1. **Macro Trends**: What is driving the market today? Which economic data/decisions matter?

2. **Sector Analysis**: Which sectors are performing best/worst? Why?

3. **Company News**: Relevant earnings, M&A, product launches?

4. **Risks**: What downside risks should be noted?

5. **Opportunities**: Which positive developments offer opportunities?

6. **Correlations**: Are there links between different news items/asset classes?

7. **Trade Ideas**: Concrete setups based on the analysis (not financial advice!)

8. **Sources**: Original links for further research

Be analytical, objective, and opinionated where appropriate.
Deliver a substantial report (500-800 words).
"""

    try:
        result = subprocess.run(
            ['gemini', prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"⚠️ Gemini research error: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return "⚠️ Gemini research timeout"
    except FileNotFoundError:
        return "⚠️ Gemini CLI not found. Install: brew install gemini-cli"


def format_raw_data_report(market_data: dict, portfolio_data: dict) -> str:
    parts = []
    if market_data:
        parts.append(format_market_data(market_data))
        if market_data.get('headlines'):
            parts.append(format_headlines(market_data['headlines']))
    if portfolio_data and 'error' not in portfolio_data:
        parts.append(format_portfolio_news(portfolio_data))
    return '\n\n'.join(parts)


def generate_research_content(market_data: dict, portfolio_data: dict, focus_areas: list = None) -> dict:
    raw_report = format_raw_data_report(market_data, portfolio_data)
    if not raw_report.strip():
        return {
            'report': '',
            'source': 'none'
        }
    if gemini_available():
        return {
            'report': research_with_gemini(raw_report, focus_areas),
            'source': 'gemini'
        }
    return {
        'report': raw_report,
        'source': 'raw'
    }


def generate_research_report(args):
    """Generate full research report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    config_path = CONFIG_DIR / "config.json"
    if not config_path.exists():
        print("⚠️ No config found. Run 'finance-news wizard' first.", file=sys.stderr)
        sys.exit(1)
    
    # Fetch fresh data
    print("📡 Fetching market data...", file=sys.stderr)
    
    # Get market overview
    market_data = get_market_news(
        args.limit if hasattr(args, 'limit') else 5,
        regions=args.regions.split(',') if hasattr(args, 'regions') else ["us", "europe"],
        max_indices_per_region=2
    )
    
    # Get portfolio news
    try:
        portfolio_data = get_portfolio_news(
            args.limit if hasattr(args, 'limit') else 5,
            args.max_stocks if hasattr(args, 'max_stocks') else 10
        )
    except PortfolioError as exc:
        print(f"⚠️ Skipping portfolio: {exc}", file=sys.stderr)
        portfolio_data = None
    
    # Build report
    focus_areas = None
    if hasattr(args, 'focus') and args.focus:
        focus_areas = args.focus.split(',')

    research_result = generate_research_content(market_data, portfolio_data, focus_areas)
    research_report = research_result['report']
    source = research_result['source']

    if not research_report.strip():
        print("⚠️ No data available for research", file=sys.stderr)
        return

    if source == 'gemini':
        print("🔬 Running deep research with Gemini...", file=sys.stderr)
    else:
        print("🧾 Gemini not available; using raw data report", file=sys.stderr)
    
    # Add metadata header
    timestamp = datetime.now().isoformat()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    full_report = f"""# Market Research Report
**Generiert:** {date_str}
**Quelle:** Finance News Skill

---

{research_report}

---

*This report was generated automatically. Not financial advice.*
"""
    
    # Save to file
    output_file = OUTPUT_DIR / f"research_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, 'w') as f:
        f.write(full_report)
    
    print(f"✅ Research report saved to: {output_file}", file=sys.stderr)
    
    # Also output to stdout
    if args.json:
        print(json.dumps({
            'report': research_report,
            'saved_to': str(output_file),
            'timestamp': timestamp
        }))
    else:
        print("\n" + "="*60)
        print("RESEARCH REPORT")
        print("="*60)
        print(research_report)


def main():
    parser = argparse.ArgumentParser(description='Deep Market Research')
    parser.add_argument('--limit', type=int, default=5, help='Max headlines per source')
    parser.add_argument('--regions', default='us,europe', help='Comma-separated regions')
    parser.add_argument('--max-stocks', type=int, default=10, help='Max portfolio stocks')
    parser.add_argument('--focus', help='Focus areas (comma-separated)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    generate_research_report(args)


if __name__ == '__main__':
    main()
