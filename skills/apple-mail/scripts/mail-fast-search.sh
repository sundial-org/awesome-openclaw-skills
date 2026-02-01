#!/bin/bash
# Fast SQLite-based email search (~50ms vs minutes with AppleScript)
# Safe to use even if Mail.app is running (copies DB to temp file)
# Usage: mail-fast-search.sh <query> [limit]

set -e

QUERY="${1:?Usage: mail-fast-search.sh <query> [limit]}"
LIMIT="${2:-20}"

# Find the Mail envelope index database
find_db() {
    local db
    for v in 11 10 9; do
        db="$HOME/Library/Mail/V$v/MailData/Envelope Index"
        if [[ -f "$db" ]]; then
            # Verify this DB has the messages table
            if sqlite3 "$db" "SELECT 1 FROM messages LIMIT 1" &>/dev/null; then
                echo "$db"
                return 0
            fi
        fi
    done
    return 1
}

SOURCE_DB=$(find_db)

if [[ -z "$SOURCE_DB" ]]; then
    echo "Error: Mail database not found or schema incompatible" >&2
    exit 1
fi

# Copy to temp file to avoid corrupting the live DB while Mail.app is running
TEMP_DB=$(mktemp -t mail-search.XXXXXX)
cleanup() {
    rm -f "$TEMP_DB" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cp "$SOURCE_DB" "$TEMP_DB"

# Search by subject, sender address, or sender name
sqlite3 -header -separator ' | ' "$TEMP_DB" "
SELECT 
  m.ROWID as id,
  CASE WHEN (m.flags & 1) = 0 THEN '●' ELSE ' ' END as unread,
  datetime(m.date_sent, 'unixepoch', 'localtime') as date,
  COALESCE(a.comment, a.address, 'Unknown') as sender,
  COALESCE(s.subject, '(no subject)') as subject
FROM messages m
LEFT JOIN subjects s ON m.subject = s.ROWID
LEFT JOIN addresses a ON m.sender = a.ROWID
WHERE s.subject LIKE '%${QUERY}%' 
   OR a.address LIKE '%${QUERY}%'
   OR a.comment LIKE '%${QUERY}%'
ORDER BY m.date_sent DESC
LIMIT ${LIMIT};
"
