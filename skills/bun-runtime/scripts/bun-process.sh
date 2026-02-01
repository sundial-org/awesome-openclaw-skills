#!/usr/bin/env bash

# Bun process execution
# Usage: scripts/bun-process.sh <command>

COMMAND="$1"

if [ -z "$COMMAND" ]; then
  echo "{\"error\":\"Command required\"}"
  exit 1
fi

OUTPUT=$(eval "$COMMAND" 2>&1)
EXIT_CODE=$?

bun -e "console.log(JSON.stringify({ output: \`$OUTPUT\`, exitCode: $EXIT_CODE }))"
