#!/usr/bin/env python3
"""
AI Trading Skill - Claude Code Entry Point

This is the main entry point for using the AI Trading skill with Claude Code.
Provides a simple interface for comprehensive cryptocurrency trading analysis.

Usage:
    python -m cryptocurrency_trader_skill [OPTIONS]
    python skill.py analyze BTC/USDT --balance 10000
    python skill.py scan --balance 10000 --top 5
"""

import sys
import os
import argparse
import json
from typing import Dict, Optional

# Add scripts directory to path
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, SCRIPT_DIR)


def get_agent_class():
    """Import and return the appropriate TradingAgent class"""
    try:
        # Try V2 (enhanced 12-stage) first
        from trading_agent_v2 import TradingAgentV2
        return TradingAgentV2, 'v2 (enhanced 12-stage)'
    except ImportError:
        try:
            # Fall back to refactored version
            from trading_agent_refactored import TradingAgent
            return TradingAgent, 'refactored'
        except ImportError:
            try:
                # Fall back to enhanced version
                from trading_agent_enhanced import EnhancedTradingAgent as TradingAgent
                return TradingAgent, 'enhanced'
            except ImportError:
                # Fall back to original
                from trading_agent import TradingAgent
                return TradingAgent, 'original'


def analyze_symbol(symbol: str, balance: float, timeframes: Optional[list] = None) -> Dict:
    """
    Analyze a specific cryptocurrency trading pair

    Args:
        symbol: Trading pair (e.g., 'BTC/USDT')
        balance: Account balance for position sizing
        timeframes: List of timeframes to analyze (default: ['15m', '1h', '4h'])

    Returns:
        Dictionary with comprehensive analysis
    """
    timeframes = timeframes or ['15m', '1h', '4h']

    print(f"\n{'='*80}")
    print(f"AI TRADING ANALYSIS - {symbol}")
    print(f"{'='*80}\n")

    try:
        # Get appropriate agent class
        TradingAgent, version = get_agent_class()
        print(f"Using {version} trading agent")

        # Initialize agent
        agent = TradingAgent(balance=balance)

        # Run comprehensive analysis
        print(f"\nAnalyzing {symbol} across {len(timeframes)} timeframes...")
        analysis = agent.comprehensive_analysis(symbol=symbol, timeframes=timeframes)

        # Display results
        if hasattr(agent, 'display_analysis'):
            agent.display_analysis(analysis)
        else:
            # Basic display if display_analysis not available
            print("\n" + "="*80)
            print("ANALYSIS RESULTS")
            print("="*80)
            print(json.dumps(analysis, indent=2, default=str))

        return analysis

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}


def scan_market(balance: float, top_n: int = 5, categories: Optional[list] = None) -> list:
    """
    Scan market for best trading opportunities

    Args:
        balance: Account balance
        top_n: Number of top opportunities to return
        categories: Market categories to scan (None = all)

    Returns:
        List of best trading opportunities
    """
    print(f"\n{'='*80}")
    print(f"MARKET SCANNER - Finding Top {top_n} Opportunities")
    print(f"{'='*80}\n")

    try:
        # Get appropriate agent class
        TradingAgent, version = get_agent_class()
        print(f"Using {version} trading agent")

        # Initialize agent
        agent = TradingAgent(balance=balance)

        # Check if agent has market scanner
        if not hasattr(agent, 'market_scanner'):
            print("\n⚠️  Market scanner not available in this agent version")
            print("Falling back to individual symbol analysis...")
            # Analyze a few popular pairs
            symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
            opportunities = []
            for symbol in symbols[:top_n]:
                try:
                    analysis = agent.comprehensive_analysis(symbol)
                    if analysis.get('execution_ready'):
                        opportunities.append(analysis)
                except Exception as e:
                    print(f"Error analyzing {symbol}: {e}")
            return opportunities

        # Run market scan
        print(f"Scanning market categories: {categories or 'All'}")
        opportunities = agent.market_scanner.scan_market(
            categories=categories,
            top_n=top_n
        )

        # Display results
        if opportunities:
            print(f"\n✅ Found {len(opportunities)} opportunities:")
            for i, opp in enumerate(opportunities, 1):
                rec = opp.get('final_recommendation', {})
                print(f"\n{i}. {opp.get('symbol', 'Unknown')}")
                print(f"   Action: {rec.get('action', 'N/A')}")
                print(f"   Confidence: {rec.get('confidence', 0)}%")
                print(f"   EV Score: {opp.get('ev_score', 'N/A')}")
        else:
            print("\n⚠️  No execution-ready opportunities found")

        return opportunities

    except Exception as e:
        print(f"\n❌ Error during market scan: {e}")
        import traceback
        traceback.print_exc()
        return []


