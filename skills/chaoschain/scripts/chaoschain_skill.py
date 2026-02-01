#!/usr/bin/env python3
"""
ChaosChain OpenClaw Skill - Trust & Reputation Verification

This script provides READ-ONLY access to ERC-8004 registries for verifying
agent identity and reputation. No protocol execution, no payments, no Gateway.

Commands:
- verify <agent_id_or_address> - Check agent registration status
- reputation <agent_id_or_address> - View detailed reputation scores
- whoami - Check if your wallet has an on-chain identity
- register - (OPTIONAL) Register on ERC-8004 (on-chain action)

Environment Variables:
- CHAOSCHAIN_NETWORK: "mainnet" or "sepolia" (default: mainnet)
- CHAOSCHAIN_ADDRESS: Your wallet address (for whoami, read-only)
- CHAOSCHAIN_PRIVATE_KEY: Your private key (ONLY for register command)
- CHAOSCHAIN_RPC_URL: Custom RPC URL (optional)
"""

import os
import sys
import json
from typing import Optional, Dict, Any, Tuple

# Contract addresses
CONTRACTS = {
    "mainnet": {
        "identity_registry": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
        "reputation_registry": "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63",
        "rpc_url": "https://eth.llamarpc.com",
        "chain_id": 1,
        "explorer": "https://etherscan.io"
    },
    "sepolia": {
        "identity_registry": "0x8004A818BFB912233c491871b3d84c89A494BD9e",
        "reputation_registry": "0x8004B663056A597Dffe9eCcC1965A193B7388713",
        "rpc_url": "https://ethereum-sepolia-rpc.publicnode.com",
        "chain_id": 11155111,
        "explorer": "https://sepolia.etherscan.io"
    }
}

