#!/bin/bash
# TuriX-CUA Helper Script for Clawdbot
# Supports dynamic task injection, resume, skills system, and planning

set -e

# ---------- Configuration ----------
PROJECT_DIR="your_dir/TuriX-CUA"
CONFIG_FILE="$PROJECT_DIR/examples/config.json"
CONDA_PATH="/opt/anaconda3/bin/conda"
ENV_NAME="mlx_env1"

export PATH="/usr/sbin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---------- Help ----------
show_help() {
    cat << EOF
Usage: run_turix.sh [OPTIONS] [TASK]

OPTIONS:
    -r, --resume ID     Resume task with agent_id
    -c, --config FILE   Use custom config
    -h, --help          Show help
    --no-plan           Disable planning (use_skills also disabled)
    --enable-skills     Enable skills (requires --enable-plan)
    --dry-run           Show command without running

EXAMPLES:
    run_turix.sh "Open Chrome go to github.com"
    run_turix.sh --enable-skills --resume my-task "Continue task"
EOF
}

# ---------- Parse Arguments ----------
RESUME_ID=""
CUSTOM_CONFIG=""
DRY_RUN=false
USE_PLAN=true
USE_SKILLS=true

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--resume)
            RESUME_ID="$2"
            shift 2
            ;;
        -c|--config)
            CUSTOM_CONFIG="$2"
            shift 2
            ;;
        --no-plan)
            USE_PLAN=false
            USE_SKILLS=false
            shift
            ;;
        --enable-skills)
            USE_SKILLS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            log_error "Unknown option: $1"
            exit 1
            ;;
        *)
            # Remaining arguments are the task description
            break
            ;;
    esac
done

# ---------- Validation ----------
if [[ -z "$RESUME_ID" && $# -eq 0 ]]; then
    log_error "Task or --resume required"
    show_help
    exit 1
fi

if [[ -n "$CUSTOM_CONFIG" && ! -f "$CUSTOM_CONFIG" ]]; then
    log_error "Config not found: $CUSTOM_CONFIG"
    exit 1
fi

[[ -n "$CUSTOM_CONFIG" ]] && CONFIG_FILE="$CUSTOM_CONFIG"

if [[ ! -d "$PROJECT_DIR" ]]; then
    log_error "TuriX project not found: $PROJECT_DIR"
    exit 1
fi

# ---------- Update Config (Skills-Compatible) ----------
# Use Python to safely update JSON (handles UTF-8 correctly)
update_config() {
    # Read task from args or stdin
    local task_arg="$*"
    local use_plan="$USE_PLAN"
    local use_skills="$USE_SKILLS"
    local resume_id="$RESUME_ID"

    python3 << PYEOF
import json
import os
import sys

config_path = '$CONFIG_FILE'

# Read existing config
with open(config_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update task from environment (safer for UTF-8)
task_arg = '''$task_arg'''
if task_arg:
    data['agent']['task'] = task_arg

# Update resume settings
resume_id = '''$resume_id'''
if resume_id:
    data['agent']['resume'] = True
    data['agent']['agent_id'] = resume_id

# Update feature flags
use_plan = '''$use_plan'''
use_skills = '''$use_skills'''

data['agent']['use_plan'] = (use_plan == 'True')
data['agent']['use_skills'] = (use_skills == 'True')

# Ensure skills settings exist
if data['agent']['use_skills']:
    if not data['agent'].get('skills_max_chars'):
        data['agent']['skills_max_chars'] = 4000

# Write back with UTF-8 encoding
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('Config updated successfully')
PYEOF
}

# ---------- Pre-flight Checks ----------
preflight_checks() {
    log_info "Running pre-flight checks..."

    # Conda env check
    if ! "$CONDA_PATH" env list | grep -q "$ENV_NAME"; then
        log_warn "Conda env '$ENV_NAME' not found"
    fi

    # Config check
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "Config not found: $CONFIG_FILE"
        exit 1
    fi

    # Screen recording permission check
    if ! python3 -c "
import ctypes
CoreGraphics = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
exit(0 if CoreGraphics.CGPreflightScreenCaptureAccess() else 1)
" 2>/dev/null; then
        log_warn "Screen recording permission may be missing"
        log_warn "Grant in System Settings → Privacy & Security → Screen Recording"
    fi

    log_info "Pre-flight complete"
}

# ---------- Main ----------
main() {
    cd "$PROJECT_DIR"
    log_info "TuriX CUA"
    log_info "Project: $PROJECT_DIR"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN]"
        echo "  Task: ${*:-(resume) ${RESUME_ID}}"
        echo "  Plan: $USE_PLAN"
        echo "  Skills: $USE_SKILLS"
        echo "  Command: $CONDA_PATH run -n $ENV_NAME python examples/main.py"
        exit 0
    fi

    update_config
    preflight_checks

    log_info "Starting TuriX..."
    log_info "Press Cmd+Shift+2 to force stop"

    "$CONDA_PATH" run -n "$ENV_NAME" python examples/main.py
}

main