---
name: confluence
description: Search and manage Confluence pages and spaces using confluence-cli. Read documentation, create pages, and navigate spaces.
homepage: https://github.com/pchuri/confluence-cli
metadata: {"clawdbot":{"emoji":"📄","primaryEnv":"CONFLUENCE_TOKEN","requires":{"bins":["confluence"],"env":["CONFLUENCE_TOKEN"]},"install":[{"id":"npm","kind":"node","package":"confluence-cli","bins":["confluence"],"label":"Install confluence-cli (npm)"}]}}
---

# Confluence

Search and manage Confluence pages using confluence-cli.

## REQUIRED: First-Time Setup

Before using this skill, complete these steps:

**Step 1: Install the CLI**

```bash
npm install -g confluence-cli
```

**Step 2: Get an API token**

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "confluence-cli")
4. Copy the token

**Step 3: Configure the CLI**

```bash
confluence init
```

When prompted, enter:
- **Domain**: `yourcompany.atlassian.net` (without https://)
- **Email**: Your Atlassian account email
- **API token**: Paste the token from Step 2

**Step 4: Verify setup**

```bash
confluence spaces
```

If you see your spaces listed, you're ready to use Confluence.

---

## Search Pages

```bash
confluence search "deployment guide"
```

## Read Page

```bash
confluence read <page-id>
```

Page IDs are in the URL: `https://yoursite.atlassian.net/wiki/spaces/SPACE/pages/123456/Title` → ID is `123456`

## Get Page Info

```bash
confluence info <page-id>
```

## Find Page by Title

```bash
confluence find "Page Title"
```

## List Spaces

```bash
confluence spaces
```

## Create Page

```bash
confluence create "Page Title" SPACEKEY --body "Page content here"
```

## Create Child Page

```bash
confluence create-child "Child Page Title" <parent-page-id> --body "Content"
```

Or from a file:

```bash
confluence create-child "Page Title" <parent-id> --file content.html --format storage
```

## Update Page

```bash
confluence update <page-id> --body "Updated content"
```

Or from a file:

```bash
confluence update <page-id> --file content.html --format storage
```

## List Child Pages

```bash
confluence children <page-id>
```

## Export Page with Attachments

```bash
confluence export <page-id> --output ./exported-page/
```

## Tips

- Domain in config should NOT include `https://` - just `yourcompany.atlassian.net`
- Use `--format storage` when content is in Confluence storage format (HTML-like)
- Page IDs are numeric and found in page URLs
- Config is stored at `~/.confluence-cli/config.json`
