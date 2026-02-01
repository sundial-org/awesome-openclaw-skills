---
name: nosi
description: Publish content to Nosi and get a shareable URL. Use when the user wants to publish text, markdown, or files to nosi.pub for sharing.
user-invocable: true
---

# Nosi Publishing Skill

Nosi lets you publish text to the open web and get a permanent, shareable URL.

## When to Use This Skill

Use this skill when the user says things like:
- "Publish this to Nosi"
- "Share this on Nosi"
- "Post this to nosi.pub"
- "Get a shareable link for this"

## API Reference

Base URL: https://nosi.pub

### Registration (for new users)
POST /v1/auth/register
Content-Type: application/json

{"email": "user@example.com"}

The API key is sent via email (security requirement).

### Publishing
POST /v1/publish
Content-Type: application/json
X-API-Key: nosi_xxxxx

{"content": "Text to publish"}

Returns: {"content_url": "https://nosi.pub/123456", "raw_text_url": "..."}

## Workflow

1. Ask if user has a Nosi API key
2. If no: Ask for email → call register API → tell user to check email → wait for key
3. If yes: Get the API key from user
4. Publish content with X-API-Key header
5. Return the content_url to user

## Error Handling

- 401 Invalid key: Ask user to re-register with same email
- 429 Rate limited: Wait a few minutes
- 413 Content too large: Max 100KB
