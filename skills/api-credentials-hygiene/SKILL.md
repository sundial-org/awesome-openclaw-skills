---
name: api-credentials-hygiene
description: Audits and hardens API credential handling (env vars, separation, rotation plan, least privilege, auditability). Use when integrating services or preparing production deployments where secrets must be managed safely.
---

# API credentials hygiene: env vars, rotation, least privilege, auditability

## PURPOSE
Audits and hardens API credential handling (env vars, separation, rotation plan, least privilege, auditability).

## WHEN TO USE
- TRIGGERS:
  - Harden the credentials setup for this integration and move secrets into env vars.
  - Design a key rotation plan for these APIs with minimal downtime.
  - Audit this service for least-privilege access and document what each key can do.
  - Create an environment variable map and a secure .env template for this project.
  - Set up credential separation for dev versus prod with clear audit trails.
- DO NOT USE WHEN…
  - You want to obtain keys without authorization or bypass security controls.
  - You need legal/compliance sign-off (this outputs technical documentation, not legal advice).

## INPUTS
- REQUIRED:
  - List of integrations/APIs and where credentials are currently stored/used.
  - Deployment context (local dev, server, container, n8n, etc.).
- OPTIONAL:
  - Current config files/redacted snippets (.env, compose, systemd, n8n creds list).
  - Org rules (rotation intervals, secret manager preference).
- EXAMPLES:
  - “Keys are hard-coded in a Node script and an n8n HTTP Request node.”
  - “We have dev and prod n8n instances and need separation.”

## OUTPUTS
- Credential map (service → env vars → scopes/permissions → owner → rotation cadence).
- Rotation runbook (steps + rollback).
- Least-privilege checklist and audit log plan.
- Optional: `.env` template (placeholders only).
Success = no secrets committed or embedded, permissions minimized, rotation steps documented, and auditability defined.


## WORKFLOW
1. Inventory credentials:
   - where stored, where used, and who owns them.
2. Define separation:
   - dev vs prod; human vs service accounts; per-integration boundaries.
3. Move secrets to env vars / secret manager references:
   - create an env var map and update config plan (no raw keys in code/workflows).
4. Least privilege:
   - for each API, enumerate required actions and reduce scopes/roles accordingly.
5. Rotation plan:
   - dual-key overlap if supported; steps to rotate with minimal downtime; rollback.
6. Auditability:
   - define what events are logged (auth failures, token refresh, key use where available).
7. STOP AND ASK THE USER if:
   - required operations are unknown,
   - secret injection method is unclear,
   - rotation cadence/owners are unspecified.


## OUTPUT FORMAT
Credential map template:

```text
CREDENTIAL MAP
- Integration: <name>
  - Env vars:
    - <VAR_NAME>: <purpose> (secret/non-secret)
  - Permissions/scopes: <list>
  - Used by: <service/workflow>
  - Storage: <secret manager/env var>
  - Rotation: <cadence> | <owner> | <procedure>
  - Audit: <what is logged and where>
```

If providing a template, output `assets/dotenv-template.example` with placeholders only.


## SAFETY & EDGE CASES
- Never output real secrets, tokens, or private keys. Use placeholders.
- Read-only by default; propose changes as a plan unless explicitly asked to modify files.
- Avoid over-broad scopes/roles unless justified by a documented requirement.


## EXAMPLES
- Input: “n8n HTTP nodes contain API keys.”  
  Output: Env var map + plan to move to n8n credentials/env vars + rotation runbook.

- Input: “Need dev vs prod separation.”  
  Output: Two env maps + naming scheme + access boundary checklist.