def interactive_mode(balance: float):
    """
    Interactive mode for exploring trading analysis

    Args:
        balance: Account balance
    """
    print(f"\n{'='*80}")
    print("AI TRADING SKILL - INTERACTIVE MODE")
    print(f"{'='*80}\n")
    print(f"Balance: ${balance:,.2f}")
    print("\nCommands:")
    print("  analyze <SYMBOL>  - Analyze a specific trading pair")
    print("  scan              - Scan market for opportunities")
    print("  help              - Show this help")
    print("  quit              - Exit interactive mode")

    while True:
        try:
            command = input("\n> ").strip()

            if not command:
                continue

            parts = command.split()
            cmd = parts[0].lower()

            if cmd in ['quit', 'exit', 'q']:
                print("\nExiting interactive mode...")
                break

            elif cmd == 'help':
                print("\nCommands:")
                print("  analyze <SYMBOL>  - Analyze a specific trading pair")
                print("  scan              - Scan market for opportunities")
                print("  help              - Show this help")
                print("  quit              - Exit")

            elif cmd == 'analyze':
                if len(parts) < 2:
                    print("❌ Please specify a symbol (e.g., analyze BTC/USDT)")
                    continue
                symbol = parts[1]
                analyze_symbol(symbol, balance)

            elif cmd == 'scan':
                top_n = 5
                if len(parts) > 1 and parts[1].isdigit():
                    top_n = int(parts[1])
                scan_market(balance, top_n)

            else:
                print(f"❌ Unknown command: {cmd}")
                print("Type 'help' for available commands")

        except KeyboardInterrupt:
            print("\n\nExiting interactive mode...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point for the AI Trading skill"""
    parser = argparse.ArgumentParser(
        description='AI Trading Skill - Comprehensive cryptocurrency trading analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a specific trading pair
  python skill.py analyze BTC/USDT --balance 10000

  # Scan market for top 5 opportunities
  python skill.py scan --balance 10000 --top 5

  # Interactive mode
  python skill.py interactive --balance 10000

  # Use environment variable for balance
  export TRADING_BALANCE=10000
  python skill.py analyze ETH/USDT
        """
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a specific trading pair')
    analyze_parser.add_argument('symbol', type=str, help='Trading pair (e.g., BTC/USDT)')
    analyze_parser.add_argument('--balance', type=float, help='Account balance')
    analyze_parser.add_argument('--timeframes', nargs='+', default=['15m', '1h', '4h'],
                               help='Timeframes to analyze (default: 15m 1h 4h)')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan market for opportunities')
    scan_parser.add_argument('--balance', type=float, help='Account balance')
    scan_parser.add_argument('--top', type=int, default=5,
                            help='Number of top opportunities (default: 5)')
    scan_parser.add_argument('--categories', nargs='+',
                            help='Market categories to scan')

    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')
    interactive_parser.add_argument('--balance', type=float, help='Account balance')

    args = parser.parse_args()

    # Get balance from args or environment
    balance = args.balance if hasattr(args, 'balance') and args.balance else None
    if balance is None:
        balance = float(os.environ.get('TRADING_BALANCE', 10000))
        print(f"Using balance from environment: ${balance:,.2f}")

    # Execute command
    if args.command == 'analyze':
        analyze_symbol(args.symbol, balance, args.timeframes)

    elif args.command == 'scan':
        scan_market(balance, args.top, args.categories)

    elif args.command == 'interactive':
        interactive_mode(balance)

    else:
        # No command specified - show help
        parser.print_help()
        print("\n💡 Tip: Start with 'python skill.py analyze BTC/USDT --balance 10000'")


if __name__ == '__main__':
    main()
