#!/bin/bash
# Daily Dilbert cron script for Helmut
# Run via: /home/node/clawd/workspace/skills/dilbert/daily_dilbert.sh

SKILL_SCRIPT="/home/node/clawd/workspace/skills/dilbert/skill.sh"
TELEGRAM_CHAT_ID="954799023"

# Fetch the comic
COMIC=$($SKILL_SCRIPT)
if [ -f "$COMIC" ]; then
    # Send via curl to Telegram Bot API
    # You'll need to configure the bot token
    curl -s -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendPhoto" \
        -F chat_id="$TELEGRAM_CHAT_ID" \
        -F photo="@$COMIC" \
        -F caption="☀️ Morning Dilbert for you!"
    
    # Clean up
    rm -f "$COMIC"
fi
