#!/usr/bin/env bash
# Weekly Earnings Alert Cron Job (Lobster Workflow)
# Schedule: Sunday 7:00 AM PT (before market week starts)
#
# Sends upcoming week's earnings calendar to WhatsApp/Telegram.
# Shows all portfolio stocks reporting Mon-Fri.

set -e

export SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FINANCE_NEWS_TARGET="${FINANCE_NEWS_TARGET:-120363421796203667@g.us}"
export FINANCE_NEWS_CHANNEL="${FINANCE_NEWS_CHANNEL:-whatsapp}"

echo "[$(date)] Checking next week's earnings via Lobster..."

lobster run --file "$SKILL_DIR/workflows/earnings-weekly-cron.yaml" \
  --args-json '{"lang":"en"}'

echo "[$(date)] Weekly earnings alert complete."
