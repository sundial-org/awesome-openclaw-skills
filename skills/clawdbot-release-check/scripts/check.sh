#!/usr/bin/env bash
set -uo pipefail

# Try to find clawdbot source directory
if [[ -n "${CLAWDBOT_DIR:-}" ]]; then
  CLAWDBOT_DIR="$CLAWDBOT_DIR"
elif [[ -f "${HOME}/dev/clawdis/package.json" ]]; then
  CLAWDBOT_DIR="${HOME}/dev/clawdis"
elif [[ -f "${HOME}/clawdbot/package.json" ]]; then
  CLAWDBOT_DIR="${HOME}/clawdbot"
else
  # Fallback: find via npm
  CLAWDBOT_DIR=$(npm root -g 2>/dev/null)/clawdbot
fi
STATE_DIR="${HOME}/.clawdbot"
STATE_FILE="${STATE_DIR}/clawdbot-release-check-state.json"
CACHE_FILE="${STATE_DIR}/clawdbot-release-check-cache.json"
RELEASES_URL="https://api.github.com/repos/clawdbot/clawdbot/releases"
CACHE_MAX_AGE_HOURS="${CACHE_MAX_AGE_HOURS:-24}"

usage() {
  cat <<'EOF'
Clawdbot Release Checker

Checks for new clawdbot releases and notifies once per version.

Usage: check.sh [OPTIONS]

Options:
  --status          Show current vs latest version (no notification)
  --force           Show full notification even if already notified
  --all-highlights  Show highlights from ALL missed releases
  --reset           Clear notification state (will notify again on next run)
  --clear-cache     Clear cached release data
  -h, --help        Show this help

Examples:
  check.sh                  # Silent if up-to-date or already notified
  check.sh --status         # Quick version check
  check.sh --force          # Force fetch and show notification
  check.sh --all-highlights # See highlights from all missed versions

Cache: Release data cached for 24h. Highlights extracted once per release.
EOF
  exit 0
}

force=false
status_only=false
all_highlights=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) force=true; shift ;;
    --status) status_only=true; shift ;;
    --all-highlights) all_highlights=true; force=true; shift ;;
    --reset) rm -f "$STATE_FILE"; echo "State cleared."; exit 0 ;;
    --clear-cache) rm -f "$CACHE_FILE"; echo "Cache cleared."; exit 0 ;;
    -h|--help) usage ;;
    *) shift ;;
  esac
done

# Ensure state directory exists
mkdir -p "$STATE_DIR"

# Get current installed version from package.json
current_version=$(jq -r '.version' "$CLAWDBOT_DIR/package.json" 2>/dev/null || echo "unknown")

# Check if cache is valid
use_cache=false
if [[ -f "$CACHE_FILE" && "$force" == "false" ]]; then
  cache_time=$(jq -r '.fetchedAtMs // 0' "$CACHE_FILE" 2>/dev/null)
  now_ms=$(date +%s)000
  cache_age_hours=$(( (now_ms - cache_time) / 1000 / 3600 ))
  if [[ $cache_age_hours -lt $CACHE_MAX_AGE_HOURS ]]; then
    use_cache=true
  fi
fi

# Fetch or use cache
if [[ "$use_cache" == "true" ]]; then
  releases_json=$(jq '.releases' "$CACHE_FILE" 2>/dev/null)
else
  # Fetch from GitHub
  releases_json=$(curl -sS "$RELEASES_URL" 2>/dev/null)
  if [[ -n "$releases_json" && "$releases_json" != "null" ]]; then
    # Save to cache
    now_ms=$(date +%s)000
    jq -n --argjson releases "$releases_json" --argjson time "$now_ms" \
      '{fetchedAtMs: $time, releases: $releases, highlights: {}}' > "$CACHE_FILE"
  fi
fi

if [[ -z "$releases_json" || "$releases_json" == "null" ]]; then
  exit 0
fi

# Get latest release info
latest_tag=$(echo "$releases_json" | jq -r '.[0].tag_name // empty')
release_url=$(echo "$releases_json" | jq -r '.[0].html_url // empty')

if [[ -z "$latest_tag" ]]; then
  exit 0
fi

latest_version="${latest_tag#v}"

# Function to get highlights for a release (with caching)
get_highlights() {
  local tag="$1"
  local body="$2"
  
  # Check cache for pre-computed highlights
  if [[ -f "$CACHE_FILE" ]]; then
    cached=$(jq -r --arg tag "$tag" '.highlights[$tag] // empty' "$CACHE_FILE" 2>/dev/null)
    if [[ -n "$cached" ]]; then
      echo "$cached"
      return
    fi
  fi
  
  # Extract highlights
  local hl=""
  if echo "$body" | grep -qi "Highlights"; then
    hl=$(echo "$body" | sed -n '/[Hh]ighlights/,/^##[^#]/p' | head -8 | sed '/^##[^#]/d' | sed 's/^### //' | sed 's/^## //')
  else
    hl=$(echo "$body" | grep -v "^$" | head -6 | sed 's/^### //' | sed 's/^## //')
  fi
  
  # Save to cache
  if [[ -n "$hl" && -f "$CACHE_FILE" ]]; then
    local escaped_hl
    escaped_hl=$(echo "$hl" | jq -Rs .)
    jq --arg tag "$tag" --argjson hl "$escaped_hl" '.highlights[$tag] = $hl' "$CACHE_FILE" > /tmp/cache-update.json
    mv /tmp/cache-update.json "$CACHE_FILE"
  fi
  
  echo "$hl"
}

