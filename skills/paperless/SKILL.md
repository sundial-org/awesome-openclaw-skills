---
name: paperless
description: Interact with Paperless-NGX document management system via ppls CLI. Search, retrieve, upload, and organize documents.
emoji: 📄
metadata: {"clawdbot":{"requires":{"bins":["ppls"],"env":["PPLS_HOSTNAME","PPLS_TOKEN"]},"install":[{"id":"node","kind":"node","package":"@nickchristensen/ppls","bins":["ppls"],"label":"Install ppls CLI (npm/bun)"}]}}
---

# Paperless-NGX CLI

Search and manage documents in Paperless-NGX using `ppls`.

## Setup

```bash
npm install -g @nickchristensen/ppls
ppls config set hostname http://your-paperless-host
ppls config set token your-api-token
```

## Searching Documents

```bash
# By name
ppls documents list --name-contains "invoice" --json

# By date range
ppls documents list --created-after 2024-01-01 --created-before 2024-12-31 --json

# By tag (OR — any of these tags)
ppls documents list --tag 5 --tag 12 --json

# By tag (AND — must have all)
ppls documents list --tag-all 5,12 --json

# Exclude tags
ppls documents list --tag-not 3 --json

# By correspondent
ppls documents list --correspondent 7 --json

# By document type
ppls documents list --document-type 2 --json

# Documents missing metadata
ppls documents list --no-correspondent --json
ppls documents list --no-tag --json

# Recently added/modified
ppls documents list --added-after 2024-06-01 --json
ppls documents list --modified-after 2024-06-01 --json

# Combine filters
ppls documents list --correspondent 7 --created-after 2024-01-01 --tag 5 --json
```

## Viewing & Downloading

```bash
# Get full document details (includes OCR content)
ppls documents show 1234 --json

# Download single document
ppls documents download 1234 --output ~/Downloads/doc.pdf

# Download multiple documents
ppls documents download 1234 5678 --output-dir ~/Downloads

# Download original (pre-processed) version
ppls documents download 1234 --original
```

## Uploading Documents

```bash
# Simple upload (Paperless auto-processes)
ppls documents add scan.pdf

# With metadata
ppls documents add receipt.pdf \
  --title "Store Receipt" \
  --correspondent 5 \
  --document-type 2 \
  --tag 10
```

## Managing Metadata

```bash
# List tags/correspondents/document-types
ppls tags list --json
ppls correspondents list --json
ppls document-types list --json

# Create new
ppls tags add "Tax 2024" --color "#ff0000"
ppls correspondents add "New Vendor"
ppls document-types add "Contract"

# Update document metadata
ppls documents update 1234 --title "New Title" --correspondent 5 --tag 10
```

## Tips

- **Always use `--json`** for AI/automation — it's the most parseable format
- **Date formats:** `YYYY-MM-DD` or full ISO 8601
- **IDs are numeric** — use `list --json` commands to find them
- **Filters are repeatable:** `--tag 1 --tag 2` or `--tag 1,2` both work
- **Pagination:** Use `--page` and `--page-size` for large result sets

## Links

- [ppls on GitHub](https://github.com/NickChristensen/ppls)
- [Paperless-NGX Docs](https://docs.paperless-ngx.com/)
