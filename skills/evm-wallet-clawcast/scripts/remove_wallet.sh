#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DIR}/00_lib.sh"
state_init
enable_strict_path
if ! confirm_prompt "This will delete your keystore/password/address and all related info. Continue?" "N"; then
  ok "Aborted wallet removal."
  exit 0
fi
KEYSTORE_FILE="$(state_get "KEYSTORE_FILE")"
PASSWORD_FILE="$(state_get "PASSWORD_FILE")"
PRIVATE_KEY_FILE="$(state_get "PRIVATE_KEY_FILE")"
ADDRESS="$(state_get "ADDRESS")"
KEYSTORE_NAME="$(state_get "KEYSTORE_NAME")"
APP_DIR="${APP_DIR:-${HOME}/.agent-wallet}"
FOUNDRY_KEYSTORE_DIR="${FOUNDRY_KEYSTORE_DIR:-${HOME}/.foundry/keystores}" # just in case
WORKSPACE_ROOT="$(cd "${DIR}/../.." && pwd)"
TX_LOG_FILE="${WORKSPACE_ROOT}/logs/tx_mentions.log"
remove_path() {
  local path="$1"
  local label="$2"
  if [[ -n "$path" && -f "$path" ]]; then
    rm -f "$path"
    ok "Removed ${label}: ${path}"
  elif [[ -n "$path" ]]; then
    warn "Expected ${label} at ${path}, but it was already gone."
  fi
}
remove_path "$KEYSTORE_FILE" "keystore"
remove_path "$PASSWORD_FILE" "password stash"
remove_path "$PRIVATE_KEY_FILE" "temporary private key"
cleanup_mnemonics() {
  local pattern="${APP_DIR}/mnemonic-words-*.txt"
  local removed=0
  if compgen -G "$pattern" >/dev/null 2>&1; then
    for file in "${APP_DIR}"/mnemonic-words-*.txt; do
      if [[ -f "$file" ]]; then
        rm -f "$file"
        ok "Removed mnemonic backup: ${file}"
        removed=1
      fi
    done
  fi
  if [[ $removed -eq 0 ]]; then
    dim "No mnemonic backups found."
  fi
}
cleanup_mnemonics

cleanup_tx_mentions() {
  local file="$TX_LOG_FILE"
  if [[ -z "$ADDRESS" || ! -f "$file" ]]; then
    return
  fi
  if ! grep -Fq "$ADDRESS" "$file"; then
    return
  fi
  local tmp
  tmp="$(mktemp)"
  grep -vF "$ADDRESS" "$file" >"$tmp"
  mv "$tmp" "$file"
  ok "Removed wallet mentions from ${file}"
}
cleanup_tx_mentions

remove_foundry_keystore() {
  local name="$1"
  if [[ -z "$name" ]]; then
    warn "Keystore name unknown; skipping Foundry keystore pruning."
    return
  fi
  local removed=0
  for candidate in "${FOUNDRY_KEYSTORE_DIR}/${name}" "${FOUNDRY_KEYSTORE_DIR}/${name}.json"; do
    if [[ -f "$candidate" ]]; then
      rm -f "$candidate"
      ok "Removed Foundry keystore: ${candidate}"
      removed=1
    fi
  done
  if [[ $removed -eq 0 ]]; then
    dim "No Foundry keystore artifacts for '${name}' were present."
  fi
}
remove_foundry_keystore "$KEYSTORE_NAME"
for key in KEYSTORE_FILE PASSWORD_FILE ADDRESS PRIVATE_KEY_FILE SAVE_PASSWORD KEYSTORE_NAME NETWORK CHAIN_ID ETH_RPC_URL NETWORK_KEY; do
  state_unset "$key"
done
ok "Cleared wallet metadata from ${STATE_FILE}."
if [[ -d "${APP_DIR}" ]]; then
  rm -rf "${APP_DIR}"
  ok "Removed ${APP_DIR} directory to wipe remaining artefacts."
fi
ensure_app_dir
state_init
ok "Fresh wallet state directory ready."
if [[ -n "$ADDRESS" ]]; then
  printf "Removed wallet address: %s
" "$ADDRESS"
fi
ok "Wallet removal complete."
