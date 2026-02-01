#!/bin/bash
# Council Chamber Orchestrator - Persona Aggregation Pattern

TOPIC="$1"
MEMBER_IDS="$2"

if [ -z "$TOPIC" ] || [ -z "$MEMBER_IDS" ]; then
    echo "Usage: chamber-orchestrator.sh <topic> <member-ids>"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🏛️ Convening Council Chamber: $TOPIC"
echo ""

# 1. Memory Bridge
CONTEXT=$("$SCRIPT_DIR/graphiti-bridge.sh" "$TOPIC" 10)

# 2. Load Personas
IDS_SQL=$(echo "$MEMBER_IDS" | sed "s/,/','/g")
PERSONAS=$(sqlite3 ~/.clawdbot/council.db "
SELECT '**' || name || '** (' || role || '):' || char(10) || system_message || char(10)
FROM council_members 
WHERE id IN ('$IDS_SQL')
")

# 3. Chamber Task
CHAMBER_TASK="You are moderating a **Council Meeting**.

📋 Topic: $TOPIC

🏛️ Council Members:
$PERSONAS

🧠 Institutional Memory:
$CONTEXT

📜 Rules:
1. 3-turn deliberation (Initial → Critique → Synthesis)
2. Maintain distinct personas
3. Cross-pollination between members
4. End with Executive Summary

Begin deliberation."

# 4. Create session
SESSION_ID=$(uuidgen 2>/dev/null || echo "council-$(date +%s)")
sqlite3 ~/.clawdbot/council.db "
INSERT INTO council_sessions (id, topic, member_ids, status)
VALUES ('$SESSION_ID', '$TOPIC', '[$MEMBER_IDS]', 'active');
"

echo "✅ Chamber Session: $SESSION_ID"
echo ""
echo "$CHAMBER_TASK"
