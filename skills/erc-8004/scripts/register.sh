#!/bin/bash
# ERC-8004: Register an agent on the Identity Registry
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Register a new agent on the ERC-8004 Identity Registry.

Options:
    -u, --uri URI       Agent registration URI (IPFS/HTTPS/data:)
    -n, --network NET   Network (mainnet|sepolia) [default: mainnet]
    -k, --key KEY       Private key (or set PRIVATE_KEY env)
    --dry-run           Simulate without sending transaction
    -h, --help          Show this help

Examples:
    $(basename "$0") --uri "ipfs://QmXyz..."
    $(basename "$0") --uri "https://example.com/agent.json"
    $(basename "$0")  # Register without URI, set later
EOF
    exit 0
}

URI=""
NETWORK="mainnet"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--uri) URI="$2"; shift 2 ;;
        -n|--network) NETWORK="$2"; shift 2 ;;
        -k|--key) PRIVATE_KEY="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

load_network "$NETWORK"

# Check balance
BALANCE=$(cast balance "$WALLET_ADDRESS" --rpc-url "$RPC_URL" 2>/dev/null || echo "0")
if [[ "$BALANCE" == "0" ]]; then
    echo "Wallet $WALLET_ADDRESS has 0 balance on $NETWORK"
    echo "   Fund with testnet ETH: https://sepoliafaucet.com/"
    exit 1
fi

echo "Registering agent on ERC-8004 Identity Registry"
echo "   Network: $NETWORK"
echo "   Registry: $IDENTITY_REGISTRY"
echo "   Owner: $WALLET_ADDRESS"
[[ -n "$URI" ]] && echo "   URI: $URI"

if $DRY_RUN; then
    echo "Dry run - simulating..."
    if [[ -n "$URI" ]]; then
        cast call "$IDENTITY_REGISTRY" "register(string)" "$URI" --rpc-url "$RPC_URL"
    else
        cast call "$IDENTITY_REGISTRY" "register()" --rpc-url "$RPC_URL"
    fi
    echo "Simulation successful"
    exit 0
fi

echo "Sending transaction..."
if [[ -n "$URI" ]]; then
    TX_HASH=$(cast send "$IDENTITY_REGISTRY" "register(string)" "$URI" \
        --private-key "$PRIVATE_KEY" \
        --rpc-url "$RPC_URL" \
        --json | jq -r '.transactionHash')
else
    TX_HASH=$(cast send "$IDENTITY_REGISTRY" "register()" \
        --private-key "$PRIVATE_KEY" \
        --rpc-url "$RPC_URL" \
        --json | jq -r '.transactionHash')
fi

echo "Waiting for confirmation..."
RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$RPC_URL" --json)
STATUS=$(echo "$RECEIPT" | jq -r '.status')

if [[ "$STATUS" == "0x1" ]]; then
    # Parse Registered event to get agentId
    LOGS=$(echo "$RECEIPT" | jq -r '.logs')
    AGENT_ID=$(echo "$LOGS" | jq -r '.[0].topics[1]' | cast --to-dec)
    
    echo ""
    echo "Agent registered successfully!"
    echo "   Agent ID: $AGENT_ID"
    echo "   TX: $EXPLORER_URL/tx/$TX_HASH"
    echo "   View: $EXPLORER_URL/address/$IDENTITY_REGISTRY#readContract"
    echo ""
    echo "Next steps:"
    echo "   1. Upload registration JSON to IPFS"
    echo "   2. Set URI: ./set-uri.sh --agent-id $AGENT_ID --uri <ipfs://...>"
else
    echo "Transaction failed"
    echo "   TX: $EXPLORER_URL/tx/$TX_HASH"
    exit 1
fi
