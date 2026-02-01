---
name: telegram-bot
description: Build and manage Telegram bots via the Telegram Bot API. Create bots, send messages, handle webhooks, manage groups and channels.
homepage: https://core.telegram.org/bots/api
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":["jq","curl"],"env":["TELEGRAM_BOT_TOKEN"]}}}
---

# Telegram Bot Builder Skill

Build and manage Telegram bots directly from Clawdbot.

## Setup

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts to create your bot
3. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Set environment variable:
   ```bash
   export TELEGRAM_BOT_TOKEN="your-bot-token"
   ```

## API Base URL

All requests go to:
```
https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/METHOD_NAME
```

## Usage

### Bot Information

#### Get bot info
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" | jq
```

#### Get bot commands
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMyCommands" | jq
```

#### Set bot commands
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {"command": "start", "description": "Start the bot"},
      {"command": "help", "description": "Show help message"},
      {"command": "settings", "description": "Bot settings"}
    ]
  }' | jq
```

### Sending Messages

#### Send text message
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "text": "Hello from Clawdbot!",
    "parse_mode": "HTML"
  }' | jq
```

#### Send message with inline keyboard
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "text": "Choose an option:",
    "reply_markup": {
      "inline_keyboard": [
        [{"text": "Option 1", "callback_data": "opt1"}, {"text": "Option 2", "callback_data": "opt2"}],
        [{"text": "Visit Website", "url": "https://example.com"}]
      ]
    }
  }' | jq
```

#### Send message with reply keyboard
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "text": "Choose from keyboard:",
    "reply_markup": {
      "keyboard": [
        [{"text": "Button 1"}, {"text": "Button 2"}],
        [{"text": "Send Location", "request_location": true}]
      ],
      "resize_keyboard": true,
      "one_time_keyboard": true
    }
  }' | jq
```

#### Send photo
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendPhoto" \
  -F "chat_id=CHAT_ID" \
  -F "photo=@/path/to/image.jpg" \
  -F "caption=Photo caption here" | jq
```

#### Send photo by URL
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendPhoto" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "photo": "https://example.com/image.jpg",
    "caption": "Image from URL"
  }' | jq
```

#### Send document
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendDocument" \
  -F "chat_id=CHAT_ID" \
  -F "document=@/path/to/file.pdf" \
  -F "caption=Here is your document" | jq
```

#### Send location
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendLocation" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "latitude": 40.7128,
    "longitude": -74.0060
  }' | jq
```

### Getting Updates

#### Get updates (polling)
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates" | jq
```

#### Get updates with offset (mark as read)
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates?offset=UPDATE_ID" | jq
```

#### Get updates with timeout (long polling)
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates?timeout=30" | jq
```

### Webhooks

#### Set webhook
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "allowed_updates": ["message", "callback_query"]
  }' | jq
```

#### Get webhook info
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo" | jq
```

#### Delete webhook
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/deleteWebhook" | jq
```

### Chat Management

#### Get chat info
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getChat?chat_id=CHAT_ID" | jq
```

#### Get chat member count
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getChatMemberCount?chat_id=CHAT_ID" | jq
```

#### Get chat administrators
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getChatAdministrators?chat_id=CHAT_ID" | jq
```

#### Ban user from chat
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/banChatMember" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "user_id": USER_ID
  }' | jq
```

#### Unban user
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/unbanChatMember" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "user_id": USER_ID,
    "only_if_banned": true
  }' | jq
```

### Message Management

#### Edit message text
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/editMessageText" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "message_id": MESSAGE_ID,
    "text": "Updated message text"
  }' | jq
```

#### Delete message
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/deleteMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "message_id": MESSAGE_ID
  }' | jq
```

#### Pin message
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/pinChatMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "CHAT_ID",
    "message_id": MESSAGE_ID
  }' | jq
```

#### Forward message
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/forwardMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "TARGET_CHAT_ID",
    "from_chat_id": "SOURCE_CHAT_ID",
    "message_id": MESSAGE_ID
  }' | jq
```

### Callback Queries

#### Answer callback query
```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/answerCallbackQuery" \
  -H "Content-Type: application/json" \
  -d '{
    "callback_query_id": "CALLBACK_QUERY_ID",
    "text": "Button clicked!",
    "show_alert": false
  }' | jq
```

## Notes

- **Chat ID**: Can be positive (user) or negative (group/channel). Get it from updates or use @userinfobot
- **Parse modes**: `HTML`, `Markdown`, `MarkdownV2`
- **Rate limits**: ~30 messages/second to different chats, 1 message/second to same chat
- **File limits**: Photos up to 10MB, documents up to 50MB
- **Bot permissions**: Bots can't message users first - user must /start the bot

## HTML Formatting

```html
<b>bold</b>
<i>italic</i>
<u>underline</u>
<s>strikethrough</s>
<code>inline code</code>
<pre>code block</pre>
<a href="https://example.com">link</a>
<tg-spoiler>spoiler</tg-spoiler>
```

## Examples

### Simple echo bot (bash script)
```bash
#!/bin/bash
OFFSET=0
while true; do
  UPDATES=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates?offset=$OFFSET&timeout=30")
  
  for UPDATE in $(echo "$UPDATES" | jq -c '.result[]'); do
    UPDATE_ID=$(echo "$UPDATE" | jq '.update_id')
    CHAT_ID=$(echo "$UPDATE" | jq '.message.chat.id')
    TEXT=$(echo "$UPDATE" | jq -r '.message.text')
    
    if [ "$TEXT" != "null" ]; then
      curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -H "Content-Type: application/json" \
        -d "{\"chat_id\": $CHAT_ID, \"text\": \"You said: $TEXT\"}"
    fi
    
    OFFSET=$((UPDATE_ID + 1))
  done
done
```

### Get your chat ID
```bash
# 1. Send a message to your bot
# 2. Run this to see your chat ID:
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates" | jq '.result[-1].message.chat.id'
```

### Send to channel
```bash
# Use @channelname or channel ID (starts with -100)
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "@your_channel_name",
    "text": "Channel announcement!"
  }' | jq
```

## Useful Resources

- [Bot API Documentation](https://core.telegram.org/bots/api)
- [BotFather Commands](https://core.telegram.org/bots#botfather)
- [Bot API Changelog](https://core.telegram.org/bots/api-changelog)
