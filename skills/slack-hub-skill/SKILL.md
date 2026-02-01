# Slack Hub Skill

Professional Slack integration for OpenClaw. Supports messaging, threading, and workspace search.

## Configuration
Requires a Slack Bot Token (`xoxb-...`) in your `.env` as `SLACK_BOT_TOKEN`.

## Tools

### slack_send
Send a message to a channel or user.
- `target`: Channel ID or name (e.g., "#general").
- `message`: Text content.
- `thread_ts`: (Optional) Timestamp for replying to a thread.

### slack_search
Search the workspace for messages or files.
- `query`: The search term.

### slack_list_channels
List all public channels in the workspace.

## Implementation Notes
- Uses `https://slack.com/api/chat.postMessage`
- Uses `https://slack.com/api/search.messages`
- Implements rate-limit handling for high-volume workspaces.
