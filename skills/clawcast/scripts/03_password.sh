#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DIR}/00_lib.sh"
state_init
enable_strict_path
bold "3) Set password and create encrypted keystore"
line
if ! has_cmd cast; then
  err "cast is not installed. Run ./01_install_cast.sh first."
  exit 1
fi
PK_FILE="$(state_get "PRIVATE_KEY_FILE")"
if [[ -z "$PK_FILE" || ! -f "$PK_FILE" ]]; then
  err "Private key temp file not found. Run ./02_wallet.sh first."
  exit 1
fi
KEYSTORE_FILE="${APP_DIR}/keystore.json"
PASSWORD_FILE="${APP_DIR}/pw.txt"
state_set "KEYSTORE_FILE" "${KEYSTORE_FILE}"
state_set "PASSWORD_FILE" "${PASSWORD_FILE}"
echo "This password encrypts the keystore file."
echo
PW="$(ask_hidden "Enter password: ")"
if [[ -z "$PW" ]]; then
  err "Password cannot be empty."
  exit 1
fi
state_set "SAVE_PASSWORD" "y"
umask 077
printf "%s" "$PW" > "${PASSWORD_FILE}"
chmod 600 "${PASSWORD_FILE}" || true
ok "Password saved to ${PASSWORD_FILE}"
acct_name="agent"
state_set "KEYSTORE_NAME" "${acct_name}"
PRIVATE_KEY="$(cat "${PK_FILE}")"
if ! [[ "$PRIVATE_KEY" =~ ^0x[0-9a-fA-F]{64}$ ]]; then
  err "Temp private key file is invalid."
  exit 1
fi
warn "Creating keystore via cast..."
dim "If cast prompts you, enter the password you just set."
set +e
CAST_UNSAFE_PASSWORD="$PW" \
  cast wallet import "$acct_name" --private-key "$PRIVATE_KEY"
rc=$?
if [[ $rc -ne 0 ]]; then
  warn "Non-interactive import failed; falling back to interactive mode."
  CAST_UNSAFE_PASSWORD="$PW" \
    cast wallet import "$acct_name" --interactive
  rc=$?
fi
set -e
if [[ ${rc:-1} -ne 0 ]]; then
  err "Keystore creation failed."
  exit 1
fi
candidate=""
if [[ -f "${FOUNDRY_KEYSTORE_DIR}/${acct_name}" ]]; then
  candidate="${FOUNDRY_KEYSTORE_DIR}/${acct_name}"
elif [[ -f "${FOUNDRY_KEYSTORE_DIR}/${acct_name}.json" ]]; then
  candidate="${FOUNDRY_KEYSTORE_DIR}/${acct_name}.json"
else
  newest="$(ls -t "${FOUNDRY_KEYSTORE_DIR}" 2>/dev/null | head -n 1 || true)"
  [[ -n "$newest" && -f "${FOUNDRY_KEYSTORE_DIR}/${newest}" ]] && candidate="${FOUNDRY_KEYSTORE_DIR}/${newest}" || candidate=""
fi
if [[ -z "$candidate" ]]; then
  err "Could not locate created keystore file in ${FOUNDRY_KEYSTORE_DIR}."
  exit 1
fi
cp -f "$candidate" "${KEYSTORE_FILE}"
chmod 600 "${KEYSTORE_FILE}" || true
ok "Keystore saved to ${KEYSTORE_FILE}"
rm -f "${PK_FILE}" || true
state_set "PRIVATE_KEY_FILE" ""
ok "Temporary private key file deleted."
ADDRESS="$(cast wallet address --keystore "${KEYSTORE_FILE}" --password-file "${PASSWORD_FILE}")"
state_set "ADDRESS" "${ADDRESS}"
ok "Address: ${ADDRESS}"
