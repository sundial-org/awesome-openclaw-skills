# Apps commands

All `dokku apps:*` subcommands. Run on the Dokku host (SSH or local).

## apps:create

Create a new app.

```bash
dokku apps:create <app>
```

Example:

```bash
dokku apps:create node-js-app
```

## apps:destroy

Permanently destroy an app and all add-ons. Prompts for app name unless `--force`.

```bash
dokku apps:destroy <app>
dokku --force apps:destroy <app>
```

## apps:list

List all apps.

```bash
dokku apps:list
dokku --quiet apps:list   # one per line, no extra output
```

## apps:exists

Check if an app exists. Exits 0 if exists, non-zero otherwise. Useful for CI/CD.

```bash
dokku apps:exists <app>
```

## apps:rename

Rename an app. App must have been deployed at least once. Preserves config; rebuilds and deploys the new app. Update git remote on your machine: `git remote set-url dokku dokku@<host>:<new-app>`.

```bash
dokku apps:rename <old-app> <new-app>
dokku apps:rename --skip-deploy <old-app> <new-app>
```

## apps:clone

Clone an existing app. App must have been deployed at least once. Config is preserved; custom domains and SSL certs are not copied.

```bash
dokku apps:clone <old-app> <new-app>
dokku apps:clone --skip-deploy <old-app> <new-app>
dokku apps:clone --ignore-existing <old-app> <new-app>
```

## apps:lock

Lock an app for deployment (prevents new deploys).

```bash
dokku apps:lock <app>
```

## apps:unlock

Remove deploy lock. Does not stop in-progress deploys.

```bash
dokku apps:unlock <app>
```

## apps:locked

Check if an app is locked. Exits non-zero if no lock.

```bash
dokku apps:locked <app>
```

## apps:report

Display report about one or all apps. Use flags to output a single value (e.g. `--app-dir`).

```bash
dokku apps:report
dokku apps:report <app>
dokku apps:report <app> --app-dir
```
