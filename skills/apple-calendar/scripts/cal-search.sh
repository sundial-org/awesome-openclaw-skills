#!/bin/bash
# Search events by text (summary, location, or description)
# Usage: cal-search.sh <query> [days_ahead] [calendar_name]
# Examples:
#   cal-search.sh "meeting"           # Search all calendars, next 30 days
#   cal-search.sh "dentist" 90        # Search next 90 days
#   cal-search.sh "standup" 14 Work   # Search Work calendar, next 14 days

QUERY="${1:-}"
DAYS_AHEAD="${2:-30}"
CALENDAR_NAME="${3:-}"

if [ -z "$QUERY" ]; then
    echo "Usage: cal-search.sh <query> [days_ahead] [calendar_name]"
    exit 1
fi

osascript - "$QUERY" "$DAYS_AHEAD" "$CALENDAR_NAME" <<'EOF'
on run argv
    set searchQuery to item 1 of argv as string
    set daysAhead to item 2 of argv as integer
    set calendarName to item 3 of argv as string
    
    tell application "Calendar"
        set today to current date
        set startOfDay to today - (time of today)
        set endDate to startOfDay + (daysAhead * 24 * 60 * 60)
        
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
                    set eventSummary to summary of e
                    set eventLoc to location of e
                    set eventDesc to description of e
                    
                    if eventLoc is missing value then set eventLoc to ""
                    if eventDesc is missing value then set eventDesc to ""
                    
                    -- Case-insensitive search in summary, location, or description
                    set lowerQuery to my toLowerCase(searchQuery)
                    set matchFound to false
                    
                    if my toLowerCase(eventSummary) contains lowerQuery then
                        set matchFound to true
                    else if my toLowerCase(eventLoc) contains lowerQuery then
                        set matchFound to true
                    else if my toLowerCase(eventDesc) contains lowerQuery then
                        set matchFound to true
                    end if
                    
                    if matchFound then
                        set eventStart to start date of e
                        set isAllDay to allday event of e
                        set eventLine to (uid of e) & " | " & eventSummary & " | " & (eventStart as string) & " | " & (isAllDay as string) & " | " & eventLoc & " | " & (name of cal)
                        set end of results to eventLine
                    end if
                end repeat
            end try
        end repeat
        
        if (count of results) = 0 then
            return "No events found matching: " & searchQuery
        end if
        
        set output to ""
        repeat with r in results
            set output to output & r & linefeed
        end repeat
        return output
    end tell
end run

on toLowerCase(theString)
    set lowercaseChars to "abcdefghijklmnopqrstuvwxyz"
    set uppercaseChars to "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    set resultString to ""
    repeat with c in theString
        set charIndex to offset of c in uppercaseChars
        if charIndex > 0 then
            set resultString to resultString & character charIndex of lowercaseChars
        else
            set resultString to resultString & c
        end if
    end repeat
    return resultString
end toLowerCase
EOF
