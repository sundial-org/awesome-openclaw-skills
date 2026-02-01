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

### Rank Users (Main Endpoint)

Search and rank GitHub developers by location and tech stack.

```bash
curl -X POST "https://api.githunt.ai/v1/rank/users" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "berlin",
    "role": "frontend",
    "skills": ["react", "typescript"],
    "maxUsers": 50
  }'
```

**Body Parameters:**
| Param | Required | Description |
|-------|----------|-------------|
| `location` | Yes | City, country, or region (e.g., "berlin", "germany", "san francisco") |
| `role` | No | Role type: "frontend", "backend", "fullstack", "devops", "mobile", "data" |
| `skills` | No | Array of technology keywords to match |
| `maxUsers` | No | Max users to return (default: 100, max: 1000) |

### Rank Users Streaming

Same as above but returns results via Server-Sent Events for real-time updates.

```bash
curl -X POST "https://api.githunt.ai/v1/rank/users/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "location": "london",
    "skills": ["python", "django"],
    "maxUsers": 100
  }'
```

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

## Usage Examples

### Find React Developers in Berlin
```bash
curl -s -X POST "https://api.githunt.ai/v1/rank/users" \
  -H "Content-Type: application/json" \
  -d '{"location": "berlin", "skills": ["react", "typescript"], "maxUsers": 10}' \
  | gunzip | jq '.results[:5] | .[] | {login, name, score, location}'
```

### Find Backend Engineers in Europe
```bash
curl -s -X POST "https://api.githunt.ai/v1/rank/users" \
  -H "Content-Type: application/json" \
  -d '{"location": "europe", "role": "backend", "skills": ["go", "kubernetes"], "maxUsers": 20}' \
  | gunzip | jq '.results'
```

### Score a Specific Candidate
```bash
curl -s -X POST "https://api.githunt.ai/v1/rank/user" \
  -H "Content-Type: application/json" \
  -d '{"username": "DHH", "skills": ["ruby", "rails"]}' | jq
```

## Response Format

Results include:
```json
{
  "results": [
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
      "followers": 1234,
      "repositories": 45,
      "primaryLanguage": "TypeScript",
      "languages": ["TypeScript", "Python", "Go"],
      "technologies": ["react", "node", "aws"],
      "avatarUrl": "https://avatars.githubusercontent.com/...",
      "scoreDetails": {
        "totalScore": 85,
        "activityScore": 9,
        "techStackScore": 8,
        "profileScore": 7,
        "matchedTechnologies": ["react", "typescript"]
      }
    }
  ],
  "totalCount": 150,
  "dataSource": "github-api"
}
```

## Scoring System

Candidates are scored 0-100 based on:

1. **Tech Stack Match** (weighted highest)
   - Languages in repos match requested skills
   - Bio/readme mentions relevant technologies
   - Smart keyword matching (e.g., "k8s" → "kubernetes")

2. **Activity Score**
   - Recent commits and contributions
   - PR and issue activity
   - Contribution calendar analysis

3. **Repository Quality**
   - Stars and forks on repos
   - Number of public repositories
   - Code quality indicators

4. **Profile Completeness**
   - Bio present
   - Hireable flag set
   - Contact info available (email, website, Twitter)

## Role Presets

Use `role` parameter for pre-configured skill sets:

| Role | Auto-includes |
|------|---------------|
| `frontend` | react, vue, angular, typescript, css |
| `backend` | node, python, java, go, rust |
| `fullstack` | react, node, typescript, postgresql |
| `devops` | kubernetes, docker, terraform, aws |
| `mobile` | swift, kotlin, react-native, flutter |
| `data` | python, sql, spark, tensorflow |

## Tips

1. **Combine location + skills** for best results
2. **Response is gzipped** - pipe through `gunzip` or use `--compressed` with curl
3. **Use streaming endpoint** for large searches (100+ users)
4. **Be specific with location** - "san francisco" works better than "usa"

## Rate Limits

- Free tier: Limited preview (first 15 results)
- Paid: Full results via githunt.ai checkout

## Integration Ideas

- **Recruiting pipeline**: Search → Filter by score → Export contacts
- **Talent mapping**: Analyze developer density by location/tech
- **Competitive intel**: Track where top talent is concentrated
- **Outreach automation**: Get emails for high-score hireable candidates
