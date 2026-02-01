---
name: 4todo
description: Manage 4todo (4to.do) from chat. Capture tasks, prioritize with the Eisenhower Matrix, reorder, complete, and manage recurring tasks across workspaces.
---

# 4todo
[4to.do](https://4to.do) Eisenhower Matrix To‑Do List

## Goal

- Use `curl` to call the 4todo API (`https://4to.do/api/v0`) to manage:
  - workspaces
  - todos
  - recurring todos
- Store the token in a way that is injectable but not leak-prone (prefer OpenClaw per-run env injection; do not paste secrets into prompts, logs, or repo files).

## Required Environment Variable

- `FOURTODO_API_TOKEN`: your 4todo API token (Bearer token)
- If missing, ask the user to set it via OpenClaw config (do not ask them to paste the token into chat).

## Runtime Requirement

- `curl` must be available on `PATH` (and inside the sandbox container, if the agent is sandboxed).

## User-facing output rules (important)

- Be non-technical by default. Focus on outcomes, not implementation.
  - Avoid mentioning: curl, endpoints, headers, API mechanics, JSON payloads, config patches.
  - Mention technical details only when debugging or if the user explicitly asks “how does it work?”.
- Do not print internal IDs by default:
  - Do **not** show `ws_...`, `todo_...`, `rec_todo_...` unless the user asks.
  - Refer to workspaces and tasks by **name**.
  - If disambiguation is needed (duplicate names), ask a clarifying question and present a short numbered list of names; only offer IDs if the user requests them.
- Quadrants:
  - In chat, prefer plain language: “urgent & important”, “important (not urgent)”, “urgent (not important)”, “neither”.
  - Use `IU | IN | NU | NN` internally for API calls. Only show codes if the user uses codes first or explicitly asks.

### Examples (preferred)

Workspaces:

```
Your workspaces:
1) Haoya (default)
2) 4todo
3) Echopark
```

Todos (summary):

```
Urgent & important:
1) UK company dissolution
2) Hetzner monthly payment (recurring, monthly)

Important (not urgent):
1) Weekly review (recurring, Fridays)
```

## Store / Inject the Token in OpenClaw (recommended)

OpenClaw can inject environment variables only for the duration of an agent run (then restores the original env), which helps keep secrets out of prompts.

Recommended (production): set `FOURTODO_API_TOKEN` in your Gateway process environment using your hosting provider’s secret store, and do not store tokens in chat logs.

### Host runs (not sandboxed): use `skills.entries`

Edit `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "4todo": {
        enabled: true,
        env: {
          FOURTODO_API_TOKEN: "YOUR_4TODO_API_TOKEN"
        }
      }
    }
  }
}
```

Notes:
- `skills.entries.<skill>.env` is injected only if the variable is not already set.

### Sandboxed sessions: use `agents.defaults.sandbox.docker.env`

When a session is sandboxed, skill env injection does **not** propagate into the Docker container. Provide the token via Docker env:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          env: {
            FOURTODO_API_TOKEN: "YOUR_4TODO_API_TOKEN"
          }
        }
      }
    }
  }
}
```

## Request Conventions

- Every request must include `Authorization: Bearer <token>`.
- Requests with a JSON body must include `Content-Type: application/json`.
- `GET /todos` requires a `workspace` query parameter.
- Quadrants: `IU | IN | NU | NN` (internal).

## Workflow (recommended order)

Copy this checklist and keep it updated while executing:

```
Task checklist:
- [ ] List workspaces (pick `ws_...`)
- [ ] List todos for that workspace
- [ ] Perform the requested mutation (create / complete / reorder / recurring)
- [ ] Re-fetch to verify the change
```

1. `GET /workspaces`: pick a target `ws_...` (usually the default workspace).
2. `GET /todos?workspace=ws_...`: fetch todos (grouped by quadrant).
3. Create: `POST /todos`.
4. Complete: `POST /todos/:id/complete` (idempotent).
5. Reorder / move quadrant: `POST /todos/reorder`.
6. Recurring todos: use the `/recurring-todos` endpoints.

## HTTP Examples (curl)

This skill intentionally uses `curl` for maximum portability across OSes and environments.

Notes:
- HTTPS only (`https://4to.do/api/v0`).
- Always pass the token via `FOURTODO_API_TOKEN` (never paste tokens into chat).

```bash
curl -sS -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" "https://4to.do/api/v0/workspaces"
curl -sS -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" "https://4to.do/api/v0/todos?workspace=ws_...&show=all"
curl -sS -X POST -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"name":"...","quadrant":"IU","workspace_id":"ws_..."}' "https://4to.do/api/v0/todos"
curl -sS -X POST -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" "https://4to.do/api/v0/todos/todo_.../complete"
curl -sS -X POST -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"moved_todo_id":"todo_...","previous_todo_id":"todo_...","next_todo_id":null,"quadrant":"IN"}' "https://4to.do/api/v0/todos/reorder"
```
Note: if `moved_todo_id` starts with `rec_todo_`, the API updates only the recurring todo quadrant and ignores `previous_todo_id/next_todo_id`.

## Common Error Handling (agent guidance)

- `401 token_expired / token_paused / invalid_token`: stop retrying; ask the user to create a new token in 4todo settings and update OpenClaw config.
- `402 WORKSPACE_RESTRICTED`: the workspace is read-only; do not retry mutations; switch workspace or prompt user to upgrade/unlock.
- `429 rate_limited`: honor `Retry-After` / `X-RateLimit-*` and back off before retry.
- `400 Invalid quadrant type`: ensure quadrant is one of `IU|IN|NU|NN`.

## Reference

- Full API doc bundled with this skill: `{baseDir}/references/api_v0.md`
