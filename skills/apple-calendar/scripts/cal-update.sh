#!/bin/bash
# Update an existing calendar event
# Usage: cal-update.sh <event-uid> [--calendar <name>] [--summary <text>] [--start <date>] [--end <date>] [--location <text>] [--description <text>] [--allday <true/false>] [--recurrence <rrule>]
# Date format: "YYYY-MM-DD HH:MM" or "YYYY-MM-DD" for all-day events
# Examples:
#   cal-update.sh ABC123 --summary "Updated Meeting"
#   cal-update.sh ABC123 --calendar Personal --start "2026-01-16 14:00" --end "2026-01-16 15:00"
#   cal-update.sh ABC123 --location "Room 101" --description "Bring laptop"

EVENT_UID=""
CALENDAR_NAME=""
SUMMARY=""
START_DATE=""
END_DATE=""
LOCATION=""
DESCRIPTION=""
ALL_DAY=""
RECURRENCE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --calendar) CALENDAR_NAME="$2"; shift 2 ;;
        --summary) SUMMARY="$2"; shift 2 ;;
        --start) START_DATE="$2"; shift 2 ;;
        --end) END_DATE="$2"; shift 2 ;;
        --location) LOCATION="$2"; shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        --allday) ALL_DAY="$2"; shift 2 ;;
        --recurrence) RECURRENCE="$2"; shift 2 ;;
        *)
            if [ -z "$EVENT_UID" ]; then
                EVENT_UID="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$EVENT_UID" ]; then
    echo "Usage: cal-update.sh <event-uid> [--calendar <name>] [--summary <text>] [--start <date>] [--end <date>] [--location <text>] [--description <text>] [--allday <true/false>] [--recurrence <rrule>]"
    exit 1
fi

osascript - "$EVENT_UID" "$CALENDAR_NAME" "$SUMMARY" "$START_DATE" "$END_DATE" "$LOCATION" "$DESCRIPTION" "$ALL_DAY" "$RECURRENCE" <<'EOF'
on splitString(theString, theDelimiter)
    set oldDelimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to theDelimiter
    set theArray to every text item of theString
    set AppleScript's text item delimiters to oldDelimiters
    return theArray
end splitString

on parseDate(dateStr)
    if dateStr is "" then return missing value
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
    set eventUID to item 1 of argv as string
    set calendarName to item 2 of argv as string
    set newSummary to item 3 of argv as string
    set newStartStr to item 4 of argv as string
    set newEndStr to item 5 of argv as string
    set newLocation to item 6 of argv as string
    set newDescription to item 7 of argv as string
    set newAllDay to item 8 of argv as string
    set newRecurrence to item 9 of argv as string
    
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
                    
                    if not (writable of cal) then
                        return "Error: Calendar '" & (name of cal) & "' is read-only"
                    end if
                    
                    if newSummary is not "" then
                        set summary of e to newSummary
                    end if
                    
                    if newStartStr is not "" then
                        set start date of e to my parseDate(newStartStr)
                    end if
                    
                    if newEndStr is not "" then
                        set end date of e to my parseDate(newEndStr)
                    end if
                    
                    if newLocation is not "" then
                        set location of e to newLocation
                    end if
                    
                    if newDescription is not "" then
                        set description of e to newDescription
                    end if
                    
                    if newAllDay is "true" then
                        set allday event of e to true
                    else if newAllDay is "false" then
                        set allday event of e to false
                    end if
                    
                    if newRecurrence is not "" then
                        set recurrence of e to newRecurrence
                    end if
                    
                    return "Updated event: " & eventUID
                end if
            end try
        end repeat
        
        return "Error: Event with UID '" & eventUID & "' not found"
    end tell
end run
EOF
