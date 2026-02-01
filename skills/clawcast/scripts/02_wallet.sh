#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${DIR}/00_lib.sh"
state_init
enable_strict_path
extract_mnemonic_words() {
  local raw_output="$1"
  printf "%s\n" "$raw_output" | python3 -c 'import re, sys; text=sys.stdin.read(); match=re.search(r"([a-z]+(?: [a-z]+){11,23})", text);
if match:
    print(match.group(1))'
}

ask_default_tty() {
  local prompt="$1"
  local default="$2"
  local tty="/dev/tty"
  local answer
  if [[ -t 0 ]]; then
    printf "%s [%s]: " "$prompt" "$default" >&2
    read -r answer
  else
    if [[ -r "$tty" ]]; then
      local tty_fd
      if exec {tty_fd}<>"$tty" 2>/dev/null; then
        read -rp "$prompt [$default]: " answer <&"$tty_fd" || true
        exec {tty_fd}>&-
      else
        read -rp "$prompt [$default]: " answer || true
      fi
    else
      read -rp "$prompt [$default]: " answer || true
    fi
  fi
  if [[ -z "${answer:-}" ]]; then
    printf "%s" "$default"
  else
    printf "%s" "$answer"
  fi
}

ensure_at_available() {
  if has_cmd at; then
    return 0
  fi
  local installer
  if [[ -x "/usr/bin/apt-get" ]]; then
    installer="apt-get install -y at"
  elif [[ -x "/usr/bin/apt" ]]; then
    installer="apt install -y at"
  else
    warn "'at' command missing and no apt-like installer found; mnemonic cleanup must be manual."
    return 1
  fi
  if [[ -x "/usr/bin/sudo" ]]; then
    if ! sudo sh -c "$installer > /tmp/at-install.log 2>&1"; then
      warn "Failed to install 'at' with sudo; mnemonic cleanup will be manual."
      return 1
    fi
  else
    if ! sh -c "$installer > /tmp/at-install.log 2>&1"; then
      warn "Failed to install 'at'; mnemonic cleanup will be manual."
      return 1
    fi
  fi
  hash -r
  if has_cmd at; then
    ok "Installed 'at' so mnemonic cleanup can be scheduled."
    return 0
  fi
  warn "Installation succeeded but 'at' still unavailable; cleanup will be manual."
  return 1
}

schedule_mnemonic_file_cleanup() {
  local target="$1"
  if ! ensure_at_available; then
    warn "Mnemonic file ${target} won't auto-delete (no 'at'). Please remove it after ~1 hour."
    return
  fi
  local job_output rc
  set +e
  job_output="$(printf 'rm -f -- %q\n' "$target" | at now + 1 hour 2>&1)"
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    ok "Mnemonic file scheduled for deletion (${job_output//$'\n'/; })."
  else
    warn "Scheduling deletion failed (${job_output//$'\n'/; }). Please remove ${target} manually."
  fi
}
bold "2) Create or import wallet"
line
if ! has_cmd cast; then
  err "cast is not installed. Run ./01_install_cast.sh first."
  exit 1
