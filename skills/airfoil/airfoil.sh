#!/bin/bash
# Airfoil AirPlay Speaker Control
# Uses AppleScript via osascript
# Author: Andy Steinberger (with help from his Clawdbot Owen the Frog 🐸)

set -e

CMD="${1:-help}"
SPEAKER="$2"
VALUE="$3"

case "$CMD" in
    list)
        # List all available speakers
        osascript -e 'tell application "Airfoil" to get name of every speaker'
        ;;
    
    connect)
        if [[ -z "$SPEAKER" ]]; then
            echo "Usage: $0 connect <speaker>" >&2
            exit 1
        fi
        osascript -e "tell application \"Airfoil\" to connect to (first speaker whose name is \"$SPEAKER\")"
        echo "Connected: $SPEAKER"
        ;;
    
    disconnect)
        if [[ -z "$SPEAKER" ]]; then
            echo "Usage: $0 disconnect <speaker>" >&2
            exit 1
        fi
        osascript -e "tell application \"Airfoil\" to disconnect from (first speaker whose name is \"$SPEAKER\")"
        echo "Disconnected: $SPEAKER"
        ;;
    
    volume)
        if [[ -z "$SPEAKER" ]] || [[ -z "$VALUE" ]]; then
            echo "Usage: $0 volume <speaker> <0-100>" >&2
            exit 1
        fi
        # Convert 0-100 to 0.0-1.0 for Airfoil's internal scale
        VOL=$(echo "scale=2; $VALUE / 100" | bc)
        osascript -e "tell application \"Airfoil\" to set (volume of (first speaker whose name is \"$SPEAKER\")) to $VOL"
        echo "Volume $SPEAKER: $VALUE%"
        ;;
    
    status)
        # Show connected speakers with their volume levels
        osascript <<'EOF'
tell application "Airfoil"
    set output to ""
    repeat with s in (every speaker whose connected is true)
        set speakerName to name of s
        set speakerVol to volume of s
        set volPercent to round (speakerVol * 100)
        set output to output & speakerName & ": " & volPercent & "%" & linefeed
    end repeat
    if output is "" then
        return "No speakers connected"
    else
        return text 1 thru -2 of output
    end if
end tell
EOF
        ;;
    
    help|*)
        echo "Airfoil Speaker Control 🔊"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  list                     List all available speakers"
        echo "  connect <speaker>        Connect to speaker"
        echo "  disconnect <speaker>     Disconnect from speaker"
        echo "  volume <speaker> <0-100> Set speaker volume"
        echo "  status                   Show connected speakers with volume"
        echo ""
        echo "Author: Andy Steinberger (with help from Owen the Frog 🐸)"
        ;;
esac
