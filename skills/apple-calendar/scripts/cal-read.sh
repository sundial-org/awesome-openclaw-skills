#!/bin/bash
# Read a single event by UID
# Usage: cal-read.sh <event-uid> [calendar_name]
# If calendar not specified, searches all calendars

EVENT_UID="${1:-}"
CALENDAR_NAME="${2:-}"

if [ -z "$EVENT_UID" ]; then
    echo "Usage: cal-read.sh <event-uid> [calendar_name]"
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
                    
                    set eventSummary to summary of e
                    set eventStart to start date of e
                    set eventEnd to end date of e
                    set isAllDay to allday event of e
                    set eventLoc to location of e
                    set eventDesc to description of e
                    set eventURL to url of e
                    set eventRecur to recurrence of e
                    
                    if eventLoc is missing value then set eventLoc to ""
                    if eventDesc is missing value then set eventDesc to ""
                    if eventURL is missing value then set eventURL to ""
                    if eventRecur is missing value then set eventRecur to ""
                    
                    set output to "UID: " & eventUID & linefeed
                    set output to output & "Calendar: " & (name of cal) & linefeed
                    set output to output & "Summary: " & eventSummary & linefeed
                    set output to output & "Start: " & (eventStart as string) & linefeed
                    set output to output & "End: " & (eventEnd as string) & linefeed
                    set output to output & "All Day: " & (isAllDay as string) & linefeed
                    set output to output & "Location: " & eventLoc & linefeed
                    set output to output & "Description: " & eventDesc & linefeed
                    set output to output & "URL: " & eventURL & linefeed
                    set output to output & "Recurrence: " & eventRecur
                    
                    return output
                end if
            end try
        end repeat
        
        return "Error: Event with UID '" & eventUID & "' not found"
    end tell
end run
EOF
