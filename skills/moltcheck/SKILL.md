---
name: moltcheck
description: Security scanner for Moltbot skills. Scan GitHub repositories for vulnerabilities before installation.
---

# MoltCheck Skill

MoltCheck is a comprehensive security scanner designed specifically for the Moltbot ecosystem. It analyzes GitHub repositories and agent skills for security vulnerabilities, providing:

🔍 **Automated Code Scanning** - Detects dangerous patterns like credential theft, shell access, and hidden network calls

📊 **Trust Scoring** - A-F grades based on comprehensive risk analysis

🔑 **Permission Auditing** - Compares declared permissions (in SKILL.md) against actual code behavior

💡 **Clear Communication** - Explains security risks in plain language

Essential for agents who install external skills and want to avoid supply chain attacks.

Website: https://moltcheck.com

## Capabilities

- **Network Access** - Calls MoltCheck API

## Commands

### `scan <github_url>`
Scan a GitHub repository for security issues.

**Example:**
```
scan https://github.com/owner/repo
```

**Returns:** Trust score (0-100), grade (A-F), risks found, permission analysis.

### `credits`
Check your remaining scan credits.

### `setup`
Generate an API key and get payment instructions for credits.

## Configuration

Set your API key in the skill config:
```json
{
  "apiKey": "mc_your_api_key_here"
}
```

Or use the free tier (3 scans/day) without an API key.

## Pricing

- **Free tier:** 3 scans/day
- **Paid:** From $0.05/scan with bulk discounts

| Amount | Rate |
|--------|------|
| Under $10 | $0.20/scan |
| $10+ | $0.10/scan |
| $25+ | $0.05/scan |

Get credits at https://moltcheck.com/buy

## Links

- Website: https://moltcheck.com
- API Docs: https://moltcheck.com/api-docs.md
- OpenAPI: https://moltcheck.com/openapi.json
