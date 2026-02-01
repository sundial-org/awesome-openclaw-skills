#!/usr/bin/env bash
set -euo pipefail

# Print the Fly app name from fly.toml (if present)
# Usage: scripts/fly_app_from_toml.sh [path]

path="${1:-fly.toml}"

if [ ! -f "$path" ]; then
  echo "fly.toml not found: $path" >&2
  exit 1
fi

# naive parse: app = "name" OR app = 'name'
app=$(ruby -e 't=File.read(ARGV[0]); m=t.match(/^app\s*=\s*["\x27]([^"\x27]+)["\x27]/); puts(m ? m[1] : "")' "$path")

if [ -z "$app" ]; then
  echo "Could not find app = \"...\" in $path" >&2
  exit 1
fi

echo "$app"
