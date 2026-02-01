---
name: dokku
description: Installs, upgrades, and uses Dokku to create apps, deploy, run one-off/background tasks, and clean up containers. Use when the user asks to install or upgrade Dokku, deploy to Dokku, install an app, run something in the background, or clean up Dokku/containers. Trigger terms: dokku, install dokku, upgrade dokku, migration guide, deploy, cleanup, prune, containers.
metadata: {"openclaw":{"requires":{"bins":["dokku"]}}}
---

# Dokku

Dokku is a PaaS; commands run on the Dokku host (SSH or local). Prefer running long operations (deploys, builds) in the **background** — use exec with `background: true` or short `yieldMs` when the tool allows.

## Section index

Detailed command syntax and examples live in each section file. Read the relevant file when performing that category of task.

| Section                    | File                                       | Commands / topics                                             |
| -------------------------- | ------------------------------------------ | ------------------------------------------------------------- |
| Apps                       | [apps/commands.md](apps/commands.md)       | create, destroy, list, rename, clone, lock, unlock, report    |
| Config                     | [config/commands.md](config/commands.md)   | get, set, unset, export                                       |
| Domains                    | [domains/commands.md](domains/commands.md) | add, set, remove, set-global, report                          |
| Git / deploy               | [git/commands.md](git/commands.md)         | from-image, set, deploy-branch, git push                      |
| Run (one-off / background) | [run/commands.md](run/commands.md)         | run, run:detached                                             |
| Logs                       | [logs/commands.md](logs/commands.md)       | logs, logs:failed, logs:set                                   |
| Process (ps)               | [ps/commands.md](ps/commands.md)           | scale, rebuild, restart, start, stop                          |
| Plugin                     | [plugin/commands.md](plugin/commands.md)   | list, install, update, uninstall                              |
| Certs                      | [certs/commands.md](certs/commands.md)     | add, remove, generate                                         |
| Nginx                      | [nginx/commands.md](nginx/commands.md)     | build-config, show-config, set                                |
| Storage                    | [storage/commands.md](storage/commands.md) | mount, list                                                   |
| Network                    | [network/commands.md](network/commands.md) | report, bind-all-interfaces                                   |
| **Install**                | [install/commands.md](install/commands.md) | Installing Dokku (bootstrap, post-install, alternatives)      |
| **Upgrade**                | [upgrade/commands.md](upgrade/commands.md) | Upgrading Dokku; check migration guides before upgrading      |
| **Cleanup**                | [cleanup/commands.md](cleanup/commands.md) | Cleaning up Dokku and containers (prune, builder prune, apps) |

## Quick reference

- **Create app:** `dokku apps:create <app-name>`
- **Deploy (git):** Add remote `dokku@<host>:<app-name>`, then `git push dokku <branch>:master`
- **Deploy (image):** `dokku git:from-image <app> <docker-image>`
- **Run in background (Dokku):** `dokku run:detached <app> <cmd>` or `dokku run --detach <app> <cmd>`
- **Agent-side background:** For long deploys/installs, run the shell command via exec with `background: true` or short `yieldMs`; poll or check logs as needed.

For full command details and options, see the section files above.
