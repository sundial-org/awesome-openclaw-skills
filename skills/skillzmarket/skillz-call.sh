#!/bin/bash
# Dispatched by OpenClaw with: command skillName commandName

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMAND="$1"
shift

case "$COMMAND" in
  search)
    npx tsx "$SCRIPT_DIR/skillz-cli.ts" search "$@"
    ;;
  info)
    npx tsx "$SCRIPT_DIR/skillz-cli.ts" info "$@"
    ;;
  call)
    npx tsx "$SCRIPT_DIR/skillz-cli.ts" call "$@"
    ;;
  direct)
    npx tsx "$SCRIPT_DIR/skillz-cli.ts" direct "$@"
    ;;
  *)
    echo "Usage: /skillzmarket <search|info|call|direct> [args]"
    exit 1
    ;;
esac
