#!/usr/bin/env bash
# Price Alerts Cron Job (Lobster Workflow)
# Schedule: 2:00 PM PT / 5:00 PM ET (1 hour after market close)
#
# Checks price alerts against current prices including after-hours.
# Sends triggered alerts and watchlist status to WhatsApp/Telegram.

set -e

export SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FINANCE_NEWS_TARGET="${FINANCE_NEWS_TARGET:-120363421796203667@g.us}"
export FINANCE_NEWS_CHANNEL="${FINANCE_NEWS_CHANNEL:-whatsapp}"

echo "[$(date)] Checking price alerts via Lobster..."

lobster run --file "$SKILL_DIR/workflows/alerts-cron.yaml" \
  --args-json '{"lang":"en"}'

echo "[$(date)] Price alerts check complete."
