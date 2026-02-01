#!/usr/bin/env bash
# Context Compressor - Automated context management for Clawdbot
# Detects when context limits approach, compresses history, transfers to new session

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPRESSED_DIR="$SCRIPT_DIR/../memory/compressed"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# Default configuration
DEFAULT_THRESHOLD=80
DEFAULT_DEPTH="balanced"
QUIET_HOURS=""

# Colors for output
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
NC=$'\033[0m'

# Ensure compressed memory directory exists
mkdir -p "$COMPRESSED_DIR"

# Load configuration
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        THRESHOLD=$(jq -r '.threshold // env.DEFAULT_THRESHOLD' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_THRESHOLD")
        DEPTH=$(jq -r '.depth // env.DEFAULT_DEPTH' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_DEPTH")
        QUIET_HOURS=$(jq -r '.quiet_hours // ""' "$CONFIG_FILE" 2>/dev/null || echo "")
    else
        THRESHOLD=$DEFAULT_THRESHOLD
        DEPTH=$DEFAULT_DEPTH
        QUIET_HOURS=""
    fi
}

# Save configuration
save_config() {
    load_config
    cat > "$CONFIG_FILE" <<EOF
{
  "threshold": $THRESHOLD,
  "depth": "$DEPTH",
  "quiet_hours": "$QUIET_HOURS",
  "last_compression": "$(date -Iseconds 2>/dev/null || echo "")",
  "total_compressions": $((TOTAL_COMPRESSIONS + 1))
}
EOF
}

# Get current session info (simulated - adapt to actual Clawdbot metrics)
get_session_info() {
    # This would integrate with Clawdbot's session API
    # For now, returns estimated values
    SESSION_ID=$(cat /proc/self/cgroup 2>/dev/null | head -1 | md5sum | cut -c1-8 || echo "unknown")
    CURRENT_TOKENS=${CURRENT_TOKENS:-50000}
    MAX_TOKENS=${MAX_TOKENS:-100000}
}

# Calculate context usage percentage
calculate_usage() {
    get_session_info
    USAGE=$((CURRENT_TOKENS * 100 / MAX_TOKENS))
    echo "$USAGE"
}

# Check if we're in quiet hours
in_quiet_hours() {
    if [[ -z "$QUIET_HOURS" ]]; then
        return 1
    fi
    
    local current_hour=$(date +%H)
    local start=$(echo "$QUIET_HOURS" | cut -d'-' -f1)
    local end=$(echo "$QUIET_HOURS" | cut -d'-' -f2)
    
    if [[ "$current_hour" -ge "$start" ]] && [[ "$current_hour" -lt "$end" ]]; then
        return 0
    fi
    return 1
}

# Extract key decisions from conversation
extract_decisions() {
    local transcript="$1"
    local output="$2"
    
    # Look for decision markers
    grep -i "decided\|decision\|chose\|chose to\|we'll\|we're going\|let's go with\|i'll use\|using" "$transcript" 2>/dev/null | \
        grep -v "let me know\|feel free to\|you might want" | \
        head -20 > "$output.decisions.tmp" || true
    
    if [[ -s "$output.decisions.tmp" ]]; then
        echo -e "\n## Key Decisions" >> "$output"
        cat "$output.decisions.tmp" >> "$output"
        rm "$output.decisions.tmp"
    fi
}

# Extract file modifications
extract_files() {
    local transcript="$1"
    local output="$2"
    
    # Look for file operations
    grep -E "(created|modified|edited|updated|deleted|changed)" "$transcript" 2>/dev/null | \
        grep -E "\.(tsx|ts|jsx|js|py|md|json|yaml|yml|css|html|svelte)$" | \
        head -15 > "$output.files.tmp" || true
    
    if [[ -s "$output.files.tmp" ]]; then
        echo -e "\n## File Modifications" >> "$output"
        cat "$output.files.tmp" >> "$output"
        rm "$output.files.tmp"
    fi
}

# Extract code snippets
extract_code() {
    local transcript="$1"
    local output="$2"
    
    # Extract code blocks (simple heuristic)
    grep -A5 '```' "$transcript" 2>/dev/null | head -100 > "$output.code.tmp" || true
    
    if [[ -s "$output.code.tmp" ]]; then
        echo -e "\n## Code Snippets" >> "$output"
        cat "$output.code.tmp" >> "$output"
        rm "$output.code.tmp"
    fi
}

# Extract pending tasks
extract_todos() {
    local transcript="$1"
    local output="$2"
    
    grep -i "todo\|to-do\|pending\|still need\|remaining\|next step" "$transcript" 2>/dev/null | \
        head -10 > "$output.todos.tmp" || true
    
    if [[ -s "$output.todos.tmp" ]]; then
        echo -e "\n## Pending Tasks" >> "$output"
        cat "$output.todos.tmp" >> "$output"
        rm "$output.todos.tmp"
    fi
}

# Generate executive summary
generate_summary() {
    local transcript="$1"
    local session_id="$2"
    local output="$3"
    
    local timestamp=$(date -Iseconds 2>/dev/null || date)
    
    cat > "$output" <<EOF
# Session Summary - $session_id
Generated: $timestamp

## Executive Summary
Automated context compression summary for session handoff.

## Session Context
EOF
    
    # Add current working directory and key files
    echo "- Working Directory: $(pwd)" >> "$output"
    echo "- Git Status:" >> "$output"
    git status --short 2>/dev/null | head -10 >> "$output" || echo "  (Not a git repository)" >> "$output"
    
    # Extract key information
    extract_decisions "$transcript" "$output"
    extract_files "$transcript" "$output"
    extract_code "$transcript" "$output"
    extract_todos "$transcript" "$output"
    
    # Add recent git commits as timeline
    echo -e "\n## Recent Activity" >> "$output"
    git log --oneline -10 2>/dev/null >> "$output" || echo "  No git history" >> "$output"
    
    echo -e "\n## Continuation Notes" >> "$output"
    echo "This summary was automatically generated to preserve context across session handoff." >> "$output"
    echo "For full details, see: $COMPRESSED_DIR/$session_id.transcript.md" >> "$output"
}

# Main compression function
compress_session() {
    echo -e "${YELLOW}🧠 Starting context compression...${NC}"
    
    local session_id=$(date +%Y%m%d-%H%M%S)
    local transcript_file="$COMPRESSED_DIR/$session_id.transcript.md"
    local summary_file="$COMPRESSED_DIR/$session_id.summary.md"
    
    # In a real implementation, this would:
    # 1. Fetch current session transcript via Clawdbot API
    # 2. Analyze and score conversation turns
    # 3. Preserve high-signal content, summarize low-signal
    # 4. Generate handoff package
    
    # For now, create placeholder indicating skill is ready
    cat > "$transcript_file" <<EOF
# Session Transcript - $session_id
Timestamp: $(date -Iseconds)

[This is a placeholder - in production, this would contain the actual session transcript]

## Session Statistics
- Context Usage: ${USAGE:-0}%
- Threshold: ${THRESHOLD}%
- Compression Depth: ${DEPTH}
EOF
    
    # Generate summary
    generate_summary "$transcript_file" "$session_id" "$summary_file"
    
    echo -e "${GREEN}✅ Compression complete!${NC}"
    echo "  - Transcript: $transcript_file"
    echo "  - Summary: $summary_file"
    
    # Trigger session handoff (in production)
    # handoff_to_new_session "$session_id"
    
    return 0
}

# Status command
cmd_status() {
    load_config
    
    echo "📊 Context Compressor Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Threshold: ${THRESHOLD}%"
    echo "  Depth: ${DEPTH}"
    echo "  Quiet Hours: ${QUIET_HOURS:-None}"
    
    local usage=$(calculate_usage)
    echo "  Current Usage: ${usage}%"
    
    if [[ -d "$COMPRESSED_DIR" ]]; then
        local compressions=$(ls -1 "$COMPRESSED_DIR"/*.summary.md 2>/dev/null | wc -l)
        echo "  Total Compressions: $compressions"
    fi
    
    if [[ "$usage" -ge "$THRESHOLD" ]]; then
        echo -e "\n${YELLOW}⚠️  Context usage above threshold!${NC}"
        echo "  Run 'context-compressor compress' to compress and reset."
    else
        echo -e "\n${GREEN}✓ Context usage normal${NC}"
    fi
}

# Set threshold
cmd_set_threshold() {
    local new_threshold="${1:-80}"
    
    if [[ "$new_threshold" -lt 50 ]] || [[ "$new_threshold" -gt 99 ]]; then
        echo -e "${RED}Error: Threshold must be between 50 and 99${NC}"
        exit 1
    fi
    
    THRESHOLD=$new_threshold
    save_config
    echo -e "${GREEN}✅ Threshold set to ${THRESHOLD}%${NC}"
}

# Set depth
cmd_set_depth() {
    local new_depth="${1:-balanced}"
    
    if [[ "$new_depth" != "brief" ]] && [[ "$new_depth" != "balanced" ]] && [[ "$new_depth" != "comprehensive" ]]; then
        echo -e "${RED}Error: Depth must be brief, balanced, or comprehensive${NC}"
        exit 1
    fi
    
    DEPTH=$new_depth
    save_config
    echo -e "${GREEN}✅ Depth set to ${DEPTH}${NC}"
}

# Set quiet hours
cmd_set_quiet_hours() {
    local range="${1:-}"
    
    if [[ -z "$range" ]]; then
        QUIET_HOURS=""
        echo -e "${GREEN}✅ Quiet hours disabled${NC}"
    else
        # Validate format HH:00-HH:00
        if ! [[ "$range" =~ ^[0-2][0-9]:00-[0-2][0-9]:00$ ]]; then
            echo -e "${RED}Error: Format must be HH:00-HH:00 (e.g., 23:00-07:00)${NC}"
            exit 1
        fi
        QUIET_HOURS=$range
        echo -e "${GREEN}✅ Quiet hours set to ${QUIET_HOURS}${NC}"
    fi
    
    save_config
}

# Force compression
cmd_compress() {
    load_config
    
    if in_quiet_hours; then
        echo -e "${YELLOW}⏸️  In quiet hours (${QUIET_HOURS}). Compression skipped.${NC}"
        exit 0
    fi
    
    compress_session
}

# Check and compress if needed
cmd_check() {
    load_config
    
    local usage=$(calculate_usage)
    
    echo "Context usage: ${usage}% (threshold: ${THRESHOLD}%)"
    
    if in_quiet_hours; then
        echo "In quiet hours - skipping compression check."
        exit 0
    fi
    
    if [[ "$usage" -ge "$THRESHOLD" ]]; then
        echo -e "${YELLOW}⚠️  Context above threshold. Compressing...${NC}"
        compress_session
    else
        echo -e "${GREEN}✓ Context within limits${NC}"
    fi
}

# Main command routing
case "${1:-status}" in
    status)
        cmd_status
        ;;
    compress)
        cmd_compress
        ;;
    check)
        cmd_check
        ;;
    set-threshold)
        cmd_set_threshold "${2:-}"
        ;;
    set-depth)
        cmd_set_depth "${2:-}"
        ;;
    set-quiet-hours)
        cmd_set_quiet_hours "${2:-}"
        ;;
    *)
        echo "Context Compressor - Automated context management"
        echo ""
        echo "Usage: $0 <command> [arguments]"
        echo ""
        echo "Commands:"
        echo "  status              Show current status and configuration"
        echo "  compress            Force compression and session handoff"
        echo "  check               Check and compress if needed"
        echo "  set-threshold N     Set compression threshold (50-99, default: 80)"
        echo "  set-depth LEVEL     Set summarization depth (brief/balanced/comprehensive)"
        echo "  set-quiet-hours HH  Set quiet hours range (e.g., '23:00-07:00')"
        exit 1
        ;;
esac
