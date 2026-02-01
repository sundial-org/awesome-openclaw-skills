---
name: githunt
description: Find and rank GitHub developers by location, technology, and role. Search for candidates, get scored profiles with tech stack matches, activity, and contact info.
version: 1.0.0
author: mordka
---

# GitHunt - GitHub Developer Discovery

Find top developers on GitHub by location, tech stack, and role. Get scored, ranked candidates with detailed profiles.

**Website:** https://githunt.ai

## When to Use

- Finding developers/candidates in a specific location
- Searching for developers with specific tech stacks
- Recruiting/sourcing engineers
- Building talent pipelines

## API Endpoints

Base URL: `https://api.githunt.ai/v1`

### Search Developers (Streaming) - Main Endpoint

Real-time streaming search that returns candidates as they're found. Returns **top 10 sample results** for free.

```bash
curl -N -X POST "https://api.githunt.ai/v1/rank/users/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "location": "berlin",
    "role": "frontend",
    "skills": ["react", "typescript"],
    "maxUsers": 100
  }'
```

**Body Parameters:**
| Param | Required | Description |
|-------|----------|-------------|
| `location` | Yes | City, country, or region (e.g., "berlin", "germany", "san francisco") |
| `role` | No | Role type (see Supported Roles below) |
| `skills` | No | Array of technology keywords to match |
| `maxUsers` | No | Max users to search (default: 100) |

### Supported Roles

| Role | Technologies Included |
|------|----------------------|
| `frontend` | react, vue, angular, svelte, typescript, css, tailwind, nextjs |
| `backend` | nodejs, python, django, flask, go, rust, java, spring, postgresql |
| `fullstack` | react, nodejs, nextjs, postgresql, typescript, graphql |
| `mobile` | react-native, flutter, swift, kotlin, ios, android |
| `devops` | docker, kubernetes, terraform, aws, azure, jenkins, github-actions |
| `data` | python, pandas, tensorflow, pytorch, spark, sql, jupyter |
| `security` | penetration, owasp, cryptography, ethical-hacking, forensics |
| `blockchain` | ethereum, solidity, web3, smart-contract, defi, nft |
| `ai` | machine-learning, pytorch, tensorflow, llm, langchain, huggingface |
| `gaming` | unity, unreal, godot, opengl, vulkan, game-engine |

### Rank Single User

Get detailed score for a specific GitHub user.

```bash
curl -X POST "https://api.githunt.ai/v1/rank/user" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "torvalds",
    "skills": ["c", "linux"]
  }'
```

## Stream Response Format

The streaming endpoint returns Server-Sent Events (SSE):

```
data: {"type": "connected", "timestamp": 1234567890}

data: {"type": "user", "data": {"login": "developer1", "name": "...", "score": 85, ...}}

data: {"type": "user", "data": {"login": "developer2", "name": "...", "score": 82, ...}}

data: {"type": "progress", "data": {"found": 10, "searched": 50}}

data: {"type": "complete", "data": {"totalCount": 150, "previewLimitReached": true, "previewLimit": 10}}
```

## User Data Fields

Each user result includes:
```json
{
  "login": "username",
  "name": "Full Name",
  "bio": "Developer bio",
  "location": "Berlin, Germany",
  "company": "@company",
  "email": "dev@example.com",
  "websiteUrl": "https://...",
  "twitterUsername": "handle",
  "isHireable": true,
  "score": 85,
  "avatarUrl": "https://avatars.githubusercontent.com/...",
  "followers": 1234,
  "repositories": 45,
  "primaryLanguage": "TypeScript",
  "languages": ["TypeScript", "Python", "Go"],
  "matchingKeywords": ["react", "typescript", "node"]
}
```

## Free vs Paid

| Feature | Free (via API) | Full Report ($19) |
|---------|----------------|-------------------|
| Results | Top 10 sample | All matched developers |
| Export | — | Excel/CSV download |
| Contact info | Limited | Full (emails, websites, socials) |
| Scoring details | Basic | Detailed breakdown |

### 💰 Get Full Report

For the complete list of all matched developers with full contact info:

1. Go to **https://githunt.ai**
2. Run your search with location + role
3. Click **"Buy Full Report"** ($19 one-time)
4. Get Excel report with all candidates

## Usage Examples

### Find React Developers in Berlin (Streaming)
```bash
curl -N -X POST "https://api.githunt.ai/v1/rank/users/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"location": "berlin", "role": "frontend"}' 2>/dev/null | \
  grep -o '{"type":"user"[^}]*}' | head -5
```

### Score a Specific Candidate
```bash
curl -s -X POST "https://api.githunt.ai/v1/rank/user" \
  -H "Content-Type: application/json" \
  -d '{"username": "sindresorhus", "skills": ["javascript", "typescript"]}' | jq
```

## Tips

1. **Be specific with location** - "san francisco" works better than "usa"
2. **Use role OR skills** - role auto-includes relevant tech keywords
3. **Streaming is real-time** - results appear as they're found
4. **Free preview = top 10** - buy full report for complete list
