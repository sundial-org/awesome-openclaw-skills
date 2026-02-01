#!/usr/bin/env bash
# Earnings Alert Cron Job (Lobster Workflow)
# Schedule: 6:00 AM PT / 9:00 AM ET (30 min before market open)
#
# Sends today's earnings calendar to WhatsApp/Telegram.
# Alerts users about portfolio stocks reporting today.

set -e

export SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FINANCE_NEWS_TARGET="${FINANCE_NEWS_TARGET:-120363421796203667@g.us}"
export FINANCE_NEWS_CHANNEL="${FINANCE_NEWS_CHANNEL:-whatsapp}"

echo "[$(date)] Checking today's earnings via Lobster..."

lobster run --file "$SKILL_DIR/workflows/earnings-cron.yaml" \
  --args-json '{"lang":"en"}'

echo "[$(date)] Earnings alert complete."
