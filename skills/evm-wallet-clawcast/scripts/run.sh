#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
chmod +x "${DIR}/"*.sh || true
"${DIR}/01_install_cast.sh"
"${DIR}/02_wallet.sh"
"${DIR}/03_password.sh"
"${DIR}/04_network.sh"
"${DIR}/05_tokens.sh"
"${DIR}/06_finish.sh"
