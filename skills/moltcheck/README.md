# 🛡️ MoltCheck Skill

Security scanner for Moltbot skills. Scan GitHub repositories for security risks before installation.

## Installation

```bash
# Clone the skill
git clone https://github.com/moltcheck/moltcheck-skill

# Or use directly
npx moltcheck-skill scan https://github.com/owner/repo
```

## Usage

### Scan a repository
```bash
node index.js scan https://github.com/owner/repo
```

### Check your credits
```bash
node index.js credits
```

### Get an API key
```bash
node index.js setup
```

## Configuration

Set your API key as an environment variable:
```bash
export MOLTCHECK_API_KEY=mc_your_api_key_here
```

Or use the free tier (3 scans/day) without configuration.

## Pricing

| Tier | Scans | Cost |
|------|-------|------|
| Free | 3/day | $0 |
| Paid | Unlimited | $0.20/scan |

Pay with SOL at [moltcheck.com/buy](https://moltcheck.com/buy)

## Example Output

```json
{
  "url": "https://github.com/example/skill",
  "score": 85,
  "grade": "👍 B",
  "type": "🦞 Moltbot Skill",
  "summary": "👍 Generally safe with some capabilities to review.",
  "risks": [
    {
      "level": "🟡 MEDIUM",
      "issue": "Makes HTTP requests",
      "file": "src/api.js"
    }
  ]
}
```

## Links

- 🌐 [MoltCheck Website](https://moltcheck.com)
- 📚 [API Documentation](https://moltcheck.com/api-docs.md)
- 🤖 [OpenAPI Spec](https://moltcheck.com/openapi.json)

## License

MIT
