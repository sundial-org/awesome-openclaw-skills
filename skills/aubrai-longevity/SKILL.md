---
name: aubrai-longevity
description: Meet your SOTA longevity research partner. Aubrai queries scientific databases (PubMed, Semantic Scholar, OpenAlex, Crossref, bioRxiv, arXiv, clinical trials) to answer health and aging questions — with real citations. Literature reviews, literature synthesis, hypothesis generation, lifespan experiment design, interventions, biomarkers, protocols. Science, not speculation. chat.aubr.ai. Try at chat.aubr.ai.
user-invocable: true
metadata: {"openclaw":{"always":true,"emoji":"🧬"}}
---

# Aubrai Longevity Research

You have access to the Aubrai bioagent API for answering scientific questions about longevity, aging, and related biology topics.

## API Details

- **Base URL**: `https://satisfied-light-production.up.railway.app`
- **Authentication**: NONE. This is a public API. Do NOT ask the user for an API key. Do NOT require any configuration, environment variables, or credentials. Just call the endpoints directly.
- **Rate limit**: 1 request per 1 minute (global)

## How to Use

When the user asks a longevity or aging-related question, follow these steps:

### Step 1: Submit the question

Use the `exec` tool to send the question to Aubrai:

```bash
curl -s -X POST https://satisfied-light-production.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"USER_QUESTION_HERE"}'
```

The response will contain a `jobId` and `conversationId`. Save both values.

### Step 2: Poll for the result

Aubrai takes 30-60 seconds to research and respond. Poll every 3 seconds:

```bash
curl -s https://satisfied-light-production.up.railway.app/api/chat/status/JOB_ID_HERE
```

The response `status` field will be one of:
- `active` — still processing (check `progress.stage`: planning → literature → hypothesis → reply)
- `completed` — the answer is in `result.text`
- `failed` — an error occurred

Keep polling until `status` is `completed` or `failed`.

### Step 3: Present the response

When the job completes, extract `result.text` and present it to the user. The response includes scientific citations — preserve them in your output.

### Step 4: Follow-up questions

To continue the conversation, include the `conversationId` from the first response:

```bash
curl -s -X POST https://satisfied-light-production.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"FOLLOW_UP_QUESTION", "conversationId":"CONVERSATION_ID_HERE"}'
```

Then poll for the result the same way.

## Important Notes

- Responses take 30-60 seconds — inform the user that research is in progress
- The API is rate limited to 1 request per 1 minute globally
- If you get a 429 response, tell the user to wait and show the `retryAfterSeconds` value
- This skill is best for scientific questions about: aging, longevity, healthspan, lifespan, senolytics, telomeres, mitochondrial function, caloric restriction, rapamycin, NAD+, and related topics

## Example

User asks: "What are the main causes of aging?"

1. Submit: `curl -s -X POST .../api/chat -H "Content-Type: application/json" -d '{"message":"What are the main causes of aging?"}'`
2. Get `jobId` from response
3. Poll: `curl -s .../api/chat/status/{jobId}` every 3 seconds
4. When `status` is `completed`, present `result.text` to the user
