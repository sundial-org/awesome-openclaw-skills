#!/usr/bin/env bash
# Evening Briefing Cron Job (Lobster Workflow)
# Schedule: 1:00 PM PT (US Market Close at 4:00 PM ET)
#
# Uses Lobster workflow to generate and send briefing directly,
# bypassing LLM agent reformatting that truncates output.

set -e

export SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FINANCE_NEWS_TARGET="${FINANCE_NEWS_TARGET:-120363421796203667@g.us}"
export FINANCE_NEWS_CHANNEL="${FINANCE_NEWS_CHANNEL:-whatsapp}"

echo "[$(date)] Starting evening briefing via Lobster..."

lobster run --file "$SKILL_DIR/workflows/briefing-cron.yaml" \
  --args-json '{"time":"evening","lang":"de"}'

echo "[$(date)] Evening briefing complete."
