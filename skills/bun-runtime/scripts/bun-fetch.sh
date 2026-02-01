#!/usr/bin/env bash

# Bun HTTP requests
# Usage: scripts/bun-fetch.sh <url> [method] [body]

URL="$1"
METHOD="${2:-GET}"
BODY="$3"

if [ -z "$URL" ]; then
  echo "{\"error\":\"URL required\"}"
  exit 1
fi

if [ -n "$BODY" ]; then
  bun -e "const res = await fetch('$URL', { method: '$METHOD', body: '$BODY', headers: { 'Content-Type': 'application/json' } }); console.log(JSON.stringify({ status: res.status, ok: res.ok, data: await res.text() }))"
else
  bun -e "const res = await fetch('$URL', { method: '$METHOD' }); console.log(JSON.stringify({ status: res.status, ok: res.ok, data: await res.text() }))"
fi
