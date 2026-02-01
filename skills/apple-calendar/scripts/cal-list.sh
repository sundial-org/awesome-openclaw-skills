#!/bin/bash
# List all calendars with their properties
# Usage: cal-list.sh

osascript <<'EOF'
tell application "Calendar"
    set calNames to name of every calendar
    set calWritable to writable of every calendar
    set output to ""
    repeat with i from 1 to count of calNames
        set calName to item i of calNames
        set isWritable to item i of calWritable
        if isWritable then
            set writeStatus to "writable"
        else
            set writeStatus to "read-only"
        end if
        set output to output & calName & " | " & writeStatus & linefeed
    end repeat
    return output
end tell
EOF
