#!/bin/bash
# ERC-8004: Query agents and reputation
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

usage() {
    cat <<EOF
Usage: $(basename "$0") <command> [OPTIONS]

Query ERC-8004 registries.

Commands:
    agent <id>          Get agent info by ID
    total               Get total registered agents
    reputation <id>     Get reputation summary for agent
    search <term>       Search agents (requires indexer)

Options:
    -n, --network NET   Network (mainnet|sepolia) [default: mainnet]
    -h, --help          Show this help

Examples:
    $(basename "$0") agent 1
    $(basename "$0") total
    $(basename "$0") reputation 1
EOF
    exit 0
}

NETWORK="mainnet"

# Parse network flag if present
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--network) NETWORK="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) break ;;
    esac
done

[[ $# -lt 1 ]] && usage

COMMAND="$1"
shift

load_network "$NETWORK"

case "$COMMAND" in
    agent)
        [[ $# -lt 1 ]] && { echo "Usage: query.sh agent <id>"; exit 1; }
        AGENT_ID="$1"
        
        echo "Querying agent $AGENT_ID on $NETWORK..."
        echo ""
        
        # Check if agent exists by calling ownerOf (reverts if doesn't exist)
        OWNER=$(cast call "$IDENTITY_REGISTRY" "ownerOf(uint256)(address)" "$AGENT_ID" --rpc-url "$RPC_URL" 2>/dev/null || echo "")
        if [[ -z "$OWNER" || "$OWNER" == "0x0000000000000000000000000000000000000000" ]]; then
            echo "Agent $AGENT_ID does not exist"
            exit 1
        fi
        
        URI=$(cast call "$IDENTITY_REGISTRY" "tokenURI(uint256)(string)" "$AGENT_ID" --rpc-url "$RPC_URL" 2>/dev/null || echo "")
        
        # Try getAgentWallet if it exists (may not be in all implementations)
        WALLET=$(cast call "$IDENTITY_REGISTRY" "getAgentWallet(uint256)(address)" "$AGENT_ID" --rpc-url "$RPC_URL" 2>/dev/null || echo "")
        
        echo "Agent #$AGENT_ID"
        echo "   Owner:  $OWNER"
        if [[ -n "$WALLET" && "$WALLET" != "0x0000000000000000000000000000000000000000" ]]; then
            echo "   Wallet: $WALLET"
        fi
        if [[ -n "$URI" && "$URI" != '""' ]]; then
            echo "   URI:    $URI"
        else
            echo "   URI:    (not set)"
        fi
        echo ""
        echo "Explorer: $EXPLORER_URL/token/$IDENTITY_REGISTRY?a=$AGENT_ID"
        ;;
        
    total)
        echo "Checking agent registry on $NETWORK..."
        echo ""
        
        # The official contracts don't have totalAgents(), so we probe for existence
        # by checking sequential IDs until we hit a non-existent one
        COUNT=0
        MAX_CHECK=1000
        
        for i in $(seq 1 $MAX_CHECK); do
            EXISTS=$(cast call "$IDENTITY_REGISTRY" "ownerOf(uint256)" "$i" --rpc-url "$RPC_URL" 2>/dev/null || echo "error")
            if [[ "$EXISTS" == "error" || "$EXISTS" == "" ]]; then
                COUNT=$((i - 1))
                break
            fi
            COUNT=$i
            # Show progress for large counts
            if (( i % 50 == 0 )); then
                echo "   Checked $i agents..."
            fi
        done
        
        echo "Total registered agents: $COUNT"
        echo "Registry: $EXPLORER_URL/address/$IDENTITY_REGISTRY"
        ;;
        
    reputation)
        [[ $# -lt 1 ]] && { echo "Usage: query.sh reputation <agent_id>"; exit 1; }
        AGENT_ID="$1"
        
        echo "Querying reputation for agent $AGENT_ID..."
        echo ""
        
        # Get summary with empty filters
        SUMMARY=$(cast call "$REPUTATION_REGISTRY" \
            "getSummary(uint256,address[],string,string)" \
            "$AGENT_ID" "[]" "" "" \
            --rpc-url "$RPC_URL" 2>/dev/null || echo "error")
        
        if [[ "$SUMMARY" == "error" ]]; then
            echo "No reputation data or query failed"
        else
            echo "Reputation Summary:"
            echo "   Raw: $SUMMARY"
            # Parse: (uint64 count, int128 summaryValue, uint8 summaryValueDecimals)
        fi
        ;;
        
    search)
        echo "Search requires an indexer (The Graph subgraph)"
        echo "   For now, iterate through agent IDs manually"
        ;;
        
    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac
