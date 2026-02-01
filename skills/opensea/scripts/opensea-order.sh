#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: opensea-order.sh <chain> <order_hash>" >&2
  echo "Example: opensea-order.sh ethereum 0x1234..." >&2
  exit 1
fi

chain="$1"
order_hash="$2"
protocol="0x00000000000000adc04c56bf30ac9d3c0aaf14dc"

"$(dirname "$0")/opensea-get.sh" "/api/v2/orders/chain/${chain}/protocol/${protocol}/${order_hash}"