fi
PK_TMP="${APP_DIR}/privatekey.tmp"
state_set "PRIVATE_KEY_FILE" "${PK_TMP}"
echo "Choose an option:"
echo " 1) Create a new wallet (recommended)"
echo " 2) Import 12/24-word mnemonic (MetaMask derivation m/44'/60'/0'/0/0)"
echo " 3) Import a private key (0x...)"
choice="$(ask_default_tty "Select (1/2/3)" "1")"
PRIVATE_KEY=""
MNEMONIC=""
CREATED_NEW_WALLET=0
case "$choice" in
  1)
    bold "Creating a new wallet key"
    line
    set +e
    out="$(cast wallet new-mnemonic --words 12 --accounts 1 --color never)"
    rc=$?
    set -e
    if [[ $rc -ne 0 ]]; then
      warn "cast wallet new-mnemonic failed; falling back to generic key creation"
      set +e
      out="$(cast wallet new)"
      rc=$?
      set -e
      if [[ $rc -ne 0 ]]; then
        err "Unable to generate wallet material."
        exit 1
      fi
    fi
    PRIVATE_KEY="$(printf "%s" "$out" | grep -Eo '0x[0-9a-fA-F]{64}' | head -n 1 || true)"
    MNEMONIC="$(extract_mnemonic_words "$out")"
    CREATED_NEW_WALLET=1
    if [[ -z "$PRIVATE_KEY" ]]; then
      err "Failed to parse private key from cast output."
      exit 1
    fi
    ok "Generated a new key (private key not printed again)."
    ;;
  2)
    bold "Importing mnemonic (MetaMask-compatible)"
    line
    echo "Paste your 12/24-word mnemonic. It will NOT be printed back."
    MNEMONIC="$(ask_hidden "Mnemonic: ")"
    PRIVATE_KEY="$(derive_pk_from_mnemonic "$MNEMONIC")"
    if [[ -z "$PRIVATE_KEY" ]]; then
      err "Could not derive a private key from mnemonic using your cast version."
      err "Fix: update Foundry (foundryup) or choose 'Import a private key'."
      exit 1
    fi
    ok "Derived private key from mnemonic (not printed)."
    ;;
  3)
    bold "Importing private key"
    line
    echo "Paste your private key (0x...). It will NOT be printed back."
    PRIVATE_KEY="$(ask_hidden "Private key: ")"
    ;;
  *)
    warn "Invalid choice. Defaulting to 'Create a new wallet'."
    set +e
    out="$(cast wallet new-mnemonic --words 12 --accounts 1 --color never)"
    rc=$?
    set -e
    if [[ $rc -ne 0 ]]; then
      warn "cast wallet new-mnemonic failed; falling back to generic key creation"
      set +e
      out="$(cast wallet new)"
      rc=$?
      set -e
      if [[ $rc -ne 0 ]]; then
        err "Unable to generate wallet material."
        exit 1
      fi
    fi
    PRIVATE_KEY="$(printf "%s" "$out" | grep -Eo '0x[0-9a-fA-F]{64}' | head -n 1 || true)"
    MNEMONIC="$(extract_mnemonic_words "$out")"
    CREATED_NEW_WALLET=1
    ;;
esac
umask 077
if [[ "$CREATED_NEW_WALLET" == "1" ]]; then
  if [[ -n "$MNEMONIC" ]]; then
    MNEMONIC_FILE="${APP_DIR}/mnemonic-words-$(date +%Y%m%d%H%M%S).txt"
    printf "%s\n" "$MNEMONIC" > "${MNEMONIC_FILE}"
    chmod 600 "${MNEMONIC_FILE}" || true
    ok "Recovery words saved to ${MNEMONIC_FILE}"
    cleanup_note="$(schedule_mnemonic_file_cleanup "${MNEMONIC_FILE}")"
    warn "Mnemonic file will be deleted in ~1 hour (${cleanup_note})."
  else
    warn "Could not automatically capture the mnemonic from cast; please record it securely now."
  fi
fi
if ! [[ "$PRIVATE_KEY" =~ ^0x[0-9a-fA-F]{64}$ ]]; then
  err "Private key format invalid."
  exit 1
fi
printf "%s" "${PRIVATE_KEY}" > "${PK_TMP}"
chmod 600 "${PK_TMP}" || true
ok "Wallet material prepared."
warn "A temporary private key file was created: ${PK_TMP}"
dim "Step 03 will encrypt it into a keystore and then delete this temp file."
ADDR="$(cast wallet address --private-key "${PRIVATE_KEY}" 2>/dev/null || true)"
if [[ -n "$ADDR" ]]; then
  ok "Address: ${ADDR}"
  state_set "ADDRESS" "${ADDR}"
else
  warn "Could not compute address from private key in this cast version."
fi
