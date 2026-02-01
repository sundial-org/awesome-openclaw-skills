#!/usr/bin/env bash
# memory-pipeline setup — detect environment, check deps, run first pipeline
set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
RESET='\033[0m'

info()  { echo -e "${BOLD}→${RESET} $*"; }
ok()    { echo -e "${GREEN}✔${RESET} $*"; }
warn()  { echo -e "${YELLOW}⚠${RESET} $*"; }
fail()  { echo -e "${RED}✖${RESET} $*"; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "\n${BOLD}Memory Pipeline + Performance Routine${RESET}"
echo -e "Setup & First Run\n"

# ─── Step 1: Detect workspace ───
info "Detecting workspace..."

WORKSPACE=""
if [ -n "${CLAWDBOT_WORKSPACE:-}" ]; then
  WORKSPACE="$CLAWDBOT_WORKSPACE"
elif [ -f "./SOUL.md" ] || [ -f "./AGENTS.md" ]; then
  WORKSPACE="$(pwd)"
elif [ -f "$HOME/.clawdbot/workspace/SOUL.md" ] || [ -f "$HOME/.clawdbot/workspace/AGENTS.md" ]; then
  WORKSPACE="$HOME/.clawdbot/workspace"
elif [ -f "$HOME/clawd/SOUL.md" ] || [ -f "$HOME/clawd/AGENTS.md" ]; then
  WORKSPACE="$HOME/clawd"
fi

if [ -z "$WORKSPACE" ]; then
  fail "Could not detect workspace."
  echo "  Set CLAWDBOT_WORKSPACE or run from your workspace directory."
  echo "  Example: CLAWDBOT_WORKSPACE=~/my-workspace bash $0"
  exit 1
fi

ok "Workspace: $WORKSPACE"

# ─── Step 2: Check Python ───
info "Checking Python..."

PYTHON=""
if command -v python3 &>/dev/null; then
  PYTHON="python3"
elif command -v python &>/dev/null; then
  PYTHON="python"
fi

if [ -z "$PYTHON" ]; then
  fail "Python 3 not found. Install it first."
  exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1)
ok "Found $PY_VERSION"

# ─── Step 3: Check LLM API key ───
info "Checking for LLM API key..."

LLM_PROVIDER=""

# Check environment variables
if [ -n "${OPENAI_API_KEY:-}" ]; then
  LLM_PROVIDER="OpenAI (env)"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  LLM_PROVIDER="Anthropic (env)"
elif [ -n "${GEMINI_API_KEY:-}" ]; then
  LLM_PROVIDER="Gemini (env)"
# Check config files
elif [ -f "$HOME/.config/openai/api_key" ] && [ -s "$HOME/.config/openai/api_key" ]; then
  LLM_PROVIDER="OpenAI (config file)"
elif [ -f "$HOME/.config/anthropic/api_key" ] && [ -s "$HOME/.config/anthropic/api_key" ]; then
  LLM_PROVIDER="Anthropic (config file)"
elif [ -f "$HOME/.config/gemini/api_key" ] && [ -s "$HOME/.config/gemini/api_key" ]; then
  LLM_PROVIDER="Gemini (config file)"
fi

if [ -z "$LLM_PROVIDER" ]; then
  fail "No LLM API key found."
  echo ""
  echo "  Set one of these environment variables:"
  echo "    export OPENAI_API_KEY='sk-...'"
  echo "    export ANTHROPIC_API_KEY='sk-ant-...'"
  echo "    export GEMINI_API_KEY='AI...'"
  echo ""
  echo "  Or save to a config file:"
  echo "    mkdir -p ~/.config/openai && echo 'sk-...' > ~/.config/openai/api_key"
  echo ""
  exit 1
fi

ok "Using $LLM_PROVIDER"

# ─── Step 4: Create memory directory ───
info "Setting up memory directory..."

mkdir -p "$WORKSPACE/memory"
ok "memory/ directory ready"

# ─── Step 5: Check for source material ───
info "Checking for source material..."

HAS_SOURCES=false
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null || echo "")

if [ -f "$WORKSPACE/memory/$TODAY.md" ]; then
  ok "Found today's notes: memory/$TODAY.md"
  HAS_SOURCES=true
elif [ -n "$YESTERDAY" ] && [ -f "$WORKSPACE/memory/$YESTERDAY.md" ]; then
  ok "Found yesterday's notes: memory/$YESTERDAY.md"
  HAS_SOURCES=true
