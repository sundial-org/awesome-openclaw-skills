#!/bin/bash
# Delete a calendar event by UID
# Usage: cal-delete.sh <event-uid> [calendar_name]
# If calendar not specified, searches all calendars

EVENT_UID="${1:-}"
CALENDAR_NAME="${2:-}"

if [ -z "$EVENT_UID" ]; then
    echo "Usage: cal-delete.sh <event-uid> [calendar_name]"
    exit 1
fi

osascript - "$EVENT_UID" "$CALENDAR_NAME" <<'EOF'
on run argv
    set eventUID to item 1 of argv as string
    set calendarName to item 2 of argv as string
    
    tell application "Calendar"
        if calendarName is not "" then
            try
                set cals to {calendar calendarName}
            on error
                return "Error: Calendar '" & calendarName & "' not found"
            end try
        else
            set cals to calendars
        end if
        
        repeat with cal in cals
            try
                set matchingEvents to (every event of cal whose uid is eventUID)
                if (count of matchingEvents) > 0 then
                    set e to item 1 of matchingEvents
                    set eventName to summary of e
                    
                    if not (writable of cal) then
                        return "Error: Calendar '" & (name of cal) & "' is read-only"
                    end if
                    
                    delete e
                    return "Deleted event: " & eventName & " (" & eventUID & ")"
                end if
            end try
        end repeat
        
        return "Error: Event with UID '" & eventUID & "' not found"
    end tell
end run
EOF
