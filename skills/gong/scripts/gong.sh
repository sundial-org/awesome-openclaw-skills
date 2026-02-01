#!/bin/bash
# Gong CLI - Helper script for common Gong API operations
# Usage: gong.sh <command> [args]

set -e

CREDS=${GONG_CREDS:-~/.config/gong/credentials.json}

if [ ! -f "$CREDS" ]; then
  echo "Error: Credentials not found at $CREDS"
  echo "Create with: {\"base_url\": \"https://us-XXXXX.api.gong.io\", \"access_key\": \"...\", \"secret_key\": \"...\"}"
  exit 1
fi

BASE=$(jq -r '.base_url' "$CREDS")
AUTH=$(jq -r '"\(.access_key):\(.secret_key)"' "$CREDS" | base64)

cmd=${1:-help}
shift 2>/dev/null || true

api() {
  curl -s "$BASE$1" -H "Authorization: Basic $AUTH" -H "Content-Type: application/json" "${@:2}"
}

case $cmd in
  users)
    api "/v2/users" | jq '[.users[] | {id, email: .emailAddress, name: "\(.firstName) \(.lastName)", active}]'
    ;;

  calls)
    DAYS=${1:-7}
    FROM=$(date -v-${DAYS}d +%Y-%m-%dT00:00:00Z 2>/dev/null || date -d "$DAYS days ago" +%Y-%m-%dT00:00:00Z)
    TO=$(date +%Y-%m-%dT23:59:59Z)
    api "/v2/calls/extensive" -X POST \
      -d "{\"filter\":{\"fromDateTime\":\"$FROM\",\"toDateTime\":\"$TO\"},\"contentSelector\":{}}" | \
      jq '{total:.records.totalRecords, calls:[.calls[]|{id:.metaData.id,title:.metaData.title,started:.metaData.started,duration_min:((.metaData.duration//0)/60|floor),url:.metaData.url}]}'
    ;;

  call)
    [ -z "$1" ] && echo "Usage: gong.sh call <call_id>" && exit 1
    api "/v2/calls/extensive" -X POST \
      -d "{\"filter\":{\"callIds\":[\"$1\"]},\"contentSelector\":{\"exposedFields\":{\"content\":true,\"parties\":true}}}" | \
      jq '.calls[0]'
    ;;

  transcript)
    [ -z "$1" ] && echo "Usage: gong.sh transcript <call_id>" && exit 1
    api "/v2/calls/transcript" -X POST -d "{\"filter\":{\"callIds\":[\"$1\"]}}" | \
      jq -r '.callTranscripts[0].transcript[]? | "\(.speakerName // "Speaker"): \(.sentences[]?.text)"' 2>/dev/null || \
      api "/v2/calls/transcript" -X POST -d "{\"filter\":{\"callIds\":[\"$1\"]}}"
    ;;

  stats)
    DAYS=${1:-30}
    FROM=$(date -v-${DAYS}d +%Y-%m-%dT00:00:00Z 2>/dev/null || date -d "$DAYS days ago" +%Y-%m-%dT00:00:00Z)
    TO=$(date +%Y-%m-%dT23:59:59Z)
    api "/v2/stats/activity/aggregate" -X POST \
      -d "{\"filter\":{\"fromDateTime\":\"$FROM\",\"toDateTime\":\"$TO\"}}"
    ;;

  test)
    echo "Testing Gong API connection..."
    RESULT=$(api "/v2/users" | jq '{connected: (.users | length > 0), users: (.users | length)}')
    echo "$RESULT"
    ;;

  help|*)
    cat <<EOF
Gong CLI Helper

Commands:
  users              List all users
  calls [days]       List calls from last N days (default: 7)
  call <id>          Get call details
  transcript <id>    Get call transcript
  stats [days]       Activity stats for last N days (default: 30)
  test               Test API connection

Environment:
  GONG_CREDS         Path to credentials JSON (default: ~/.config/gong/credentials.json)

Examples:
  gong.sh calls 14
  gong.sh transcript 4746011978819076085
  gong.sh stats 7
EOF
    ;;
esac
