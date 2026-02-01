# Fly + GitHub Actions

## Production deploy (simple)

Workflow outline:
- checkout
- setup flyctl
- `fly deploy --remote-only`

Secrets:
- `FLY_API_TOKEN`

## PR previews (recommended architecture)

Goal: per-PR URL + per-PR DB.

Pattern:
- preview app per PR: `myapp-pr-<n>`
- database per PR inside shared Fly Postgres cluster: `myapp_pr_<n>`

Per PR update:
1) create app if missing
2) create db if missing
3) attach postgres to preview app
4) set env/secrets (DATABASE_URL points at per-PR db)
5) deploy
6) comment URL on PR

On PR close:
- destroy preview app
- drop PR database

Notes:
- Be conservative with secrets (use dummy/test where possible).
- Avoid destructive actions without explicit confirmation when running manually.
