---
name: canva
version: 1.0.0
description: |
  Manage Canva designs, assets, and folders via the Connect API.
  
  WHAT IT CAN DO:
  - List/search/organize designs and folders
  - Export finished designs (PNG/PDF/JPG)
  - Upload images to asset library
  - Autofill brand templates with data
  - Create blank designs (doc/presentation/whiteboard/custom)
  
  WHAT IT CANNOT DO:
  - Add content to designs (text, shapes, elements)
  - Edit existing design content
  - Upload documents (images only)
  - AI design generation
  
  Best for: asset pipelines, export automation, organization, template autofill.
  Triggers: /canva, "upload to canva", "export design", "list my designs", "canva folder".
author: clawdbot
license: MIT
metadata:
  clawdbot:
    emoji: "🎨"
    triggers: ["/canva"]
    requires:
      env:
        - CANVA_CLIENT_ID
        - CANVA_CLIENT_SECRET
    primaryEnv: CANVA_CLIENT_ID
    homepage: https://canva.dev/docs/connect/
---

# Canva Connect

Manage Canva designs, assets, and folders via the Connect API.

## What This Skill Does (and Doesn't Do)

| ✅ CAN DO | ❌ CANNOT DO |
|-----------|--------------|
| List/search designs | Add content to designs |
| Create blank designs | Edit existing design content |
| Export designs (PNG/PDF/JPG) | Upload documents (images only) |
| Create/manage folders | AI design generation |
| Move items between folders | |
| Upload images as assets | |
| Autofill brand templates | |

## Realistic Use Cases

**1. Asset Pipeline** 🖼️
```
Generate diagram → upload to Canva → organize in project folder
```

**2. Export Automation** 📤
```
Design finished in Canva → export via CLI → use in docs/website
```

**3. Design Organization** 📁
```
Create project folders → move related designs → keep Canva tidy
```

**4. Brand Template Autofill** 📋
```
Set up template in Canva → pass data via API → get personalized output
```

## Quick Start

```bash
# Authenticate (opens browser for OAuth)
{baseDir}/scripts/canva.sh auth

# List your designs
{baseDir}/scripts/canva.sh designs list

# Create a new design
{baseDir}/scripts/canva.sh designs create --type doc --title "My Document"

# Export a design
{baseDir}/scripts/canva.sh export <design_id> --format pdf
```

## Setup

### 1. Create Canva Integration

1. Go to [canva.com/developers/integrations](https://canva.com/developers/integrations)
2. Click **Create an integration**
3. Set scopes:
   - `design:content` (Read + Write)
   - `design:meta` (Read)
   - `asset` (Read + Write)
   - `brandtemplate:meta` (Read)
   - `brandtemplate:content` (Read)
   - `profile` (Read)
4. Set OAuth redirect: `http://127.0.0.1:3001/oauth/redirect`
5. Note **Client ID** and generate **Client Secret**

### 2. Configure Environment

Add to `~/.clawdbot/clawdbot.json` under `skills.entries`:

```json
{
  "skills": {
    "entries": {
      "canva": {
        "clientId": "YOUR_CLIENT_ID",
        "clientSecret": "YOUR_CLIENT_SECRET"
      }
    }
  }
}
```

Or set environment variables:
```bash
export CANVA_CLIENT_ID="your_client_id"
export CANVA_CLIENT_SECRET="your_client_secret"
```

### 3. Authenticate

```bash
{baseDir}/scripts/canva.sh auth
```

Opens browser for OAuth consent. Tokens stored in `~/.clawdbot/canva-tokens.json`.

## Commands

### Authentication
| Command | Description |
|---------|-------------|
| `auth` | Start OAuth flow (opens browser) |
| `auth status` | Check authentication status |
| `auth logout` | Clear stored tokens |

### Designs
| Command | Description |
|---------|-------------|
| `designs list [--limit N]` | List your designs |
| `designs get <id>` | Get design details |
| `designs create --type <type> --title <title>` | Create new design |
| `designs delete <id>` | Move design to trash |

**Design types:** `doc`, `presentation`, `whiteboard`, `poster`, `instagram_post`, `facebook_post`, `video`, `logo`, `flyer`, `banner`

### Export
| Command | Description |
|---------|-------------|
| `export <design_id> --format <fmt>` | Export design |
| `export status <job_id>` | Check export job status |

**Formats:** `pdf`, `png`, `jpg`, `gif`, `pptx`, `mp4`

### Assets
| Command | Description |
|---------|-------------|
| `assets list` | List uploaded assets |
| `assets upload <file> [--name <name>]` | Upload asset |
| `assets get <id>` | Get asset details |
| `assets delete <id>` | Delete asset |

### Brand Templates
| Command | Description |
|---------|-------------|
| `templates list` | List brand templates |
| `templates get <id>` | Get template details |
| `autofill <template_id> --data <json>` | Autofill template with data |

### Folders
| Command | Description |
|---------|-------------|
| `folders list` | List folders |
| `folders create <name>` | Create folder |
| `folders get <id>` | Get folder contents |

### User
| Command | Description |
|---------|-------------|
| `me` | Get current user profile |

## Examples

### Create and Export a Poster
```bash
# Create
{baseDir}/scripts/canva.sh designs create --type poster --title "Event Poster"

# Export as PNG
{baseDir}/scripts/canva.sh export DAF... --format png --output ./poster.png
```

### Upload Brand Assets
```bash
# Upload logo
{baseDir}/scripts/canva.sh assets upload ./logo.png --name "Company Logo"

# Upload multiple
for f in ./brand/*.png; do
  {baseDir}/scripts/canva.sh assets upload "$f"
done
```

### Autofill a Template
```bash
# List available templates
{baseDir}/scripts/canva.sh templates list

# Autofill with data
{baseDir}/scripts/canva.sh autofill TEMPLATE_ID --data '{
  "title": "Q1 Report",
  "subtitle": "Financial Summary",
  "date": "January 2026"
}'
```

## API Reference

Base URL: `https://api.canva.com/rest`

See [references/api.md](references/api.md) for detailed endpoint documentation.

## Troubleshooting

### Token Expired
```bash
{baseDir}/scripts/canva.sh auth  # Re-authenticate
```

### Rate Limited
The API has per-endpoint rate limits. The script handles backoff automatically.

### Missing Scopes
If operations fail with 403, ensure your integration has the required scopes enabled.

## Data Files

| File | Purpose |
|------|---------|
| `~/.clawdbot/canva-tokens.json` | OAuth tokens (encrypted) |
| `~/.clawdbot/canva-cache.json` | Response cache |
