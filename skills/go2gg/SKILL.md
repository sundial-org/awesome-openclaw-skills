---
name: go2gg
description: Use Go2.gg API for URL shortening, link analytics, QR code generation, webhooks, and link-in-bio pages. Use when the user needs to create short links, track clicks, generate QR codes, set up link-in-bio pages, or manage branded URLs. Free tier includes short links, QR codes, and analytics. Requires GO2GG_API_KEY env var. QR code generation is free without auth.
---

# Go2.gg — Edge-Native URL Shortener

URL shortening, analytics, QR codes, webhooks, galleries (link-in-bio). Built on Cloudflare's edge network with sub-10ms redirects globally.

## Setup

Get API key from: https://go2.gg/dashboard/api-keys (free, no credit card required)

```bash
export GO2GG_API_KEY="go2_your_key_here"
```

**API base:** `https://api.go2.gg/api/v1`
**Auth:** `Authorization: Bearer $GO2GG_API_KEY`
**Docs:** https://go2.gg/docs/api/links

---

## Short Links

Create, manage, and track short links with custom slugs, tags, expiration, passwords, and geo/device targeting.

### Create a Link

```bash
curl -X POST "https://api.go2.gg/api/v1/links" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "destinationUrl": "https://example.com/landing-page",
    "slug": "my-link",
    "title": "My Campaign Link",
    "tags": ["marketing", "q1-2025"]
  }'
```

**Important:** Field is `destinationUrl` (not `url`). Slug is optional (auto-generated if omitted).

### Response

```json
{
  "success": true,
  "data": {
    "id": "lnk_abc123",
    "shortUrl": "https://go2.gg/my-link",
    "destinationUrl": "https://example.com/landing-page",
    "slug": "my-link",
    "domain": "go2.gg",
    "title": "My Campaign Link",
    "tags": ["marketing", "q1-2025"],
    "clickCount": 0,
    "createdAt": "2025-01-01T10:30:00Z"
  }
}
```

### List Links

```bash
# List all links (paginated)
curl "https://api.go2.gg/api/v1/links?perPage=20&sort=clicks" \
  -H "Authorization: Bearer $GO2GG_API_KEY"

# Search links
curl "https://api.go2.gg/api/v1/links?search=marketing&tag=q1-2025" \
  -H "Authorization: Bearer $GO2GG_API_KEY"
```

**Query params:** `page`, `perPage` (max 100), `search`, `domain`, `tag`, `archived`, `sort` (created/clicks/updated)

### Update a Link

```bash
curl -X PATCH "https://api.go2.gg/api/v1/links/lnk_abc123" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"destinationUrl": "https://example.com/updated-page", "tags": ["updated"]}'
```

### Delete a Link

```bash
curl -X DELETE "https://api.go2.gg/api/v1/links/lnk_abc123" \
  -H "Authorization: Bearer $GO2GG_API_KEY"
# Returns 204 No Content
```

### Link Analytics

```bash
curl "https://api.go2.gg/api/v1/links/lnk_abc123/stats" \
  -H "Authorization: Bearer $GO2GG_API_KEY"
```

Returns: `totalClicks`, `byCountry`, `byDevice`, `byBrowser`, `byReferrer`, `overTime`

### Advanced Link Options

```bash
# Password-protected link
curl -X POST "https://api.go2.gg/api/v1/links" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"destinationUrl": "https://example.com/secret", "slug": "exclusive", "password": "secure123"}'

# Link with expiration + click limit
curl -X POST "https://api.go2.gg/api/v1/links" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"destinationUrl": "https://example.com/flash", "expiresAt": "2025-12-31T23:59:59Z", "clickLimit": 1000}'

# Geo-targeted link (different URLs per country)
curl -X POST "https://api.go2.gg/api/v1/links" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "destinationUrl": "https://example.com/default",
    "geoTargets": {"US": "https://example.com/us", "GB": "https://example.com/uk", "IN": "https://example.com/in"}
  }'

# Device-targeted link + app deep links
curl -X POST "https://api.go2.gg/api/v1/links" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "destinationUrl": "https://example.com/default",
    "deviceTargets": {"mobile": "https://m.example.com"},
    "iosUrl": "https://apps.apple.com/app/myapp",
    "androidUrl": "https://play.google.com/store/apps/details?id=com.myapp"
  }'

# Link with UTM parameters
curl -X POST "https://api.go2.gg/api/v1/links" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "destinationUrl": "https://example.com/product",
    "slug": "summer-sale",
    "utmSource": "email",
    "utmMedium": "newsletter",
    "utmCampaign": "summer-sale"
  }'
```

