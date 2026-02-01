#!/usr/bin/env bash
set -euo pipefail

APP_NAME="agent-wallet"
APP_DIR="${HOME}/.${APP_NAME}"
STATE_FILE="${APP_DIR}/state.env"
FOUNDRY_BIN_DIR="${HOME}/.foundry/bin"
FOUNDRY_KEYSTORE_DIR="${HOME}/.foundry/keystores"
ASSETS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../assets" && pwd)"
NETWORKS_JSON="${ASSETS_DIR}/evm-networks.json"
TOKENS_JSON="${ASSETS_DIR}/evm-network-tokens.json"

bold() { printf "\033[1m%s\033[0m " "$*"; }
dim() { printf "\033[2m%s\033[0m " "$*"; }
ok() { printf "\033[32m✔\033[0m %s " "$*"; }
warn() { printf "\033[33m!\033[0m %s " "$*"; }
err() { printf "\033[31m✖\033[0m %s " "$*"; }
line() { printf "%s " "------------------------------------------------------------"; }

enable_strict_path() {
  if [[ ":$PATH:" != *":${FOUNDRY_BIN_DIR}:"* ]]; then
    export PATH="${FOUNDRY_BIN_DIR}:$PATH"
  fi
}

has_cmd() { command -v "$1" >/dev/null 2>&1; }

ask_default() {
  local q="$1"
  local d="$2"
  local a
  printf "%s [%s]: " "$q" "$d" >&2
  read -r a || true
  if [[ -z "${a:-}" ]]; then
    printf "%s" "$d"
  else
    printf "%s" "$a"
  fi
}

ask_hidden() {
  local prompt="$1"
  local v
  read -rs -p "$prompt" v
  printf "\n"
  printf "%s" "$v"
}

is_yes() {
  local val
  val="$(printf "%s" "$1" | tr '[:upper:]' '[:lower:]')"
  [[ "$val" == "y" || "$val" == "yes" ]]
}

confirm_prompt() {
  local prompt="$1"
  local default="${2:-N}"
  local answer
  local tty="/dev/tty"
  if [[ -t 0 ]]; then
    while true; do
      read -rp "$prompt [$default]: " answer
      answer="${answer:-$default}"
      answer="$(printf "%s" "$answer" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')"
      case "$answer" in
        y|yes) return 0;;
        n|no) return 1;;
        *) printf "Please answer y or n.\n";;
      esac
    done
  else
    while true; do
      if ! read -rp "$prompt [$default]: " answer <"$tty"; then
        return 1
      fi
      answer="${answer:-$default}"
      answer="$(printf "%s" "$answer" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')"
      case "$answer" in
        y|yes) return 0;;
        n|no) return 1;;
        *) printf "Please answer y or n.\n";;
      esac
    done
  fi
}

_escape_squotes() {
  printf "%s" "$1" | sed "s/'/'\"'\"'/g"
}

ensure_app_dir() {
  mkdir -p "${APP_DIR}"
  chmod 700 "${APP_DIR}" || true
}

state_init() {
  ensure_app_dir
  if [[ ! -f "${STATE_FILE}" ]]; then
    cat > "${STATE_FILE}" <<EOF
APP_DIR='${APP_DIR}'
STATE_FILE='${STATE_FILE}'
EOF
    chmod 600 "${STATE_FILE}" || true
  fi
}

state_get() {
  local key="$1"
  state_init
  # shellcheck disable=SC1090
  source "${STATE_FILE}"
  printf '%s' "${!key-}"
}

state_set() {
  local key="$1"
  local val="$2"
  state_init
  local esc
  esc="$(_escape_squotes "$val")"
  if grep -qE "^${key}=" "${STATE_FILE}"; then
    if sed --version >/dev/null 2>&1; then
      sed -i -E "s#^${key}=.*#${key}='${esc}'#" "${STATE_FILE}"
    else
      sed -i '' -E "s#^${key}=.*#${key}=\'${esc}\'#" "${STATE_FILE}"
    fi
  else
    printf "%s='%s'\n" "$key" "$esc" >> "${STATE_FILE}"
  fi
  chmod 600 "${STATE_FILE}" || true
}

state_unset() {
  local key="$1"
  state_init
  local tmp
  tmp="$(mktemp)"
  grep -vE "^${key}=" "${STATE_FILE}" > "$tmp" || true
  mv "$tmp" "${STATE_FILE}"
  chmod 600 "${STATE_FILE}" || true
}

write_default_networks_if_missing() {
  local target="$1"
  if [[ -f "$target" ]]; then
    return
  fi
  python3 - "${NETWORKS_JSON}" <<'PY' > "$target"
import json, sys
networks=json.load(open(sys.argv[1], 'r'))
for net in networks.get('evmNetworks', []):
    name=net.get('name')
    cid=net.get('chainId')
    key=net.get('key', '')
    if name and cid is not None:
        print(f"{name}\t{cid}\t{key}")
PY
  chmod 600 "$target" || true
}

