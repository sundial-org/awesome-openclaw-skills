# Jellyseerr Webhook Setup Guide

This guide will help you set up instant notifications from Jellyseerr using webhooks instead of polling.

## Benefits

- **Instant notifications** - Get notified immediately when media becomes available
- **Lower API usage** - No need to poll every few minutes
- **More reliable** - Direct push notifications from Jellyseerr

## Step 1: Install the Webhook Server

Run the setup script to create a systemd service:

```bash
cd /home/clawd/clawd/skills/jellyseerr
./scripts/setup_webhook.sh 8384
```

This will:
- Create a systemd service running on port 8384
- Start the service automatically
- Configure it to restart on failure

## Step 2: Configure Jellyseerr

### Get Your Server IP

```bash
hostname -I | awk '{print $1}'
```

### Configure Webhook in Jellyseerr

1. Open Jellyseerr web interface
2. Go to **Settings** → **Notifications** → **Webhook**
3. Click **Enable** toggle
4. Set **Webhook URL** to: `http://YOUR_IP:8384/`
   (Replace YOUR_IP with your server's IP address)

### Set JSON Payload Template

In the **JSON Payload** field, use this base64-encoded template:

```
eyJub3RpZmljYXRpb25fdHlwZSI6Int7bm90aWZpY2F0aW9uX3R5cGV9fSIsInN1YmplY3QiOiJ7e3N1YmplY3R9fSIsIm1lc3NhZ2UiOiJ7e21lc3NhZ2V9fSIsIm1lZGlhX3R5cGUiOiJ7e21lZGlhX3R5cGV9fSIsIm1lZGlhX3RtZGJpZCI6Int7bWVkaWFfdG1kYmlkfX0ifQ==
```

This decodes to:
```json
{
  "notification_type": "{{notification_type}}",
  "subject": "{{subject}}",
  "message": "{{message}}",
  "media_type": "{{media_type}}",
  "media_tmdbid": "{{media_tmdbid}}"
}
```

### Enable Notification Types

Under **Notification Types**, enable:
- ✅ **Media Available**

You can optionally enable other types if you want notifications for:
- Media Requested
- Media Approved
- Media Failed
- etc.

### Test and Save

1. Click **Test** button to send a test notification
2. Check the webhook server logs: `sudo journalctl -u jellyseerr-webhook -f`
3. If successful, click **Save Changes**

## Step 3: Configure Telegram Chat ID (Optional)

If not already configured, add your Telegram chat ID to the config:

```bash
config_file="$HOME/.config/jellyseerr/config.json"
jq '. + {"telegram_chat_id": "YOUR_CHAT_ID"}' "$config_file" > "$config_file.tmp" && mv "$config_file.tmp" "$config_file"
```

Or set it as an environment variable:
```bash
export TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
```

## Verification

### Check Service Status

```bash
sudo systemctl status jellyseerr-webhook
```

### View Live Logs

```bash
sudo journalctl -u jellyseerr-webhook -f
```

### Test a Request

1. Request a movie in Jellyseerr
2. Watch the webhook logs
3. When it becomes available, you should see:
   - Webhook received in logs
   - Notification queued
   - Message sent to Telegram (on next heartbeat or immediately if you trigger it)

## Troubleshooting

### Service won't start

Check logs:
```bash
sudo journalctl -u jellyseerr-webhook -n 50
```

### Webhook not receiving requests

1. Verify firewall allows port 8384:
   ```bash
   sudo ufw allow 8384/tcp
   ```

2. Test locally:
   ```bash
   curl -X POST http://localhost:8384/ \
     -H "Content-Type: application/json" \
     -d '{"notification_type":"TEST","subject":"Test Movie"}'
   ```

### Notifications not being sent

Check if notifications are queued:
```bash
cat ~/.cache/jellyseerr/pending_notifications.json
```

If they exist but aren't being sent, trigger a manual send or wait for the next heartbeat.

## Maintenance

### Restart Service

```bash
sudo systemctl restart jellyseerr-webhook
```

### Stop Service

```bash
sudo systemctl stop jellyseerr-webhook
```

### Uninstall Service

```bash
sudo systemctl stop jellyseerr-webhook
sudo systemctl disable jellyseerr-webhook
sudo rm /etc/systemd/system/jellyseerr-webhook.service
sudo systemctl daemon-reload
```

## Migration from Polling

If you were using the old polling method:

1. Remove cron job (if any):
   ```bash
   crontab -l | grep -v jellyseerr | crontab -
   ```

2. Clear HEARTBEAT.md (it's now just comments)

3. Set up webhook as described above

The new system is more efficient and provides instant notifications!
