#!/bin/bash
# Read full email content by message ID (supports multiple IDs)
# Usage: mail-read.sh <message-id> [message-id...]

if [ $# -eq 0 ]; then
    echo "Usage: mail-read.sh <message-id> [message-id...]"
    exit 1
fi

# Find the Mail database
find_db() {
    local db
    for v in 11 10 9; do
        db="$HOME/Library/Mail/V$v/MailData/Envelope Index"
        if [[ -f "$db" ]]; then
            echo "$db"
            return 0
        fi
    done
    return 1
}

DB_PATH=$(find_db)

if [[ -z "$DB_PATH" ]]; then
    echo "Error: Mail database not found" >&2
    exit 1
fi

READ_COUNT=0
FAILED_COUNT=0
FIRST=true

for MSG_ID in "$@"; do
    # Add separator between messages
    if [ "$FIRST" = true ]; then
        FIRST=false
    else
        echo ""
        echo "========================================"
        echo ""
    fi
    
    # Get account UUID, mailbox path, and approximate position from database
    MSG_INFO=$(sqlite3 "$DB_PATH" "
    SELECT 
        substr(mb.url, 8, instr(substr(mb.url, 8), '/') - 1) as account_uuid,
        replace(replace(substr(mb.url, 8 + instr(substr(mb.url, 8), '/')), '%5B', '['), '%5D', ']') as mailbox_path,
        (SELECT COUNT(*) FROM messages m2 WHERE m2.mailbox = m.mailbox AND m2.date_received >= m.date_received) as approx_pos
    FROM messages m
    JOIN mailboxes mb ON m.mailbox = mb.ROWID
    WHERE m.ROWID = $MSG_ID;" 2>/dev/null)

    if [[ -z "$MSG_INFO" ]]; then
        echo "Error: Message $MSG_ID not found in database" >&2
        FAILED_COUNT=$((FAILED_COUNT + 1))
        continue
    fi

    IFS='|' read -r ACCOUNT_UUID MAILBOX_PATH APPROX_POS <<< "$MSG_INFO"
    MAILBOX_PATH=$(python3 -c "import urllib.parse; print(urllib.parse.unquote('$MAILBOX_PATH'))")

    START_POS=$((APPROX_POS > 5 ? APPROX_POS - 5 : 1))
    END_POS=$((APPROX_POS + 20))

    # Use AppleScript with direct account and position access
    RESULT=$(osascript <<EOF
tell application "Mail"
    try
        set targetId to $MSG_ID
        set targetAccountId to "$ACCOUNT_UUID"
        set targetMailboxPath to "$MAILBOX_PATH"
        set startPos to $START_POS
        set endPos to $END_POS
        set foundMsg to missing value
        
        set targetAccount to first account whose id is targetAccountId
        set mbx to mailbox targetMailboxPath of targetAccount
        set msgCount to count of messages of mbx
        
        if endPos > msgCount then set endPos to msgCount
        if startPos < 1 then set startPos to 1
        
        repeat with i from startPos to endPos
            try
                set msg to message i of mbx
                if id of msg = targetId then
                    set foundMsg to msg
                    exit repeat
                end if
            end try
        end repeat
        
        if foundMsg is missing value then
            repeat with i from 1 to msgCount
                try
                    set msg to message i of mbx
                    if id of msg = targetId then
                        set foundMsg to msg
                        exit repeat
                    end if
                end try
            end repeat
        end if
        
        if foundMsg is missing value then
            return "ERROR:Message not found with ID: $MSG_ID"
        end if
        
        set output to "From: " & sender of foundMsg & linefeed
        
        set mto to ""
        try
            set recipList to to recipients of foundMsg
            repeat with r in recipList
                set mto to mto & address of r & ", "
            end repeat
            if mto ends with ", " then set mto to text 1 thru -3 of mto
        end try
        set output to output & "To: " & mto & linefeed
        
        set output to output & "Date: " & date received of foundMsg & linefeed
        set output to output & "Subject: " & subject of foundMsg & linefeed
        set output to output & linefeed & "---" & linefeed & linefeed
        set output to output & content of foundMsg
        
        return output
    on error errMsg
        return "ERROR:" & errMsg
    end try
end tell
EOF
)

    if [[ "$RESULT" == ERROR:* ]]; then
        echo "${RESULT#ERROR:}" >&2
        FAILED_COUNT=$((FAILED_COUNT + 1))
    else
        echo "$RESULT"
        READ_COUNT=$((READ_COUNT + 1))
    fi
done

# Print summary if multiple messages
if [ $# -gt 1 ]; then
    echo ""
    echo "========================================"
    echo "Summary: $READ_COUNT read, $FAILED_COUNT failed"
fi
