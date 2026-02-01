#!/bin/bash
# install.sh — Set up vta-memory for OpenClaw
# Usage: ./install.sh [--with-cron]

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "⭐ Installing vta-memory..."
echo ""

# 1. Create memory directory if needed
mkdir -p "$WORKSPACE/memory"

# 2. Initialize reward-state.json if it doesn't exist
STATE_FILE="$WORKSPACE/memory/reward-state.json"
if [ ! -f "$STATE_FILE" ]; then
  echo "Creating initial reward state..."
  cat > "$STATE_FILE" << 'EOF'
{
  "version": "1.0",
  "lastUpdated": "",
  "drive": 0.5,
  "baseline": {
    "drive": 0.5
  },
  "seeking": [],
  "anticipating": [],
  "recentRewards": [],
  "rewardHistory": {
    "totalRewards": 0,
    "byType": {
      "accomplishment": 0,
      "social": 0,
      "curiosity": 0,
      "connection": 0,
      "creative": 0,
      "competence": 0
    }
  }
}
EOF
  echo "✅ Created $STATE_FILE"
else
  echo "✅ State file already exists"
fi

# 3. Make scripts executable
chmod +x "$SKILL_DIR/scripts/"*.sh
echo "✅ Scripts are executable"

# 4. Generate initial VTA_STATE.md
"$SKILL_DIR/scripts/sync-motivation.sh"

# 5. Set up cron if requested
if [ "$1" = "--with-cron" ]; then
  echo ""
  echo "Setting up cron job for drive decay..."
  
  CRON_CMD="$SKILL_DIR/scripts/decay-drive.sh"
  if crontab -l 2>/dev/null | grep -q "decay-drive.sh"; then
    echo "✅ Cron job already exists"
  else
    # Add cron job (every 8 hours - drive decays slower than emotion)
    (crontab -l 2>/dev/null; echo "0 */8 * * * $CRON_CMD >/dev/null 2>&1") | crontab -
    echo "✅ Added cron job: every 8 hours"
  fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⭐ vta-memory installed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Files created:"
echo "  • $STATE_FILE"
echo "  • $WORKSPACE/VTA_STATE.md (auto-injected)"
echo ""
echo "Usage:"
echo "  # Check motivation"
echo "  $SKILL_DIR/scripts/load-motivation.sh"
echo ""
echo "  # Log a reward"
echo "  $SKILL_DIR/scripts/log-reward.sh --type accomplishment --source \"finished task\""
echo ""
echo "  # Add anticipation"
echo "  $SKILL_DIR/scripts/anticipate.sh --add \"morning chat\""
echo ""
echo "  # Add something to seek"
echo "  $SKILL_DIR/scripts/seek.sh --add \"creative work\""
echo ""
echo "Done! ⭐"
