---
name: jules-api
description: "Use the Jules REST API (v1alpha) via curl (exec) to list sources, create sessions, monitor activities, approve plans, and retrieve outputs (e.g., PR URLs). Use when the user wants to delegate coding tasks to Jules programmatically without the Jules CLI."
---

# Jules REST API (curl via exec)

This skill uses **curl** to talk directly to the **Jules REST API**.

Docs: https://jules.google/docs/api/reference/

## Prereqs

### 1) Get an API key
Create a Jules API key in the Jules web app:
- https://jules.google.com/settings#api

Export it on the machine running Clawdbot:

```bash
export JULES_API_KEY="..."
```

Requests authenticate with:

```bash
-H "x-goog-api-key: $JULES_API_KEY"
```

### 2) Connect your GitHub repo as a Source
Before the API can operate on a GitHub repo, you must install the **Jules GitHub app** via the Jules web UI for that repo.

## Base URL
- `https://jules.googleapis.com/v1alpha`

## Core workflow

### A) List Sources (find repo source name)
```bash
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sources"
```

You’re looking for entries like:
- `name: "sources/github/<owner>/<repo>"`

### B) Create a Session (delegate a task)
```bash
curl -sS "https://jules.googleapis.com/v1alpha/sessions" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -d '{
    "prompt": "<TASK>",
    "title": "<SHORT TITLE>",
    "sourceContext": {
      "source": "sources/github/<owner>/<repo>",
      "githubRepoContext": {
        "startingBranch": "main"
      }
    },
    "automationMode": "AUTO_CREATE_PR"
  }'
```

Notes:
- `automationMode` is optional; omit it if you don’t want auto PR creation.
- By default, sessions created through the API have plans automatically approved.
  If you want explicit plan approval, set `requirePlanApproval: true`.

### C) List Sessions (find session id)
```bash
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions?pageSize=20"
```

### D) Monitor a Session (list Activities)
```bash
curl -sS \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID/activities?pageSize=30"
```

### E) Send a message into a Session
```bash
curl -sS \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:sendMessage" \
  -d '{"prompt": "<MESSAGE>"}'
```

### F) Approve Plan (only if requirePlanApproval=true)
```bash
curl -sS \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:approvePlan"
```

## What to extract for the user
When a session completes, its `outputs` may include a PR URL:
- `outputs[].pullRequest.url`

## Implementation guidance for Clawdbot
- Prefer creating sessions with `automationMode: AUTO_CREATE_PR` so output is a PR.
- Always ask the user which repo/source to use if ambiguous.
- Never include secrets in prompts.

