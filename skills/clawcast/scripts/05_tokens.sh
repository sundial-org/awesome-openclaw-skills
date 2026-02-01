#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DIR}/00_lib.sh"
state_init
enable_strict_path
bold "5) Token list"
line
dim "Default tokens (sourced from assets/evm-network-tokens.json):"
print_tokens_from_json "${TOKENS_JSON}"

NET_KEY="$(state_get "NETWORK_KEY")"
NET_NAME="$(state_get "NETWORK")"
if [[ -z "${NET_KEY}" ]]; then
  NET_KEY="$(python3 - "${TOKENS_JSON}" <<'PY'
import json, sys
nets=json.load(open(sys.argv[1], 'r')).get('networks', {})
print(next(iter(nets), ''))
PY
)"
  [[ -n "${NET_KEY}" ]] && state_set "NETWORK_KEY" "${NET_KEY}"
fi
if [[ -z "${NET_NAME}" && -n "${NET_KEY}" ]]; then
  NET_NAME="$(python3 - "${TOKENS_JSON}" "${NET_KEY}" <<'PY'
import json, sys
net=json.load(open(sys.argv[1], 'r')).get('networks', {}).get(sys.argv[2], {})
print(net.get('name', ''))
PY
)"
  [[ -n "${NET_NAME}" ]] && state_set "NETWORK" "${NET_NAME}"
fi
if [[ -z "${NET_NAME}" ]]; then
  NET_NAME="<не указана>"
fi
if [[ -z "${NET_KEY}" ]]; then
  err "Нужно сначала выбрать сеть (шаг 4)."
  exit 1
fi

add_input="$(ask_default "Добавить токен для сети ${NET_NAME}? (y/N)" "N")"
if ! is_yes "${add_input}"; then
  ok "Token setup skipped."
  exit 0
fi

while true; do
  sym="$(ask_default "Token symbol (e.g., LINK)" "")"
  if [[ -z "${sym}" ]]; then
    warn "Empty symbol. Stopping."
    break
  fi
  addr="$(ask_default "Token contract address (0x...)" "0x")"
  dec="$(ask_default "Token decimals" "18")"
  if ! [[ "${addr}" =~ ^0x[0-9a-fA-F]{40}$ ]]; then
    warn "Invalid token address. Try again."
    continue
  fi
  if ! [[ "${dec}" =~ ^[0-9]+$ ]]; then
    warn "Decimals must be a number."
    continue
  fi
  add_custom_token_to_json "${TOKENS_JSON}" "${NET_KEY}" "${sym}" "${addr}" "${dec}"
  more_input="$(ask_default "Add another token? (y/N)" "N")"
  if ! is_yes "${more_input}"; then
    break
  fi

done
ok "Token list saved in ${TOKENS_JSON}."
