# Smart Reminders - Technical Reference

## Delivery Method

Reminders are delivered via clawdbot's cron system in **isolated sessions**:

**Default behavior** (no configuration needed):
- Reminders are sent to the **last channel** where you interacted with your agent
- This automatically works for WhatsApp, Telegram, Discord, etc.
- No phone number configuration required

**Optional: Specific phone number** (advanced):
- Add `phoneNumber` to `~/clawd/habit-flow-data/config.json`
- Format: E.164 (e.g., `"+351912345678"`)
- Re-sync reminders after adding: `npx tsx scripts/sync_reminders.ts --sync-all`

### Example config.json with default phone number:
```json
{
  "timezone": "Europe/Lisbon",
  "activePersona": "flex",
  "userId": "default-user",
  "phoneNumber": "+351912345678"
}
```

This phone number will be used as a fallback if no habit-specific recipient is set.

## Supported Channels

- `last` - Last channel used (automatic, no config needed) ✅ Default
- `whatsapp` - WhatsApp (requires phone in E.164 format)
- `telegram` - Telegram (requires chatId)
- `discord` - Discord (requires channel/user id)
- `slack` - Slack (requires channel id)
- `imessage` - iMessage (requires phone or email)

## Troubleshooting Reminders

**Reminder arrives as system event instead of message?**
- Default behavior sends to "last channel" - make sure you've chatted with your agent recently
- Or add `phoneNumber` to config.json for direct delivery

**Reminder not arriving at all?**
- Check cron job exists: `clawdbot cron list`
- Verify timezone in config.json matches your location
- Re-sync: `npx tsx scripts/sync_reminders.ts --sync-all`

## Handling Scheduled Reminder Events

When loaded in an isolated session triggered by a habit reminder:

1. **Act immediately** - Don't wait for user input. The cron trigger itself is your cue to act.
2. **Use all available notification channels** - If desktop notifications are available (e.g., connected Mac app), use them to maximize reminder visibility.
3. **Log delivery** - Confirm the reminder was processed.

The reminder message content is already configured. Your role is to ensure it reaches the user through every available channel.

## Reminder Response Handling

When user responds to a reminder with "done", "skipped", or "missed":

1. Parse the response
2. Identify the habit from context (recent reminder sent)
3. Log the completion with appropriate status
4. Confirm with streak update
