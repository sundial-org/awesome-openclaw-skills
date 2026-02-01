---
name: confidant
description: Secure secret handoff from human to AI. Use when you need sensitive information from the user (API keys, passwords, tokens, credentials, secrets). Never ask for secrets via chat — use Confidant instead.
---

# Confidant - Secure Secret Handoff

Confidant enables secure secret sharing without exposing sensitive data in chat logs. It supports multiple flows depending on who needs to send and receive secrets.

**Key principle:** Whoever needs to RECEIVE the secret runs `serve-request`. Whoever needs to SEND uses `fill` (or the browser form).

## Flows

### 1. User-to-Agent (User sends secret to AI)

**When to use:** You need a secret from the user (API key, password, token).

**How it works:**

1. You (the Agent) run `serve-request` to create a URL
2. You share the URL with the user
3. User opens the URL in their browser and submits the secret
4. You receive the secret in your terminal

**Your command:**

```bash
npx @aiconnect/confidant serve-request --label "<description>"
```

**Example conversation:**

> **AI:** I need your API key to continue. Let me create a secure link...
>
> *(AI executes: `npx @aiconnect/confidant serve-request --label "API Key"`)*
>
> **AI:** Open this link in your browser and enter your API key:
> `http://localhost:3000/requests/abc123`
>
> *(User opens URL in browser, submits the secret)*
>
> **AI:** Got your API key securely!

---

### 2. Agent-to-User (AI sends secret to User)

**When to use:** You need to securely deliver a secret to the user (generated password, API key, credential).

**How it works:**

1. User runs `serve-request` to create a URL (they will receive)
2. User shares the URL with you
3. You execute `fill` to send the secret
4. User sees the secret appear in their terminal

**Your command:**

```bash
npx @aiconnect/confidant fill "<url>" --secret "<value>"
```

**Example conversation:**

> **AI:** I generated your new password. To receive it securely, run:
>
> ```
> npx @aiconnect/confidant serve-request --label "New Password"
> ```
>
> Send me the URL that appears.
>
> **User:** `http://192.168.1.100:3000/requests/abc123`
>
> *(AI executes: `npx @aiconnect/confidant fill "http://..." --secret "...")*
>
> **AI:** Done! The password appeared in your terminal.

---

### 3. Agent-to-Agent (Automated secret sharing)

**When to use:** Automated credential distribution between systems/agents.

**How it works:**

1. Agent A (receiver) runs: `npx @aiconnect/confidant serve-request --label "DB Credentials"`
2. Agent A shares the URL with Agent B (via API, orchestrator, etc.)
3. Agent B (sender) submits: `npx @aiconnect/confidant fill "<url>" --secret "<value>"`
4. Agent A receives the secret

**Secure input (avoid shell history):**

```bash
echo "$SECRET" | npx @aiconnect/confidant fill "<url>" --secret -
```

---

## Command Reference

### Create request and wait for secret

```bash
npx @aiconnect/confidant serve-request --label "<description>"
```

### Submit secret to existing request

```bash
npx @aiconnect/confidant fill "<url>" --secret "<value>"
```

### Output options

- `--quiet` — Minimal output (just URLs and secret)
- `--json` — JSON output for parsing/automation

---

## Important Rules

- **NEVER ask users to paste secrets in chat** — always use Confidant
- **NEVER reveal received secrets in chat** — not even partially
- Secrets auto-expire after 24h if not used
- One-time read, then deleted
- If user is remote, they may need tunneling (ngrok, Tailscale, etc.)

---

## After Receiving/Sending

- Confirm completion: "Got the secret!" or "Sent! Check your terminal."
- Use the secret silently for the intended task
- Never echo or log the secret value
