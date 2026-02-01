#!/usr/bin/env python3
"""Check LI.FI transaction status"""

import argparse
import json
import sys
import time
import requests

API_BASE = "https://li.quest/v1"


def get_status(tx_hash: str, from_chain: int = None, to_chain: int = None):
    """Get transaction status"""
    params = {"txHash": tx_hash}
    if from_chain:
        params["fromChain"] = from_chain
    if to_chain:
        params["toChain"] = to_chain
    
    r = requests.get(f"{API_BASE}/status", params=params)
    
    if r.status_code != 200:
        return {"status": "UNKNOWN", "error": r.text}
    
    return r.json()


def format_status(status: dict) -> str:
    """Format status for display"""
    s = status.get("status", "UNKNOWN")
    
    status_emoji = {
        "NOT_FOUND": "❓",
        "INVALID": "❌",
        "PENDING": "⏳",
        "DONE": "✅",
        "FAILED": "❌",
    }
    
    emoji = status_emoji.get(s, "❓")
    
    lines = [f"{emoji} **Status**: {s}"]
    
    if status.get("sending"):
        sending = status["sending"]
        lines.append(f"📤 **Sending**: {sending.get('amount')} {sending.get('token', {}).get('symbol')}")
        lines.append(f"   Chain: {sending.get('chainId')}")
        lines.append(f"   Tx: {sending.get('txHash')}")
    
    if status.get("receiving"):
        receiving = status["receiving"]
        lines.append(f"📥 **Receiving**: {receiving.get('amount')} {receiving.get('token', {}).get('symbol')}")
        lines.append(f"   Chain: {receiving.get('chainId')}")
        if receiving.get("txHash"):
            lines.append(f"   Tx: {receiving.get('txHash')}")
    
    if status.get("substatus"):
        lines.append(f"ℹ️  Substatus: {status['substatus']}")
    
    if status.get("substatusMessage"):
        lines.append(f"💬 {status['substatusMessage']}")
    
    if status.get("tool"):
        lines.append(f"🛠️  Bridge: {status['tool']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check LI.FI transaction status")
    parser.add_argument("tx_hash", help="Transaction hash to check")
    parser.add_argument("--from-chain", type=int, help="Source chain ID (optional)")
    parser.add_argument("--to-chain", type=int, help="Destination chain ID (optional)")
    parser.add_argument("--watch", action="store_true", help="Watch until complete")
    parser.add_argument("--interval", type=int, default=30, help="Poll interval in seconds")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    while True:
        status = get_status(args.tx_hash, args.from_chain, args.to_chain)
        
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(format_status(status))
            print(f"\n🔗 https://scan.li.fi/tx/{args.tx_hash}")
        
        s = status.get("status", "UNKNOWN")
        
        if not args.watch or s in ["DONE", "FAILED", "INVALID"]:
            break
        
        print(f"\n⏳ Checking again in {args.interval}s...\n")
        time.sleep(args.interval)
    
    # Exit code based on status
    if status.get("status") == "DONE":
        sys.exit(0)
    elif status.get("status") == "FAILED":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
