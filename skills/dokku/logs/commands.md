# Logs commands

View and manage application and deploy logs.

## logs

Display recent log output for an app.

```bash
dokku logs <app>
dokku logs -t <app>          # follow (tail)
dokku logs -n 100 <app>      # last N lines
dokku logs -p web <app>      # specific process type
dokku logs -q <app>          # quiet (raw, no colors/timestamps)
```

## logs:failed

Show logs from the last failed deploy.

```bash
dokku logs:failed <app>
```

## logs:set

Set log properties (e.g. max size for Docker log driver).

```bash
dokku logs:set <app> max-size 10m
```

## logs:report

Display logs report for one or all apps.

```bash
dokku logs:report
dokku logs:report <app>
```

## logs:vector-\*

If Vector logging plugin is installed, additional `logs:vector-*` subcommands may be available for log shipping.
