#!/bin/bash
# Mark emails as read by message ID (optimized with position hints)
# Usage: mail-mark-read.sh <message-id> [message-id...]

if [[ $# -eq 0 ]]; then
    echo "Usage: mail-mark-read.sh <message-id> [message-id...]" >&2
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

MARKED=0
FAILED=0

for MSG_ID in "$@"; do
    # Get account UUID, mailbox path, and approximate position
    MSG_INFO=$(sqlite3 "$DB_PATH" "
    SELECT 
        substr(mb.url, 8, instr(substr(mb.url, 8), '/') - 1) as account_uuid,
        replace(replace(substr(mb.url, 8 + instr(substr(mb.url, 8), '/')), '%5B', '['), '%5D', ']') as mailbox_path,
        (SELECT COUNT(*) FROM messages m2 WHERE m2.mailbox = m.mailbox AND m2.date_received >= m.date_received) as approx_pos
    FROM messages m
    JOIN mailboxes mb ON m.mailbox = mb.ROWID
    WHERE m.ROWID = $MSG_ID;" 2>/dev/null)
    
    if [[ -z "$MSG_INFO" ]]; then
        echo "Message $MSG_ID not found in database" >&2
        FAILED=$((FAILED + 1))
        continue
    fi
    
    IFS='|' read -r ACCOUNT_UUID MAILBOX_PATH APPROX_POS <<< "$MSG_INFO"
    MAILBOX_PATH=$(python3 -c "import urllib.parse; print(urllib.parse.unquote('$MAILBOX_PATH'))")
    
    START_POS=$((APPROX_POS > 5 ? APPROX_POS - 5 : 1))
    END_POS=$((APPROX_POS + 20))
    
    RESULT=$(osascript << EOF
tell application "Mail"
    try
        set targetId to $MSG_ID
        set targetAccount to first account whose id is "$ACCOUNT_UUID"
        set mbx to mailbox "$MAILBOX_PATH" of targetAccount
        set msgCount to count of messages of mbx
        
        if $END_POS > msgCount then
            set endPos to msgCount
        else
            set endPos to $END_POS
        end if
        
        -- Search in expected range first
        repeat with i from $START_POS to endPos
            try
                set msg to message i of mbx
                if id of msg = targetId then
                    set read status of msg to true
                    return "OK"
                end if
            end try
        end repeat
        
        -- Expand search if not found
        repeat with i from 1 to msgCount
            try
                set msg to message i of mbx
                if id of msg = targetId then
                    set read status of msg to true
                    return "OK"
                end if
            end try
        end repeat
        
        return "ERROR: Message not found"
    on error errMsg
        return "ERROR: " & errMsg
    end try
end tell
EOF
)
    
    if [[ "$RESULT" == "OK" ]]; then
        echo "Marked message $MSG_ID as read"
        MARKED=$((MARKED + 1))
    else
        echo "Failed to mark message $MSG_ID: $RESULT" >&2
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "Summary: $MARKED marked, $FAILED failed"
