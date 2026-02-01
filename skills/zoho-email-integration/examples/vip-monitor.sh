#!/bin/bash
# Monitor for VIP emails and send notifications
# Run periodically: */15 * * * * /path/to/vip-monitor.sh

# Load credentials
source ~/.clawdbot/zoho-credentials.sh

# VIP email addresses (customize these)
VIP_SENDERS=(
    "boss@company.com"
    "important-client@example.com"
)

# Check each VIP
for sender in "${VIP_SENDERS[@]}"; do
    # Search for recent emails from this sender
    RESULTS=$(python3 scripts/zoho-email.py search "FROM \"$sender\"")
    COUNT=$(echo "$RESULTS" | jq '. | length')
    
    if [ $COUNT -gt 0 ]; then
        SUBJECT=$(echo "$RESULTS" | jq -r '.[0].subject')
        echo "⚠️  VIP Email Alert!"
        echo "From: $sender"
        echo "Subject: $SUBJECT"
        
        # Optional: Send notification to Telegram, Slack, etc.
        # message telegram "VIP email from $sender: $SUBJECT"
    fi
done
