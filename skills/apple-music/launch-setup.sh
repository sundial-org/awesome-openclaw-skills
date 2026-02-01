#!/bin/bash
# Launch setup.sh in Terminal.app for interactive setup
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

osascript <<APPLESCRIPT
tell application "Terminal"
    activate
    do script "cd '$SKILL_DIR' && ./setup.sh"
end tell
APPLESCRIPT
