# ecto

Command-line interface for the https://ghost.io Admin API.

Manage your Ghost blog from the terminal: create posts, publish pages, upload images, and more.

## Installation

```bash
go install github.com/visionik/ecto@latest
```

Or build from source:

```bash
git clone https://github.com/visionik/ecto
cd ecto
go build -o ecto .
```

## Quick Start

### 1. Get your Admin API key

Ghost Admin → Settings → Integrations → Add Custom Integration

Copy the Admin API Key (format: `id:secret`)

### 2. Configure ecto

```bash
ecto auth add mysite --url https://mysite.ghost.io --key 1234567890abcdef:abcdef1234567890
ecto auth default mysite
```

### 3. Start using it

```bash
# List posts
ecto posts

# Create a post from markdown
ecto post create --title "Hello World" --markdown-file post.md --status published

# Publish a draft
ecto post publish my-draft-slug
```

## Commands

### Authentication

```bash
ecto auth add <name> --url <ghost-url> --key <admin-api-key>
ecto auth list
ecto auth default <name>
ecto auth remove <name>
```

### Posts

```bash
ecto posts [--status draft|published|scheduled|all] [--limit N] [--json]
ecto post <id|slug> [--json] [--body]
ecto post create --title "Title" [--markdown-file file.md] [--tag tag1,tag2] [--status draft|published]
ecto post edit <id|slug> [--title "New Title"] [--markdown-file file.md] [--status draft|published]
ecto post delete <id|slug> [--force]
ecto post publish <id|slug>
ecto post unpublish <id|slug>
ecto post schedule <id|slug> --at "2025-01-25T10:00:00Z"
```

### Pages

```bash
ecto pages [--status draft|published|all] [--limit N] [--json]
ecto page <id|slug> [--json] [--body]
ecto page create --title "Title" [--markdown-file file.md] [--status draft|published]
ecto page edit <id|slug> [--title "New Title"] [--markdown-file file.md]
ecto page delete <id|slug> [--force]
ecto page publish <id|slug>
```

### Tags

```bash
ecto tags [--json]
ecto tag <id|slug> [--json]
ecto tag create --name "Tag Name" [--description "desc"]
ecto tag edit <id|slug> [--name "New Name"] [--description "desc"]
ecto tag delete <id|slug> [--force]
```

### Images

```bash
ecto image upload <path> [--json]
```

### Site Info

```bash
ecto site [--json]
ecto settings [--json]
ecto users [--json]
ecto user <id|slug> [--json]
ecto newsletters [--json]
ecto newsletter <id> [--json]
```

### Webhooks

```bash
ecto webhook create --event <event> --target-url <url> [--name "Hook Name"]
ecto webhook delete <id> [--force]
```

## Multi-Site Support

Configure multiple sites and switch between them:

```bash
ecto auth add production --url https://blog.example.com --key xxx
ecto auth add staging --url https://staging.example.com --key yyy

# Use --site flag
ecto posts --site staging
ecto post create --title "Test" --site staging
```

## Environment Variables

Override config with environment variables:

- `GHOST_URL` - Ghost site URL
- `GHOST_ADMIN_KEY` - Admin API key (id:secret format)
- `GHOST_SITE` - Site name from config

## JSON Output

All read commands support `--json` for scripting:

```bash
# Get all post titles
ecto posts --json | jq -r '.posts[].title'

# Batch publish drafts
for id in $(ecto posts --status draft --json | jq -r '.posts[].id'); do
  ecto post publish "$id"
done
```

## Common Workflows

### Create and publish from markdown

```bash
ecto post create --title "My Post" --markdown-file post.md --tag blog --status published
```

### Pipe content from stdin

```bash
echo "# Quick Note" | ecto post create --title "Quick Note" --stdin-format markdown
```

### Schedule a post

```bash
ecto post create --title "Future Post" --markdown-file post.md
ecto post schedule future-post --at "2025-02-01T09:00:00Z"
```

## AI Integration

For LLM/AI agents, use `--ai-help` to get comprehensive documentation:

```bash
ecto --ai-help
```

## Configuration

Config file location: `~/.config/ecto/config.json`

```json
{
  "default_site": "mysite",
  "sites": {
    "mysite": {
      "name": "mysite",
      "url": "https://mysite.ghost.io",
      "api_key": "id:secret"
    }
  }
}
```

## Requirements

- Go 1.21+
- Ghost 5.x (Admin API v5)

## Library

ecto is built on [libecto](https://github.com/visionik/libecto), a Go library for the Ghost Admin API. Use libecto directly for programmatic access.

## License

MIT
