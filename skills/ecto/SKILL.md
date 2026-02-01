---
name: ecto
description: Ghost.io Admin API CLI for managing blog posts, pages, tags, and content.
---

# ecto - Ghost.io Admin API CLI

Manage Ghost.io blogs via the Admin API. Supports multi-site configuration, markdown-to-HTML conversion, and JSON output for scripting.

## Quick Reference

### Authentication
```bash
ecto auth add <name> --url <ghost-url> --key <admin-api-key>
ecto auth list
ecto auth default <name>
ecto auth remove <name>
```

Environment overrides: `GHOST_URL`, `GHOST_ADMIN_KEY`, `GHOST_SITE`

### Posts
```bash
ecto posts [--status draft|published|scheduled|all] [--limit N] [--json]
ecto post <id|slug> [--json] [--body]
ecto post create --title "Title" [--markdown-file file.md] [--stdin-format markdown] [--tag tag1,tag2] [--status draft|published]
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

Events: `post.published`, `post.unpublished`, `post.added`, `post.deleted`, `page.published`, etc.

## Multi-Site
Use `--site <name>` to target a specific configured site:
```bash
ecto posts --site blog2
```

## Common Workflows

Create and publish from markdown:
```bash
ecto post create --title "My Post" --markdown-file post.md --tag blog --status published
```

Pipe content from stdin:
```bash
echo "# Hello World" | ecto post create --title "Quick Post" --stdin-format markdown
```

Schedule a post:
```bash
ecto post schedule future-post --at "2025-02-01T09:00:00Z"
```

Batch publish drafts:
```bash
for id in $(ecto posts --status draft --json | jq -r '.posts[].id'); do
  ecto post publish "$id"
done
```

## Limitations
- Ghost API does not support listing images or webhooks
- Member/subscription management not available via Admin API
- Read-only access to users

## Full Docs
Run `ecto --ai-help` for comprehensive documentation.