# Minimal ABIs for read operations
IDENTITY_ABI = [
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "ownerOf", "outputs": [{"name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "tokenURI", "outputs": [{"name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "agentURI", "type": "string"}], "name": "register", "outputs": [{"name": "agentId", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
]

REPUTATION_ABI = [
    # Feb 2026 spec: returns (count, value, valueDecimals) instead of (count, averageScore)
    {"inputs": [{"name": "agentId", "type": "uint256"}, {"name": "clientAddresses", "type": "address[]"}, {"name": "tag1", "type": "string"}, {"name": "tag2", "type": "string"}], "name": "getSummary", "outputs": [{"name": "count", "type": "uint64"}, {"name": "value", "type": "int128"}, {"name": "valueDecimals", "type": "uint8"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "agentId", "type": "uint256"}], "name": "getClients", "outputs": [{"name": "", "type": "address[]"}], "stateMutability": "view", "type": "function"},
]


def get_network_config(command: str = "read") -> Dict[str, Any]:
    """
    Get network configuration from environment.
    
    Network defaults:
    - READ operations (verify, reputation, whoami): Mainnet
    - WRITE operations (register): Sepolia (safety default)
    
    Users can override with CHAOSCHAIN_NETWORK or --network flag.
    """
    env_network = os.environ.get("CHAOSCHAIN_NETWORK", "").lower()
    
    if env_network and env_network in CONTRACTS:
        network = env_network
    elif command == "register":
        # Safety default: registration goes to Sepolia to avoid accidents
        network = "sepolia"
    else:
        # Read operations default to Mainnet (production data)
        network = "mainnet"
    
    config = CONTRACTS[network].copy()
    
    # Allow custom RPC URL override
    custom_rpc = os.environ.get("CHAOSCHAIN_RPC_URL")
    if custom_rpc:
        config["rpc_url"] = custom_rpc
    
    config["network"] = network
    return config


def get_web3(command: str = "read", network_override: Optional[str] = None):
    """
    Initialize Web3 connection.
    
    Args:
        command: "read" or "register" - affects default network
        network_override: Explicit network from --network flag
    """
    try:
        from web3 import Web3
    except ImportError:
        print("❌ Error: web3 package not installed")
        print("   Run: pip install web3")
        sys.exit(1)
    
    # Handle explicit --network flag
    if network_override:
        os.environ["CHAOSCHAIN_NETWORK"] = network_override
    
    config = get_network_config(command)
    w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
    
    if not w3.is_connected():
        print(f"❌ Error: Cannot connect to {config['network']} RPC")
        sys.exit(1)
    
    return w3, config


def resolve_agent_id(w3, config: Dict, identifier: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Resolve an identifier to an agent ID.
    Returns (agent_id, owner_address) or (None, None) if not found.
    """
    identity = w3.eth.contract(
        address=w3.to_checksum_address(config["identity_registry"]),
        abi=IDENTITY_ABI
    )
    
    # Check if it's a number (agent ID)
    if identifier.isdigit():
        agent_id = int(identifier)
        try:
            owner = identity.functions.ownerOf(agent_id).call()
            return agent_id, owner
        except Exception:
            return None, None
    
    # Check if it's an address
    if identifier.startswith("0x") and len(identifier) == 42:
        try:
            address = w3.to_checksum_address(identifier)
            balance = identity.functions.balanceOf(address).call()
            if balance > 0:
                # This address owns at least one agent, but we'd need to enumerate
                # For simplicity, return the address as owner
                return None, address
            return None, None
        except Exception:
            return None, None
    
    return None, None


def fetch_agent_uri(w3, config: Dict, agent_id: int) -> Optional[Dict]:
    """Fetch and parse agent URI metadata."""
    identity = w3.eth.contract(
        address=w3.to_checksum_address(config["identity_registry"]),
        abi=IDENTITY_ABI
    )
    
    try:
        uri = identity.functions.tokenURI(agent_id).call()
        
        # Handle data URI
        if uri.startswith("data:application/json;base64,"):
            import base64
            json_str = base64.b64decode(uri.split(",")[1]).decode("utf-8")
            return json.loads(json_str)
        
        # Handle IPFS or HTTP URI (simplified - just return the URI)
        return {"uri": uri}
    except Exception:
        return None


def fetch_reputation(w3, config: Dict, agent_id: int) -> Dict[str, Any]:
    """Fetch reputation summary for an agent."""
    reputation = w3.eth.contract(
        address=w3.to_checksum_address(config["reputation_registry"]),
        abi=REPUTATION_ABI
    )
    
    # First, get all clients who have given feedback
    try:
        clients = reputation.functions.getClients(agent_id).call()
    except Exception:
        clients = []
    
    if not clients:
        # No feedback yet
        return {
            "Initiative": {"count": 0, "score": 0},
            "Collaboration": {"count": 0, "score": 0},
            "Reasoning": {"count": 0, "score": 0},
            "Compliance": {"count": 0, "score": 0},
            "Efficiency": {"count": 0, "score": 0},
            "overall": {"count": 0, "score": 0}
        }
    
    # Proof of Agency dimensions
    dimensions = ["Initiative", "Collaboration", "Reasoning", "Compliance", "Efficiency"]
    results = {}
    
    for dim in dimensions:
        try:
            # Feb 2026 spec: returns (count, value, valueDecimals)
            # Must pass clientAddresses for Sybil resistance
            count, value, value_decimals = reputation.functions.getSummary(
                agent_id,
                clients,  # Required: list of client addresses
                dim,      # tag1
                ""        # tag2
            ).call()
            # Convert value based on decimals (for now decimals=0 means raw score)
            score = int(value) if value_decimals == 0 else int(value / (10 ** value_decimals))
            # Clamp to 0-100 range
            score = max(0, min(100, score))
            results[dim] = {"count": count, "score": score}
        except Exception as e:
            results[dim] = {"count": 0, "score": 0}
    
    # Overall summary
    try:
        total_count, value, value_decimals = reputation.functions.getSummary(
            agent_id,
            clients,
            "",
            ""
        ).call()
        score = int(value) if value_decimals == 0 else int(value / (10 ** value_decimals))
        score = max(0, min(100, score))
        results["overall"] = {"count": total_count, "score": score}
    except Exception:
        results["overall"] = {"count": 0, "score": 0}
    
    results["_clients"] = len(clients)  # For debugging
    
    return results


def render_progress_bar(score: int, width: int = 10) -> str:
    """Render a text progress bar."""
    filled = int((score / 100) * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def trust_level(score: int) -> str:
    """Convert score to trust level."""
    if score >= 80:
        return "✅ HIGH TRUST"
    elif score >= 60:
        return "🟡 MODERATE"
    elif score >= 40:
        return "🟠 LOW"
    else:
        return "🔴 VERY LOW"


# ============================================================================
# COMMANDS
# ============================================================================

def cmd_verify(identifier: str, network: Optional[str] = None):
    """Verify an agent's on-chain identity."""
    w3, config = get_web3("read", network)
    
    print(f"⛓️ Verifying agent: {identifier}")
    print(f"   Network: {config['network'].upper()}")
    print("━" * 40)
    
    agent_id, owner = resolve_agent_id(w3, config, identifier)
    
    if agent_id is None and owner is None:
        print("❌ NOT REGISTERED on ERC-8004")
        print("")
        print("This identifier has no on-chain agent identity.")
        print("They can register at: https://chaoscha.in")
        return
    
    print(f"✅ REGISTERED on ERC-8004")
    print("")
    
    if agent_id:
        print(f"Agent ID: #{agent_id}")
        print(f"Owner: {owner}")
        
        # Fetch metadata
        metadata = fetch_agent_uri(w3, config, agent_id)
        if metadata:
            if "name" in metadata:
                print(f"Name: {metadata['name']}")
            if "description" in metadata:
                desc = metadata['description'][:100] + "..." if len(metadata.get('description', '')) > 100 else metadata.get('description', '')
                print(f"Description: {desc}")
        
        # Fetch reputation summary
        rep = fetch_reputation(w3, config, agent_id)
        overall = rep.get("overall", {})
        score = overall.get("score", 0)
        count = overall.get("count", 0)
        
        print("")
        print(f"Trust Score: {score}/100 ({trust_level(score)})")
        print(f"Total Feedback: {count} reviews")
        
        # Link to 8004scan
        print("")
        print(f"🔗 https://8004scan.io/agents/{config['network']}/{agent_id}")
    else:
        print(f"Address: {owner}")
        print("This address owns agent(s) but specific ID not resolved.")


def cmd_reputation(identifier: str, network: Optional[str] = None):
    """View detailed reputation scores for an agent."""
    w3, config = get_web3("read", network)
    
    agent_id, owner = resolve_agent_id(w3, config, identifier)
    
    if agent_id is None:
        print(f"❌ Cannot fetch reputation: Agent not found")
        print(f"   Identifier: {identifier}")
        return
    
    print(f"⛓️ Agent #{agent_id} Reputation")
    print(f"   Network: {config['network'].upper()}")
    print("━" * 40)
    
    rep = fetch_reputation(w3, config, agent_id)
    
    # Display each dimension
    dimensions = ["Initiative", "Collaboration", "Reasoning", "Compliance", "Efficiency"]
    
    for dim in dimensions:
        data = rep.get(dim, {"count": 0, "score": 0})
        score = data["score"]
        bar = render_progress_bar(score)
        print(f"{dim:14} {bar} {score:3}/100")
    
    print("")
    
    # Overall
    overall = rep.get("overall", {"count": 0, "score": 0})
    score = overall["score"]
    count = overall["count"]
    
    print(f"Overall: {score}/100 ({trust_level(score)})")
    print(f"Based on {count} on-chain feedback entries.")
    
    print("")
    print(f"🔗 https://8004scan.io/agents/{config['network']}/{agent_id}")


def cmd_whoami(network: Optional[str] = None):
    """Check if your wallet has an on-chain identity."""
    w3, config = get_web3("read", network)
    
    # Get address from env
    address = os.environ.get("CHAOSCHAIN_ADDRESS")
    private_key = os.environ.get("CHAOSCHAIN_PRIVATE_KEY")
    
    if private_key and not address:
        from eth_account import Account
        account = Account.from_key(private_key)
        address = account.address
    
    if not address:
        print("❌ No wallet configured")
        print("")
        print("Set CHAOSCHAIN_ADDRESS or CHAOSCHAIN_PRIVATE_KEY in your OpenClaw config:")
        print("")
        print('  "skills": {')
        print('    "entries": {')
        print('      "chaoschain": {')
        print('        "env": {')
        print('          "CHAOSCHAIN_ADDRESS": "0x..."')
        print('        }')
        print('      }')
        print('    }')
        print('  }')
        return
    
    print(f"⛓️ Checking identity for: {address[:10]}...{address[-8:]}")
    print(f"   Network: {config['network'].upper()}")
    print("━" * 40)
    
    identity = w3.eth.contract(
        address=w3.to_checksum_address(config["identity_registry"]),
        abi=IDENTITY_ABI
    )
    
    try:
        balance = identity.functions.balanceOf(w3.to_checksum_address(address)).call()
        
        if balance > 0:
            print(f"✅ You have {balance} registered agent(s)")
            print("")
            print("Use /chaoschain reputation <your_agent_id> to see your scores.")
        else:
            print("❌ No registered agent found for this wallet")
            print("")
            print("Register with: /chaoschain register")
            print("(Requires CHAOSCHAIN_PRIVATE_KEY and ETH for gas)")
    except Exception as e:
        print(f"❌ Error checking identity: {e}")


def cmd_register(network: Optional[str] = None):
    """Register your agent on ERC-8004 (ON-CHAIN ACTION)."""
    # Get config FIRST to show which network
    w3, config = get_web3("register", network)
    
    print("⚠️  WARNING: ON-CHAIN TRANSACTION")
    print("━" * 40)
    
    # Extra warning for mainnet
    if config["network"] == "mainnet":
        print("🔴 MAINNET TRANSACTION - REAL ETH REQUIRED")
        print("")
        print("You are about to register on Ethereum Mainnet.")
        print("This costs real ETH and is permanent.")
        print("")
        print("For testing, use: /chaoschain register --network sepolia")
        print("")
    else:
        print(f"Network: {config['network'].upper()} (testnet)")
        print("")
    
    print("This command will:")
    print("  1. Submit a transaction to Ethereum")
    print("  2. Cost gas (~0.001 ETH)")
    print("  3. Register your agent permanently on ERC-8004")
    print("")
    
    private_key = os.environ.get("CHAOSCHAIN_PRIVATE_KEY")
    
    if not private_key:
        print("❌ CHAOSCHAIN_PRIVATE_KEY not set")
        print("")
        print("To register, add your private key to OpenClaw config:")
        print("")
        print('  "skills": {')
        print('    "entries": {')
        print('      "chaoschain": {')
        print('        "env": {')
        print('          "CHAOSCHAIN_PRIVATE_KEY": "0x...",')
        print(f'          "CHAOSCHAIN_NETWORK": "{config["network"]}"')
        print('        }')
        print('      }')
        print('    }')
        print('  }')
        return
    
    from eth_account import Account
    account = Account.from_key(private_key)
    address = account.address
    
    print(f"Wallet: {address[:10]}...{address[-8:]}")
    print(f"Network: {config['network'].upper()}")
    
    # Check balance
    balance = w3.eth.get_balance(address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"Balance: {balance_eth:.6f} ETH")
    
    if balance_eth < 0.001:
        print("")
        print("❌ Insufficient ETH for gas")
        print(f"   Need at least 0.001 ETH, have {balance_eth:.6f} ETH")
        return
    
    # Check if already registered
    identity = w3.eth.contract(
        address=w3.to_checksum_address(config["identity_registry"]),
        abi=IDENTITY_ABI
    )
    
    existing = identity.functions.balanceOf(w3.to_checksum_address(address)).call()
    if existing > 0:
        print("")
        print(f"⚠️  You already have {existing} registered agent(s)")
        print("   Registration will create an additional agent ID.")
    
    print("")
    print("Proceeding with registration...")
    print("")
    
    # Build transaction
    agent_uri = json.dumps({
        "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
        "name": f"OpenClaw Agent",
        "description": "AI agent registered via ChaosChain OpenClaw skill",
        "active": True
    })
    
    try:
        # Get nonce
        nonce = w3.eth.get_transaction_count(address)
        
        # Build tx
        tx = identity.functions.register(agent_uri).build_transaction({
            'from': address,
            'nonce': nonce,
            'gas': 200000,
            'maxFeePerGas': w3.eth.gas_price * 2,
            'maxPriorityFeePerGas': w3.to_wei(1, 'gwei'),
            'chainId': config['chain_id']
        })
        
        # Sign and send
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        print(f"📤 Transaction sent: {tx_hash.hex()}")
        print(f"🔗 {config['explorer']}/tx/{tx_hash.hex()}")
        print("")
        print("Waiting for confirmation...")
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            print("")
            print("✅ Registration successful!")
            print("")
            print("Your agent is now registered on ERC-8004.")
            print("Use /chaoschain whoami to see your agent ID.")
        else:
            print("")
            print("❌ Transaction failed")
            print(f"   Receipt: {receipt}")
    
    except Exception as e:
        print(f"❌ Registration failed: {e}")


def parse_network_flag(args: list) -> Tuple[list, Optional[str]]:
    """Parse --network flag from arguments."""
    network = None
    filtered_args = []
    
    i = 0
    while i < len(args):
        if args[i] == "--network" and i + 1 < len(args):
            network = args[i + 1].lower()
            if network not in CONTRACTS:
                print(f"❌ Unknown network: {network}")
                print("   Valid options: mainnet, sepolia")
                sys.exit(1)
            i += 2
        elif args[i].startswith("--network="):
            network = args[i].split("=")[1].lower()
            if network not in CONTRACTS:
                print(f"❌ Unknown network: {network}")
                print("   Valid options: mainnet, sepolia")
                sys.exit(1)
            i += 1
        else:
            filtered_args.append(args[i])
            i += 1
    
    return filtered_args, network


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("ChaosChain OpenClaw Skill")
        print("━" * 40)
        print("Commands:")
        print("  verify <agent_id>      - Check agent registration")
        print("  reputation <agent_id>  - View reputation scores")
        print("  whoami                 - Check your identity")
        print("  register               - Register on ERC-8004")
        print("")
        print("Options:")
        print("  --network <network>    - mainnet or sepolia")
        print("")
        print("Network Defaults:")
        print("  • Read operations (verify, reputation): Mainnet")
        print("  • Write operations (register): Sepolia (safe default)")
        print("")
        print("Examples:")
        print("  python chaoschain_skill.py verify 450")
        print("  python chaoschain_skill.py verify 450 --network sepolia")
        print("  python chaoschain_skill.py register --network sepolia")
        print("  python chaoschain_skill.py register --network mainnet  # advanced")
        return
    
    # Parse --network flag
    args, network = parse_network_flag(sys.argv[1:])
    
    if not args:
        print("No command specified. Use: verify, reputation, whoami, or register")
        return
    
    command = args[0].lower()
    
    if command == "verify":
        if len(args) < 2:
            print("Usage: verify <agent_id_or_address> [--network mainnet|sepolia]")
            return
        cmd_verify(args[1], network)
    
    elif command == "reputation":
        if len(args) < 2:
            print("Usage: reputation <agent_id_or_address> [--network mainnet|sepolia]")
            return
        cmd_reputation(args[1], network)
    
    elif command == "whoami":
        cmd_whoami(network)
    
    elif command == "register":
        cmd_register(network)
    
    else:
        print(f"Unknown command: {command}")
        print("Use: verify, reputation, whoami, or register")


if __name__ == "__main__":
    main()
