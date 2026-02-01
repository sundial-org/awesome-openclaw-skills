#!/bin/bash
# List events in a date range
# Usage: cal-events.sh [days_ahead] [calendar_name]
# Examples:
#   cal-events.sh              # Today's events from all calendars
#   cal-events.sh 7            # Next 7 days from all calendars
#   cal-events.sh 7 Personal   # Next 7 days from Personal calendar only

DAYS_AHEAD="${1:-0}"
CALENDAR_NAME="${2:-}"

osascript - "$DAYS_AHEAD" "$CALENDAR_NAME" <<'EOF'
on run argv
    set daysAhead to item 1 of argv as integer
    set calendarName to item 2 of argv as string
    
    tell application "Calendar"
        set today to current date
        set startOfDay to today - (time of today)
        
        if daysAhead = 0 then
            set endDate to startOfDay + (24 * 60 * 60)
        else
            set endDate to startOfDay + ((daysAhead + 1) * 24 * 60 * 60)
        end if
        
        set results to {}
        
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
                set calEvents to (every event of cal whose start date ≥ startOfDay and start date < endDate)
                repeat with e in calEvents
                    set eventStart to start date of e
                    set eventEnd to end date of e
                    set isAllDay to allday event of e
                    set eventLoc to location of e
                    if eventLoc is missing value then set eventLoc to ""
                    
                    set eventLine to (uid of e) & " | " & (summary of e) & " | " & (eventStart as string) & " | " & (eventEnd as string) & " | " & (isAllDay as string) & " | " & eventLoc & " | " & (name of cal)
                    set end of results to eventLine
                end repeat
            end try
        end repeat
        
        if (count of results) = 0 then
            return "No events found"
        end if
        
        set output to ""
        repeat with r in results
            set output to output & r & linefeed
        end repeat
        return output
    end tell
end run
EOF
