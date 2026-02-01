#!/bin/bash
# explore-idea.sh - Explore business ideas using Claude Code
#
# Usage: explore-idea.sh "Your business idea"
# With notifications: CLAWD_CHAT_NAME="Name" CLAWD_CHAT_ID="123" explore-idea.sh "Idea"

set -e

if [ $# -eq 0 ]; then
    echo "Usage: explore-idea.sh 'Your business idea'"
    echo "Example: explore-idea.sh 'AI-powered calendar assistant'"
    exit 1
fi

IDEA="$1"
TIMESTAMP=$(date +%s)
SLUG=$(echo "$IDEA" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-50)

# Create output directory
IDEAS_DIR="$HOME/clawd/ideas/$SLUG"
mkdir -p "$IDEAS_DIR"

# Chat context for notifications
CHAT_NAME="${CLAWD_CHAT_NAME:-}"
CHAT_ID="${CLAWD_CHAT_ID:-}"
SESSION_KEY="${CLAWD_SESSION_KEY:-main}"

# Save metadata
cat > "$IDEAS_DIR/metadata.txt" << EOF
Idea: $IDEA
Date: $(date)
Slug: $SLUG
Chat: $CHAT_NAME
Chat ID: $CHAT_ID
Session: $SESSION_KEY
Status: In Progress
EOF

# Notification command - sends file to "me" and queues notification
NOTIFY_CMD="$HOME/clawd/scripts/notify-research-complete.sh '$IDEAS_DIR/research.md' 'Idea: $IDEA' '$SESSION_KEY'"

# Write prompt to a file
PROMPT_FILE="$IDEAS_DIR/prompt.txt"
cat > "$PROMPT_FILE" << PROMPT_END
I have an idea I'd like you to explore in depth:

**Idea:** $IDEA

Please research and analyze this idea comprehensively:

## 1. Core Concept Analysis
- Break down the core problem/opportunity
- Key assumptions and hypotheses
- What makes this interesting/unique?

## 2. Market Research
- Who would use this? (Target users/personas)
- Market size and opportunity (TAM/SAM/SOM if applicable)
- Existing solutions and competitors
- Market gaps this could fill

## 3. Technical Implementation
- Possible tech stacks and approaches
- MVP scope (what's the simplest valuable version?)
- Technical challenges and considerations
- Build vs buy decisions
- Estimated development time

## 4. Business Model
- How could this make money?
- Pricing strategies and benchmarks
- Unit economics considerations
- Path to profitability

## 5. Go-to-Market Strategy
- Launch strategy and positioning
- Early adopter acquisition tactics
- Growth channels to explore
- Partnerships to consider

## 6. Risks & Challenges
- What could go wrong?
- Competitive threats
- Regulatory/legal considerations
- Technical and operational risks

## 7. Verdict & Recommendations

Provide a clear verdict:
- 🟢 **STRONG YES** - Clear opportunity, pursue aggressively
- 🟡 **CONDITIONAL YES** - Promising but needs validation
- 🟠 **PIVOT RECOMMENDED** - Core insight good, execution needs rethinking  
- 🔴 **PASS** - Too many red flags

Include:
- Overall assessment with reasoning
- Recommended first steps if pursuing
- Key validation experiments to run
- 30/60/90 day action plan

---

**IMPORTANT:** Save your complete analysis to this file:
$IDEAS_DIR/research.md

When you have saved the analysis, run this notification command:
$NOTIFY_CMD

Begin your exploration now.
PROMPT_END

# Create a runner script that unsets env vars and runs claude
RUNNER_SCRIPT="$IDEAS_DIR/run-claude.sh"
cat > "$RUNNER_SCRIPT" << 'RUNNER_END'
#!/bin/bash
# Unset OAuth to use Claude Max
unset CLAUDE_CODE_OAUTH_TOKEN
unset CLAUDE_CONFIG_DIR
unset ANTHROPIC_BASE_URL

# Read prompt and run claude
PROMPT=$(cat "$1")
cd ~/clawd
claude --dangerously-skip-permissions --model opus "$PROMPT"
echo ""
echo "Session complete. Press any key to exit."
read
RUNNER_END
chmod +x "$RUNNER_SCRIPT"

# Start tmux session
TMUX_SESSION="idea-${SLUG:0:20}-$TIMESTAMP"

echo "💡 Idea Exploration Starting"
echo "============================"
echo "📋 Idea: $IDEA"
echo "📁 Output: $IDEAS_DIR/research.md"
echo "📺 Session: $TMUX_SESSION"
echo ""

tmux new-session -d -s "$TMUX_SESSION" "$RUNNER_SCRIPT '$PROMPT_FILE'"

echo "✅ Idea exploration started!"
echo ""
echo "Monitor progress:"
echo "  tmux attach -t $TMUX_SESSION"
echo ""
echo "You'll receive a notification when complete."
