#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DIR}/00_lib.sh"
state_init
enable_strict_path
KEYSTORE_FILE="$(state_get "KEYSTORE_FILE")"
ADDRESS="$(state_get "ADDRESS")"
if [[ -n "${KEYSTORE_FILE}" && -f "${KEYSTORE_FILE}" && -n "${ADDRESS}" ]]; then
  ok "Wallet exists"
  printf "Address: %s\n" "${ADDRESS}"
  printf "Keystore: %s\n" "${KEYSTORE_FILE}"
  exit 0
fi
warn "No wallet detected"
if [[ -n "${KEYSTORE_FILE}" ]]; then
  printf "Expected keystore: %s\n" "${KEYSTORE_FILE}"
fi
if [[ -n "${ADDRESS}" ]]; then
  printf "Last known address: %s\n" "${ADDRESS}"
fi
exit 1