if [[ "$status_only" == "true" ]]; then
  echo "Current: $current_version"
  echo "Latest:  $latest_version (tag: $latest_tag)"
  echo "Release: $release_url"
  if [[ -f "$STATE_FILE" ]]; then
    last_notified=$(jq -r '.lastNotifiedVersion // "none"' "$STATE_FILE" 2>/dev/null)
    echo "Last notified: $last_notified"
  fi
  if [[ -f "$CACHE_FILE" ]]; then
    cache_time=$(jq -r '.fetchedAtMs // 0' "$CACHE_FILE" 2>/dev/null)
    cached_count=$(jq '.highlights | keys | length' "$CACHE_FILE" 2>/dev/null)
    echo "Cache: $cached_count highlights cached"
  fi
  exit 0
fi

# Compare versions (semver-style: major.minor.patch)
version_gt() {
  # Returns 0 (true) if $1 > $2
  local IFS='.'
  read -ra v1 <<< "$1"
  read -ra v2 <<< "$2"
  for i in 0 1 2; do
    local n1=${v1[i]:-0}
    local n2=${v2[i]:-0}
    if (( n1 > n2 )); then return 0; fi
    if (( n1 < n2 )); then return 1; fi
  done
  return 1  # Equal
}

# Exit silently if current >= latest
if [[ "$current_version" == "$latest_version" ]]; then
  exit 0
fi

# Exit silently if running ahead of latest (dev build)
if version_gt "$current_version" "$latest_version"; then
  exit 0
fi

# We're behind - check if already notified
if [[ "$force" == "false" && -f "$STATE_FILE" ]]; then
  last_notified=$(jq -r '.lastNotifiedVersion // ""' "$STATE_FILE" 2>/dev/null)
  if [[ "$last_notified" == "$latest_tag" ]]; then
    exit 0
  fi
fi

# Count how many releases behind
versions_behind=0
found_current=false
while IFS= read -r tag; do
  if [[ "${tag#v}" == "$current_version" ]]; then
    found_current=true
    break
  fi
  ((versions_behind++))
done <<< "$(echo "$releases_json" | jq -r '.[].tag_name')"

if [[ "$found_current" == "false" ]]; then
  versions_behind="several"
fi

# Build notification message
cat <<EOF
🔄 **Clawdbot Update Available!**

Current: \`$current_version\`
Latest:  \`$latest_version\`
EOF

if [[ "$versions_behind" != "0" && "$versions_behind" != "1" ]]; then
  echo ""
  echo "_($versions_behind versions behind)_"
fi

if [[ "$all_highlights" == "true" ]]; then
  echo ""
  echo "**Highlights from all missed releases:**"
  
  echo "$releases_json" | jq -c '.[]' 2>/dev/null | while read -r release; do
    tag=$(echo "$release" | jq -r '.tag_name')
    body=$(echo "$release" | jq -r '.body // ""')
    tag_version="${tag#v}"
    
    if [[ "$tag_version" == "$current_version" ]]; then
      break
    fi
    
    hl=$(get_highlights "$tag" "$body")
    if [[ -n "$hl" && "$hl" != "null" ]]; then
      echo ""
      echo "📦 **$tag**"
      echo "$hl"
    fi
  done
else
  release_body=$(echo "$releases_json" | jq -r '.[0].body // empty')
  if [[ -n "$release_body" ]]; then
    highlights=$(get_highlights "$latest_tag" "$release_body")
    if [[ -n "$highlights" ]]; then
      # Truncate if too long
      if [[ ${#highlights} -gt 500 ]]; then
        highlights="${highlights:0:500}..."
      fi
      cat <<EOF

**Highlights:**
$highlights
EOF
    fi
  fi
fi

echo ""
echo "🔗 $release_url"
echo ""

# Show appropriate update command
if [[ -d "$CLAWDBOT_DIR/.git" ]]; then
  echo "To update: \`cd $CLAWDBOT_DIR && git pull && pnpm install && pnpm build\`"
else
  echo "To update: \`npm update -g clawdbot\`"
fi

# Save state
now_ms=$(date +%s)000
jq -n --arg v "$latest_tag" --arg t "$now_ms" \
  '{lastNotifiedVersion: $v, lastCheckMs: ($t | tonumber)}' > "$STATE_FILE"
