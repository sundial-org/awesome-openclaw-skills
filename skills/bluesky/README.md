# 🦋 Bluesky Skill

A Moltbot skill for interacting with Bluesky (AT Protocol) from the command line.

**Version:** 1.2.0

## Features

- **Timeline** - View your home feed
- **Post** - Create new posts (with `--dry-run` preview)
- **Search** - Search posts across Bluesky
- **Notifications** - Check likes, reposts, follows, mentions
- **Profile** - Look up user profiles
- **Delete** - Remove your posts

## Setup

### 1. Get an App Password

1. Go to [bsky.app](https://bsky.app) → Settings → Privacy and Security → App Passwords
2. Create a new app password (looks like `xxxx-xxxx-xxxx-xxxx`)

### 2. Login

```bash
bsky login --handle yourhandle.bsky.social --password xxxx-xxxx-xxxx-xxxx
```

### 3. Verify

```bash
bsky whoami
```

## Usage

```bash
# Authentication
bsky login --handle user.bsky.social --password xxxx-xxxx-xxxx-xxxx
bsky logout
bsky whoami

# Timeline
bsky timeline          # Show 10 posts
bsky tl -n 20          # Show 20 posts

# Post
bsky post "Hello Bluesky!"
bsky p "Short post"         # Alias
bsky post "Test" --dry-run  # Preview without posting

# Delete
bsky delete <post_id>  # Delete by ID
bsky rm <url>          # Delete by URL

# Search
bsky search "query"
bsky search "offsec" -n 20

# Notifications  
bsky notifications
bsky notif -n 30

# Profile
bsky profile                        # Your profile
bsky profile @someone.bsky.social   # Someone else's

# Version
bsky --version
```

## Output Format

```
@handle · Jan 25 14:30
  Post text here...
  ❤️ 42  🔁 5  💬 3
  🔗 https://bsky.app/profile/handle/post/id
```

## Requirements

- Python 3.8+

## Installation

Via MoltHub:
```bash
molthub install bluesky
```

Or clone directly:
```bash
git clone https://github.com/jeffaf/bluesky-skill.git ~/clawd/skills/bluesky
```

## License

MIT

---

*Built for [Moltbot](https://github.com/moltbot/moltbot)*
