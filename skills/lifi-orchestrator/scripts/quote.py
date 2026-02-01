#!/usr/bin/env python3
"""Get a bridge/swap quote from LI.FI"""

import argparse
import json
import requests
import sys

API_BASE = "https://li.quest/v1"

# Common token shortcuts
TOKEN_SHORTCUTS = {
    "ETH": "0x0000000000000000000000000000000000000000",
    "MATIC": "0x0000000000000000000000000000000000000000",
    "BNB": "0x0000000000000000000000000000000000000000",
    "AVAX": "0x0000000000000000000000000000000000000000",
    "USDC": {
        1: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        137: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        42161: "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        10: "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
        8453: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    },
    "USDT": {
        1: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        137: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        42161: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    }
}

CHAIN_NAMES = {
    1: "Ethereum",
    137: "Polygon", 
    42161: "Arbitrum",
    10: "Optimism",
    8453: "Base",
    56: "BSC",
    43114: "Avalanche",
}


def resolve_token(token: str, chain_id: int) -> str:
    """Resolve token shortcut to address"""
    token = token.upper()
    if token.startswith("0X"):
        return token
    if token in TOKEN_SHORTCUTS:
        val = TOKEN_SHORTCUTS[token]
        if isinstance(val, dict):
            return val.get(chain_id, val.get(1))
        return val
    return token


def get_quote(from_chain: int, to_chain: int, from_token: str, to_token: str, 
              amount: float, from_address: str = None, slippage: float = 0.005):
    """Get a bridge quote"""
    
    from_token_addr = resolve_token(from_token, from_chain)
    to_token_addr = resolve_token(to_token, to_chain)
    
    # Get token decimals (assume 18 for native, fetch for others)
    if from_token_addr == "0x0000000000000000000000000000000000000000":
        decimals = 18
    else:
        # Fetch token info
        try:
            r = requests.get(f"{API_BASE}/token", params={
                "chain": from_chain,
                "token": from_token_addr
            })
            decimals = r.json().get("decimals", 18)
        except:
            decimals = 18
    
    from_amount = int(amount * (10 ** decimals))
    
    params = {
        "fromChain": from_chain,
        "toChain": to_chain,
        "fromToken": from_token_addr,
        "toToken": to_token_addr,
        "fromAmount": str(from_amount),
        "slippage": slippage,
    }
    
    # fromAddress is required - use a default if not provided
    params["fromAddress"] = from_address or "0x552008c0f6870c2f77e5cC1d2eb9bdff03e30Ea0"
    
    r = requests.get(f"{API_BASE}/quote", params=params)
    
    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        print(r.text)
        sys.exit(1)
    
    return r.json()


def format_quote(quote: dict, amount: float) -> str:
    """Format quote for display"""
    estimate = quote.get("estimate", {})
    action = quote.get("action", {})
    
    from_chain = CHAIN_NAMES.get(action.get("fromChainId"), action.get("fromChainId"))
    to_chain = CHAIN_NAMES.get(action.get("toChainId"), action.get("toChainId"))
    
    # Token info is in action, not estimate
    from_token = action.get("fromToken", {})
    to_token = action.get("toToken", {})
    
    from_amount = int(estimate.get("fromAmount", 0)) / (10 ** from_token.get("decimals", 18))
    to_amount = int(estimate.get("toAmount", 0)) / (10 ** to_token.get("decimals", 18))
    to_amount_min = int(estimate.get("toAmountMin", 0)) / (10 ** to_token.get("decimals", 18))
    
    gas_usd = float(estimate.get("gasCosts", [{}])[0].get("amountUSD", 0)) if estimate.get("gasCosts") else 0
    fee_usd = sum(float(f.get("amountUSD", 0)) for f in estimate.get("feeCosts", []))
    
    execution_time = estimate.get("executionDuration", 0)
    
    tool = quote.get("tool", "unknown")
    
    lines = [
        f"🌉 **LI.FI Quote**",
        f"",
        f"**Route**: {from_chain} → {to_chain}",
        f"**Bridge**: {tool}",
        f"",
        f"**Send**: {from_amount:.6f} {from_token.get('symbol', '?')}",
        f"**Receive**: ~{to_amount:.6f} {to_token.get('symbol', '?')}",
        f"**Minimum**: {to_amount_min:.6f} {to_token.get('symbol', '?')}",
        f"",
        f"**Gas**: ${gas_usd:.2f}",
        f"**Fees**: ${fee_usd:.2f}",
        f"**Time**: ~{execution_time // 60}m {execution_time % 60}s",
    ]
    
    if estimate.get("fromAmountUSD") and estimate.get("toAmountUSD"):
        from_usd = float(estimate["fromAmountUSD"])
        to_usd = float(estimate["toAmountUSD"])
        slippage_pct = ((from_usd - to_usd) / from_usd) * 100 if from_usd > 0 else 0
        lines.append(f"**Value loss**: {slippage_pct:.2f}%")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Get LI.FI bridge quote")
    parser.add_argument("--from-chain", type=int, required=True, help="Source chain ID")
    parser.add_argument("--to-chain", type=int, required=True, help="Destination chain ID")
    parser.add_argument("--from-token", required=True, help="Source token (symbol or address)")
    parser.add_argument("--to-token", required=True, help="Destination token (symbol or address)")
    parser.add_argument("--amount", type=float, required=True, help="Amount to bridge")
    parser.add_argument("--from-address", help="Sender address (for accurate gas)")
    parser.add_argument("--slippage", type=float, default=0.005, help="Slippage tolerance (default 0.5%%)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    quote = get_quote(
        from_chain=args.from_chain,
        to_chain=args.to_chain,
        from_token=args.from_token,
        to_token=args.to_token,
        amount=args.amount,
        from_address=args.from_address,
        slippage=args.slippage
    )
    
    if args.json:
        print(json.dumps(quote, indent=2))
    else:
        print(format_quote(quote, args.amount))
        print(f"\nQuote ID: {quote.get('id', 'N/A')}")


if __name__ == "__main__":
    main()
