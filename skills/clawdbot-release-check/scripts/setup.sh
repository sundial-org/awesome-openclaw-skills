#!/usr/bin/env bash
set -euo pipefail

# Default values
CRON_HOUR="${UPDATE_CHECK_HOUR:-9}"
TELEGRAM_TO="${TELEGRAM_TO:-}"
CHANNEL="${CHANNEL:-telegram}"

usage() {
  cat <<'EOF'
Setup Clawdbot Release Check cron job

Usage: setup.sh [OPTIONS]

Options:
  --hour <0-23>       Hour to run daily check (default: 9)
  --telegram <id>     Telegram user/group ID to notify
  --channel <name>    Channel: telegram|whatsapp|discord (default: telegram)
  --uninstall         Remove the cron job
  -h, --help          Show this help

Examples:
  setup.sh --telegram 88230176              # Daily at 9am to Telegram
  setup.sh --hour 8 --telegram 88230176     # Daily at 8am
  setup.sh --uninstall                      # Remove cron job
EOF
  exit 0
}

uninstall=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hour) CRON_HOUR="$2"; shift 2 ;;
    --telegram) TELEGRAM_TO="$2"; CHANNEL="telegram"; shift 2 ;;
    --channel) CHANNEL="$2"; shift 2 ;;
    --uninstall) uninstall=true; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown: $1"; usage ;;
  esac
done

CRON_FILE="${HOME}/.clawdbot/cron/jobs.json"
JOB_NAME="Clawdbot Release Check"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ "$uninstall" == "true" ]]; then
  if [[ -f "$CRON_FILE" ]]; then
    jq --arg name "$JOB_NAME" '.jobs = [.jobs[] | select(.name != $name)]' "$CRON_FILE" > /tmp/cron-updated.json
    mv /tmp/cron-updated.json "$CRON_FILE"
    echo "✓ Removed '$JOB_NAME' cron job"
  else
    echo "No cron file found"
  fi
  exit 0
fi

if [[ -z "$TELEGRAM_TO" && "$CHANNEL" == "telegram" ]]; then
  echo "Error: --telegram <id> required"
  echo "Run with --help for usage"
  exit 1
fi

# Check if job already exists
if [[ -f "$CRON_FILE" ]] && jq -e --arg name "$JOB_NAME" '.jobs[] | select(.name == $name)' "$CRON_FILE" >/dev/null 2>&1; then
  echo "Job '$JOB_NAME' already exists. Use --uninstall first to replace."
  exit 1
fi

# Ensure cron directory exists
mkdir -p "$(dirname "$CRON_FILE")"

# Create jobs file if it doesn't exist
if [[ ! -f "$CRON_FILE" ]]; then
  echo '{"version":1,"jobs":[]}' > "$CRON_FILE"
fi

# Generate job ID
JOB_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
NOW_MS=$(date +%s)000

# Add the job
jq --arg id "$JOB_ID" \
   --arg name "$JOB_NAME" \
   --arg hour "$CRON_HOUR" \
   --arg channel "$CHANNEL" \
   --arg to "$TELEGRAM_TO" \
   --arg script "$SCRIPT_DIR/check.sh" \
   --argjson now "$NOW_MS" \
   '.jobs += [{
     "id": $id,
     "name": $name,
     "enabled": true,
     "createdAtMs": $now,
     "updatedAtMs": $now,
     "schedule": {
       "kind": "cron",
       "expr": ("0 " + $hour + " * * *")
     },
     "sessionTarget": "isolated",
     "wakeMode": "now",
     "payload": {
       "kind": "agentTurn",
       "message": ("UPDATE_CHECK: Run " + $script + " and if there is output, send it to the user."),
       "deliver": true,
       "channel": $channel,
       "to": $to
     },
     "isolation": {
       "postToMainPrefix": "System"
     },
     "state": {}
   }]' "$CRON_FILE" > /tmp/cron-updated.json

mv /tmp/cron-updated.json "$CRON_FILE"

echo "✓ Added '$JOB_NAME' cron job"
echo "  Schedule: Daily at ${CRON_HOUR}:00"
echo "  Channel: $CHANNEL → $TELEGRAM_TO"
echo ""
echo "Restart gateway to apply: launchctl kickstart -k gui/\$(id -u)/com.clawdis.gateway"
