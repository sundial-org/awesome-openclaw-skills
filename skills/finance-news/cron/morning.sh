#!/usr/bin/env bash
# Morning Briefing Cron Job (Lobster Workflow)
# Schedule: 6:30 AM PT (US Market Open at 9:30 AM ET)
#
# Uses Lobster workflow to generate and send briefing directly,
# bypassing LLM agent reformatting that truncates output.

set -e

export SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FINANCE_NEWS_TARGET="${FINANCE_NEWS_TARGET:-120363421796203667@g.us}"
export FINANCE_NEWS_CHANNEL="${FINANCE_NEWS_CHANNEL:-whatsapp}"

echo "[$(date)] Starting morning briefing via Lobster..."

lobster run --file "$SKILL_DIR/workflows/briefing-cron.yaml" \
  --args-json '{"time":"morning","lang":"de"}'

echo "[$(date)] Morning briefing complete."
