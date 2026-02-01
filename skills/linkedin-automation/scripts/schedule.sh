#!/bin/bash
# LinkedIn Post Scheduler
# Usage: ./schedule.sh "content" "2026-01-31 09:00" [--image /path/to/image]

CONTENT="$1"
SCHEDULE_TIME="$2"
IMAGE=""

shift 2
while [[ $# -gt 0 ]]; do
    case $1 in
        --image)
            IMAGE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [ -z "$CONTENT" ] || [ -z "$SCHEDULE_TIME" ]; then
    echo "Usage: ./schedule.sh \"content\" \"YYYY-MM-DD HH:MM\" [--image /path/to/image]"
    exit 1
fi

cat << EOF
📅 LINKEDIN SCHEDULED POST
═══════════════════════════════════════

Schedule: $SCHEDULE_TIME (UTC)

Content:
---
$CONTENT
---
$([ -n "$IMAGE" ] && echo "Image: $IMAGE")

## To schedule in OpenClaw:

Use the cron tool with an "at" schedule:

\`\`\`json
{
  "schedule": {
    "kind": "at",
    "atMs": <timestamp_for_$SCHEDULE_TIME>
  },
  "payload": {
    "kind": "systemEvent",
    "text": "Post to LinkedIn now: $CONTENT"
  },
  "sessionTarget": "main"
}
\`\`\`

Or use cron expression for recurring posts:
- Daily at 9am: "0 9 * * *"
- Weekdays at 9am: "0 9 * * 1-5"  
- Mon/Wed/Fri at 2pm: "0 14 * * 1,3,5"

## Quick Setup

Convert your desired time to Unix milliseconds:
\`date -d "$SCHEDULE_TIME" +%s000\`

Then create the cron job via the OpenClaw cron tool.

💡 Tip: Keep a content calendar in a file and schedule a week at a time.
EOF
