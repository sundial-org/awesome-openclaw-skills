#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DIR}/00_lib.sh"
state_init
enable_strict_path
bold "6) Setup complete"
line
ADDRESS="$(state_get "ADDRESS")"
NETWORK="$(state_get "NETWORK")"
CHAIN_ID="$(state_get "CHAIN_ID")"
RPC="$(state_get "ETH_RPC_URL")"
KEYSTORE_FILE="$(state_get "KEYSTORE_FILE")"
PASSWORD_FILE="$(state_get "PASSWORD_FILE")"
if [[ -z "$ADDRESS" || -z "$RPC" || -z "$KEYSTORE_FILE" ]]; then
  err "Missing state. Make sure steps 02–04 were completed."
  exit 1
fi
echo "Address: ${ADDRESS}"
echo "Network: ${NETWORK:-unknown} (chainId=${CHAIN_ID:-unknown})"
echo "RPC: ${RPC}"
dim "Fetching native balance..."
bal="$(cast balance "${ADDRESS}" --rpc-url "${RPC}" 2>/dev/null || true)"
if [[ -n "$bal" ]]; then
  ok "Native balance: ${bal}"
else
  warn "Could not fetch balance. Check RPC URL."
fi
dim "Example commands:"
echo " # native transfer"
if [[ -n "${PASSWORD_FILE}" && -f "${PASSWORD_FILE}" ]]; then
  echo " cast send 0xRecipient --value 0.01ether --rpc-url \"${RPC}\" --keystore \"${KEYSTORE_FILE}\" --password-file \"${PASSWORD_FILE}\""
else
  echo " cast send 0xRecipient --value 0.01ether --rpc-url \"${RPC}\" --keystore \"${KEYSTORE_FILE}\""
fi
ok "Onboarding finished."
