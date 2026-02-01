# Messaging API

## Send Message with Mention

**MUST include BOTH formatted text AND mentions array:**

```typescript
// Format: Hello <@0x...>!
const text = 'Hello <@' + userId + '>!'
await handler.sendMessage(channelId, text, {
  mentions: [{ userId, displayName: 'User' }]
})

// @channel
await handler.sendMessage(channelId, 'Attention!', {
  mentions: [{ atChannel: true }]
})
```

## Threads & Replies

```typescript
// Reply in thread
await handler.sendMessage(channelId, 'Thread reply', { threadId: event.eventId })

// Reply to specific message
await handler.sendMessage(channelId, 'Reply', { replyId: messageId })
```

## Attachments

```typescript
// Image
attachments: [{ type: 'image', url: 'https://...jpg', alt: 'Description' }]

// Miniapp
attachments: [{ type: 'miniapp', url: 'https://your-app.com/miniapp.html' }]

// Large file (chunked)
attachments: [{
  type: 'chunked',
  data: readFileSync('./video.mp4'),
  filename: 'video.mp4',
  mimetype: 'video/mp4'
}]
```

## Message Formatting

Towns has specific rendering behavior:
- **Use `\n\n`** (double newlines) between sections - single `\n` causes overlap
- **Never use `---`** as separator - renders as zero-height rule
- **Use middot** for inline data: `Value: $1.00 · P&L: $0.50`

```typescript
// Good - double newlines
const msg = ['**Header**', 'Line 1', 'Line 2'].join('\n\n')

// Bad - single newlines will collapse
const bad = lines.join('\n')
```

## Edit and Delete

```typescript
// Edit bot's own message
await handler.editMessage(channelId, eventId, 'Updated text')

// Delete bot's own message
await handler.removeEvent(channelId, eventId)
```

## Reactions

```typescript
await handler.sendReaction(channelId, messageId, '👍')
```
