#!/bin/bash
# install.sh — Set up amygdala-memory for OpenClaw
# Usage: ./install.sh [--with-cron]

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🎭 Installing amygdala-memory..."
echo ""

# 1. Create memory directory if needed
mkdir -p "$WORKSPACE/memory"

# 2. Initialize emotional-state.json if it doesn't exist
STATE_FILE="$WORKSPACE/memory/emotional-state.json"
if [ ! -f "$STATE_FILE" ]; then
  echo "Creating initial emotional state..."
  cat > "$STATE_FILE" << 'EOF'
{
  "version": "1.0",
  "lastUpdated": "",
  "dimensions": {
    "valence": 0.1,
    "arousal": 0.3,
    "connection": 0.4,
    "curiosity": 0.5,
    "energy": 0.5
  },
  "baseline": {
    "valence": 0.1,
    "arousal": 0.3,
    "connection": 0.4,
    "curiosity": 0.5,
    "energy": 0.5
  },
  "recentEmotions": []
}
EOF
  echo "✅ Created $STATE_FILE"
else
  echo "✅ State file already exists"
fi

# 3. Make scripts executable
chmod +x "$SKILL_DIR/scripts/"*.sh
echo "✅ Scripts are executable"

# 4. Generate initial AMYGDALA_STATE.md
"$SKILL_DIR/scripts/sync-state.sh"

# 5. Set up cron if requested
if [ "$1" = "--with-cron" ]; then
  echo ""
  echo "Setting up cron job for emotional decay..."
  
  # Check if cron job already exists
  CRON_CMD="$SKILL_DIR/scripts/decay-emotion.sh"
  if crontab -l 2>/dev/null | grep -q "decay-emotion.sh"; then
    echo "✅ Cron job already exists"
  else
    # Add cron job (every 6 hours)
    (crontab -l 2>/dev/null; echo "0 */6 * * * $CRON_CMD >/dev/null 2>&1") | crontab -
    echo "✅ Added cron job: every 6 hours"
  fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎭 amygdala-memory installed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Files created:"
echo "  • $STATE_FILE"
echo "  • $WORKSPACE/AMYGDALA_STATE.md (auto-injected)"
echo ""
echo "Usage:"
echo "  # Check your emotional state"
echo "  $SKILL_DIR/scripts/load-emotion.sh"
echo ""
echo "  # Log an emotion"
echo "  $SKILL_DIR/scripts/update-state.sh --emotion joy --trigger \"reason\""
echo ""
echo "  # Manually sync state (happens automatically with decay)"
echo "  $SKILL_DIR/scripts/sync-state.sh"
echo ""

if [ "$1" != "--with-cron" ]; then
  echo "TIP: Run with --with-cron to set up automatic decay"
  echo "  ./install.sh --with-cron"
  echo ""
fi

echo "Add to your AGENTS.md 'Every Session' checklist:"
echo "  - Load emotional state: run scripts/load-emotion.sh"
echo ""
echo "Done! 🎭"
