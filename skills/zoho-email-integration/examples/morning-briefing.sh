#!/bin/bash
# Morning email briefing
# Add to crontab: 0 7 * * * /path/to/morning-briefing.sh

# Load credentials
source ~/.clawdbot/zoho-credentials.sh

# Get unread count
UNREAD=$(python3 scripts/zoho-email.py unread | jq -r '.unread_count')

# Generate briefing
echo "☀️ Good morning!"
echo "📧 You have $UNREAD unread emails"

# Show recent important emails
if [ $UNREAD -gt 0 ]; then
    echo ""
    echo "Recent emails:"
    python3 scripts/zoho-email.py search "ALL" | jq -r '.[] | "• \(.subject) - \(.from)"' | head -3
fi
