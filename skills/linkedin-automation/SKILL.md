---
name: linkedin-automator
description: Automate LinkedIn content creation, posting, engagement tracking, and audience growth. Use for posting content, scheduling posts, analyzing engagement metrics, generating content ideas, commenting on posts, and building LinkedIn presence. Requires browser access with LinkedIn logged in.
metadata: {"openclaw":{"emoji":"💼","requires":{"tools":["browser"]}}}
---

# LinkedIn Automator

Automate your LinkedIn presence: post content, track engagement, generate ideas, and grow your audience.

## Prerequisites

1. Browser tool enabled in OpenClaw
2. LinkedIn logged in via browser (use profile with LinkedIn session)

## Quick Commands

```bash
# Post content
{baseDir}/scripts/post.sh "Your post content here"

# Post with image
{baseDir}/scripts/post.sh "Content" --image /path/to/image.png

# Get engagement stats for recent posts
{baseDir}/scripts/analytics.sh

# Generate content ideas based on trending topics
{baseDir}/scripts/ideas.sh [topic]

# Engage with feed (like/comment on relevant posts)
{baseDir}/scripts/engage.sh --limit 10
```

## Workflows

### Posting Content

Use browser automation to post:

1. Navigate to linkedin.com/feed
2. Click "Start a post" button
3. Enter content in the post editor
4. Optionally attach media
5. Click "Post" button

For scheduled posts, use OpenClaw cron:
```
cron add --schedule "0 9 * * 1-5" --payload "Post my LinkedIn content: [content]"
```

### Content Strategy

See [references/content-strategy.md](references/content-strategy.md) for:
- High-engagement post formats
- Best posting times by region
- Hashtag strategies
- Hook templates

### Engagement Automation

See [references/engagement.md](references/engagement.md) for:
- Comment templates
- Engagement workflows
- Growth tactics

### Analytics Tracking

The analytics script extracts:
- Impressions per post
- Engagement rate (likes + comments + shares / impressions)
- Profile views trend
- Follower growth
- Top performing content themes

## Browser Selectors

Key LinkedIn selectors (as of 2026):

```
Post button: button[aria-label="Start a post"]
Post editor: div.ql-editor[data-placeholder]
Submit post: button.share-actions__primary-action
Like button: button[aria-label*="Like"]
Comment button: button[aria-label*="Comment"]
Profile stats: section.pv-top-card-v2-ctas
```

## Rate Limits

LinkedIn enforces activity limits. Stay under:
- Posts: 2-3 per day max
- Comments: 20-30 per day
- Connection requests: 100 per week
- Profile views: Natural browsing pace

## Troubleshooting

- **Login required**: Ensure browser profile has active LinkedIn session
- **Rate limited**: Reduce activity, wait 24h
- **Selector not found**: LinkedIn may have updated UI, check selectors