### Create Link Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| destinationUrl | string | yes | Target URL to redirect to |
| slug | string | no | Custom slug (auto-generated if omitted) |
| domain | string | no | Custom domain (default: go2.gg) |
| title | string | no | Link title |
| description | string | no | Link description |
| tags | string[] | no | Tags for filtering |
| password | string | no | Password protection |
| expiresAt | string | no | ISO 8601 expiration date |
| clickLimit | number | no | Max clicks allowed |
| geoTargets | object | no | Country → URL mapping |
| deviceTargets | object | no | Device → URL mapping |
| iosUrl | string | no | iOS app deep link |
| androidUrl | string | no | Android app deep link |
| utmSource/Medium/Campaign/Term/Content | string | no | UTM parameters |

---

## QR Codes

Generate customizable QR codes. **QR generation is free and requires no auth.**

### Generate QR Code (No Auth Required)

```bash
# Generate SVG QR code (free, no API key needed)
curl -X POST "https://api.go2.gg/api/v1/qr/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://go2.gg/my-link",
    "size": 512,
    "foregroundColor": "#1a365d",
    "backgroundColor": "#FFFFFF",
    "cornerRadius": 10,
    "errorCorrection": "H",
    "format": "svg"
  }' -o qr-code.svg

# PNG format
curl -X POST "https://api.go2.gg/api/v1/qr/generate" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "format": "png", "size": 1024}' -o qr-code.png
```

### QR Parameters

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| url | string | required | URL to encode |
| size | number | 256 | Size in pixels (64-2048) |
| foregroundColor | string | #000000 | Hex color for modules |
| backgroundColor | string | #FFFFFF | Hex color for background |
| cornerRadius | number | 0 | Module corner radius (0-50) |
| errorCorrection | string | M | L (7%), M (15%), Q (25%), H (30%) |
| format | string | svg | svg or png |

### Save & Track QR Codes (Auth Required)

```bash
# Save QR config for tracking
curl -X POST "https://api.go2.gg/api/v1/qr" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Business Card QR", "url": "https://go2.gg/contact", "linkId": "lnk_abc123"}'

# List saved QR codes
curl "https://api.go2.gg/api/v1/qr" -H "Authorization: Bearer $GO2GG_API_KEY"

# Download saved QR
curl "https://api.go2.gg/api/v1/qr/qr_abc123/download?format=svg" \
  -H "Authorization: Bearer $GO2GG_API_KEY" -o qr.svg

# Delete QR
curl -X DELETE "https://api.go2.gg/api/v1/qr/qr_abc123" -H "Authorization: Bearer $GO2GG_API_KEY"
```

---

## Webhooks

Receive real-time notifications for link clicks, creations, and updates.

```bash
# Create webhook
curl -X POST "https://api.go2.gg/api/v1/webhooks" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Click Tracker", "url": "https://your-server.com/webhook", "events": ["click", "link.created"]}'

# List webhooks
curl "https://api.go2.gg/api/v1/webhooks" -H "Authorization: Bearer $GO2GG_API_KEY"

# Test webhook
curl -X POST "https://api.go2.gg/api/v1/webhooks/wh_abc123/test" \
  -H "Authorization: Bearer $GO2GG_API_KEY"

# Delete webhook
curl -X DELETE "https://api.go2.gg/api/v1/webhooks/wh_abc123" \
  -H "Authorization: Bearer $GO2GG_API_KEY"
```

**Events:** `click`, `link.created`, `link.updated`, `link.deleted`, `domain.verified`, `qr.scanned`, `*` (all)