elif [ -f "$WORKSPACE/MEMORY.md" ]; then
  ok "Found MEMORY.md"
  HAS_SOURCES=true
fi

# Check for session transcripts
TRANSCRIPT_DIR="$HOME/.clawdbot/agents/main/sessions"
if [ -d "$TRANSCRIPT_DIR" ] && [ "$(ls -A "$TRANSCRIPT_DIR" 2>/dev/null)" ]; then
  TRANSCRIPT_COUNT=$(ls "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | wc -l)
  if [ "$TRANSCRIPT_COUNT" -gt 0 ]; then
    ok "Found $TRANSCRIPT_COUNT session transcript(s)"
    HAS_SOURCES=true
  fi
fi

if [ "$HAS_SOURCES" = false ]; then
  warn "No daily notes or transcripts found yet."
  echo "  The pipeline needs something to extract from."
  echo "  Create a daily note first:"
  echo "    echo '# $(date +%Y-%m-%d)' > $WORKSPACE/memory/$TODAY.md"
  echo "    echo '- Started using memory-pipeline' >> $WORKSPACE/memory/$TODAY.md"
  echo ""
  
  # Create a starter note so the pipeline has something
  read -r -p "  Create a starter note now? [Y/n] " REPLY
  REPLY=${REPLY:-Y}
  if [[ "$REPLY" =~ ^[Yy] ]]; then
    cat > "$WORKSPACE/memory/$TODAY.md" << EOF
# $TODAY

## Setup
- Installed memory-pipeline skill
- Running first extraction pipeline
EOF
    ok "Created memory/$TODAY.md"
    HAS_SOURCES=true
  fi
fi

# ─── Step 6: Run the pipeline ───
if [ "$HAS_SOURCES" = true ]; then
  echo ""
  info "Running memory pipeline..."
  echo ""

  # Stage 1: Extract
  info "Stage 1/3: Extracting facts..."
  if CLAWDBOT_WORKSPACE="$WORKSPACE" $PYTHON "$SCRIPT_DIR/memory-extract.py" 2>&1; then
    ok "Extraction complete"
  else
    warn "Extraction had issues (may be normal on first run with minimal notes)"
  fi

  echo ""

  # Stage 2: Link
  info "Stage 2/3: Building knowledge graph..."
  if CLAWDBOT_WORKSPACE="$WORKSPACE" $PYTHON "$SCRIPT_DIR/memory-link.py" 2>&1; then
    ok "Knowledge graph built"
  else
    warn "Linking had issues (needs extracted facts to work with)"
  fi

  echo ""

  # Stage 3: Briefing
  info "Stage 3/3: Generating briefing..."
  if CLAWDBOT_WORKSPACE="$WORKSPACE" $PYTHON "$SCRIPT_DIR/memory-briefing.py" 2>&1; then
    ok "Briefing generated"
  else
    warn "Briefing generation had issues"
  fi
else
  warn "Skipping pipeline run — no source material yet."
fi

# ─── Summary ───
echo ""
echo -e "${BOLD}─── Setup Complete ───${RESET}"
echo ""

# Check what was created
[ -f "$WORKSPACE/memory/extracted.jsonl" ] && ok "memory/extracted.jsonl — extracted facts"
[ -f "$WORKSPACE/memory/knowledge-graph.json" ] && ok "memory/knowledge-graph.json — knowledge graph"
[ -f "$WORKSPACE/memory/knowledge-summary.md" ] && ok "memory/knowledge-summary.md — graph summary"
[ -f "$WORKSPACE/BRIEFING.md" ] && ok "BRIEFING.md — daily briefing"

echo ""
echo -e "${BOLD}Next steps:${RESET}"
echo ""
echo "  1. Start a new OpenClaw session so it picks up the skill"
echo ""
echo "  2. Add to your HEARTBEAT.md for daily automation:"
echo "     python3 skills/memory-pipeline/scripts/memory-extract.py"
echo "     python3 skills/memory-pipeline/scripts/memory-link.py"  
echo "     python3 skills/memory-pipeline/scripts/memory-briefing.py"
echo ""
echo "  3. Write daily notes in memory/YYYY-MM-DD.md — the pipeline"
echo "     extracts facts, builds connections, and generates briefings"
echo "     from whatever you write there."
echo ""
echo "  4. The performance routine hooks (pre-game briefing, tool"
echo "     discipline, output compression, after-action review) will"
echo "     activate automatically once enabled in your OpenClaw config."
echo ""
echo -e "${GREEN}You're all set. Happy remembering.${RESET} ⚡"
