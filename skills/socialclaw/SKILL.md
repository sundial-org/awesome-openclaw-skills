---
name: socialclaw
description: Schedule and publish social media posts across 13 platforms via SocialClaw. Use when the user wants to connect social accounts, upload media, apply a post schedule, or publish to X, LinkedIn, Instagram, Facebook Pages, TikTok, Discord, Telegram, YouTube, Reddit, WordPress, or Pinterest.
metadata: {"clawdbot":{"emoji":"📣","always":false,"requires":{"bins":["curl","npm"]},"primaryEnv":"SC_API_KEY"}}
---

# SocialClaw 📣

Agent-first social media scheduling and publishing via the [SocialClaw](https://getsocialclaw.com) API. One workspace API key publishes to 13 platforms.

## Setup

```bash
export SC_API_KEY="<workspace-key>"

# Verify access
curl -sS -H "Authorization: Bearer $SC_API_KEY" https://getsocialclaw.com/v1/keys/validate

# Optional CLI
npm install -g socialclaw
socialclaw login --api-key <workspace-key>
```

## Supported Platforms

X, LinkedIn (profile + page), Instagram (Business + standalone), Facebook Pages, TikTok, Discord, Telegram, YouTube, Reddit, WordPress, Pinterest

## Features

- Connect social accounts via OAuth (dashboard)
- Upload media assets
- Build and validate post schedules
- Publish campaigns across multiple platforms
- Monitor run status and analytics

## Usage

```bash
# List connected accounts
socialclaw accounts list --json

# Upload media
socialclaw assets upload --file ./image.png --json

# Validate schedule
socialclaw validate -f schedule.json --json

# Publish
socialclaw apply -f schedule.json --json

# Monitor
socialclaw status --run-id <id> --json
```

## Source

- GitHub: https://github.com/ndesv21/socialclaw
- npm: https://www.npmjs.com/package/socialclaw
- Dashboard: https://getsocialclaw.com/dashboard
