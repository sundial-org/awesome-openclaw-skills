#!/usr/bin/env bash
set -euo pipefail

IMG=${1:-}
if [[ -z "${IMG}" ]]; then
  echo "Usage: recipe-to-list <image-path>" >&2
  exit 2
fi

# Load keys/tokens
set -a
[[ -f ~/.clawdbot/.env ]] && source ~/.clawdbot/.env
set +a

python3 "$(dirname "$0")/recipe_to_list.py" --image "$IMG" --project "Shopping" --source "photo:$IMG"
