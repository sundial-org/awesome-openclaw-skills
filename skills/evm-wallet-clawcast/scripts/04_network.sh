#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DIR}/00_lib.sh"
state_init
enable_strict_path
bold "4) Select network"
line

NETS_JSON="${ASSETS_DIR}/evm-networks.json"
TMP_NETS="$(mktemp)"
if ! python3 - "${NETS_JSON}" <<'PY' > "${TMP_NETS}"
import json
from pathlib import Path
import sys
path = Path(sys.argv[1])
if not path.is_file():
    raise SystemExit(1)
data = json.load(open(path))
nets = data.get('evmNetworks', [])
for net in nets:
    rpc_urls = net.get('rpcUrls') or []
    if not rpc_urls:
        continue
    name = net.get('name') or net.get('key') or 'Unnamed network'
    cid = net.get('chainId')
    if cid is None:
        continue
    rpc = rpc_urls[0]
    key = net.get('key') or name.lower().replace(' ', '_')
    print(f"{name}\t{cid}\t{rpc}\t{key}")
PY
then
  rm -f "${TMP_NETS}"
  err "Failed to read networks from ${NETS_JSON}."
  exit 1
fi

i=0
names=()
chainIds=()
rpcs=()
keys=()
set +e
while IFS=$'\t' read -r name cid rpc key; do
  [[ -z "$name" ]] && continue
  [[ -z "$cid" ]] && continue
  [[ -z "$rpc" ]] && continue
  ((i++))
  names+=("$name")
  chainIds+=("$cid")
  rpcs+=("$rpc")
  keys+=("${key:-}")
  if [[ $i -eq 1 ]]; then
    printf " %d) %s (chainId=%s) [default]\n" "$i" "$name" "$cid"
  else
    printf " %d) %s (chainId=%s)\n" "$i" "$name" "$cid"
  fi
done < "${TMP_NETS}"
set -e
rm -f "${TMP_NETS}"

if [[ $i -eq 0 ]]; then
  err "No networks could be loaded from ${NETS_JSON}."
  exit 1
fi

sel="$(ask_default "Choose a network number" "1")"
if ! [[ "$sel" =~ ^[0-9]+$ ]] || (( sel < 1 || sel > ${#names[@]} )); then
  warn "Invalid selection. Falling back to the first network."
  sel=1
fi
net="${names[$((sel-1))]}"
cid="${chainIds[$((sel-1))]}"
rpc="${rpcs[$((sel-1))]}"
key="${keys[$((sel-1))]}"
bold "Network selected: ${net} (chainId=${cid})"
state_set "NETWORK" "${net}"
state_set "CHAIN_ID" "${cid}"
state_set "ETH_RPC_URL" "${rpc}"
state_set "NETWORK_KEY" "${key}"
ok "Network config saved."
dim "Using RPC endpoint: ${rpc}"