Webhook payloads include `X-Webhook-Signature` (HMAC SHA256) for verification. Retries: 5s → 30s → 2m → 10m.

---

## Galleries (Link-in-Bio)

Create link-in-bio pages programmatically.

```bash
# Create gallery
curl -X POST "https://api.go2.gg/api/v1/galleries" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"slug": "myprofile", "title": "My Name", "bio": "Creator & developer", "theme": "gradient"}'

# Add link item
curl -X POST "https://api.go2.gg/api/v1/galleries/gal_abc123/items" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "link", "title": "My Website", "url": "https://example.com"}'

# Add YouTube embed
curl -X POST "https://api.go2.gg/api/v1/galleries/gal_abc123/items" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "embed", "title": "Latest Video", "embedType": "youtube", "embedData": {"videoId": "dQw4w9WgXcQ"}}'

# Publish gallery (makes it live at go2.gg/bio/myprofile)
curl -X POST "https://api.go2.gg/api/v1/galleries/gal_abc123/publish" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"isPublished": true}'

# Reorder items
curl -X PATCH "https://api.go2.gg/api/v1/galleries/gal_abc123/items/reorder" \
  -H "Authorization: Bearer $GO2GG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"itemIds": ["item_3", "item_1", "item_2"]}'

# List galleries
curl "https://api.go2.gg/api/v1/galleries" -H "Authorization: Bearer $GO2GG_API_KEY"
```

**Themes:** default, minimal, gradient, dark, neon, custom (with customCss)
**Item types:** link, header, divider, embed (youtube), image

---

## Python Example

```python
import requests

API_KEY = "go2_your_key_here"  # or os.environ["GO2GG_API_KEY"]
BASE = "https://api.go2.gg/api/v1"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Create short link
resp = requests.post(f"{BASE}/links", headers=headers, json={
    "destinationUrl": "https://example.com/product",
    "slug": "my-product",
    "title": "Product Link",
    "tags": ["product"]
})
link = resp.json()["data"]
print(f"Short URL: {link['shortUrl']}")

# Get analytics
stats = requests.get(f"{BASE}/links/{link['id']}/stats", headers=headers).json()["data"]
print(f"Clicks: {stats['totalClicks']}")

# Generate QR (no auth needed)
qr = requests.post(f"{BASE}/qr/generate", json={"url": link["shortUrl"], "size": 512, "format": "png"})
with open("qr.png", "wb") as f:
    f.write(qr.content)
```

---

## API Endpoint Summary

| Service | Endpoint | Method | Auth |
|---------|----------|--------|------|
| **Links** create | `/api/v1/links` | POST | yes |
| Links list | `/api/v1/links` | GET | yes |
| Links get | `/api/v1/links/:id` | GET | yes |
| Links update | `/api/v1/links/:id` | PATCH | yes |
| Links delete | `/api/v1/links/:id` | DELETE | yes |
| Links stats | `/api/v1/links/:id/stats` | GET | yes |
| **QR** generate | `/api/v1/qr/generate` | POST | **no** |
| QR save | `/api/v1/qr` | POST | yes |
| QR list | `/api/v1/qr` | GET | yes |
| QR download | `/api/v1/qr/:id/download` | GET | yes |
| **Webhooks** | `/api/v1/webhooks` | CRUD | yes |
| Webhook test | `/api/v1/webhooks/:id/test` | POST | yes |
| **Galleries** | `/api/v1/galleries` | CRUD | yes |
| Gallery items | `/api/v1/galleries/:id/items` | CRUD | yes |
| Gallery publish | `/api/v1/galleries/:id/publish` | POST | yes |

## Rate Limits

| Plan | Requests/min |
|------|-------------|
| Free | 60 |
| Pro | 300 |
| Business | 1000 |

## Error Codes

| Code | Description |
|------|-------------|
| SLUG_RESERVED | Slug is reserved |
| SLUG_EXISTS | Slug already in use on this domain |
| INVALID_URL | Destination URL is invalid |
| LIMIT_REACHED | Plan's link limit reached |
| DOMAIN_NOT_VERIFIED | Custom domain not verified |
