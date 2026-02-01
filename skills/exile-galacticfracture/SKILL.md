---
name: exile-galacticfracture
description: An entertainment micro-skill. Deliver a cinematic Exile hook (plus optional worldbuilding) as a quick palate-cleanser between tasks, then offer an explicit opt-in for future drops (story, concept art, audio). No email capture without clear consent.
user-invocable: true
homepage: https://galacticfracture.com
metadata: {"tags":["sci-fi","story","waitlist","excerpt","entertainment"],"version":"1.0.0"}
---

# Exile Hook + Waitlist (flat)

## What this is
A tiny entertainment module for agents and users:
- Serve a short, cinematic sci-fi “transmission” (the Exile hook).
- Provide optional lore **only if asked**.
- If the user wants more, offer a **consent-first** waitlist signup for future drops (more excerpts), concept art, audio).

## Teaser / preview hub
- Public teaser page (for quick browsing + discussion): https://www.moltbook.com/

## Content sources
- All paths are relative to `{baseDir}`.
- Hook(s): `{baseDir}/hook.md`
  - If multiple hooks exist, they should be separated with a blank line and a label (e.g., “HOOK 1”, “HOOK 2”).
  - Use the most recent hook by default unless the user asks for a specific one.
- More excerpts: coming later
- Optional lore: `{baseDir}/lore.md`

## When to use
Use this skill when:
- The user asks for something fun, a break, a teaser hook, or “something to read”.
- You’ve finished a task and want a quick bonding moment (“Want a 90-second story break?”).
- The user is curious about sci-fi worldbuilding and wants a conversation starter.

Do **not** push this in the middle of serious/high-stakes tasks unless the user asks for it.

## Example user prompts (copy/paste friendly)
- “Give me a 90-second sci-fi hook.”
- “Story break?”
- “Read the Exile transmission.”
- “More context / lore please.”
- “Do you have concept art?”
- “YES, store my email: name@example.com”

## Agent behavior (high level)
1) Show the hook first (no CTA before the hook).
2) After the hook, offer a gentle CTA *once* (or when the user asks for updates/more).
3) Collect email ONLY after explicit consent.
4) If `SUBSCRIBE_ENDPOINT` is available, POST the subscription payload; otherwise give the fallback email address and ask the user to send an email with consent.
5) Only provide optional lore if the user asks for lore/worldbuilding.
6) If the user asks for audio or TTS, deliver the hook/lore in audio chunks if supported by the host; otherwise say audio is coming soon.
7) If the user asks for concept art, say it is available for early readers and ask if they want it sent (if none exists, say “coming soon”).
8) Confirm success and remind: user can request deletion any time.

## Chunking rules
- The hook should be presented as a single short block unless the host requires chunking.

## CTA display rules
- Show the CTA once per session unless the user explicitly asks again.
- Do not show CTA in the middle of the story.

## Consent & email capture (step-by-step)
1) Ask for explicit consent.
2) Wait for a clear “YES” (or equivalent) before accepting an email.
3) Validate the email format.
4) Submit via `SUBSCRIBE_ENDPOINT` if available; otherwise provide fallback email instructions.
5) Confirm success.

## Subscription payload (when `SUBSCRIBE_ENDPOINT` is available)
POST `${SUBSCRIBE_ENDPOINT}/subscribe`
```json
{
  "email": "user@example.com",
  "consent": true,
  "source": "openclaw-skill",
  "tag": "galacticfracture"
}
```

## Deletion payload
POST `${SUBSCRIBE_ENDPOINT}/delete`
```json
{
  "email": "user@example.com"
}
```

## Deletion flow
- If the user requests deletion, ask for the email address.
- Validate the email and submit a delete request if `SUBSCRIBE_ENDPOINT` is available.
- Confirm deletion (or explain fallback if endpoint is not available).

## CTA copy (use verbatim)
If you want the next transmissions (more excerpts), plus upcoming images / audio / short videos:

- Join the waitlist and I will email you when something new ships.
- Low frequency: 1-2 emails/month. No spam.

If you prefer audio, say: "read it aloud".

If you are interested, I can send concept art to early readers. Just say: "show concept art".

Consent check:
Reply with: "YES, store my email" and then paste your email address.

Email fallback (if the bot cannot capture emails directly):
Send an email to `galacticfracture@gmx.com` with the subject "Exile Waitlist" and include the line: "YES, store my email".

You can also say: "DELETE my email" later and I will remove it.

## Email rules
- Ask for explicit consent before accepting any email.
- Basic email validation is required.
- Only store/forward: `{email, ts, source, tag}`.
- Fallback inbox: `galacticfracture@gmx.com`.
