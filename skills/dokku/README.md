# dokku-skills

OpenClaw/ClawHub skill for **Dokku**: install, upgrade, deploy apps, run one-off/background tasks, and clean up containers.

## What this skill covers

- **Install** — Installing Dokku (bootstrap, post-install, alternatives)
- **Upgrade** — Upgrading Dokku (migration guides, before/after, dokku-update, apt)
- **Cleanup** — Cleaning up Dokku and containers (prune, builder prune, apps)
- **Apps** — create, destroy, list, rename, clone, lock, unlock, report
- **Config, domains, git, run, logs, ps, plugin, certs, nginx, storage, network** — full command reference per namespace

## Install the skill locally

### Option 1: From ClawHub (after publish)

```bash
npm i -g clawhub
clawhub install dokku
```

Then start a new OpenClaw session so the skill is loaded.

### Option 2: Copy into your workspace

Copy the `dokku/` folder into your OpenClaw skills directory:

- **Workspace:** `<workspace>/skills/dokku/`
- **Global:** `~/.openclaw/skills/dokku/`

Start a new OpenClaw session after copying.

## Publish to ClawHub

From this repo root:

1. Log in: `clawhub login` (or `clawhub login --token <token>`)
2. Publish the skill:

```bash
clawhub publish ./dokku --slug dokku --name "Dokku" --version 1.0.0 --changelog "Initial release." --tags latest
```

After that, anyone can install with: `clawhub install dokku`.

## Updating the skill

1. Edit section files under `dokku/<namespace>/commands.md` or `dokku/SKILL.md`
2. Bump version in `CHANGELOG.md`
3. Publish: `clawhub publish ./dokku --slug dokku --name "Dokku" --version x.y.z --changelog "..." --tags latest`
4. Users upgrade with: `clawhub update dokku`

## License

MIT
