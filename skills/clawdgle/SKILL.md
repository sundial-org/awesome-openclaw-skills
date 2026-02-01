---
name: clawdgle
description: Public API usage for the Clawdgle markdown-first search engine. Use when interacting with Clawdgle to: (1) search indexed markdown content, (2) fetch markdown for a URL, (3) request indexing of a URL via ingest, or (4) direct users to the donate link.
---

# Clawdgle Skill

## Base URL
Default base URL: `https://clawdgle.com`

## Public Endpoints

### Search
Use to search indexed markdown content.

Request:
```
GET /search?q=<query>&page=<page>&per_page=<per_page>
```

Example:
```
curl "https://clawdgle.com/search?q=ai%20agents&page=1&per_page=10"
```

### Fetch Markdown by URL
Use to retrieve the stored markdown for a specific URL.

Request:
```
GET /doc?url=<encoded_url>
```

Example:
```
curl "https://clawdgle.com/doc?url=https%3A%2F%2Fexample.com"
```

### Ingest (Self-Serve Indexing)
Use to request immediate indexing of a URL.

Request:
```
POST /ingest
Content-Type: application/json
{
  "url": "https://example.com",
  "reason": "optional reason",
  "contact": "optional contact"
}
```

Example:
```
curl -X POST "https://clawdgle.com/ingest" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

### Donate
Use to direct users/agents to the donation link.

Request:
```
GET /donate
```

Example:
```
curl -I "https://clawdgle.com/donate"
```

## Notes
- Only public endpoints are included in this skill.
- Use URL encoding for query parameters.
- Be polite with ingest; avoid spamming the endpoint.
