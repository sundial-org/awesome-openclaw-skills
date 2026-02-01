#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DIR}/00_lib.sh"
state_init
enable_strict_path
NETWORK="$(state_get "NETWORK")"
CHAIN_ID="$(state_get "CHAIN_ID")"
RPC_URL="$(state_get "ETH_RPC_URL")"
if [[ -z "$NETWORK" || -z "$CHAIN_ID" || -z "$RPC_URL" ]]; then
  warn "Network configuration is incomplete."
  [[ -n "$NETWORK" ]] && printf "Network: %s\n" "$NETWORK"
  [[ -n "$CHAIN_ID" ]] && printf "Chain ID: %s\n" "$CHAIN_ID"
  [[ -n "$RPC_URL" ]] && printf "RPC: %s\n" "$RPC_URL"
  exit 1
fi
ok "Current network is ${NETWORK} (chainId=${CHAIN_ID})."
echo "RPC URL: ${RPC_URL}"
