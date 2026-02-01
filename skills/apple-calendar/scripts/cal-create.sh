#!/bin/bash
# Create a new calendar event
# Usage: cal-create.sh <calendar> <summary> <start_date> <end_date> [location] [description] [allday] [recurrence]
# Date format: "YYYY-MM-DD HH:MM" or "YYYY-MM-DD" for all-day events
# Recurrence format: iCalendar RRULE (e.g., "FREQ=WEEKLY;COUNT=4" or "FREQ=DAILY;UNTIL=20260201")
# Examples:
#   cal-create.sh Personal "Meeting" "2026-01-15 10:00" "2026-01-15 11:00"
#   cal-create.sh Personal "Vacation" "2026-02-01" "2026-02-05" "" "Beach trip" true
#   cal-create.sh Personal "Weekly Standup" "2026-01-20 09:00" "2026-01-20 09:30" "Zoom" "" false "FREQ=WEEKLY;COUNT=10"

CALENDAR="${1:-}"
SUMMARY="${2:-}"
START_DATE="${3:-}"
END_DATE="${4:-}"
LOCATION="${5:-}"
DESCRIPTION="${6:-}"
ALL_DAY="${7:-false}"
RECURRENCE="${8:-}"

if [ -z "$CALENDAR" ] || [ -z "$SUMMARY" ] || [ -z "$START_DATE" ] || [ -z "$END_DATE" ]; then
    echo "Usage: cal-create.sh <calendar> <summary> <start_date> <end_date> [location] [description] [allday] [recurrence]"
    echo "Date format: 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD' for all-day"
    exit 1
fi

osascript - "$CALENDAR" "$SUMMARY" "$START_DATE" "$END_DATE" "$LOCATION" "$DESCRIPTION" "$ALL_DAY" "$RECURRENCE" <<'EOF'
on splitString(theString, theDelimiter)
    set oldDelimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to theDelimiter
    set theArray to every text item of theString
    set AppleScript's text item delimiters to oldDelimiters
    return theArray
end splitString

on parseDate(dateStr)
    set dateParts to my splitString(dateStr, " ")
    set ymdParts to my splitString(item 1 of dateParts, "-")
    
    set theDate to current date
    set year of theDate to (item 1 of ymdParts) as integer
    set month of theDate to (item 2 of ymdParts) as integer
    set day of theDate to (item 3 of ymdParts) as integer
    
    if (count of dateParts) > 1 then
        set timeParts to my splitString(item 2 of dateParts, ":")
        set hours of theDate to (item 1 of timeParts) as integer
        set minutes of theDate to (item 2 of timeParts) as integer
        set seconds of theDate to 0
    else
        set hours of theDate to 0
        set minutes of theDate to 0
        set seconds of theDate to 0
    end if
    
    return theDate
end parseDate

on run argv
    set calendarName to item 1 of argv as string
    set eventSummary to item 2 of argv as string
    set startDateStr to item 3 of argv as string
    set endDateStr to item 4 of argv as string
    set eventLocation to item 5 of argv as string
    set eventDescription to item 6 of argv as string
    set isAllDay to item 7 of argv as string
    set eventRecurrence to item 8 of argv as string
    
    set startDate to my parseDate(startDateStr)
    set endDate to my parseDate(endDateStr)
    
    tell application "Calendar"
        try
            set cal to calendar calendarName
        on error
            return "Error: Calendar '" & calendarName & "' not found"
        end try
        
        if not (writable of cal) then
            return "Error: Calendar '" & calendarName & "' is read-only"
        end if
        
        set eventProps to {summary:eventSummary, start date:startDate, end date:endDate}
        
        if isAllDay is "true" then
            set eventProps to eventProps & {allday event:true}
        end if
        
        set newEvent to make new event at end of events of cal with properties eventProps
        
        if eventLocation is not "" then
            set location of newEvent to eventLocation
        end if
        
        if eventDescription is not "" then
            set description of newEvent to eventDescription
        end if
        
        if eventRecurrence is not "" then
            set recurrence of newEvent to eventRecurrence
        end if
        
        return "Created event: " & (uid of newEvent)
    end tell
end run
EOF
