---
name: flyio-cli-public
description: "Use the Fly.io flyctl CLI for deploying and operating apps on Fly.io: deploys (local or remote builder), viewing status/logs, SSH/console, secrets/config, scaling, machines, volumes, and Fly Postgres (create/attach/manage databases). Use when asked to deploy to Fly.io, debug fly deploy/build/runtime failures, set up GitHub Actions deploys/previews, or safely manage Fly apps and Postgres."
---

# Fly.io (flyctl) CLI

Operate Fly.io apps safely and repeatably with `flyctl`.

## Common tasks

- Deploy: `fly deploy` / `fly deploy --remote-only`
- Logs: `fly logs -a <app>`
- SSH / run commands: `fly ssh console -a <app> -C "…"`
- Secrets: `fly secrets list/set -a <app>`
- Postgres: `fly postgres list/connect/db create/attach`
- GitHub Actions deploys / PR previews

## Defaults / safety

- Prefer **read-only** commands first: `fly status`, `fly logs`, `fly config show`, `fly releases`, `fly secrets list`.
- **Do not run state-changing Fly.io commands without explicit user approval** (deploy/scale, secrets set/unset, volume/db create/drop, app destroy, attach/detach).
  - Read-only actions are OK without approval.
  - Destructive actions (destroy/drop) always require explicit approval.
- When debugging, classify the failure as: build/packaging vs runtime vs platform.

## Quick start (typical deploy)

From the app repo directory:

1) Confirm which app you’re targeting
- `fly app list`
- `fly status -a <app>`
- Check `fly.toml` for `app = "..."`

2) Deploy
- `fly deploy` (default)
- `fly deploy --remote-only` (common when local docker/build env is inconsistent)

3) Validate
- `fly status -a <app>`
- `fly logs -a <app>`
- `fly open -a <app>`

## Debugging deploy/build failures

### Common checks
- `fly deploy --verbose` (more build logs)
- If using Dockerfile builds: verify Dockerfile Ruby/version and Gemfile.lock platforms match your builder OS/arch.

### Rails + Docker + native gems (nokogiri, pg, etc.)
Symptoms: Bundler can’t find a platform gem like `nokogiri-…-x86_64-linux` during build.

Fix pattern:
- Ensure `Gemfile.lock` includes the Linux platform used by Fly’s builder (usually `x86_64-linux`).
  - Example: `bundle lock --add-platform x86_64-linux`
- Ensure Dockerfile’s Ruby version matches `.ruby-version`.

(See `references/rails-docker-builds.md`.)

## Logs, SSH, console

- Stream logs:
  - `fly logs -a <app>`
- SSH console:
  - `fly ssh console -a <app>`
- Run a one-off command:
  - `fly ssh console -a <app> -C "bin/rails db:migrate"`

## Secrets / config

- List secrets:
  - `fly secrets list -a <app>`
- Set secrets:
  - `fly secrets set -a <app> KEY=value OTHER=value`
- Show config:
  - `fly config show -a <app>`

## Fly Postgres basics

### Identify the Postgres app
- `fly postgres list`

### Attach Postgres to an app
- `fly postgres attach <pg-app> -a <app>`

### Create a database inside the cluster
- `fly postgres db create <db_name> -a <pg-app>`
- `fly postgres db list -a <pg-app>`

### Connect (psql)
- `fly postgres connect -a <pg-app>`

## GitHub Actions deploys / previews

- For production CD: use Fly’s GitHub Action (`superfly/flyctl-actions/setup-flyctl`) and run `fly deploy` (often with `--remote-only`).
- For PR previews:
  - Prefer one **preview app per PR** and one **database per PR** inside a shared Fly Postgres cluster.
  - Automate create/deploy/comment on PR; destroy on close.

(See `references/github-actions.md`.)

## Bundled resources

- `references/rails-docker-builds.md`: Rails/Docker/Fly build failure patterns + fixes.
- `references/github-actions.md`: Fly deploy + preview workflows.
- `scripts/fly_app_from_toml.sh`: tiny helper to print the Fly app name from fly.toml.
