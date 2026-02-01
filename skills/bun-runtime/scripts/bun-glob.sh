#!/usr/bin/env bash

# Glob file matching
# Usage: scripts/bun-glob.sh <pattern>

PATTERN="$1"

if [ -z "$PATTERN" ]; then
  echo "{\"error\":\"Pattern required\"}"
  exit 1
fi

# Use shell globbing and format as JSON
files=($PATTERN)
printf '{"files":['
first=true
for file in "${files[@]}"; do
  if [ -e "$file" ]; then
    if [ "$first" = true ]; then
      printf '"%s"' "$file"
      first=false
    else
      printf ',"%s"' "$file"
    fi
  fi
done
printf '],"count":%d}\n' $((${#files[@]}))
