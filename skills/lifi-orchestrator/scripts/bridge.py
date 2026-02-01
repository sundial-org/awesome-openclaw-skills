#!/usr/bin/env python3
"""Execute a cross-chain bridge via LI.FI"""

import argparse
import json
import os
import sys
import requests

try:
    from web3 import Web3
    from eth_account import Account
except ImportError:
    print("Error: web3 and eth-account required. Install with: pip install web3 eth-account")
    sys.exit(1)

API_BASE = "https://li.quest/v1"

# Common RPC endpoints
RPCS = {
    1: "https://ethereum-rpc.publicnode.com",
    137: "https://polygon-rpc.com",
    42161: "https://arb1.arbitrum.io/rpc",
    10: "https://mainnet.optimism.io",
    8453: "https://mainnet.base.org",
    56: "https://bsc-rpc.publicnode.com",
    43114: "https://api.avax.network/ext/bc/C/rpc",
}

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
}


def resolve_token(token: str, chain_id: int) -> str:
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
              amount: float, from_address: str, slippage: float = 0.005):
    """Get bridge quote with transaction data"""
    
    from_token_addr = resolve_token(from_token, from_chain)
    to_token_addr = resolve_token(to_token, to_chain)
    
    # Get decimals
    if from_token_addr == "0x0000000000000000000000000000000000000000":
        decimals = 18
    else:
        try:
            r = requests.get(f"{API_BASE}/token", params={"chain": from_chain, "token": from_token_addr})
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
        "fromAddress": from_address,
        "slippage": slippage,
    }
    
    r = requests.get(f"{API_BASE}/quote", params=params)
    if r.status_code != 200:
        print(f"Quote error: {r.text}")
        sys.exit(1)
    
    return r.json()


def check_and_approve(w3: Web3, account, token_address: str, spender: str, amount: int):
    """Check allowance and approve if needed"""
    if token_address == "0x0000000000000000000000000000000000000000":
        return None  # Native token, no approval needed
    
    # ERC20 ABI (just allowance and approve)
    erc20_abi = [
        {"constant": True, "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}],
         "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
         "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
    ]
    
    token = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)
    allowance = token.functions.allowance(account.address, Web3.to_checksum_address(spender)).call()
    
    if allowance >= amount:
        print(f"✅ Already approved")
        return None
    
    print(f"🔐 Approving token spend...")
    max_uint = 2**256 - 1
    tx = token.functions.approve(Web3.to_checksum_address(spender), max_uint).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
    })
    
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Approval tx: {tx_hash.hex()}")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt['status'] != 1:
        print("❌ Approval failed")
        sys.exit(1)
    
    print(f"✅ Approved")
    return tx_hash.hex()


def execute_bridge(quote: dict, private_key: str, rpc_url: str = None):
    """Execute the bridge transaction"""
    
    action = quote.get("action", {})
    from_chain = action.get("fromChainId")
    
    if not rpc_url:
        rpc_url = RPCS.get(from_chain)
        if not rpc_url:
            print(f"No RPC for chain {from_chain}. Provide --rpc")
            sys.exit(1)
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"❌ Cannot connect to RPC: {rpc_url}")
        sys.exit(1)
    
    account = Account.from_key(private_key)
    print(f"🔑 Wallet: {account.address}")
    
    # Check and approve if needed
    from_token = action.get("fromToken", {}).get("address", "0x0000000000000000000000000000000000000000")
    from_amount = int(quote.get("estimate", {}).get("fromAmount", 0))
    
    tx_request = quote.get("transactionRequest", {})
    spender = tx_request.get("to")
    
    if from_token != "0x0000000000000000000000000000000000000000":
        check_and_approve(w3, account, from_token, spender, from_amount)
    
    # Build and send bridge transaction
    print(f"🌉 Executing bridge...")
    
    tx = {
        'from': account.address,
        'to': Web3.to_checksum_address(tx_request['to']),
        'data': tx_request['data'],
        'value': int(tx_request.get('value', 0), 16) if isinstance(tx_request.get('value'), str) else int(tx_request.get('value', 0)),
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': int(tx_request.get('gasLimit', 500000), 16) if isinstance(tx_request.get('gasLimit'), str) else int(tx_request.get('gasLimit', 500000)),
        'gasPrice': int(tx_request.get('gasPrice', w3.eth.gas_price), 16) if isinstance(tx_request.get('gasPrice'), str) else w3.eth.gas_price,
        'chainId': from_chain,
    }
    
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    print(f"📤 Tx sent: {tx_hash.hex()}")
    print(f"⏳ Waiting for confirmation...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    
    if receipt['status'] == 1:
        print(f"✅ Bridge initiated!")
        print(f"🔗 Track at: https://scan.li.fi/tx/{tx_hash.hex()}")
    else:
        print(f"❌ Transaction failed")
        sys.exit(1)
    
    return tx_hash.hex()


def main():
    parser = argparse.ArgumentParser(description="Execute LI.FI bridge")
    parser.add_argument("--from-chain", type=int, required=True)
    parser.add_argument("--to-chain", type=int, required=True)
    parser.add_argument("--from-token", required=True)
    parser.add_argument("--to-token", required=True)
    parser.add_argument("--amount", type=float, required=True)
    parser.add_argument("--private-key", help="Private key (or set PRIVATE_KEY env)")
    parser.add_argument("--rpc", help="Custom RPC URL")
    parser.add_argument("--slippage", type=float, default=0.005)
    parser.add_argument("--dry-run", action="store_true", help="Get quote only, don't execute")
    
    args = parser.parse_args()
    
    private_key = args.private_key or os.environ.get("PRIVATE_KEY")
    if not private_key and not args.dry_run:
        print("Error: --private-key or PRIVATE_KEY env required")
        sys.exit(1)
    
    # Get wallet address for quote
    if private_key:
        account = Account.from_key(private_key)
        from_address = account.address
    else:
        from_address = "0x0000000000000000000000000000000000000000"
    
    print(f"📊 Getting quote...")
    quote = get_quote(
        from_chain=args.from_chain,
        to_chain=args.to_chain,
        from_token=args.from_token,
        to_token=args.to_token,
        amount=args.amount,
        from_address=from_address,
        slippage=args.slippage
    )
    
    estimate = quote.get("estimate", {})
    from_token = estimate.get("fromToken", {})
    to_token = estimate.get("toToken", {})
    to_amount = int(estimate.get("toAmount", 0)) / (10 ** to_token.get("decimals", 18))
    
    print(f"💰 {args.amount} {from_token.get('symbol')} → ~{to_amount:.6f} {to_token.get('symbol')}")
    print(f"🛤️  Via: {quote.get('tool')}")
    
    if args.dry_run:
        print("\n[Dry run - not executing]")
        print(json.dumps(quote, indent=2))
        return
    
    tx_hash = execute_bridge(quote, private_key, args.rpc)
    print(f"\n✅ Bridge transaction: {tx_hash}")


if __name__ == "__main__":
    main()
