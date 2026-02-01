# Teams via Microsoft Graph (optional)

This is optional because many tenants restrict Teams message access.

## What you need

- Ability to create an Entra ID (Azure AD) **App Registration**
- Admin consent for permissions (often required)

## Typical permissions (varies by tenant policy)

- Read chats/mentions: `Chat.Read`, `Chat.ReadBasic`, possibly `ChannelMessage.Read.All` (for channels)
- Send message (if you want reminders in Teams): `ChatMessage.Send` (or webhook approach)

## Auth

Recommended for local scripts:
- Device Code flow (interactive sign-in)

## Notes

- Even with Graph, Teams message APIs can be limited.
- If you can’t get permissions approved, fall back to Telegram reminders + Outlook-only tracking.
