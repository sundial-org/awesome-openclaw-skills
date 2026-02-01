---
name: static-files
description: >
  Host static files on subdomains with optional authentication. Use when you need to
  serve HTML, images, CSS, JS, or any static content on a dedicated subdomain. Supports
  file upload, basic auth, quota management, and automatic SSL via Caddy. Commands
  include sf sites (create/list/delete), sf upload (files/directories), sf files (list/delete).
---

# Static Files Hosting

Host static content on `*.{domain}` subdomains with automatic SSL.

## Quick Reference

```bash
# Create site
sf sites create mysite
# → https://mysite.498as.com

# Upload file
sf upload ./index.html mysite

# Upload directory  
sf upload ./dist mysite

# Add authentication
sf sites auth mysite admin:secretpass123

# List files
sf files mysite

# Delete file
sf files mysite delete path/to/file.txt

# Delete site
sf sites delete mysite
```

## Environment Setup

```bash
export SF_API_URL=http://localhost:3000   # API endpoint
export SF_API_KEY=sk_xxxxx                # Your API key
```

## Workflows

### Deploy a Static Website

```bash
# 1. Create the site
sf sites create docs

# 2. Upload the build directory
sf upload ./build docs

# 3. Verify
curl -I https://docs.498as.com
```

### Protected File Sharing

```bash
# 1. Create site with auth
sf sites create private
sf sites auth private user:strongpassword

# 2. Upload sensitive files
sf upload ./reports private

# 3. Share URL + credentials
# https://private.498as.com (user / strongpassword)
```

### Update Existing Files

```bash
# Overwrite existing file
sf upload ./new-version.pdf mysite --overwrite

# Or delete and re-upload
sf files mysite delete old-file.pdf
sf upload ./new-file.pdf mysite
```

## CLI Commands

### sites

| Command | Description |
|---------|-------------|
| `sf sites list` | List all sites |
| `sf sites create <name>` | Create new site |
| `sf sites delete <name>` | Delete site and all files |
| `sf sites auth <name> <user:pass>` | Set basic auth |
| `sf sites auth <name> --remove` | Remove auth |

### upload

```bash
sf upload <path> <site> [subdir] [--overwrite] [--json]
```

- `path`: File or directory to upload
- `site`: Target site name
- `subdir`: Optional subdirectory
- `--overwrite`: Replace existing files
- `--json`: Output JSON

### files

| Command | Description |
|---------|-------------|
| `sf files <site>` | List all files |
| `sf files <site> delete <path>` | Delete specific file |

### stats

```bash
sf stats              # Global stats
sf stats <site>       # Site-specific stats
```

## API Endpoints

Base: `$SF_API_URL` with `Authorization: Bearer $SF_API_KEY`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/sites` | List sites |
| POST | `/sites` | Create site |
| DELETE | `/sites/{name}` | Delete site |
| PATCH | `/sites/{name}` | Update auth |
| GET | `/sites/{name}/files` | List files |
| POST | `/sites/{name}/files` | Upload file |
| DELETE | `/sites/{name}/files/{path}` | Delete file |
| GET | `/stats` | Global stats |
| GET | `/stats/{name}` | Site stats |
| GET | `/health` | Health check |

## Constraints

- **Site names**: lowercase, alphanumeric, hyphens only (max 63 chars)
- **File size**: 50MB default (configurable)
- **Quota**: 100MB per site default
- **Rate limit**: 100 requests/minute per API key

## Troubleshooting

### "Cannot connect to API"
```bash
# Check service status
systemctl status kleo-static-files

# Check if port is listening
curl http://localhost:3000/health
```

### "Invalid API key"
```bash
# Verify key is set
echo $SF_API_KEY

# Create new key if needed
bun run /opt/kleo-static-files/scripts/create-key.ts "new-key"
```

### "Quota exceeded"
```bash
# Check current usage
sf stats mysite

# Delete unused files
sf files mysite delete large-file.zip
```

### Site not accessible via HTTPS
```bash
# Verify DNS points to server
dig mysite.498as.com

# Check Caddy config
cat /etc/caddy/sites.d/static-files.caddy

# Resync Caddy
bun run /opt/kleo-static-files/scripts/sync-caddy.ts --reload
```

## Installation

### Server Installation (run once on host)

```bash
curl -fsSL https://raw.githubusercontent.com/498AS/kleo-static-files/main/install.sh | sudo bash
```

The installer outputs JSON with connection details between `KLEO_SF_CONFIG_BEGIN` and `KLEO_SF_CONFIG_END` markers. Parse this to get `api_url` and `api_key`.

### After Installation

```bash
export SF_API_URL=http://localhost:3000
export SF_API_KEY=sk_xxxxx  # from installer output
```

### Check Status

```bash
sudo /opt/kleo-static-files/install.sh --status
```

See [references/install.md](references/install.md) for manual installation.