write_default_tokens_if_missing() {
  local target="$1"
  if [[ -f "$target" ]]; then
    return
  fi
  python3 - "${TOKENS_JSON}" <<'PY' > "$target"
import json, sys
networks=json.load(open(sys.argv[1], 'r')).get('networks', {})
seen=set()
print('# symbol\taddress\tdecimals')
for net_key, data in networks.items():
    name=data.get('name', net_key)
    tokens=data.get('tokens', {})
    for label in ('wrapped_native', 'stables'):
        block=tokens.get(label, {})
        if isinstance(block, dict):
            if 'address' in block and isinstance(block.get('symbol'), str):
                addr=block.get('address')
                if addr:
                    symbol=block.get('symbol', label.upper())
                    dec=block.get('decimals', '')
                    key=(symbol.lower(), addr.lower())
                    if key not in seen:
                        seen.add(key)
                        print(f"{symbol}\t{addr}\t{dec}")
            else:
                for symbol, info in block.items():
                    if not isinstance(info, dict):
                        continue
                    addr=info.get('address')
                    if not addr:
                        continue
                    dec=info.get('decimals', '')
                    key=(symbol.lower(), addr.lower())
                    if key in seen:
                        continue
                    seen.add(key)
                    print(f"{symbol}\t{addr}\t{dec}")
PY
  chmod 600 "$target" || true
}

print_tokens_from_json() {
  python3 - "$1" <<'PY'
import json, sys
networks=json.load(open(sys.argv[1], 'r')).get('networks', {})
seen=set()
rows=[]
for net_key, net in sorted(networks.items(), key=lambda kv: kv[1].get('chain_id', 0)):
    name=net.get('name', net_key)
    tokens=net.get('tokens', {}) or {}
    for label in ('wrapped_native', 'stables', 'custom'):
        block=tokens.get(label)
        if not isinstance(block, dict):
            continue
        entries=[]
        if 'address' in block and isinstance(block.get('symbol'), str):
            entries.append((block.get('symbol', label.upper()), block))
        else:
            entries.extend(block.items())
        for symbol, info in entries:
            if not isinstance(info, dict):
                continue
            addr=info.get('address')
            if not addr:
                continue
            key=(symbol.lower(), addr.lower())
            if key in seen:
                continue
            seen.add(key)
            dec=info.get('decimals', '')
            rows.append((name, label, symbol, addr, dec))
if rows:
    print('network	category	symbol	address	decimals')
    for row in rows:
        net, cat, sym, addr, dec=row
        print(f"{net}	{cat}	{sym}	{addr}	{dec}")
PY
}

add_custom_token_to_json() {
  local json_path="${1}"
  local net_key="${2}"
  local symbol="${3}"
  local address="${4}"
  local decimals="${5}"
  python3 - "${json_path}" "${net_key}" "${symbol}" "${address}" "${decimals}" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
net_key = sys.argv[2]
symbol = sys.argv[3]
address = sys.argv[4]
decimals = sys.argv[5]
data = json.load(open(path))
networks = data.setdefault('networks', {})
net = networks.get(net_key)
if net is None:
    raise SystemExit(f"Network key {net_key} not found")
tokens = net.setdefault('tokens', {})
custom = tokens.setdefault('custom', {})
existing = custom.get(symbol)
if isinstance(existing, dict) and existing.get('address', '').lower() == address.lower():
    print(f"Token {symbol} already exists on {net_key}")
    raise SystemExit(0)
try:
    decimal_value = int(decimals)
except ValueError:
    decimal_value = decimals
custom[symbol] = {
    'address': address,
    'decimals': decimal_value,
    'added_by': 'agent'
}
json.dump(data, open(path, 'w'), indent=2)
print(f"Token {symbol} saved for network {net_key}")
PY
}

derive_pk_from_mnemonic() {
  local mnemonic="$1"
  local hdpath="m/44'/60'/0'/0/0"
  if ! cast wallet >/dev/null 2>&1; then
    printf ""
    return 0
  fi
  local out
  set +e
  out=$(cast wallet derive --mnemonic "$mnemonic" --hd-path "$hdpath" 2>/dev/null || true)
  if [[ -z "$out" ]]; then
    out=$(cast wallet derive "$mnemonic" --hd-path "$hdpath" 2>/dev/null || true)
  fi
  set -e
  if [[ -z "$out" ]]; then
    printf ""
    return 0
  fi
  local pk
  pk=$(printf "%s" "$out" | grep -Eo '0x[0-9a-fA-F]{64}' | head -n 1 || true)
  printf "%s" "${pk:-}"
}
