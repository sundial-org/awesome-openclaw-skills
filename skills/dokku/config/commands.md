# Config commands

All `dokku config:*` subcommands. Manage app environment variables.

## config (show)

Display environment variables for an app.

```bash
dokku config <app>
```

## config:get

Display a specific environment variable.

```bash
dokku config:get <app> <KEY>
```

## config:set

Set one or more environment variables. Triggers rebuild/release by default.

```bash
dokku config:set <app> KEY1=value1 KEY2=value2
dokku config:set --no-restart <app> KEY=value
```

## config:unset

Unset one or more environment variables.

```bash
dokku config:unset <app> KEY1 KEY2
```

## config:set:file

Set environment variables from a file (e.g. `.env`). One KEY=VALUE per line.

```bash
dokku config:set:file <app> <path>
```

## config:export

Export config to format (e.g. env, shell). Useful for backups or CI.

```bash
dokku config:export <app>
dokku config:export <app> --format env
```

## config:report

Display config report for one or all apps.

```bash
dokku config:report <app>
dokku config:report
```
